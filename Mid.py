from Point import Point2
from Point import Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x


def omega_1(a: Point3, b: Point3) -> float:
    from math import inf

    t1 = b.x * b.x + b.y * b.y - b.z * b.z
    t2 = a.x * a.x + a.y * a.y - a.z * a.z

    top = a.x * a.y * t1 - b.x * b.y * t2

    t1 = b.x * b.x - b.z * b.z
    t2 = a.x * a.x - a.z * a.z

    bot = a.y * a.y * t1 - b.y * b.y * t2

    if not bot:
        return inf

    return top / bot


def theta(a: Point3, b: Point3) -> float:
    from math import inf

    t1 = b.y * b.y - b.z * b.z
    t2 = a.y * a.y - a.z * a.z

    top = a.x * a.x * t1 - b.x * b.x * t2

    t1 = b.x * b.x - b.z * b.z
    t2 = a.x * a.x - a.z * a.z

    bot = a.y * a.y * t1 - b.y * b.y * t2

    if not bot:
        return inf

    return top / bot


def c1(a: Point3, b: Point3, eps=1) -> float:
    from math import inf, isfinite, sqrt

    Omega = omega_1(a, b)
    Theta = theta(a, b)

    if not isfinite(Omega):
        return inf

    underroot = Omega * Omega - Theta

    if underroot < 0:
        return inf

    t = Omega + eps * sqrt(underroot)

    return u3(a, b) * t


def c2(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b)


def c3(a: Point3, b: Point3, eps=1) -> float:
    from math import inf, isfinite, sqrt

    Omega = omega_1(a, b)
    Theta = theta(a, b)

    if not isfinite(Omega):
        return inf

    underroot = Omega * Omega - Theta

    if underroot < 0:
        return inf

    t = Omega + eps * sqrt(underroot)

    return -u1(a, b) * t - u2(a, b)

