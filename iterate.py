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

from constants import PRECISION
from geometry import Line
from point import Point2, Point3
from special_functions import harmonic, phi, phi_bar, phi_big, u1, u2, u3
from utility import isclose_prec, signum


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    result
        numpy arrays x, y, colors returned

    '''
    result = pyqtSignal(object, object, object)


class Worker(QRunnable):
    """Main class that «plays» chaos game with settings.
    """

    def __init__(self):
        # For threading
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = ()
        self.kwargs = {}
        self.signals = WorkerSignals()

        self.start_point = Point3(0, 0, 1)
        self._vertices: List[Point3] = []
        # self.checker = self.shapely_default
        # self.checker = self.polygon_default
        self.checker = lambda p: self.shapely_default(p) and self.polygon_default(p)
        self.strategy = lambda verticies, prev: choice(verticies)
        self.vertices_colors = []
        self.double_mid = False
        self.frame_type = 2

        self.precision = PRECISION
        self.decimals = 9

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self) -> list:
        """Getter for vertices of triangle, rectangle etc.
        """
        return self._vertices

    @property
    def colors(self) -> list:
        """Getter for colors of points.
        """
        return list(self._colors)

    @vertices.setter
    def vertices(self, value) -> List[Point3]:
        """Setter for vertices. Builds  shapely polygon when points are set. Computes sings for polygon_default method

        Args:
            value (List[Point3]): self._vertices = value
        """
        self._vertices = value

        vertices_2d = [i.to_point2().to_float() for i in self._vertices]

        pairs = [i.to_tuple() for i in vertices_2d]

        # self.poly = Polygon(pairs)
        self.poly = Polygon(pairs).buffer(0.1, quad_segs=2**7)
        self.poly_prep = prep(self.poly)

        vertices_2d += [vertices_2d[0]]
        vertices_zipped = zip(vertices_2d, vertices_2d[1:])

        self.equations = [Line(a, b).equation
                          for a, b in vertices_zipped]

        point_inside = self.gen_start_point().to_point2()

        self.signs = [signum(f(point_inside.x, point_inside.y))for f in self.equations]


    def gen_random_colors(self) -> list:
        """Generating random colors in format #123456 for each vertex.
        """
        data = '0123456789ABCDEF'

        answer = ['#' + ''.join([choice(data) for j in range(6)])
                  for i in range(len(self.vertices))]

        return answer


    def shapely_default(self, point: Point3) -> bool:
        """Use built-in shapely method to check that points fit

        Args:
            point (Point3): point to check

        Returns:
            bool: point \\in Polygon?
        """
        cur = point.to_point2().to_float()

        return self.poly_prep.contains(Point(cur.x, cur.y))


    def polygon_default(self, point: Point3) -> bool:
        """Use fact that we have polygon. Point signs in line equations should
           be the same as starting point.

        Args:
            point (Point3): point to check

        Returns:
            bool: point \\in Polygon?
        """
        cur = point.to_point2().to_float()

        for idx, f in enumerate(self.equations):
            cur_sign = signum(f(cur.x, cur.y))

            if abs(cur_sign) > 0 and cur_sign != self.signs[idx]:
                return False

        return True


    def gen_start_point(self) -> Point3:
        """Randomly choose starting point using shapely polygon bounds method.

        Returns:
            Point3: random point inside
        """
        minx, miny, maxx, maxy = self.poly.bounds

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)

        # Point is from shapely.geometry
        while not self.shapely_default(Point3(x,  y, 1)):
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)

        return Point3(x, y, 1)

    def guess_limits(self, contains_absolute=False) -> Tuple[float, float, float, float]:
        """Fit polygon and maybe absolute to screen

        Args:
            contains_absolute (bool, optional): consider absolute. Defaults to False.

        Returns:
            Tuple[float, float, float, float]: xmin, xmax, ymin, ymax for plotter
        """
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
                   m: Point3,
                   b: Point3,
                   rel=1,
                   inside=True) -> Point3:
        """Main method that divides «segment» in appropriate relation.

        Args:
            m (Point3): _description_
            b (Point3): _description_
            rel (int, optional): relation for segment division. Defaults to 1.
            inside (bool, optional): double middle plotting. Defaults to True.

        Returns:
            Point3: division result
        """

        from mid_first_lambda import coord

        val = phi_big(m, b)

        if val > 0:
            mu = rel / (1 + rel)

            return Point3(coord(1, m, b, mu),
                          coord(2, m, b, mu),
                          coord(3, m, b, mu))
        elif isclose_prec(abs(val), 0):
            from mid_first_lambda_parabolic import coord

            return Point3(coord(1, m, b, rel),
                          coord(2, m, b, rel),
                          coord(3, m, b, rel))

        # val < 0
        if isclose_prec(abs(phi_bar(m, b)), 0):
            mu = rel / (1 + rel)

            c1 = Point3(coord(1, m, b, mu),
                        coord(2, m, b, mu),
                        coord(3, m, b, mu))

            mu = -rel / (1 + rel)

            c2 = Point3(coord(1, m, b, mu),
                        coord(2, m, b, mu),
                        coord(3, m, b, mu))

            if self.checker(c1) == inside:
                return c1

            return c2

        # phi_bar(m, b) \neq 0
        vertices_2d = [i.to_point2().to_float() for i in self._vertices]
        vertices_2d += [vertices_2d[0]]
        vertices2d_zipped = zip(vertices_2d, vertices_2d[1:])

        h_points = []
        for bi, bj in vertices2d_zipped:
            line_m_b = Line(m.to_point2().to_float(),
                            b.to_point2().to_float())

            result = line_m_b.intersect(Line(bi, bj))

            if result not in self.vertices:
                h_points.append(result.to_point3(1))

        # Almost surely h_points is empty after this. Don't know correct solution.
        # See work method.
        # if len(h_points) > 1:
        #     h_points = list(filter(self.polygon_default, h_points))

        if not h_points:
            return Point3(inf, inf, inf)

        h: Point3 = choice(h_points)

        b_star = Point3(-b[2] * u3(m, b) - b[3] * u2(m, b),
                        b[1] * u3(m, b) + b[3] * u1(m, b),
                        b[2] * u1(m, b) - b[1] * u2(m, b))

        if harmonic(m, b, h, b_star).real > 0:
            mu = rel / (1 + rel)

            return Point3(coord(1, m, b, mu),
                          coord(2, m, b, mu),
                          coord(3, m, b, mu))

        # Due to precision errors this sometimes doesn't work
        try:
            angle = acos(abs(phi_bar(m, b)) / (sqrt(phi(m)) * sqrt(phi(b))))
        except ValueError:
            return Point3(inf, inf, inf)

        m_star = Point3(-m[2] * u3(m, b) - m[3] * u2(m, b),
                        m[1] * u3(m, b) + m[3] * u1(m, b),
                        m[2] * u1(m, b) - m[1] * u2(m, b))

        if isclose(rel, pi / (pi - 2 * angle)):
            return self.div_in_rel(m_star, b, rel, inside)

        if rel < (pi - 2 * angle) / pi:
            mu = (2 * rel * (pi - angle)) / ((1 + rel) * (pi - 2 * angle))

            return Point3(coord(1, m, b_star, mu),
                          coord(2, m, b_star, mu),
                          coord(3, m, b_star, mu))

        if (pi - 2 * angle) / pi < rel < pi / (pi - 2 * angle):
            mu = (2 * angle + pi * (rel - 1)) / (2 * angle * (rel + 1))

            return Point3(coord(1, b_star, m_star, mu),
                          coord(2, b_star, m_star, mu),
                          coord(3, b_star, m_star, mu))

        # rel > pi / (pi - 2 * angle):
        mu = (pi * (rel - 1) - 2 * rel * angle) / ((1 + rel) * (pi - 2 * angle))

        return Point3(coord(1, m_star, b, mu),
                      coord(2, m_star, b, mu),
                      coord(3, m_star, b, mu))

    @pyqtSlot()
    def run(self):
        """Method that runs when thread starts.
        """
        x, y, colors = self.work(*self.args, **self.kwargs)

        self.signals.result.emit(x, y, colors)

    def work(self, cnt: int, rel=1):
        """Main method that «plays» chaos game.
        """
        def add_point(point: Point2,
                      x: List[float],
                      y: List[float],
                      vert,
                      colors) -> bool:
            # bounds = cur.isfinite()\
            #          and self.xmin <= point.x <= self.xmax\
            #          and self.ymin <= point.y <= self.ymax
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

        prev: List[Point3] = []
        cur: Point2 = self.start_point.to_point2()

        print(cur)

        for _ in range(cnt):
            b: Point3 = self.strategy(self.vertices, prev)
            m = self.div_in_rel(cur.to_point3(1), b, rel=rel)

            if not self.checker(m):
                print(f'bad')
                continue

            m = m.to_point2().to_float()

            if add_point(m,
                         x_coords,
                         y_coords,
                         vert=b,
                         colors=colors):
                prev.append(b)
                cur = m

            # if self.double_mid:
            #     for val in [rel, -rel]:
            #         out = self.div_in_rel(b, cur, rel=val, inside=False)
            #         add_point(out,
            #                   x_coords,
            #                   y_coords,
            #                   vert=b,
            #                   colors=colors)

        return np.array(x_coords), np.array(y_coords), np.array(colors)

    def clean(self, x, y, colors):
        """Take quotient of points by digits parameter.

        Args:
            x (List[float]): x's coordinates
            y (List[float]): y's coordinates
            colors (List[str]): color of every point

        Returns:
            tuple[List[float], List[float], List[str]]: result of cleaning
        """
        x = np.round(x, decimals=self.decimals)
        y = np.round(y, decimals=self.decimals)

        _, idx = np.unique(x + 1j * y, return_index=True)

        x = np.take(x, idx)
        y = np.take(y, idx)
        colors = np.take(colors, idx, mode='clip')

        return x, y, colors
