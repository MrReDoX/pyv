"""Formulas for the first frame type with lambda ≠ 1."""

from cmath import sqrt, inf, isclose

from point import Point3
from utility import PRECISION, u1, u2, u3


def k(a: Point3, b: Point3) -> float:
    if isclose(u3(a, b), 0, rel_tol=PRECISION):
        return inf

    return u1(a, b)**2 - u3(a, b)**2


def k12(a: Point3, b: Point3, i: int) -> complex:
    u_1 = u1(a, b)
    u_2 = u2(a, b)
    u_3 = u3(a, b)

    if isclose(u3(a, b), 0, rel_tol=PRECISION):
        return inf

    sgn = {1: 1, 2: -1}

    return -u_1 * u_2 + sgn[i] * u_3 * sqrt(u_1**2 + u_2**2 - u_3**2)


def theta(a: Point3, b: Point3, i: int) -> complex:
    numerator = a.x * k(a, b) - a.y * k12(a, b, i)
    denominator = b.x * k(a, b) - b.y * k12(a, b, i)

    if isclose(denominator, 0, rel_tol=PRECISION):
        return inf

    return numerator / denominator


def calc_coord(a: Point3, b: Point3, lamb: float, i: int) -> complex:
    f_a = {1: a.x, 2: a.y, 3: a.z}
    f_b = {1: b.x, 2: b.y, 3: b.z}

    theta1 = theta(a, b, 1)
    theta2 = theta(a, b, 2)

    degree = 1 / (1 + lamb)

    first_summand = f_a[i] * (theta1**degree - theta2**degree)
    second_summand = f_b[i] * (theta1 * theta2**degree - theta2 * theta1**degree)

    return first_summand + second_summand


def first_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get first coordinate of point or ∞ if something bad."""
    return calc_coord(a, b, coeff, 1)


def second_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get second coordinate of point or ∞ if something bad."""
    return calc_coord(a, b, coeff, 2)


def third_coord(a: Point3, b: Point3, coeff: float) -> complex:
    """Get third coordinate of point or ∞ if something bad."""
    return calc_coord(a, b, coeff, 3)
