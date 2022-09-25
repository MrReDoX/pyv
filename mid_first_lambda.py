import cmath
import math

from point import Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    answer = a.x * b.y - a.y * b.x

    if not answer:
        return math.inf

    return answer


def k(a: Point3, b: Point3) -> float:
    U1 = u1(a, b)
    U3 = u3(a, b)

    if not math.isfinite(U3):
        return math.inf

    return U1**2 - U3**2


def k1(a: Point3, b: Point3) -> complex:
    U1 = u1(a, b)
    U2 = u2(a, b)
    U3 = u3(a, b)

    if not cmath.isfinite(U3):
        return cmath.inf

    s1 = -U1 * U2
    s2 = U3 * cmath.sqrt(U1**2 + U2**2 - U3**2)

    return s1 + s2


def k2(a: Point3, b: Point3) -> complex:
    U1 = u1(a, b)
    U2 = u2(a, b)
    U3 = u3(a, b)

    if not cmath.isfinite(U3):
        return cmath.inf

    s1 = -U1 * U2
    s2 = U3 * cmath.sqrt(U1**2 + U2**2 - U3**2)

    return s1 - s2


def omega1(a: Point3, b: Point3, coeff: float) -> complex:
    K1 = k1(a, b)
    K = k(a, b)

    if not all(map(cmath.isfinite, [K1, K])):
        return cmath.inf

    m1 = a.x * K - a.y * K1
    m2 = b.x * K - b.y * K1

    if not m1 * m2:
        return cmath.inf

    return m1**(1 / (1 + coeff)) * m2**(coeff / (1 + coeff))


def omega2(a: Point3, b: Point3, coeff: float) -> float:
    K2 = k2(a, b)
    K = k(a, b)

    if not all(map(cmath.isfinite, [K2, K])):
        return cmath.inf

    m1 = a.x * K - a.y * K2
    m2 = b.x * K - b.y * K2

    if not m1 * m2:
        return cmath.inf

    return m1**(1 / (1 + coeff)) * m2**(coeff / (1 + coeff))


def first_coord(a: Point3, b: Point3, coeff: float) -> complex:
    U3 = u3(a, b)
    K1 = k1(a, b)
    K2 = k2(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U3, K1, K2, Omega1, Omega2]
    if not all(map(cmath.isfinite, vals)):
        return cmath.inf

    return U3 * (K2 * Omega1 - K1 * Omega2)


def second_coord(a: Point3, b: Point3, coeff: float) -> complex:
    U3 = u3(a, b)
    K = k(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U3, K, Omega1, Omega2]
    if not all(map(cmath.isfinite, vals)):
        return cmath.inf

    return U3 * K * (Omega1 - Omega2)


def third_coord(a: Point3, b: Point3, coeff: float) -> complex:
    U1 = u1(a, b)
    U2 = u2(a, b)
    K = k(a, b)
    K1 = k1(a, b)
    K2 = k2(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U1, U2, K, K1, K2, Omega1, Omega2]
    if not all(map(cmath.isfinite, vals)):
        return cmath.inf

    s1 = Omega2 * (U1 * K1 + U2 * K)
    s2 = Omega1 * (U1 * K2 + U2 * K)

    return s1 - s2
