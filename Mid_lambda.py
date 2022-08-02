from Point import Point2
from Point import Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    from math import inf

    answer = a.x * b.y - a.y * b.x

    if not answer:
        return inf

    return answer


def k(a: Point3, b: Point3) -> float:
    from math import inf, isfinite

    U1 = u1(a, b)
    U3 = u3(a, b)

    if not isfinite(U3):
        return inf

    return U1 * U1 - U3 * U3


def k1(a: Point3, b: Point3) -> complex:
    from cmath import inf, isfinite, sqrt

    U1 = u1(a, b)
    U2 = u2(a, b)
    U3 = u3(a, b)

    if not isfinite(U3):
        return inf

    s1 = -U1 * U2
    s2 = U3 * sqrt(U1 * U1 + U2 * U2 - U3 * U3)

    return s1 + s2


def k2(a: Point3, b: Point3) -> complex:
    from cmath import inf, isfinite, sqrt

    U1 = u1(a, b)
    U2 = u2(a, b)
    U3 = u3(a, b)

    if not isfinite(U3):
        return inf

    s1 = -U1 * U2
    s2 = U3 * sqrt(U1**2 + U2**2 - U3**2)

    return s1 - s2


def omega1(a: Point3, b: Point3, coeff: float) -> complex:
    from cmath import inf, isfinite, exp, log

    K1 = k1(a, b)
    K = k(a, b)

    if not (isfinite(K1) and isfinite(K)):
        return inf

    m1 = a.x * K - a.y * K1
    m2 = b.x * K - b.y * K1

    if not m1 * m2:
        return inf

    return m1**(1 / (1 + coeff)) * m2**(coeff / (1 + coeff))


def omega2(a: Point3, b: Point3, coeff: float) -> float:
    from cmath import inf, isfinite, exp, log

    K2 = k2(a, b)
    K = k(a, b)

    if not (isfinite(K2) and isfinite(K)):
        return inf

    m1 = a.x * K - a.y * K2
    m2 = b.x * K - b.y * K2

    if not m1 * m2:
        return inf

    return m1**(1 / (1 + coeff)) * m2**(coeff / (1 + coeff))


def c1(a: Point3, b: Point3, coeff: float) -> complex:
    from cmath import inf, isfinite

    U3 = u3(a, b)
    K1 = k1(a, b)
    K2 = k2(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U3, K1, K2, Omega1, Omega2]
    if any(map(lambda x: not isfinite(x), vals)):
        return inf

    answer = U3 * (K2 * Omega1 - K1 * Omega2)

    return answer


def c2(a: Point3, b: Point3, coeff: float) -> complex:
    from cmath import inf, isfinite

    U3 = u3(a, b)
    K = k(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U3, K, Omega1, Omega2]
    if any(map(lambda x: not isfinite(x), vals)):
        return inf

    answer = U3 * K * (Omega1 - Omega2)

    return answer


def c3(a: Point3, b: Point3, coeff: float) -> complex:
    from cmath import inf, isfinite

    U1 = u1(a, b)
    U2 = u2(a, b)
    K = k(a, b)
    K1 = k1(a, b)
    K2 = k2(a, b)
    Omega1 = omega1(a, b, coeff)
    Omega2 = omega2(a, b, coeff)

    vals = [U1, U2, K, K1, K2, Omega1, Omega2]
    if any(map(lambda x: not isfinite(x), vals)):
        return inf

    s1 = Omega2 * (U1 * K1 + U2 * K)
    s2 = Omega1 * (U1 * K2 + U2 * K)

    answer = s1 - s2

    return answer

