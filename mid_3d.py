"""Coordinates of the midpoint and the quasi-midpoint of a non-parabolic segment."""

from math import inf, isclose, sqrt

from point import nPoint
from utility import PRECISION


def p(a: nPoint, b: nPoint, j: int, k: int) -> float:
    """Plucker coordinates. See above (3.1)."""
    return a[j - 1] * b[k - 1] - a[k - 1] * b[j - 1]

def deltaI(a: nPoint, b: nPoint) -> float:
    """Formula (4.10)."""
    return a[2] * b[3] + a[3] * b[2]

def deltaII(a: nPoint, b: nPoint) -> float:
    """Formula (4.24)."""
    return a[0] * b[1] + a[1] * b[0]

def thetaI(a: nPoint, b: nPoint) -> float:
    """Formula (4.10)."""
    d = deltaI(a, b)

    p13 = p(a, b, 1, 3)
    p14 = p(a, b, 1, 4)
    p23 = p(a, b, 2, 3)
    p24 = p(a, b, 2, 4)
    p34 = p(a, b, 3, 4)

    b1 = p13**2 + p23**2 - p34**2
    b2 = p13 * p14 + p23 * p24

    numerator = d * b1 - 2 * a[2] * b[2] * b2

    b1 = p14**2 + p24**2 + p34**2

    denominator = d * b1 - 2 * a[3] * b[3] * b2

    # print(a, b)
    # print(f'b1 = {b1}\nb2 = {b2}')

    if isclose(abs(denominator), 0, rel_tol=PRECISION):
        return inf

    return -numerator / denominator

def thetaII(a: nPoint, b: nPoint) -> float:
    """Formula (4.24)."""
    d = deltaII(a, b)

    p12 = p(a, b, 1, 2)
    p13 = p(a, b, 1, 3)
    p23 = p(a, b, 2, 3)

    b1 = d * (p12**2 + p13**2)
    b2 = p13 * p23

    numerator = b1 - 2 * a[0] * b[0] * b2
    denominator = b1 - 2 * a[1] * b[1] * b2

    if isclose(abs(denominator), 0, rel_tol=PRECISION):
        return inf

    return -numerator / denominator

def omegaI(a: nPoint, b: nPoint) -> float:
    """Formula (4.10)."""
    numerator = a[2] * b[2] + thetaI(a, b) * a[3] * b[3]

    d = deltaI(a, b)
    if isclose(abs(d), 0, rel_tol=PRECISION):
        return inf

    return numerator / d

def omegaII(a: nPoint, b: nPoint) -> float:
    """Formula (4.24)."""
    numerator = a[0] * b[0] + thetaII(a, b) * a[1] * b[1]

    d = deltaII(a, b)
    if isclose(abs(d), 0, rel_tol=PRECISION):
        return inf

    return numerator / deltaII(a, b)

#def phi(a: nPoint) -> float:
#    return a[0]**2 + a[1]**2 - a[3]**2
#
#def phi_elliptic(a: nPoint) -> float:
#    return a[0]**2 + a[1]**2 + a[2]**2

# def get_coords_cal(a: nPoint, b: nPoint, eps=1) -> float:
#     """Get coordinates of a point or (∞,∞,∞,∞) if something bad."""
#
#     s = [0 for i in range(4)]
#     if p(a, b, 1, 4) == p(a, b, 2, 4) == p(a, b, 3, 4) == 0:
#         underroot = phi_elliptic(a) * phi_elliptic(b)
#
#         if underroot < 0:
#             s[i] = inf
#
#             return
#
#         for i in range(3):
#             s[i] = a[i] * a[1] * phi_elliptic(b) - b[i] * b[1] * phi_elliptic(a)\
#                     + eps * p(a, b, i, 2) * sqrt(underroot)
#
#         return nPoint(*s)
#
#     for i in range(4):
#         underroot = phi(a) * phi(b)
#
#         if underroot < 0:
#             s[i] = inf
#
#             return
#
#         s[i] = a[i] * a[3] * phi(b) - b[i] * b[3] * phi(a)\
#                + eps * sqrt(underroot)
#
#     return nPoint(*s)

def get_coords(a: nPoint, b: nPoint, eps=1) -> nPoint:
    """Compute coordinates of «middle»."""
    p14 = p(a, b, 1, 4)
    p24 = p(a, b, 2, 4)
    p34 = p(a, b, 3, 4)

    s = [0 for i in range(4)]

    if isclose(abs(p14), 0, rel_tol=PRECISION)\
            and isclose(abs(p24), 0, rel_tol=PRECISION)\
            and isclose(abs(p34), 0, rel_tol=PRECISION):
        omeg = omegaII(a, b)
        underroot = omeg**2 - thetaII(a, b)

        if underroot < 0:
            return nPoint(inf, inf, inf, inf)

        root = sqrt(underroot)

        p12 = p(a, b, 1, 2)

        s[0] = p12 * omeg + eps * p12 * root
        s[1] = p12
        s[2] = p(a, b, 1, 3) - p(a, b, 2, 3) * (omeg + eps * root)

        return nPoint(*s)

    omeg = omegaI(a, b)
    underroot = omeg**2 - thetaI(a, b)

    if underroot < 0:
        return nPoint(inf, inf, inf, inf)

    root = sqrt(underroot)

    s[0] = p14 * omeg + eps * p14 * root - p(a, b, 1, 3)
    s[1] = p24 * omeg + eps * p24 * root - p(a, b, 2, 3)
    s[2] = p34 * omeg + eps * p34 * root
    s[3] = p34

    return nPoint(*s)
