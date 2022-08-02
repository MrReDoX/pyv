# Point module


class Point2:
    def __init__(self, new_x: float, new_y: float):
        self.x = new_x
        self.y = new_y

    def __str__(self) -> str:
        return str((self.x, self.y))

    def isfinite(self) -> bool:
        from math import isfinite

        return all(map(isfinite, [self.x, self.y]))

    def to_Point3(self, new_z: float):
        return Point3(self.x, self.y, new_z)

    def to_float(self):
        if isinstance(self.x, complex):
            return Point2(self.x.real, self.y.real)

        return Point2(self.x, self.y)


class Point3:
    def __init__(self, new_x: float, new_y: float, new_z: float):
        self.x = new_x
        self.y = new_y
        self.z = new_z

    def __str__(self) -> str:
        return f'({self.x}:{self.y}:{self.z})'

    def isfinite(self) -> bool:
        from math import isfinite

        return all(map(isfinite, [self.x, self.y]))

    def to_Point2(self) -> Point2:
        if self.z:
            return Point2(self.x / self.z, self.y / self.z)

        return Point2(self.x, self.y)

    def to_float(self):
        if isinstance(self.x, complex):
            return Point3(self.x.real, self.y.real, self.z.real)

        return Point3(self.x, self.y, self.z)

