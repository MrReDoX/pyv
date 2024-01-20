"""2 and 3 coordinate point class with convinient helping functions."""

from cmath import isfinite

from utility import distance_inf, isclose_prec


class Point2:
    """2 coordinate point."""
    def __init__(self, new_x: float | complex, new_y: float | complex):
        self.x = new_x
        self.y = new_y
        self.coords = [self.x, self.y]


    def __str__(self) -> str:
        """Return string of the form (x, y)."""
        return f'({self.x}, {self.y})'


    def __iter__(self):
        """Star syntax with point coordinates."""
        return (self.__dict__[item] for item in list(sorted(self.__dict__))[1:])


    def __getitem__(self, key) -> float | complex:
        # x — 1
        # y — 2

        return self.coords[key - 1]

    def __eq__(self, other) -> bool:
        if isinstance(other, Point2):
            diffs_close = [isclose_prec(abs(self[i] - other[i]), 0) for i in range(2)]

            return all(diffs_close)

        return False



    def to_tuple(self):
    # def to_tuple(self):
        """Return tuple of the form (x, y)."""
        return tuple(self.coords)
        # return (self.x, self.y)


    def isfinite(self) -> bool:
        """Check that both coordinates are finite."""
        return all(map(isfinite, self.coords))
        # return isfinite(self.x) and isfinite(self.y)


    def to_point3(self, new_z: float | complex):
        """Convert to point with 3 coordinates."""
        return Point3(self.x, self.y, new_z)


    def is_complex(self) -> bool:
        if isinstance(self.x, complex):
            conds = [not isclose_prec(abs(t.imag), 0) for t in [self.x, self.y]]
            # conds = [abs(t.imag) > PRECISION for t in [self.x, self.y]]

            return any(conds)

        return False


    def to_float(self):
        """Convinient function when working with float lambda."""
        if isinstance(self.x, complex):
            return Point2(self.x.real, self.y.real)

        return Point2(self.x, self.y)


class Point3:
    """3 coordinate point."""
    def __init__(self, new_x: float | complex, new_y: float | complex, new_z: float | complex):
        self.x = new_x
        self.y = new_y
        self.z = new_z
        self.coords = [self.x, self.y, self.z]


    def __str__(self) -> str:
        """Return string of the form (x:y:z)."""
        return f'({self.x}:{self.y}:{self.z})'


    def __iter__(self):
        """Star syntax with point coordinates."""
        return (self.__dict__[item] for item in list(sorted(self.__dict__))[1:])


    def __getitem__(self, key) -> float | complex:
        # x — 1
        # y — 2
        # z — 3
        return self.coords[key - 1]


    def __eq__(self, other):
        if isinstance(other, Point3):
            return distance_inf(self, other)

        return False


    def to_tuple(self):
        """Return tuple of the form (x, y, z)."""
        return tuple(self.coords)
        # return (self.x, self.y, self.z)


    def isfinite(self) -> bool:
        """Check that all coordinates are finite."""
        return all(map(isfinite, self.coords))
        # return isfinite(self.x) and isfinite(self.y) and isfinite(self.z)


    def to_point2(self) -> Point2:
        """Return from homogeneous coordinates by diving on z."""
        if self.z:
            return Point2(self.x / self.z, self.y / self.z)

        return Point2(self.x, self.y)


    def to_float(self):
        """Convinient function when working with float lambda."""
        if isinstance(self.x, complex):
            return Point3(self.x.real, self.y.real, self.z.real)

        return Point3(self.x, self.y, self.z)

class nPoint:
    def __init__(self, *new_coords):
        self.v = list(new_coords)
        self.n = len(new_coords)

    def __str__(self) -> str:
        """Return string of the form (v_1, v_2, \\ldots, v_n)."""
        return '(' + ', '.join(map(str, self.v)) + ')'

    def __getitem__(self, key):
        """Reload [] operator for convenient use."""
        return self.v[key]

    def __setitem__(self, key, value):
        """Reload [] operator for convenient use."""
        self.v[key] = value

    def to_tuple(self):
        """Return tuple of the form (v_1, v_2, \\ldots, v_n)."""
        return tuple(i for i in self.v)

    def to_list(self):
        """Return list of the form [v_1, v_2, \\ldots, v_n]."""
        return self.v

    def isfinite(self) -> bool:
        """Check that all coordinates are finite."""
        return all(map(isfinite, self.v))

    def to_lower_dimension(self):
        """Convert to point with n-1 coordinates."""
        answer = self.v[:-1]
        if self.v[-1]:
            answer = list(map(lambda x: x / self.v[-1], answer))

        return nPoint(*answer)

    def to_bigger_dimension(self, new_coord: float):
        """Add new coordinate to the end."""
        l = self.v + [new_coord]

        return nPoint(*l)
