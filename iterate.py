"""Module that perfoms chaos game on plane."""

# import cProfile
from math import inf, isclose
from random import choice, uniform
from typing import List, Tuple

import numpy as np
from pyqtgraph.Qt.QtCore import *
from pyqtgraph.Qt.QtGui import *
from pyqtgraph.Qt.QtWidgets import *
from shapely.geometry import Point, Polygon

from point import Point2, Point3
from utility import PRECISION, u1, u2, u3


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
    result = pyqtSignal(object, object, object)


class Worker(QRunnable):
    """Main class that «plays» chaos game with settings."""
    def __init__(self):
        # For threading
        super(Worker, self).__init__()
        self.threadpool = QThreadPool()
        self.args = None
        self.kwargs = None
        self.signals = WorkerSignals()

        self.start_point = Point2(0.0, 0.0)
        self._vertices = []
        self.checker = self.convex_trick
        self.vertices_colors = []
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

        pairs = [(i.to_point2().x, i.to_point2().y) for i in self.vertices]

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
    def convex_trick(self, point: Point2) -> bool:
        """Use built-in shapely method to check that points fit."""
        return Point(point.x, point.y).within(self.poly)

    def gen_start_point(self) -> Point2:
        """Randomly choose starting point."""
        minx, miny, maxx, maxy = self.poly.bounds

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)

        # Point is from shapely.geometry
        while not self.poly.contains(Point(x, y)):
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
        from mid_first_type import first_coord, second_coord, third_coord

        val = u1(vertex, cur)**2 + u2(vertex, cur)**2 - u3(vertex, cur)**2
        if isclose(abs(val), 0, rel_tol=self.precision):
            # assume frame_type == 1
            from mid_parab_first_type import (first_coord, second_coord,
                                              third_coord)

        if self.frame_type == 2:
            from mid_second_type import first_coord, second_coord, third_coord

            val = 4 * u1(vertex, cur) * u2(vertex, cur) - u3(vertex, cur)**2
            if isclose(abs(val), 0, rel_tol=self.precision):
                from mid_parab_second_type import (first_coord, second_coord,
                                                   third_coord)

        if not isclose(abs(rel), 1, rel_tol=self.precision):
            from mid_first_lambda import first_coord, second_coord, third_coord

        x = first_coord(vertex, cur, rel)
        y = second_coord(vertex, cur, rel)
        z = third_coord(vertex, cur, rel)

        answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite() or self.checker(answer) != inside:
            x = first_coord(vertex, cur, -rel)
            y = second_coord(vertex, cur, -rel)
            z = third_coord(vertex, cur, -rel)

            answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite() or self.checker(answer) != inside:
            return Point2(inf, inf)

        return answer

    # def profile(func):
    #     """Decorator for run function profile"""
    #     def wrapper(*args, **kwargs):
    #         profile_filename = func.__name__ + '.prof'
    #         profiler = cProfile.Profile()
    #         result = profiler.runcall(func, *args, **kwargs)
    #         profiler.dump_stats(profile_filename)
    #         return result
    #     return wrapper

    @pyqtSlot()
    def run(self):
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

        x_coords:List[float] = []
        y_coords:List[float] = []
        colors:List[str] = []

        cur = self.start_point.to_point3(self.projective)

        print(cur)

        # while len(x_coords) < cnt:
        for _ in range(cnt):
            vertex = choice(self.vertices)
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
