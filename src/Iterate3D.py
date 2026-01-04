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

from Mid3D import get_coords
from Point import Point2, Point3, Point
from Utility import PRECISION
from scipy.spatial import ConvexHull


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

        self.start_point = Point(0.0, 0.0, 0.0)
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
        return self._vertices

    # @property
    # def x(self) -> list:
    #     """Getter for x coordinates of chaos game points."""
    #     return list(self._x)

    #dasdaasdasd @property
    # def y(self) -> list:
    #     """Getter for y coordinates of chaos game points."""
    #     return list(self._y)

    # @property
    # def colors(self) -> list:
    #     return list(self._colors)

    @vertices.setter
    def vertices(self, value):
        """Setter for vertices. Builds shapely polygon when points are set."""
        self._vertices = value

        points = [v.to_lower_dimension().to_list() for v in self.vertices]

        self.hull = ConvexHull(np.array(points, dtype=float))

    def gen_random_colors(self) -> list:
        """Generating random colors in format #123456 for each vertex."""
        data = '0123456789ABCDEF'

        def gen() -> str:
            return '#' + ''.join([choice(data) for j in range(6)])

        answer = [gen() for i in range(len(self.vertices))]

        return answer

    # TODO: rewrite using cp algorithm
    # https://cp-algorithms.com/geometry/point-in-convex-polygon.html
    def convex_trick(self, point: Point) -> bool:
        """Use built-in shapely method to check that points fit.

        Args:
            point (nPoint): point to check.

        Returns:
            bool: is point inside polygon
        """
        points = [v.to_lower_dimension().to_list() for v in self.vertices]
        points.append(point.to_list())

        new_hull = ConvexHull(np.array(points, dtype=float))

        return np.array_equal(self.hull.vertices, new_hull.vertices)


    def gen_start_point(self) -> Point:
        """Randomly choose starting point.

        Returns:
            nPoint: random point inside polygon.
        """
        xs, ys, zs = zip(*map(lambda p: p.to_lower_dimension(), self.vertices))

        low = np.array([min(xs), min(ys), min(zs)])
        high = np.array([max(xs), max(ys), max(zs)])

        x, y, z = np.random.uniform(low, high)

        while not self.convex_trick(Point(x, y, z)):
            x, y, z = np.random.uniform(low, high)

        return Point(x, y, z)


    def guess_limits(self, contains_absolute=False) -> Tuple[float, float, float, float]:
        """Try to guess x and y limits for the picture.

        Args:
            contains_absolute (bool, optional): include absolute to the screen. Defaults to False.

        Returns:
            Tuple[float, float, float, float]: xmin, ymin, xmax, ymax params
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
                   vertex: Point,
                   cur: Point,
                   rel=1,
                   inside=True) -> Point2:
        """Main method that divides «segment» in appropriate relation."""
        # print(vertex)
        # print(cur)
        # print(rel, '\t', type(rel))

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

            x.append(point[1])
            y.append(point[2])
            z.append(point[3])
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        x_coords:List[float] = []
        y_coords:List[float] = []
        z_coords:List[float] = []
        colors:List[str] = []

        cur = self.start_point.to_bigger_dimension(1)
        print(cur)
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
                cur = result.to_bigger_dimension(1)
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
