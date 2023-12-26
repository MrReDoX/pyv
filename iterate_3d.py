"""Module that perfoms chaos game in space."""

# import cProfile
from math import inf
from random import choice, uniform
from typing import List, Tuple

import numpy as np
from pyqtgraph.Qt.QtCore import *
from pyqtgraph.Qt.QtGui import *
from pyqtgraph.Qt.QtWidgets import *
from shapely.geometry import Point, Polygon

from mid_3d import get_coords
from point import Point2, Point3, nPoint
from utility import PRECISION


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object, object, object, object)


class Worker3D(QRunnable):
    """Main class that «plays» chaos game with settings."""
    def __init__(self):
        # For threading
        super(Worker3D, self).__init__()
        self.threadpool = QThreadPool()
        self.args = None
        self.kwargs = None
        self.signals = WorkerSignals()

        self.start_point = nPoint(0.0, 0.0, 0.0)
        self._vertices = []
        self.checker = self.convex_trick
        self.vertices_colors = []
        self.coloring = True
        self.double_mid = False
        self.projective = 1
        self.frame_type = 2

        self.precision = PRECISION
        self.decimals = 3

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self) -> list:
        """Getter for vertices of triangle, rectangle etc."""
        return self._vertices

    # @property
    # def x(self) -> list:
    #     """Getter for x coordinates of chaos game points."""
    #     return list(self._x)

    # @property
    # def y(self) -> list:
    #     """Getter for y coordinates of chaos game points."""
    #     return list(self._y)

    @property
    def colors(self) -> list:
        """Getter for colors of chaos game points."""
        return list(self._colors)

    @vertices.setter
    def vertices(self, value):
        """Setter for vertices. Builds shapely polygon when points are set."""
        self._vertices = value

        # pairs = [(i.to_point2().x, i.to_point2().y) for i in self.vertices]
        # pairs = [(i.to_lower_dimension().x, i.to_point2().y) for i in self.vertices]
        pairs = [i.to_lower_dimension().to_tuple() for i in self.vertices]

        self.poly = Polygon(pairs)

    def gen_random_colors(self) -> list:
        """Generating random colors in format #123456 for each vertex."""
        data = '0123456789ABCDEF'

        def gen() -> str:
            return '#' + ''.join([choice(data) for j in range(6)])

        answer = [gen() for i in range(len(self.vertices))]

        return answer

    # TODO: rewrite using cp algorithm
    # https://cp-algorithms.com/geometry/point-in-convex-polygon.html
    def convex_trick(self, point: nPoint) -> bool:
        """Use built-in shapely method to check that points fit."""
        # Check 3 projections. (WHY???)
        # https://stackoverflow.com/questions/56793060/how-to-determine-if-a-point-lies-inside-a-polygon-in-3d-space

        lower = [i.to_lower_dimension().to_tuple() for i in self.vertices]

        # debug
        # pairs1 = [i[1:] for i in lower]
        # pairs2 =[i[:1] + i[2:] for i in lower]
        # pairs3 = [i[:-1] for i in lower]
        # print(point)
        # print(lower)
        # print(pairs1)
        # print(pairs2)
        # print(pairs3, '\n')

        # Ignore X
        pairs = {i[1:] for i in lower}

        if not Point(point[1], point[2]).within(Polygon(pairs)):
            return False

        # Ignore Y
        pairs = {i[:1] + i[2:] for i in lower}

        if not Point(point[0], point[2]).within(Polygon(pairs)):
            return False

        # Ignore Z
        pairs = {i[:-1] for i in lower}
        if not Point(point[0], point[1]).within(Polygon(pairs)):
            return False

        return True

    def gen_start_point(self) -> nPoint:
        """Randomly choose starting point."""
        # minx, miny, maxx, maxy = self.poly.bounds
        # x = uniform(minx, maxx)
        # y = uniform(miny, maxy)
        # # Point is from shapely.geometry
        # while not self.poly.contains(Point(x, y)):
        #     x = uniform(minx, maxx)
        #     y = uniform(miny, maxy)
        # return Point2(x, y)

        xs, ys, zs = zip(*map(lambda p: p.to_lower_dimension(), self.vertices))

        minx, miny, minz = min(xs), min(ys), min(zs)
        maxx, maxy, maxz = max(xs), max(ys), max(zs)

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)
        z = uniform(minz, maxz)

        while not self.convex_trick(nPoint(x, y, z)):
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)
            z = uniform(minz, maxz)

        return nPoint(x, y, z)


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
                   vertex: nPoint,
                   cur: nPoint,
                   rel=1,
                   inside=True) -> Point2:
        """Main method that divides «segment» in appropriate relation."""
        answer = get_coords(vertex, cur, rel).to_lower_dimension()

        if not answer.isfinite() or self.checker(answer) != inside:
            answer = get_coords(vertex, cur, -rel).to_lower_dimension()

        if not answer.isfinite() or self.checker(answer) != inside:
            return Point3(inf, inf, inf)

        return answer

    @pyqtSlot()
    def run(self):
        x, y, z, colors = self.work(*self.args, **self.kwargs)

        self.signals.result.emit(x, y, z, colors)

    def work(self, cnt: int, rel=1):
        """Main method that «plays» chaos game."""
        def add_point(point, x, y, z, vert=None, colors=None):
            bounds = point.isfinite()
                     # and self.xmin <= point.x <= self.xmax\
                     # and self.ymin <= point.y <= self.ymax

            if not bounds:
                return False

            x.append(point[0])
            y.append(point[1])
            z.append(point[2])
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        x_coords:List[float] = []
        y_coords:List[float] = []
        z_coords:List[float] = []
        colors:List[str] = []

        cur = self.start_point.to_bigger_dimension(self.projective)
        # cur = self.start_point.to_point3(self.projective)

        # print(cur)

        # while len(x_coords) < cnt:
        for _ in range(cnt):
            vertex = choice(self.vertices)
            result = self.div_in_rel(vertex, cur, rel=rel)

            #print(vertex)
            #print(cur)
            #print(result)
            #print()

            if add_point(result,
                         x_coords,
                         y_coords,
                         z_coords,
                         vert=vertex,
                         colors=colors):
                cur = result.to_bigger_dimension(self.projective)
                # cur = result.to_point3(self.projective)

            if self.double_mid:
                for val in [rel, -rel]:
                    out = self.div_in_rel(vertex, cur, rel=val, inside=False)
                    add_point(out,
                              x_coords,
                              y_coords,
                              z_coords,
                              vert=vertex,
                              colors=colors)

        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)
        z_coords = np.array(z_coords)
        colors = np.array(colors)

        return x_coords, y_coords, z_coords, colors

    # TODO
    def clean(self, x, y, colors):
        """Take quotient of points by current precision."""
        x = np.round(x, decimals=self.decimals)
        y = np.round(y, decimals=self.decimals)

        _, idx = np.unique(x + 1j * y, return_index=True)

        x = np.take(x, idx)
        y = np.take(y, idx)
        colors = np.take(colors, idx, mode='clip')

        return x, y, colors
