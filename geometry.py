"""Auxiliary class for elementary coordinate geometry
"""

from math import inf

from point import Point2
from utility import isclose_prec


class Line:
    """Represents string. Built on two points
    """
    def __init__(self, a: Point2, b: Point2):
        self.a = (b.y - a.y)
        self.b = -(b.x - a.x)
        self.c = b.x * a.y - a.x * b.y

        self.equation = lambda x, y: self.a * x + self.b * y + self.c

    def intersect(self, l) -> Point2:
        """Intersect two lines

        Args:
            l (_type_): second line

        Returns:
            Point2: Point2(inf, inf) or actual point of intersection
        """
        def det(m):
            return m[0][0] * m[1][1] - m[0][1] * m[1][0]

        system_det = det([[self.a, self.b], [l.a, l.b]])
        if isclose_prec(system_det, 0):
            return Point2(inf, inf)

        det_x = det([[self.c, self.b], [-l.c, l.b]])
        det_y = det([[self.a, -self.c], [l.a, -l.c]])

        return Point2(det_y / system_det, det_x / system_det)