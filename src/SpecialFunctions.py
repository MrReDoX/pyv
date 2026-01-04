from cmath import inf, sqrt

from Point import Point3
from Utility import isclose_prec


def u1(m: Point3, b: Point3):
    return m[2] * b[3] - m[3] * b[2]


def u2(m: Point3, b: Point3):
    return m[3] * b[1] - m[1] * b[3]


def u3(m: Point3, b: Point3):
    return m[1] * b[2] - m[2] * b[1]


def phi_big(m: Point3, b: Point3):
    return u1(m, b)**2 + u2(m, b)**2 - u3(m, b)**2


def phi_bar(m: Point3, b: Point3):
    return m[1] * b[1] + m[2] * b[2] - m[3] * b[3]


def phi(m: Point3):
    return phi_bar(m, m)


def k(i: int, m: Point3, b: Point3, *, bar: bool) -> complex:
    sign = -1 if bar else 1

    first_summand = b[i] * phi(m) - m[i] * phi_bar(m, b)
    second_summand = sign * m[i] * sqrt(phi_big(m, b))

    return first_summand + second_summand


def harmonic(a: Point3, b: Point3, c: Point3, d: Point3) -> float:
    numer = (a[1] * c[2] - c[1] * a[2]) * (b[1] * d[2] - d[1] * b[2])
    den = (a[1] * d[2] - d[1] * a[2]) * (b[1] * c[2] - c[1] * b[2])

    # if isclose_prec(mp.fabs(den), 0):
    if isclose_prec(abs(den), 0):
        return inf

    return numer / den
