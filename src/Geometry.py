"""Auxiliary class for elementary coordinate geometry."""

from math import inf

from Point import Point2
from Utility import isclose_prec


class Line:
    """Represents line. Built on two points."""

    def __init__(self, a: Point2, b: Point2):
        """Initialize line coefficients."""
        self.a = (b[2] - a[2])
        self.b = -(b[1] - a[1])
        self.c = b[1] * a[2] - a[1] * b[2]

        self.equation = lambda x, y: self.a * x + self.b * y + self.c

        self.bpoint1 = a
        self.bpoint2 = b

    def intersect(self, another) -> Point2:
        """Intersect self with another.

        Args:
            another (_type_): second line

        Returns:
            Point2: Point2(inf, inf) or actual point of intersection
        """
        def det(m):
            return m[0][0] * m[1][1] - m[0][1] * m[1][0]

        base_points = [another.bpoint1, another.bpoint2]
        if self.bpoint1 in base_points:
            return self.bpoint1

        if self.bpoint2 in base_points:
            return self.bpoint2

        system_det = det([[self.a, self.b], [another.a, another.b]])
        if isclose_prec(system_det, 0):
            return Point2(inf, inf)

        det_x = det([[-self.c, self.b], [-another.c, another.b]])
        det_y = det([[self.a, -self.c], [another.a, -another.c]])

        return Point2(det_x / system_det, det_y / system_det)
