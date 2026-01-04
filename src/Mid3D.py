"""Coordinates of the midpoint and the quasi-midpoint of a non-parabolic segment."""

from math import inf, isclose, sqrt

from Point import Point
from Utility import PRECISION


def p(a: Point, b: Point, j: int, k: int) -> float:
    """Plucker coordinates. See above (3.1)."""
    return a[j] * b[k] - a[k] * b[j]

def delta1(a: Point, b: Point) -> float:
    """Formula (4.10)."""
    return a[3] * b[4] + a[4] * b[3]

def delta2(a: Point, b: Point) -> float:
    """Formula (4.24)."""
    return a[1] * b[2] + a[2] * b[1]

def theta1(a: Point, b: Point) -> float:
    """Formula (4.10)."""
    d = delta1(a, b)

    p13 = p(a, b, 1, 3)
    p14 = p(a, b, 1, 4)
    p23 = p(a, b, 2, 3)
    p24 = p(a, b, 2, 4)
    p34 = p(a, b, 3, 4)

    b1 = p13**2 + p23**2 - p34**2
    b2 = p13 * p14 + p23 * p24

    numerator = d * b1 - 2 * a[3] * b[3] * b2

    b1 = p14**2 + p24**2 + p34**2

    denominator = d * b1 - 2 * a[4] * b[4] * b2

    if isclose(abs(denominator), 0, rel_tol=PRECISION):
        return inf

    return -numerator / denominator

def theta2(a: Point, b: Point) -> float:
    """Formula (4.24)."""
    d = delta2(a, b)

    p12 = p(a, b, 1, 2)
    p13 = p(a, b, 1, 3)
    p23 = p(a, b, 2, 3)

    b2 = p13 * p23

    numerator = d * (p12**2 + p13**2) - 2 * a[1] * b[1] * b2
    denominator = d * (p12**2 + p23**2) - 2 * a[2] * b[2] * b2

    if isclose(abs(denominator), 0, rel_tol=PRECISION):
        return inf

    return -numerator / denominator

def omega1(a: Point, b: Point) -> float:
    """Formula (4.10)."""
    numerator = a[3] * b[3] + theta1(a, b) * a[4] * b[4]

    d = delta1(a, b)
    if isclose(abs(d), 0, rel_tol=PRECISION):
        return inf

    return numerator / d

def omega2(a: Point, b: Point) -> float:
    """Formula (4.24)."""
    numerator = a[1] * b[1] + theta2(a, b) * a[2] * b[2]

    d = delta2(a, b)
    if isclose(abs(d), 0, rel_tol=PRECISION):
        return inf

    return numerator / delta2(a, b)

def get_coords(a: Point, b: Point, eps=1) -> Point:
    """Compute coordinates of «middle»."""
    # TODO:
    # rewrite ps -- make 2d array
    p14 = p(a, b, 1, 4)
    p24 = p(a, b, 2, 4)
    p34 = p(a, b, 3, 4)

    ans = Point(0, 0, 0, 0)

    # s = [0 for i in range(4)]

    # (4.25)
    if isclose(abs(p14), 0, rel_tol=PRECISION)\
            and isclose(abs(p24), 0, rel_tol=PRECISION)\
            and isclose(abs(p34), 0, rel_tol=PRECISION):
        omeg = omega2(a, b)
        underroot = omeg**2 - theta2(a, b)

        if underroot < 0:
            return Point(inf, inf, inf, inf)

        root = sqrt(underroot)

        p12 = p(a, b, 1, 2)

        ans[1] = p12 * omeg + eps * p12 * root
        ans[2] = p12
        ans[3] = p(a, b, 1, 3) - p(a, b, 2, 3) * (omeg + eps * root)

        return ans

    # (4.11)
    omeg = omega1(a, b)
    underroot = omeg**2 - theta1(a, b)

    if underroot < 0:
        return Point(inf, inf, inf, inf)

    root = sqrt(underroot)

    ans[1] = p14 * omeg + eps * p14 * root - p(a, b, 1, 3)
    ans[2] = p24 * omeg + eps * p24 * root - p(a, b, 2, 3)
    ans[3] = p34 * omeg + eps * p34 * root
    ans[4] = p34

    return ans
