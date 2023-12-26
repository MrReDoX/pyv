"""Widely used functions firstnd precision setting for isclose."""


from cmath import sqrt
from math import inf, isclose

from point import Point2, Point3

PRECISION = 1e-10


def u1(first: Point3, second: Point3) -> float:
    return first.y * second.z - first.z * second.y


def u2(first: Point3, second: Point3) -> float:
    return first.z * second.x - first.x * second.z


def u3(first: Point3, second: Point3) -> float:
    return first.x * second.y - first.y * second.x

def phi_big(m: Point3, b: Point3):
    return u1(m, b)**2 + u2(m, b)**2 - u3(m, b)**2

def phi(m: Point3):
    return m.x**2 + m.y**2 - m.z**2

def phi_bar(m: Point3, b: Point3):
    return m.x * b.x + m.y * b.y - m.z * b.z

def k(i, m, b, bar=False):
    fm = {1: m.x, 2: m.y, 3: m.z}
    fb = {1: b.x, 2: b.y, 3: b.z}

    sign = 1
    if bar:
        sign = -1

    return fb[i] * phi(m) - fm[i] * phi_bar(m, b) + sign * fm[i] * sqrt(phi_big(m, b))


def delta(first: Point3, second: Point3) -> float:
    return first.x * second.y + first.y * second.x

def harmonic(a: Point3, b: Point3, c: Point3, d: Point3) -> float:
    numer = (a.x * c.y - c.x * a.y) * (b.x * d.y - d.x * b.y)
    den = (a.x * d.y - d.x * a.y) * (b.x * c.y - c.x * b.y)

    if isclose(abs(den), 0):
        return inf

    return numer / den

def line_intersection(x1: float, y1: float,
                      x2: float, y2: float,
                      x3: float, y3: float,
                      x4: float, y4: float) -> Point2:
    p_x_num = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    p_y_num = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if isclose(abs(den), 0):
        return Point2(inf, inf)

    return Point2(p_x_num / den, p_y_num / den)
