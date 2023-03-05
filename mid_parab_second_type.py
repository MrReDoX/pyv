"""Formulas for the second frame parabolic type with lambda = 1."""

from point import Point3
from utility import delta, u1, u2, u3


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get first coordinate of point or ∞ if something bad."""
    return u3(a, b) * (2 * a.x * b.x * u1(a, b) - u2(a, b) * delta(a, b))


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get second coordinate of point or ∞ if something bad."""
    return u3(a, b) * (u1(a, b) * delta(a, b) - 2 * a.y * b.y * u2(a, b))


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    """Get third coordinate of point or ∞ if something bad."""
    return 2 * (a.y * b.y * u2(a, b)**2 - a.x * b.x * u1(a, b)**2)
