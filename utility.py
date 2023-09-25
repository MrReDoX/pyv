"""Widely used functions firstnd precision setting for isclose."""


from point import Point3

PRECISION = 1e-3


def u1(first: Point3, second: Point3) -> float:
    return first.y * second.z - first.z * second.y


def u2(first: Point3, second: Point3) -> float:
    return first.z * second.x - first.x * second.z


def u3(first: Point3, second: Point3) -> float:
    return first.x * second.y - first.y * second.x


def delta(first: Point3, second: Point3) -> float:
    return first.x * second.y + first.y * second.x
