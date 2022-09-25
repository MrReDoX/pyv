import cProfile
from math import inf, isclose
from random import choice, uniform

import numpy as np
from shapely.geometry import Point, Polygon

from point import Point2, Point3
from utility import *


class Worker:
    def __init__(self):
        self.start_point = Point2(0.0, 0.0)
        self._vertices = []
        self.checker = self.convex_trick
        self.vertices_colors = []
        self.coloring = True
        self.double_mid = False
        self.projective = 1
        self.frame_type = 2

        self.precision = 1e-5
        self.decimals = 4

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self) -> list:
        return self._vertices

    @property
    def x(self) -> list:
        return self._x

    @property
    def y(self) -> list:
        return self._y

    @property
    def colors(self) -> list:
        return self._colors

    @vertices.setter
    def vertices(self, value):
        self._vertices = value
        self.poly = Polygon([(i.to_point2().x, i.to_point2().y) for i in self.vertices])

    def gen_random_colors(self) -> list:
        data = '0123456789ABCDEF'

        def gen() -> str:
            return '#' + ''.join([choice(data) for j in range(6)])

        answer = [gen() for i in range(len(self.vertices))]

        return answer


    # TODO: rewrite using cp algorithm
    # https://cp-algorithms.com/geometry/point-in-convex-polygon.html
    def convex_trick(self, point: Point2) -> bool:
        return Point(point.x, point.y).within(self.poly)

    def gen_start_point(self) -> Point2:
        minx, miny, maxx, maxy = self.poly.bounds

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)

        # Point is from shapely.geometry
        while not self.poly.contains(Point(x, y)):
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)

        return Point2(x, y)


    def guess_limits(self, contains_absolute=False) -> (float, float, float, float):
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
        # work with the frame type
        # idea: just import required file

        import mid_first_type as mid

        val = u1(vertex, cur)**2 + u2(vertex, cur)**2 - u3(vertex, cur)**2
        if isclose(abs(val), 0, rel_tol=self.precision):
            # assume frame_type == 1
            import mid_parab_first_type as mid

        if self.frame_type == 2:
            import mid_second_type as mid

            val = 4 * u1(vertex, cur) * u2(vertex, cur) - u3(vertex, cur)**2
            if isclose(abs(val), 0, rel_tol=self.precision):
                import mid_parab_second_type as mid

        if not isclose(abs(rel), 1, rel_tol=self.precision):
            import mid_first_lambda as mid

        x = mid.first_coord(vertex, cur, rel)
        y = mid.second_coord(vertex, cur, rel)
        z = mid.third_coord(vertex, cur, rel)

        # print(x, y, z)

        answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite() or self.checker(answer) != inside:
            x = mid.first_coord(vertex, cur, -rel)
            y = mid.second_coord(vertex, cur, -rel)
            z = mid.third_coord(vertex, cur, -rel)

            answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite() or self.checker(answer) != inside:
            return cur.to_point2()

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
        def bounds(p: Point2) -> bool:
            return p.isfinite and self.xmin < p.x < self.xmax and self.ymin < p.y < self.ymax

        def add_point(p, x, y, vert=None, colors=None):
            if not bounds(p):
                return False

            x.append(p.x)
            y.append(p.y)
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        xs = []
        ys = []
        colors = []

        cur = self.start_point.to_point3(self.projective)

        print(cur)

        while len(xs) < cnt:
            vertex = choice(self.vertices)
            result = self.div_in_rel(vertex, cur, rel=rel)

            if add_point(result, xs, ys, vert=vertex, colors=colors):
                cur = result.to_point3(self.projective)

            if self.double_mid:
                for val in [rel, -rel]:
                    out = self.div_in_rel(vertex, cur, rel=val, inside=False)
                    add_point(out, xs, ys, vert=vertex, colors=colors)

        self._x = np.array(xs)
        self._y = np.array(ys)
        self._colors = np.array(colors)

    def clean(self):
        self._x = np.round(self._x, decimals=self.decimals)
        self._y = np.round(self._y, decimals=self.decimals)

        _, idx = np.unique(self._x + 1j * self._y, return_index=True)

        self._x = np.take(self._x, idx)
        self._y = np.take(self._y, idx)
        self._colors = np.take(self._colors, idx, mode='clip')
