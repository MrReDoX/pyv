"""Module that perfoms chaos game on plane."""

from cmath import inf, isclose, pi
from math import acos, sqrt
from random import choice, uniform
from typing import List, Tuple

import numpy as np
from pyqtgraph.Qt.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal,
                                 pyqtSlot)
from shapely.geometry import Point, Polygon
from shapely.prepared import prep

from point import Point2, Point3
from utility import PRECISION, harmonic, line_intersection, u1, u2, u3


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    result
        numpy arrays x, y, colors returned

    '''
    result = pyqtSignal(object, object, object)


class Worker(QRunnable):
    """Main class that «plays» chaos game with settings."""

    def __init__(self):
        # For threading
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = ()
        self.kwargs = {}
        self.signals = WorkerSignals()

        self.start_point = Point2(0.0, 0.0)
        self._vertices = []
        self.checker = self.shapely_default
        self.strategy = lambda verticies, prev: choice(verticies)
        self.vertices_colors = []
        self.double_mid = False
        self.projective = 1
        self.frame_type = 2

        self.precision = PRECISION
        self.decimals = 9

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self) -> list:
        """Getter for vertices of triangle, rectangle etc."""
        return self._vertices

    @property
    def colors(self) -> list:
        """Getter for colors of chaos game points."""
        return list(self._colors)

    @vertices.setter
    def vertices(self, value):
        """Setter for vertices. Builds shapely polygon when points are set."""
        self._vertices = value

        pairs = [(i.to_point2().x, i.to_point2().y) for i in self.vertices]

        self.poly = Polygon(pairs)
        self.poly_prep = prep(self.poly)

    def gen_random_colors(self) -> list:
        """Generating random colors in format #123456 for each vertex."""
        data = '0123456789ABCDEF'

        answer = ['#' + ''.join([choice(data) for j in range(6)])
                  for i in range(len(self.vertices))]

        return answer

    def shapely_default(self, point: Point2) -> bool:
        """Use built-in shapely method to check that points fit."""
        return self.poly_prep.contains(Point(point.x, point.y))

    def gen_start_point(self) -> Point2:
        """Randomly choose starting point."""
        minx, miny, maxx, maxy = self.poly.bounds

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)

        # Point is from shapely.geometry
        while not self.poly_prep.contains(Point(x, y)):
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)

        return Point2(x, y)

    def guess_limits(self, contains_absolute=False) -> Tuple[float, float, float, float]:
        """Try to guess x and y limits for picture."""
        xmin, ymin = inf, inf
        xmax, ymax = -inf, -inf

        for (curx, cury) in [i.to_point2().to_tuple() for i in self.vertices]:
            xmin = min(xmin, curx)
            xmax = max(xmax, curx)

            ymin = min(ymin, cury)
            ymax = max(ymax, cury)

        if contains_absolute:
            xmin = min(xmin, -1)
            xmax = max(xmax, 1)

            ymin = min(ymin, -1)
            ymax = max(ymax, 1)

        xmin -= 0.5
        xmax += 0.5

        ymin -= 0.5
        ymax += 0.5

        return xmin, xmax, ymin, ymax

    def div_in_rel(self,
                   vertex: Point3,
                   cur: Point3,
                   rel=1,
                   inside=True) -> Point2:
        """Main method that divides «segment» in appropriate relation."""

        from mid_first_lambda import coord
        val = u1(vertex, cur)**2 + u2(vertex, cur)**2 - u3(vertex, cur)**2
        scal = vertex.x * cur.x + vertex.y * cur.y - vertex.z - cur.z

        conds = [isclose(abs(val), 0, rel_tol=self.precision),
                 isclose(abs(scal), 0, rel_tol=self.precision),
                 val > 0]
        if all(conds):
            p1 = Point3(coord(1, vertex, cur, 1 / (1 + rel)),
                        coord(2, vertex, cur, 1 / (1 + rel)),
                        coord(3, vertex, cur, 1 / (1 + rel))).to_point2().to_float()

            p2 = Point3(coord(1, vertex, cur, -1 / (1 + rel)),
                        coord(2, vertex, cur, -1 / (1 + rel)),
                        coord(3, vertex, cur, -1 / (1 + rel))).to_point2().to_float()

            if not p1.isfinite() and not p2.isfinite():
                return Point2(inf, inf)

            if self.checker(p1) == inside:
                return p1

            if self.checker(p2) == inside:
                return p2

            return Point2(inf, inf)

        if isclose(abs(val), 0, rel_tol=self.precision):
            from mid_first_lambda_parabolic import coord

            ans = Point3(coord(1, vertex, cur, rel),
                         coord(2, vertex, cur, rel),
                         coord(3, vertex, cur, rel)).to_point2().to_float()

            if not ans.isfinite():
                return Point2(inf, inf)

            return ans
        if val > 0:
            ans = Point3(coord(1, vertex, cur, 1 / (1 + rel)),
                         coord(2, vertex, cur, 1 / (1 + rel)),
                         coord(3, vertex, cur, 1 / (1 + rel))).to_point2().to_float()

            if not ans.isfinite():
                return Point2(inf, inf)

            return ans

        vertices_2d = [i.to_point2() for i in self._vertices]
        vertices_2d += [vertices_2d[0]]
        vertices_zipped = zip(vertices_2d, vertices_2d[1:])

        h_points = []
        for bi, bj in vertices_zipped:
            vertex_2d = vertex.to_point2()
            cur_2d = cur.to_point2()

            h_points.append(line_intersection(bi.x, bi.y,
                                              bj.x, bj.y,
                                              vertex_2d.x, vertex_2d.y,
                                              cur_2d.x, cur_2d.y))

        h_points = list(filter(lambda t: t.isfinite() and t != vertex, h_points))

        h = h_points.pop()

        u_1 = u1(vertex, cur)
        u_2 = u2(vertex, cur)
        u_3 = u3(vertex, cur)

        vertex_star = Point3(-vertex.y * u_3 - vertex.z * u_2,
                             vertex.x * u_3 + vertex.z * u_1,
                             vertex.y * u_1 - vertex.x * u_2)

        if harmonic(cur, vertex, h, vertex_star) > 0:
            ans = Point3(coord(1, vertex, cur, 1 / (1 + rel)),
                         coord(2, vertex, cur, 1 / (1 + rel)),
                         coord(3, vertex, cur, 1 / (1 + rel))).to_point2().to_float()

            good_conds = [ans.isfinite(), self.checker(ans) == inside]

            if not all(good_conds):
                return Point2(inf, inf)

            return ans

        vertex_phi = sqrt(vertex.x**2 + vertex.y**2 - vertex.z**2)
        cur_phi = sqrt(cur.x**2 + cur.y**2 - cur.z**2)

        phi = acos(abs(scal) / (vertex_phi * cur_phi))

        if isclose(rel, (pi - 2 * phi) / pi, rel_tol=1e-15):
            return vertex_star.to_point2().to_float()

        if isclose(rel, pi / (pi - 2 * phi), rel_tol=1e-15):
            cur_star = Point3(-cur.y * u_3 - cur.z * u_2,
                              cur.x * u_3 + cur.z * u_1,
                              cur.y * u_1 - cur.x * u_2)

            return cur_star.to_point2().to_float()

        if rel < (pi - 2 * phi) / pi:
            ans = Point3(coord(1, vertex, cur, (1 + 2 * rel) / (1 + rel)),
                         coord(2, vertex, cur, (1 + 2 * rel) / (1 + rel)),
                         coord(3, vertex, cur, (1 + 2 * rel) / (1 + rel))).to_point2().to_float()

            good_conds = [ans.isfinite(), self.checker(ans) == inside]

            if not all(good_conds):
                return Point2(inf, inf)

            return ans

        if (pi - 2 * phi) / pi < rel < pi / (pi - 2 * phi):
            ans = Point3(coord(1, vertex, cur, 1 / (1 + rel)),
                         coord(2, vertex, cur, 1 / (1 + rel)),
                         coord(3, vertex, cur, 1 / (1 + rel))).to_point2().to_float()

            good_conds = [ans.isfinite(), self.checker(ans) == inside]

            if not all(good_conds):
                return Point2(inf, inf)

            return ans

        ans = Point3(coord(1, vertex, cur, -1 / (1 + rel)),
                     coord(2, vertex, cur, -1 / (1 + rel)),
                     coord(3, vertex, cur, -1 / (1 + rel))).to_point2().to_float()

        good_conds = [ans.isfinite(), self.checker(ans) == inside]

        if not all(good_conds):
            return Point2(inf, inf)

        return ans

    @pyqtSlot()
    def run(self):
        """Method that runs when thread starts."""
        x, y, colors = self.work(*self.args, **self.kwargs)

        self.signals.result.emit(x, y, colors)

    def work(self, cnt: int, rel=1):
        """Main method that «plays» chaos game."""
        def add_point(point, x, y, vert=None, colors=None):
            bounds = point.isfinite()\
                     and self.xmin <= point.x <= self.xmax\
                     and self.ymin <= point.y <= self.ymax

            if not bounds:
                return False

            x.append(point.x)
            y.append(point.y)
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        x_coords: List[float] = []
        y_coords: List[float] = []
        colors: List[str] = []

        prev = []
        cur = self.start_point.to_point3(self.projective)

        print(cur)

        for _ in range(cnt):
            vertex = self.strategy(self.vertices, prev)
            prev.append(vertex)

            result = self.div_in_rel(vertex, cur, rel=rel)

            if add_point(result,
                         x_coords,
                         y_coords,
                         vert=vertex,
                         colors=colors):
                cur = result.to_point3(self.projective)

            if self.double_mid:
                for val in [rel, -rel]:
                    out = self.div_in_rel(vertex, cur, rel=val, inside=False)
                    add_point(out,
                              x_coords,
                              y_coords,
                              vert=vertex,
                              colors=colors)

        return np.array(x_coords), np.array(y_coords), np.array(colors)

    def clean(self, x, y, colors):
        """Take quotient of points by current precision."""
        x = np.round(x, decimals=self.decimals)
        y = np.round(y, decimals=self.decimals)

        _, idx = np.unique(x + 1j * y, return_index=True)

        x = np.take(x, idx)
        y = np.take(y, idx)
        colors = np.take(colors, idx, mode='clip')

        return x, y, colors
