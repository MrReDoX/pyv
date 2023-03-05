"""Formulas for the first frame type with lambda ≠ 1."""

import cmath
import math

from point import Point3
from utility import PRECISION, u1, u2, u3


def k(a: Point3, b: Point3) -> float:
    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    return u1(a, b)**2 - u3(a, b)**2


def k1(a: Point3, b: Point3) -> complex:
    u_1 = u1(a, b)
    u_2 = u2(a, b)
    u_3 = u3(a, b)

    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    first_summand = -u_1 * u_2
    second_summand = u_3 * cmath.sqrt(u_1**2 + u_2**2 - u_3**2)

    return first_summand + second_summand


def k2(a: Point3, b: Point3) -> complex:
    u_1 = u1(a, b)
    u_2 = u2(a, b)
    u_3 = u3(a, b)

    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    first_summand = -u_1 * u_2
    second_summand = u_3 * cmath.sqrt(u_1**2 + u_2**2 - u_3**2)

    return first_summand - second_summand


def omega1(a: Point3, b: Point3, coeff: float) -> complex:
    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    base1 = a.x * k(a, b) - a.y * k1(a, b)
    base2 = b.x * k(a, b) - b.y * k1(a, b)

    if math.isclose(abs(base1 * base2), 0, rel_tol=PRECISION):
        return cmath.inf

    return base1**(1 / (1 + coeff)) * base2**(coeff / (1 + coeff))


def omega2(a: Point3, b: Point3, coeff: float) -> complex:
    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    base1 = a.x * k(a, b) - a.y * k2(a, b)
    base2 = b.x * k(a, b) - b.y * k2(a, b)

    if math.isclose(abs(base1 * base2), 0, rel_tol=PRECISION):
        return cmath.inf

    return base1**(1 / (1 + coeff)) * base2**(coeff / (1 + coeff))


def first_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get first coordinate of point or ∞ if something bad."""
    omega_1 = omega1(a, b, coeff)
    omega_2 = omega2(a, b, coeff)

    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    return u3(a, b) * (k2(a, b) * omega_1 - k1(a, b) * omega_2)


def second_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get second coordinate of point or ∞ if something bad."""
    omega_1 = omega1(a, b, coeff)
    omega_2 = omega2(a, b, coeff)

    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    return u3(a, b) * k(a, b) * (omega_1 - omega_2)


def third_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get third coordinate of point or ∞ if something bad."""
    omega_1 = omega1(a, b, coeff)
    omega_2 = omega2(a, b, coeff)

    if cmath.isclose(u3(a, b), 0, rel_tol=PRECISION):
        return cmath.inf

    first_summand = omega_2 * (u1(a, b) * k1(a, b) + u2(a, b) * k(a, b))
    second_summand = omega_1 * (u1(a, b) * k2(a, b) + u2(a, b) * k(a, b))

    return first_summand - second_summand
