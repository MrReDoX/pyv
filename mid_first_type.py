from math import inf, isfinite, sqrt

from point import Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x



def omega(a: Point3, b: Point3) -> float:
    bot = a.y**2 * (b.x**2 - b.z**2) - b.y**2 * (a.x**2 - a.z**2)

    if abs(bot) < 1e-4:
        return inf

    top = a.x * a.y * (b.x**2 + b.y**2 - b.z**2) \
          - b.x * b.y * (a.x**2 + a.y**2 - a.z**2)

    return top / bot


def theta(a: Point3, b: Point3) -> float:
    bot = a.x**2 * (b.y**2 - b.z**2) - b.x**2 * (a.y**2 - a.z**2)

    if abs(bot) < 1e-4:
        return inf

    top = a.x**2 * (b.y**2 - b.z**2) - b.x**2 * (a.y**2 - a.z**2)

    return top / bot


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    omega_val = omega(a, b)
    u3_val = u3(a, b)

    if abs(u3_val) < 1e-4:
        return inf

    underroot = omega_val**2 - theta(a, b)

    if underroot < 0:
        return inf

    return u3_val * (omega_val + eps * sqrt(underroot))


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b)


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    omega_val = omega(a, b)
    underroot = omega_val**2 - theta(a, b)

    if underroot < 0:
        return inf

    return -u1(a, b) * (omega_val + eps * sqrt(underroot)) - u2(a, b)
