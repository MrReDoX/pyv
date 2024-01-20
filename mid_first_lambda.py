from cmath import sqrt

from point import Point3
from special_functions import k, phi_bar, phi_big


def coord(i: int, m: Point3, b: Point3, mu: float) -> float | complex:
    first = k(i, m, b, bar=True) * (phi_bar(m, b) - sqrt(phi_big(m, b)))**mu
    second = k(i, m, b) * (phi_bar(m, b) + sqrt(phi_big(m, b)))**mu

    # print(f'k_bar: {k(i, m, b, bar=True)}')
    # print(f'k: {k(i, m, b)}')

    # print(f'first: {first}')
    # print(f'second: {second}')
    # print()

    return first - second