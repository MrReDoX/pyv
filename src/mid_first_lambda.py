"""Coordinate function for frame of the first type with given relation."""

from cmath import sqrt

from Point import Point3
from SpecialFunctions import k, phi_bar, phi_big


def coord(i: int, m: Point3, b: Point3, mu: float) -> float | complex:
    """Return i'th coordinate of mid point."""
    first = k(i, m, b, bar=True) * (phi_bar(m, b) - sqrt(phi_big(m, b)))**mu
    second = k(i, m, b, bar=False) * (phi_bar(m, b) + sqrt(phi_big(m, b)))**mu

    return first - second
