from math import inf, isfinite, sqrt

from point import Point2, Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x


def omega_1(a: Point3, b: Point3) -> float:
    t1 = b.x**2 + b.y**2 - b.z**2
    t2 = a.x**2 + a.y**2 - a.z**2

    top = a.x * a.y * t1 - b.x * b.y * t2

    t1 = b.x**2 - b.z**2
    t2 = a.x**2 - a.z**2

    bot = a.y**2 * t1 - b.y**2 * t2

    if not bot:
        return inf

    return top / bot


def theta(a: Point3, b: Point3) -> float:
    t1 = b.y**2 - b.z**2
    t2 = a.y**2 - a.z**2

    top = a.x**2 * t1 - b.x**2 * t2

    t1 = b.x**2 - b.z**2
    t2 = a.x**2 - a.z**2

    bot = a.y**2 * t1 - b.y**2 * t2

    if not bot:
        return inf

    return top / bot


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    Omega = omega_1(a, b)
    Theta = theta(a, b)

    if not isfinite(Omega):
        return inf

    underroot = Omega**2 - Theta

    if underroot < 0:
        return inf

    t = Omega + eps * sqrt(underroot)

    return u3(a, b) * t


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b)


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    Omega = omega_1(a, b)
    Theta = theta(a, b)

    if not isfinite(Omega):
        return inf

    underroot = Omega**2 - Theta

    if underroot < 0:
        return inf

    t = Omega + eps * sqrt(underroot)

    return -u1(a, b) * t - u2(a, b)
