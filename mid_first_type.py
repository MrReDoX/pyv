from math import inf, isclose, isfinite, sqrt

from point import Point2, Point3
from utility import PRECISION, u1, u2, u3


def omega(a: Point3, b: Point3) -> float:
    t1 = b.x**2 + b.y**2 - b.z**2
    t2 = a.x**2 + a.y**2 - a.z**2

    top = a.x * a.y * t1 - b.x * b.y * t2

    t1 = b.x**2 - b.z**2
    t2 = a.x**2 - a.z**2

    bot = a.y**2 * t1 - b.y**2 * t2

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return top / bot


def omega_u3(a: Point3, b: Point3) -> float:
    u1_val = u1(a, b)
    u2_val = u2(a, b)

    bot = u1_val * (a.y * b.z + a.z * b.y)

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return (a.y * b.y * (u1_val**2 + u2_val**2) + a.z * b.z * u1_val**2) / bot


def theta(a: Point3, b: Point3) -> float:
    t1 = b.y**2 - b.z**2
    t2 = a.y**2 - a.z**2

    top = a.x**2 * t1 - b.x**2 * t2

    t1 = b.x**2 - b.z**2
    t2 = a.x**2 - a.z**2

    bot = a.y**2 * t1 - b.y**2 * t2

    if isclose(abs(bot), 0, rel_tol=PRECISION):
        return inf

    return top / bot


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=PRECISION):
        Omega = omega(a, b)

        underroot = Omega**2 - theta(a, b)

        if underroot < 0:
            return inf

        return u3_val * (Omega + eps * sqrt(underroot))

    # u3 ~ 0
    return -u2(a, b)


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=PRECISION):
        return u3_val

    return u1(a, b)


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=PRECISION):
        Omega = omega(a, b)
        underroot = Omega**2 - theta(a, b)

        if underroot < 0:
            return inf

        return -u1(a, b) * (Omega + eps * sqrt(underroot)) - u2(a, b)

    omega_val = omega_u3(a, b)
    underroot = omega_val**2 - u1(a, b)**2 - u2(a, b)**2

    if underroot < 0:
        return inf

    return omega_val + eps * sqrt(underroot)
