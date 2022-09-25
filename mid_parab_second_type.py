from point import Point3
from utility import *


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (2 * a.x * b.x * u1(a, b) - u2(a, b) * delta(a, b))


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (u1(a, b) * delta(a, b) - 2 * a.y * b.y * u2(a, b))


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    return 2 * (a.y * b.y * u2(a, b)**2 - a.x * b.x * u1(a, b)**2)
