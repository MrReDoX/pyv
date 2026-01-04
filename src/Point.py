"""2 and 3 coordinate point class with convinient helping functions."""

from cmath import isfinite

import mpmath as mp

from Constants import DIGITS
from Utility import distance_inf, isclose_prec

mp.mp.dps = DIGITS

class Point:
    r"""A mutable n-dimensional point supporting real, complex, and arbitrary-precision coordinates.

    Coordinates are stored in a list and can be of mixed numeric types (e.g.,
        float, complex, mp.mpf, mp.mpc).
    The point uses 1-based indexing for convenience via ``__getitem__`` and
        ``__setitem__``.
    It is explicitly **unhashable** (``__hash__ = None``) because it is mutable.

    Examples:
        >>> p = Point(1, 2, 3)
        >>> p[1]  # 1-based indexing
        1
        >>> p.to_tuple()
        (1, 2, 3)
        >>> q = Point(mp.mpf('1.5'), mp.mpc('2+3j'))
        >>> q.isfinite()
        True
    """

    __hash__ = None  # явно помечаем как нехешируемый

    def __init__(self, *new_coords):
        """Initialize a point with given coordinates.

        Args:
            *new_coords: Coordinate values (any numeric type).
        """
        self.coords = list(new_coords)

    def __getitem__(self, i: int):
        """Access coordinate by 1-based index.

        **This class intentionally violates Python indexing conventions**.

        Args:
            i (int): Coordinate index (starting from 1).

        Returns:
            Any: The i-th coordinate (equivalent to ``self.coords[i - 1]``).
        """
        return self.coords[i - 1]

    def __setitem__(self, i: int, value):
        """Set coordinate by 1-based index.

        Args:
            i (int): Coordinate index (starting from 1).
            value: New value for the i-th coordinate.
        """
        self.coords[i - 1] = value

    def __iter__(self):
        """Iterate over coordinates.

        Returns:
            iterator: An iterator over ``self.coords``.
        """
        return iter(self.coords)

    def __str__(self) -> str:
        r"""Return a human-readable string representation.

        Returns:
            str: String of the form ``(v_1, v_2, \ldots, v_n)``.
        """
        return '(' + ', '.join(map(str, self.coords)) + ')'

    def __eq__(self, other):
        """Compare two points for approximate equality. Equality is heuristic and context-dependent.

        Uses ``mp.almosteq`` for ``mp.mpf``/``mp.mpc`` coordinates;
        otherwise uses ``isclose_prec`` with infinity norm.

        Args:
            other (Point): Another point to compare with.

        Returns:
            bool: True if all coordinates are approximately equal, False otherwise.
        """
        if not isinstance(other, Point):
            return False
        if len(self.coords) != len(other.coords):
            return False
        if all(isinstance(x, mp.mpf) for x in self.coords):
            return all(mp.almosteq(a, b)
                       for a, b in zip(self.coords, other.coords, strict=True))
        return isclose_prec(distance_inf(self, other), 0)

    def to_tuple(self):
        r"""Return coordinates as a tuple.

        Returns:
            tuple: Tuple of the form ``(v_1, v_2, \ldots, v_n)``.
        """
        return tuple(self.coords)

    def to_list(self):
        r"""Return coordinates as a list.

        Returns:
            list: List of the form ``[v_1, v_2, \ldots, v_n]``.
        """
        return list(self.coords)

    def isfinite(self) -> bool:
        """Check whether all coordinates are finite numbers.

        Uses ``cmath.isfinite`` for each coordinate.

        Returns:
            bool: True if all coordinates are finite, False otherwise.
        """
        return all(map(isfinite, self.coords))

    def to_float(self):
        """Extract real parts of coordinates for compatibility with real-valued contexts.

        Converts ``mp.mpc`` → ``mp.re(...)``, ``complex`` → ``.real``; leaves others unchanged.

        Returns:
            Point: A new point with real-valued coordinates.
        """
        ans_coords = []
        for coord in self.coords:
            ans_coords.append(coord)
            if isinstance(coord, mp.mpc):
                ans_coords[-1] = mp.re(coord)
            elif isinstance(coord, complex):
                ans_coords[-1] = coord.real

        return Point(*ans_coords)

    def to_lower_dimension(self):
        """Project to (n-1)-dimensional space via homogeneous coordinate normalization.

        If the last coordinate is non-zero, divides all preceding coordinates by it.
        Otherwise, simply drops the last coordinate.

        Returns:
            Point: A new point with one fewer coordinate.
        """
        ans_coords = self.coords[:-1]
        if not isclose_prec(abs(self.coords[-1]), 0):
            ans_coords = [x / self.coords[-1] for x in ans_coords]

        return Point(*ans_coords)

    def to_bigger_dimension(self, new_coord):
        """Embed into (n+1)-dimensional space by appending a new coordinate.

        Args:
            new_coord: Value of the new last coordinate.

        Returns:
            Point: A new point with one additional coordinate at the end.
        """
        coords = [*self.coords, new_coord]

        return Point(*coords)


class Point2(Point):
    """A mutable 2-dimensional point with direct access to x and y coordinates.

    Inherits from :class:`Point` and adds named attributes ``x`` and ``y`` for
    convenience. Supports real, complex, and arbitrary-precision numeric types.
    Uses 1-based indexing like the base class, but also allows ``p.x`` and ``p.y``.

    Examples:
        >>> p = Point2(1.0, 2.0)
        >>> p.x, p[1]
        (1.0, 1.0)
        >>> q = Point2(mp.mpc('1+2j'), 3)
        >>> q.is_complex()
        True
    """

    def __init__(self, x, y):
        """Initialize a 2D point with x and y coordinates.

        Args:
            x: The first coordinate (horizontal).
            y: The second coordinate (vertical).
        """
        super().__init__(x, y)
        self.x, self.y = self.coords

    def is_complex(self) -> bool:
        """Check whether any coordinate has a non-zero imaginary part.

        Only considers coordinates of type ``complex`` or ``mp.mpc``.
        Returns ``False`` if all coordinates are real-valued.

        Returns:
            bool: True if at least one coordinate has a non-negligible imaginary component.
        """
        return any(
            not isclose_prec(abs(coord.imag), 0)
            for coord in self.coords
            if isinstance(coord, complex)
        )


class Point3(Point):
    """A mutable 3-dimensional point with direct access to x, y, and z coordinates.

    Inherits from :class:`Point` and adds named attributes ``x``, ``y``, and ``z``
    for ergonomic access. Supports real, complex, and arbitrary-precision numeric types
    (e.g., ``float``, ``complex``, ``mp.mpf``, ``mp.mpc``). Uses 1-based indexing like
    the base class but also allows ``p.x``, ``p.y``, and ``p.z``.

    Examples:
        >>> p = Point3(1.0, 2.0, 3.0)
        >>> p.z, p[3]
        (3.0, 3.0)
        >>> q = Point3(mp.mpc('1+2j'), 3, mp.mpf('4.5'))
        >>> r = q.to_float()
        >>> r.x, r.y, r.z
        (1.0, 3, 4.5)
    """

    def __init__(self, x, y, z):
        """Initialize a 3D point with x, y, and z coordinates.

        Args:
            x: The first coordinate (often interpreted as horizontal).
            y: The second coordinate (often interpreted as vertical).
            z: The third coordinate (often interpreted as depth or height).
        """
        super().__init__(x, y, z)
        self.x, self.y, self.z = self.coords

    def to_float(self):
        """Return a new Point3 with real parts of coordinates.

        Delegates coordinate conversion to the parent class and repackages
        the result as a Point3.

        Returns:
            Point3: A new 3D point with real-valued coordinates.
        """
        base_point = super().to_float()
        return Point3(*base_point.coords)
