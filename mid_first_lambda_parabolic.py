from point import Point3
from utility import phi, phi_bar


def coord(i: int, m: Point3, b: Point3, lamb: float) -> complex:
    fm = {1: m.x, 2: m.y, 3: m.z}
    fb = {1: b.x, 2: b.y, 3: b.z}

    return fm[i] * phi_bar(m, b) + lamb * fb[i] * phi(m)
