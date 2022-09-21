from point import Point3


def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y


def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z


def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x


def delta(a: Point3, b: Point3) -> float:
    return a.x * b.y + a.y * b.x


def first_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (2 * a.x * b.x * u2(a, b) - u1(a, b) * delta(a, b))


def second_coord(a: Point3, b: Point3, eps=1) -> float:
    return u3(a, b) * (u2(a, b) * delta(a, b) - 2 * a.y * b.y * u1(a, b))


def third_coord(a: Point3, b: Point3, eps=1) -> float:
    U1 = u1(a, b)
    U2 = u2(a, b)

    return delta(a, b) * (U1**2 - U2**2) - 2 * U1 * U2 * (a.x * b.x - a.y * b.y)
