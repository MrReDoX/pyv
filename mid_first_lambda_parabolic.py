from point import Point3
from special_functions import phi, phi_bar


def coord(i: int, m: Point3, b: Point3, lamb: float) -> complex:
    return m[i] * phi_bar(m, b) + lamb * b[i] * phi(m)