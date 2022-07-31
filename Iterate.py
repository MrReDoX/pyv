from Point import (
    Point2,
    Point3,
)

import numpy as np


class Worker(object):
    def __init__(self):
        from math import inf

        self.start_point = Point2(0.0, 0.0)
        self._vertices = list()
        self.checker = self.convex_trick
        self.vertices_colors = list()
        self.coloring = False
        self.double_mid = False

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        from shapely.geometry import Point, Polygon

        self._vertices = value
        self.poly = Polygon([(i.to_Point2().x, i.to_Point2().y) for i in self.vertices if isinstance(i, Point3)])

    def gen_random_colors(self) -> list:
        from random import choice

        data = '0123456789ABCDEF'
        gen = lambda : "#" + ''.join([choice(data) for j in range(6)])

        answer = [gen() for i in range(len(self.vertices))]

        # answer = [tuple(rng.integers(0, 256) / 256 for i in range(3)) for i in range(len(self.vertices))]

        return answer


    # TODO: rewrite using cp algorithm: https://cp-algorithms.com/geometry/point-in-convex-polygon.html
    # very slow
    def convex_trick(self, p: Point2) -> bool:
        from shapely.geometry import Point, Polygon

        return Point(p.x, p.y).within(self.poly)


    # TODO
    # return m instead of setting
    def gen_start_point(self) -> Point2:
        from random import uniform
        from shapely.geometry import Point, Polygon

        minx, miny, maxx, maxy = self.poly.bounds

        x = uniform(minx, maxx)
        y = uniform(miny, maxy)

        # Point is from shapely.geometry
        while not self.poly.contains(Point(x, y)):
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)

        return Point2(x, y)


    def guess_limits(self, contains_absolute=False) -> (float, float, float, float):
        from math import inf

        xmin = inf
        xmax = -inf

        ymin = inf
        ymax = -inf

        for i in self.vertices:
            curx = i.to_Point2().x
            cury = i.to_Point2().y

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


    def div_in_rel(self, Ai: Point3, M: Point3, rel=1, inside=True) -> Point2:
        from math import inf, isinf

        import Mid as mid
        if rel != 1:
            import Mid_lambda as mid

        x = mid.c1(Ai, M, rel)
        y = mid.c2(Ai, M, rel)
        z = mid.c3(Ai, M, rel)

        answer = Point3(x, y, z).to_Point2().to_float()

        if isinf(answer.x):
            return Point2(inf, inf)

        if not self.checker(answer) and inside:
            x = mid.c1(Ai, M, -1 * rel)
            y = mid.c2(Ai, M, -1 * rel)
            z = mid.c3(Ai, M, -1 * rel)

            answer = Point3(x, y, z).to_Point2().to_float()

        if isinf(answer.x) or self.checker(answer) != inside:
            return Point2(inf, inf)

        return answer

    def work(self, cnt: int, rel=1) -> (np.ndarray, np.ndarray, np.ndarray):
        from math import isfinite, inf
        from random import choice

        bounds = lambda x, y: self.xmin < x < self.xmax and self.ymin < y < self.ymax

        x = np.full(cnt, inf)
        y = np.full(cnt, inf)

        if self.double_mid:
            x_out = np.full(cnt, inf)
            y_out = np.full(cnt, inf)

        colors = ['black'] * len(self.vertices)
        if self.coloring:
            colors = np.empty(cnt, dtype='object')
            colors_out = np.empty(cnt, dtype='object')

        cur = self.start_point

        for k in range(cnt):
            Ai = choice(self.vertices)
            M1_proj = cur.to_Point3(self.projective)

            result = self.div_in_rel(Ai, M1_proj, rel=rel)

            if not isfinite(result.x):
                continue

            if bounds(result.x, result.y):
                x[k] = result.x
                y[k] = result.y

                if self.coloring:
                    idx = self.vertices.index(Ai)
                    colors[k] = self.vertices_colors[idx]

                cur = result

            if self.double_mid:
                outside = self.div_in_rel(Ai, M1_proj, rel=rel, inside=False)

                if not isfinite(outside.x):
                    continue

                if bounds(outside.x, outside.y):
                    x_out[k] = outside.x
                    y_out[k] = outside.y

                    if self.coloring:
                        idx = self.vertices.index(Ai)
                        colors_out[k] = self.vertices_colors[idx]

        if self.double_mid:
            x = np.append(x, x_out)
            y = np.append(y, y_out)

            if self.coloring:
                colors = np.append(colors, colors_out)

        # Remove inf from x, y
        idx = np.ravel(np.argwhere(np.isfinite(x)))

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')

    def clean(self, x, y, colors) -> (np.ndarray, np.ndarray, np.ndarray):
        from math import isclose

        np.round(x, decimals=3, out=x)
        np.round(y, decimals=3, out=y)

        _, idx = np.unique(x + 1j * y, return_index=True)

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')

    # TODO
    # rewrite
    # A corner point must not be selected twice in succession
    def work1(self, cnt: int):
        x = np.full(cnt, np.inf)
        y = np.full(cnt, np.inf)

        x_out = np.full(cnt, np.inf)
        y_out = np.full(cnt, np.inf)

        colors = ['black'] * len(self.vertices)
        if self.coloring:
            colors = np.empty(cnt, dtype='object')
            colors_out = np.empty(cnt, dtype='object')

        cur = self.start_point

        # prev Ai
        prev = None

        for k in range(cnt):
            # Choose Ai until we get a new one
            Ai = random.choice(self.vertices)
            while Ai == prev:
                Ai = random.choice(self.vertices)

            # Do not forget to set
            prev = Ai

            M1_proj = cur.to_Point3(self.projective)

            result = self.compute_mid(Ai, M1_proj)

            if math.isinf(result.x):
                continue

            x_fit = self.xmin < result.x < self.xmax
            y_fit = self.ymin < result.y < self.ymax

            if x_fit and y_fit:
                x[k] = result.x
                y[k] = result.y

                if self.coloring:
                    idx = self.vertices.index(Ai)
                    colors[k] = self.vertices_colors[idx]

                cur = result

            if self.double_mid:
                outside = self.compute_mid(Ai, M1_proj, inside=False)

                if math.isinf(outside.x):
                    continue

                x_fit = self.xmin < outside.x < self.xmax
                y_fit = self.ymin < outside.y < self.ymax

                if x_fit and y_fit:
                    x_out[k] = outside.x
                    y_out[k] = outside.y

                    if self.coloring:
                        idx = self.vertices.index(Ai)
                        colors_out[k] = self.vertices_colors[idx]

        if self.double_mid:
            x = np.append(x, x_out)
            y = np.append(y, y_out)
            colors = np.append(colors, colors_out)

        # Remove inf from x, y
        idx = np.ravel(np.argwhere(np.isfinite(x)))

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')

    # TODO
    # rewrite
    def work_euclidean(self, cnt: int) -> (np.ndarray, np.ndarray, np.ndarray):
        x = np.full(cnt, np.inf)
        y = np.full(cnt, np.inf)

        colors = 'black'
        if self.coloring:
            colors = np.empty(cnt, dtype='object')
            colors_out = np.empty(cnt, dtype='object')

        cur = self.start_point

        for k in range(cnt):
            Ai = random.choice(self.vertices)

            result = Point2((cur.x + Ai.x) / 2, (cur.y + Ai.y) / 2)

            if math.isinf(result.x):
                continue

            x_fit = self.xmin < result.x < self.xmax
            y_fit = self.ymin < result.y < self.ymax

            if x_fit and y_fit:
                x[k] = result.x
                y[k] = result.y

                if self.coloring:
                    idx = self.vertices.index(Ai)
                    colors[k] = self.vertices_colors[idx]

            cur = result

        # Remove inf from x, y
        idx = np.ravel(np.argwhere(np.isfinite(x)))

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')

    # TODO
    # rewrite
    def work_euclidean_1(self, cnt: int) -> (np.ndarray, np.ndarray, np.ndarray):
        x = np.full(cnt, np.inf)
        y = np.full(cnt, np.inf)

        colors = 'black'
        if self.coloring:
            colors = np.empty(cnt, dtype='object')
            colors_out = np.empty(cnt, dtype='object')

        cur = self.start_point
        prev = None

        for k in range(cnt):
            Ai = random.choice(self.vertices)
            while Ai == prev:
                Ai = random.choice(self.vertices)

            prev = Ai

            result = Point2((cur.x + Ai.x) / 2, (cur.y + Ai.y) / 2)

            if math.isinf(result.x):
                continue

            x_fit = self.xmin < result.x < self.xmax
            y_fit = self.ymin < result.y < self.ymax

            if x_fit and y_fit:
                x[k] = result.x
                y[k] = result.y

                if self.coloring:
                    idx = self.vertices.index(Ai)
                    colors[k] = self.vertices_colors[idx]

            cur = result

        # Remove inf from x, y
        idx = np.ravel(np.argwhere(np.isfinite(x)))

        return np.take(x, idx), np.take(y, idx), np.take(colors, idx, mode='clip')

