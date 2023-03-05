"""Formulas for the second frame type with lambda = 1."""

from math import inf, isclose, sqrt

from point import Point3
from utility import PRECISION, delta, u1, u2, u3


def omega(a: Point3, b: Point3) -> float:
    val1 = b.x * b.y - b.z**2
    val2 = a.x * a.y - a.z**2

    bot = a.y**2 * val1 - b.y**2 * val2

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return (a.x * a.y * val1 - b.x * b.y * val2) / bot


def omega_u3(a: Point3, b: Point3) -> float:
    return (a.z * b.z * u1(a, b) - a.y * b.y * u2(a, b))\
            / (a.y * b.z + a.z * b.y)


def theta(a: Point3, b: Point3) -> float:
    u_1 = u1(a, b)
    u_2 = u2(a, b)
    u_3 = u3(a, b)
    val = (2 * u_1 * u_2 - u_3**2)

    bot = delta(a, b) * u_1**2 + a.y * b.y * val

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return -(delta(a, b) * u_2**2 + a.x * b.x * val) / bot


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get first coordinate of point or ∞ if something bad."""
    if not isclose(abs(u3(a, b)), 0, rel_tol=PRECISION):
        underroot = omega(a, b)**2 - theta(a, b)

        if underroot < 0:
            return inf

        return u3(a, b) * (omega(a, b) + eps * sqrt(underroot))

    # u3 ~ 0
    return -u2(a, b)


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get second coordinate of point or ∞ if something bad."""
    if not isclose(abs(u3(a, b)), 0, rel_tol=PRECISION):
        return u3(a, b)

    # u3 ~ 0
    return u1(a, b)


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get third coordinate of point or ∞ if something bad."""
    if not isclose(abs(u3(a, b)), 0, rel_tol=PRECISION):
        underroot = omega(a, b)**2 - theta(a, b)

        if underroot < 0:
            return inf

        return -u1(a, b) * (omega(a, b) + eps * sqrt(underroot)) - u2(a, b)

    # u3 ~ 0
    underroot = omega_u3(a, b)**2 + u1(a, b) * u2(a, b)

    if underroot < 0:
        return inf

    return omega_u3(a, b) + eps * sqrt(underroot)
