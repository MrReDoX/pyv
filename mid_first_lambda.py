from cmath import sqrt

from point import Point3
from utility import k, phi_bar, phi_big


def coord(i: int, m: Point3, b: Point3, mu: float) -> complex:
    first = k(i, m, b) * (phi_bar(m, b) - sqrt(phi_big(m, b)))**(mu-1)
    second = k(i, m, b, bar=True) * (phi_bar(m, b) + sqrt(phi_big(m, b)))**(mu-1)

    return first - second
