from point import Point3
from utility import u1, u2, u3


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (2 * a.x * b.x * u2(a, b) - u1(a, b) * delta(a, b))


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (u2(a, b) * delta(a, b) - 2 * a.y * b.y * u1(a, b))


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    U1 = u1(a, b)
    U2 = u2(a, b)

    return delta(a, b) * (U1**2 - U2**2) - 2 * U1 * U2 * (a.x * b.x - a.y * b.y)
