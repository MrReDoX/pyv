from cmath import inf, sqrt

from point import Point3
from utility import isclose_prec


def u1(m: Point3, b: Point3) -> float:
    return m[2] * b[3] - m[3] * b[2]

def u2(m: Point3, b: Point3) -> float:
    return m[3] * b[1] - m[1] * b[3]

def u3(m: Point3, b: Point3) -> float:
    return m[1] * b[2] - m[2] * b[1]

def phi_big(m: Point3, b: Point3) -> float:
    return u1(m, b)**2 + u2(m, b)**2 - u3(m, b)**2

def phi_bar(m: Point3, b: Point3) -> complex:
    return m[1] * b[1] + m[2] * b[2] - m[3] * b[3]

def phi(m: Point3) -> float:
    return phi_bar(m, m).real

def k(i: int, m: Point3, b: Point3, bar=False) -> complex:
    sign = -1 if bar else 1

    return b[i] * phi(m) - m[i] * phi_bar(m, b) + sign * m[i] * sqrt(phi_big(m, b))

def harmonic(a: Point3, b: Point3, c: Point3, d: Point3) -> float:
    numer = (a[1] * c[2] - c[1] * a[2]) * (b[1] * d[2] - d[1] * b[2])
    den = (a[1] * d[2] - d[1] * a[2]) * (b[1] * c[2] - c[1] * b[2])

    # numer = (a.x * c.y - c.x * a.y) * (b.x * d.y - d.x * b.y)
    # den = (a.x * d.y - d.x * a.y) * (b.x * c.y - c.x * b.y)

    if isclose_prec(abs(den), 0):
        return inf

    return numer / den