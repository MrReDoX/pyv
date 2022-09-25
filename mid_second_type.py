from math import inf, isclose, isfinite, sqrt

from point import Point3
from utility import *


def omega(a: Point3, b: Point3) -> float:
    VAL1 = b.x * b.y - b.z**2
    VAL2 = a.x * a.y - a.z**2

    bot = a.y**2 * VAL1 - b.y**2 * VAL2

    if isclose(abs(bot), 0, rel_tol=precision):
        return inf

    return (a.x * a.y * VAL1 - b.x * b.y * VAL2) / bot


def omega_u3(a: Point3, b: Point3) -> float:
    return (a.z * b.z * u1(a, b) - a.y * b.y * u2(a, b))\
            / (a.y * b.z + a.z * b.y)


def theta(a: Point3, b: Point3) -> float:
    U1 = u1(a, b)
    U2 = u2(a, b)
    U3 = u3(a, b)
    DELTA = delta(a, b)
    VAL = (2 * U1 * U2 - U3**2)

    bot = DELTA * U1**2 + a.y * b.y * VAL

    if isclose(abs(bot), 0, rel_tol=precision):
        return inf

    return -(DELTA * U2**2 + a.x * b.x * VAL) / bot


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=precision):
        omega_val = omega(a, b)
        underroot = omega_val**2 - theta(a, b)

        if underroot < 0:
            return inf

        return u3_val * (omega_val + eps * sqrt(underroot))

    # u3 ~ 0
    return -u2(a, b)


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=precision):
        return u3_val

    # u3 ~ 0
    return u1(a, b)

def third_coord(a: Point3, b: Point3, eps=1) -> float:
    u3_val = u3(a, b)

    if not isclose(abs(u3_val), 0, rel_tol=precision):
        omega_val = omega(a, b)
        underroot = omega_val**2 - theta(a, b)

        if underroot < 0:
            return inf

        return -u1(a, b) * (omega_val + eps * sqrt(underroot)) - u2(a, b)

    # u3 ~ 0
    omega_val = omega_u3(a, b)
    underroot = omega_val**2 + u1(a, b) * u2(a, b)

    if underroot < 0:
        return inf

    return omega_val + eps * sqrt(underroot)
