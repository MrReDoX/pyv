def u1(a: Point3, b: Point3) -> float:
    return a.y * b.z - a.z * b.y

def u2(a: Point3, b: Point3) -> float:
    return a.z * b.x - a.x * b.z

def u3(a: Point3, b: Point3) -> float:
    return a.x * b.y - a.y * b.x

def delta(a: Point3, b: Point3) -> float:
    return a.x * b.y + a.y * b.x

def c1(a: Point3, b: Point3, rel=1) -> float:
    return u3(a, b) * (2 * a.x * b.x * u2(a, b) - u1(a, b) * delta(a, b))

def c2(a: Point3, b: Point3, rel=1) -> float:
    return u3(a, b) * (u2(a, b) * delta(a, b) - 2 * a.y * b.y * u1(a, b))

def c3(a: Point3, b: Point3, rel=1) -> float:
    U1 = u1(a, b)
    U2 = u2(a, b)
