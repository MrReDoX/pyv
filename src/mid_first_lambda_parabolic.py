"""Coordinate function for frame of the first type and parabolic lines with given relation."""

from Point import Point3
from SpecialFunctions import phi, phi_bar


def coord(i: int, m: Point3, b: Point3, lamb: float) -> complex:
    """Return i'th coordinate of mid point."""
    return m[i] * phi_bar(m, b) + lamb * b[i] * phi(m)
