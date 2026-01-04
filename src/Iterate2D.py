"""Module that perfoms chaos game on plane."""

from itertools import pairwise
from math import acos, inf, pi, sqrt
from random import choice, uniform

import numpy as np
from pyqtgraph.Qt.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from shapely.geometry import Point, Polygon
from shapely.prepared import prep

from Constants import PRECISION
from Geometry import Line
from Point import Point2, Point3
from SpecialFunctions import harmonic, phi, phi_bar, phi_big, u1, u2, u3
from Utility import isclose_prec, signum


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread.

    Supported signals are:

    result
        numpy arrays x, y, colors returned

    """

    result = pyqtSignal(object, object, object)


class Worker2D(QRunnable):
    """Main class that «plays» chaos game with settings."""

    def __init__(self):
        # For threading
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = ()
        self.kwargs = {}
        self.signals = WorkerSignals()

        self.start_point = Point3(0, 0, 1)
        self.vertices: list[Point3] = []
        self.checker = lambda p: \
            self.shapely_default_checker(p)\
            and self.polygon_default_checker(p)
        self.strategy = lambda verticies, _: choice(verticies)
        self.vertices_colors = []
        self.inside = True
        self.frame_type = 2

        self.precision = PRECISION
        self.decimals = 9

        self.xmin = -inf
        self.xmax = inf

        self.ymin = -inf
        self.ymax = inf

    def prepare_shapely_checker(self):
        """Prepare shapely polygon for fast checking that point is in."""
        vertices_2d = [i.to_lower_dimension().to_float()
                       for i in self.vertices]

        pairs = [i.to_tuple() for i in vertices_2d]

        self.poly = Polygon(pairs).buffer(0.1, quad_segs=2**7)
        self.poly_prep = prep(self.poly)

    def prepare_polygon_checker(self):
        """Point is in = signs in line equation match starting point signs. So prepare these signs."""
        vertices_2d = [i.to_lower_dimension().to_float()
                       for i in self.vertices]
        vertices_2d += [vertices_2d[0]]

        self.equations = [Line(a, b).equation
                          for a, b in pairwise(vertices_2d)]

        point_inside = self.start_point
        if not point_inside:
            point_inside = self.gen_start_point().to_lower_dimension()

        self.signs = [signum(f(point_inside[1], point_inside[2]))
                      for f in self.equations]

    def gen_random_colors(self) -> list:
        """Generate random colors in format #123456 for each vertex."""
        data = '0123456789ABCDEF'

        return ['#' + ''.join([choice(data) for _ in range(6)])
                for _ in range(len(self.vertices))]

    def shapely_default_checker(self, point: Point3) -> bool:
        r"""Use built-in shapely method to check that points fit.

        Args:
            point (Point3): point to check

        Returns:
            bool: point \in Polygon?
        """
        cur = point.to_lower_dimension().to_float()

        return self.poly_prep.contains(Point(*cur.coords))

    def polygon_default_checker(self, point: Point3) -> bool:
        r"""Use fact that we have polygon. Point signs in line equations should be the same as starting point.

        Args:
            point (Point3): point to check

        Returns:
            bool: point \in Polygon?
        """
        cur = point.to_lower_dimension().to_float()

        for idx, f in enumerate(self.equations):
            cur_sign = signum(f(cur[1], cur[2]))

            if abs(cur_sign) > 0 and cur_sign != self.signs[idx]:
                return False

        return True

    def gen_start_point(self) -> Point3:
        """Randomly choose starting point using shapely polygon bounds method.

        Returns:
            Point3: random point inside
        """
        x = uniform(self.xmin, self.xmax)
        y = uniform(self.ymin, self.ymax)

        # Point is from shapely.geometry
        # while not self.shapely_default(Point3(x,  y, 1)):
        while self.shapely_default_checker(Point3(x,  y, 1)) != self.inside:
            x = uniform(self.xmin, self.xmax)
            y = uniform(self.ymin, self.ymax)

        return Point3(x, y, 1)

    def guess_limits(
        self,
        contains_absolute=False,
    ) -> tuple[float, float, float, float]:
        """Fit polygon and maybe absolute to screen.

        Args:
            contains_absolute (bool, optional): consider absolute.
                Defaults to False.

        Returns:
            Tuple[float, float, float, float]: xmin, xmax, ymin, ymax
                for plotter
        """
        points = [i.to_lower_dimension().to_tuple() for i in self.vertices]

        xs, ys = zip(*points, strict=True)

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        if contains_absolute:
            xmin = min(xmin, -1)
            xmax = max(xmax, 1)

            ymin = min(ymin, -1)
            ymax = max(ymax, 1)

        padding = 0.5

        xmin -= padding
        xmax += padding

        ymin -= padding
        ymax += padding

        return xmin, xmax, ymin, ymax

    def div_in_rel_eucledian(
        self,
        m: Point3,
        b: Point3,
        rel=1,
        inside=True,
    ) -> Point3:
        """Divide «segment» in appropriate relation.

        Args:
            m (Point3): _description_
            b (Point3): _description_
            rel (int, optional): relation for segment division. Defaults to 1.
            inside (bool, optional): double middle plotting. Defaults to True.

        Returns:
            Point3: division result
        """
        x1, y1 = m.to_lower_dimension().to_float().to_list()
        x2, y2 = b.to_lower_dimension().to_float().to_list()

        first_coord = (x1 + rel * x2) / (1 + rel)
        second_coord = (y1 + rel * y2) / (1 + rel)

        return Point3(first_coord, second_coord, 1)

    def div_in_rel(self,
                   m: Point3,
                   b: Point3,
                   rel=1,
                   inside=True) -> Point3:
        """Divide «segment» in appropriate relation.

        Args:
            m (Point3): first point.
            b (Point3): second point.
            rel (int, optional): relation for segment division. Defaults to 1.
            inside (bool, optional): second middle plotting. Defaults to True.

        Returns:
            Point3: point that lies 'in between'.
        """
        from mid_first_lambda import coord

        val = phi_big(m, b)

        if val > 0:
            mu = rel / (1 + rel)

            return Point3(*[coord(i, m, b, mu) for i in range(1, 4)])
        if isclose_prec(abs(val), 0):
            from mid_first_lambda_parabolic import coord

            return Point3(*[coord(i, m, b, rel) for i in range(1, 4)])

        # val < 0
        if isclose_prec(abs(phi_bar(m, b)), 0):
            c1 = Point3(*[
                coord(i, m, b, rel / (1 + rel))
                for i in range(1, 4)
            ])
            c2 = Point3(*[
                coord(i, m, b, -rel / (1 + rel))
                for i in range(1, 4)
            ])

            if self.checker(c1) == inside:
                return c1

            return c2

        # phi_bar(m, b) \neq 0
        vertices_2d = [i.to_lower_dimension().to_float()
                       for i in self.vertices]
        vertices_2d += [vertices_2d[0]]

        h_points = []
        for bi, bj in pairwise(vertices_2d):
            line_m_b = Line(m.to_lower_dimension().to_float(),
                            b.to_lower_dimension().to_float())

            result = line_m_b.intersect(Line(bi, bj))

            if result not in vertices_2d:
                h_points.append(
                    result.to_bigger_dimension(1),
                )

        if not h_points:
            return Point3(inf, inf, inf)

        h: Point3 = choice(h_points)

        b_star = Point3(-b[2] * u3(m, b) - b[3] * u2(m, b),
                        b[1] * u3(m, b) + b[3] * u1(m, b),
                        b[2] * u1(m, b) - b[1] * u2(m, b))

        if harmonic(m, b, h, b_star) > 0:
            return Point3(*[
                coord(i, m, b, rel / (1 + rel))
                for i in range(1, 4)
            ])

        # Due to precision errors this sometimes doesn't work
        try:
            angle = acos(abs(phi_bar(m, b)) / (sqrt(phi(m)) * sqrt(phi(b))))
        except ValueError:
            return Point3(inf, inf, inf)

        m_star = Point3(-m[2] * u3(m, b) - m[3] * u2(m, b),
                        m[1] * u3(m, b) + m[3] * u1(m, b),
                        m[2] * u1(m, b) - m[1] * u2(m, b))

        if isclose_prec(rel, pi / (pi - 2 * angle)):
            return self.div_in_rel(m_star, b, rel, inside=inside)

        if rel < (pi - 2 * angle) / pi:
            mu = (2 * rel * (pi - angle)) / ((1 + rel) * (pi - 2 * angle))

            return Point3(*[coord(i, m, b, mu) for i in range(1, 4)])

        if (pi - 2 * angle) / pi < rel < pi / (pi - 2 * angle):
            mu = (2 * angle + pi * (rel - 1)) / (2 * angle * (rel + 1))

            return Point3(*[coord(i, m, b, mu) for i in range(1, 4)])

        # rel > pi / (pi - 2 * angle):
        numerator = (pi * (rel - 1) - 2 * rel * angle)
        denominator = ((1 + rel) * (pi - 2 * angle))
        mu = numerator / denominator

        return Point3(*[coord(i, m, b, mu) for i in range(1, 4)])

    @pyqtSlot()
    def run(self):
        """Run worker in separate thread."""
        x, y, colors = self.work(*self.args, **self.kwargs)

        min_length = 32
        min_tries = 3

        cnt = 0
        while len(x) < min_length and cnt < min_tries:
            self.start_point = self.gen_start_point()
            x, y, colors = self.work(*self.args, **self.kwargs)

            cnt += 1

        self.signals.result.emit(x, y, colors)

    def work(self, cnt: int, rel=1):
        """Start chaos game."""
        def add_point(point: Point2,
                      x: list[float],
                      y: list[float],
                      vert,
                      colors) -> bool:
            bounds = point.isfinite()\
                     and self.xmin <= point[1] <= self.xmax\
                     and self.ymin <= point[2] <= self.ymax

            if not bounds:
                return False

            x.append(point[1])
            y.append(point[2])
            colors.append(self.vertices_colors[self.vertices.index(vert)])

            return True

        x_coords: list[float] = []
        y_coords: list[float] = []
        colors: list[str] = []

        prev: list[Point3] = []
        cur: Point2 = self.start_point.to_lower_dimension()

        print(cur)

        divison_function = self.div_in_rel
        for _ in range(cnt):
            b: Point3 = self.strategy(self.vertices, prev)
            m = divison_function(
                Point3(*cur.coords, 1),
                b,
                rel=rel,
                inside=self.inside,
            )

            if self.checker(m) != self.inside:
                continue

            m = m.to_lower_dimension().to_float()

            if add_point(m,
                         x_coords,
                         y_coords,
                         vert=b,
                         colors=colors):
                prev.append(b)
                cur = m

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
