from point import Point3

precision = 1e-5

def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x


def delta(a: Point3, b: Point3) -> float:
    return a.x * b.y + a.y * b.x
