from math import inf
from random import choice, uniform

import numpy as np
from shapely.geometry import Point, Polygon

from point import Point2, Point3

from concurrent.futures import ThreadPoolExecutor

import cProfile


class Worker:
    def __init__(self):
        self.start_point = Point2(0.0, 0.0)
        self._vertices = []
        self.checker = self.convex_trick
        self.vertices_colors = []
        self.coloring = False
        self.double_mid = False
        self.projective = 1

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
        xmin = inf
        xmax = -inf

        ymin = inf
        ymax = -inf

        for i in self.vertices:
            curx = i.to_point2().x
            cury = i.to_point2().y

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
        import mid
        if abs(rel) != 1:
            import mid_lambda as mid

        x = mid.first_coord(vertex, cur, rel)
        y = mid.second_coord(vertex, cur, rel)
        z = mid.third_coord(vertex, cur, rel)

        answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite():
            return Point2(inf, inf)

        if not self.checker(answer) and inside:
            with ThreadPoolExecutor() as executor:
                functions = [mid.first_coord, mid.second_coord, mid.third_coord]
                futures = [executor.submit(f, vertex, cur, rel) for f in functions]

                x, y, z = [f.result() for f in futures]

            x = mid.first_coord(vertex, cur, -rel)
            y = mid.second_coord(vertex, cur, -rel)
            z = mid.third_coord(vertex, cur, -rel)

            answer = Point3(x, y, z).to_point2().to_float()

        if not answer.isfinite() or self.checker(answer) != inside:
            return Point2(inf, inf)

        return answer


    def profile(func):
        """Decorator for run function profile"""
        def wrapper(*args, **kwargs):
            profile_filename = func.__name__ + '.prof'
            profiler = cProfile.Profile()
            result = profiler.runcall(func, *args, **kwargs)
            profiler.dump_stats(profile_filename)
            return result
        return wrapper


    @profile
    def work(self, cnt: int, rel=1) -> (np.ndarray, np.ndarray, np.ndarray):
        def bounds(p: Point2) -> bool:
            return p.isfinite and self.xmin < p.x < self.xmax and self.ymin < p.y < self.ymax

        def add_point(p, x, y, idx_p, vert=None, colors=None):
            if not bounds(p):
                return False

            x[idx_p] = p.x
            y[idx_p] = p.y

            if self.coloring:
                colors[k] = self.vertices_colors[self.vertices.index(vert)]

            return True

        xs = []
        ys = []

        xs.append(np.full(cnt, np.inf))
        ys.append(np.full(cnt, np.inf))

        if self.double_mid:
            xs.extend([np.full(cnt, np.inf)]*2)
            ys.extend([np.full(cnt, np.inf)]*2)

        # xs[0] -- main x
        # xs[1] -- out x
        # xs[2] -- out_1 x
        # and same for ys

        colors = [['black' for i in range(len(self.vertices))]]
        if self.coloring:
            colors = [np.empty(cnt, dtype='object')] * 3

        cur = self.start_point.to_point3(self.projective)

        for k in range(cnt):
            vertex = choice(self.vertices)
            result = self.div_in_rel(vertex, cur, rel=rel)

            if add_point(result, xs[0], ys[0], k, vert=vertex, colors=colors[0]):
                cur = result.to_point3(self.projective)

            if self.double_mid:
                for idx, val in enumerate([rel, -rel], start=1):
                    out = self.div_in_rel(vertex, cur, rel=val, inside=False)
                    add_point(out, xs[idx], ys[idx], k, vert=vertex, colors=colors[idx])

        if self.double_mid:
            xs[0] = np.append(xs[0], [xs[1], xs[2]])
            ys[0] = np.append(ys[0], [ys[1], ys[2]])

            if self.coloring:
                colors[0] = np.append(colors[0], [colors[1], colors[2]])

        # Remove inf from xs[0], ys[0]
        idx = np.ravel(np.argwhere(np.isfinite(xs[0])))

        self._x = np.take(xs[0], idx)
        self._y = np.take(ys[0], idx)
        self._colors = np.take(colors[0], idx, mode='clip')

        return self._x, self._y, self._colors

    def clean(self, x, y, colors) -> (np.ndarray, np.ndarray, np.ndarray):
        np.round(x, decimals=3, out=x)
        np.round(y, decimals=3, out=y)

        _, idx = np.unique(x + 1j * y, return_index=True)

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')
