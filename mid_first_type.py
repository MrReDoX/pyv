"""Formulas for the first frame type with lambda = 1."""

from math import inf, isclose, sqrt

from point import Point3
from utility import PRECISION, u1, u2, u3


def omega(a: Point3, b: Point3) -> float:
    temp1 = b.x**2 + b.y**2 - b.z**2
    temp2 = a.x**2 + a.y**2 - a.z**2

    top = a.x * a.y * temp1 - b.x * b.y * temp2

    temp1 = b.x**2 - b.z**2
    temp2 = a.x**2 - a.z**2

    bot = a.y**2 * temp1 - b.y**2 * temp2

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return top / bot


def omega_u3(a: Point3, b: Point3) -> float:
    u_1 = u1(a, b)
    u_2 = u2(a, b)

    bot = u_1 * (a.y * b.z + a.z * b.y)

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return (a.y * b.y * (u_1**2 + u_2**2) + a.z * b.z * u_1**2) / bot


def theta(a: Point3, b: Point3) -> float:
    temp1 = b.y**2 - b.z**2
    temp2 = a.y**2 - a.z**2

    top = a.x**2 * temp1 - b.x**2 * temp2

    temp1 = b.x**2 - b.z**2
    temp2 = a.x**2 - a.z**2

    bot = a.y**2 * temp1 - b.y**2 * temp2

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return top / bot


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

    return u1(a, b)


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get third coordinate of point or ∞ if something bad."""
    if not isclose(abs(u3(a, b)), 0, rel_tol=PRECISION):
        underroot = omega(a, b)**2 - theta(a, b)

        if underroot < 0:
            return inf

        return -u1(a, b) * (omega(a, b) + eps * sqrt(underroot)) - u2(a, b)

    underroot = omega_u3(a, b)**2 - u1(a, b)**2 - u2(a, b)**2

    if underroot < 0:
        return inf

    return omega_u3(a, b) + eps * sqrt(underroot)
