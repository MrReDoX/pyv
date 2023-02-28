"""Module that perfoms chaos game."""

# import cProfile
from math import inf, isclose
from random import choice, uniform

import numpy as np
from shapely.geometry import Point, Polygon

from point import Point2, Point3
from utility import PRECISION, u1, u2, u3

class Worker:
    """Main class that «plays» chaos game with settings."""
    def __init__(self):
        self.start_point = Point2(0.0, 0.0)
        self._vertices = []
        self.checker = self.convex_trick
        self.vertices_colors = []
        self.coloring = True
        self.double_mid = False
        self.projective = 1
        self.frame_type = 2

        self.precision = PRECISION * 10
        self.decimals = 5

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self) -> list:
        """Getter for vertices of triangle, rectangle etc."""
        return self._vertices

    @property
    def x(self) -> list:
        """Getter for x coordinates of chaos game points."""
        return self._x

    @property
    def y(self) -> list:
        """Getter for y coordinates of chaos game points."""
        return self._y

    @property
    def colors(self) -> list:
        """Getter for colors of chaos game points."""
        return self._colors

    @vertices.setter
    def vertices(self, value):
        """Setter for vertices. Builds shapely polygon when points are set."""
        self._vertices = value
        self.poly = Polygon([(i.to_point2().x, i.to_point2().y) for i in self.vertices])

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


    def guess_limits(self, contains_absolute=False) -> (float, float, float, float):
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


    def div_in_rel(self, vertex: Point3, cur: Point3, rel=1, inside=True) -> Point2:
        """Main method that divides «segment» in appropriate relation."""
        from mid_first_type import first_coord, second_coord, third_coord

        val = u1(vertex, cur)**2 + u2(vertex, cur)**2 - u3(vertex, cur)**2
        if isclose(abs(val), 0, rel_tol=self.precision):
            # assume frame_type == 1
            from mid_parab_first_type import first_coord, second_coord, third_coord

        if self.frame_type == 2:
            from mid_second_type import first_coord, second_coord, third_coord

            val = 4 * u1(vertex, cur) * u2(vertex, cur) - u3(vertex, cur)**2
            if isclose(abs(val), 0, rel_tol=self.precision):
                from mid_parab_second_type import first_coord, second_coord, third_coord

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


    # @profile
    def work(self, cnt: int, rel=1):
        """Main method that «plays» chaos game."""
        def bounds(point: Point2) -> bool:
            return point.isfinite\
                   and self.xmin <= point.x <= self.xmax\
                   and self.ymin <= point.y <= self.ymax

        def add_point(point, x, y, vert=None, colors=None):
            if not bounds(point):
                return False

            x.append(point.x)
            y.append(point.y)
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        x_coords = []
        y_coords = []
        colors = []

        cur = self.start_point.to_point3(self.projective)

        print(cur)

        # while len(x_coords) < cnt:
        for _ in range(cnt):
            vertex = choice(self.vertices)
            result = self.div_in_rel(vertex, cur, rel=rel)

            if add_point(result, x_coords, y_coords, vert=vertex, colors=colors):
                cur = result.to_point3(self.projective)

            if self.double_mid:
                for val in [rel, -rel]:
                    out = self.div_in_rel(vertex, cur, rel=val, inside=False)
                    add_point(out, x_coords, y_coords, vert=vertex, colors=colors)

        self._x = np.array(x_coords)
        self._y = np.array(y_coords)
        self._colors = np.array(colors)

    def clean(self):
        """Take quotient of points by current precision."""
        self._x = np.round(self._x, decimals=self.decimals)
        self._y = np.round(self._y, decimals=self.decimals)

        _, idx = np.unique(self._x + 1j * self._y, return_index=True)

        self._x = np.take(self._x, idx)
        self._y = np.take(self._y, idx)
        self._colors = np.take(self._colors, idx, mode='clip')
