"""Widely used functions."""

from math import hypot, isclose
from typing import Literal

import mpmath as mp

from Constants import PRECISION


def distance(a, b) -> float:
    """Calculate Euclidean distance between two n-dimensional points.

    Args:
        a (nPoint): First point
        b (nPoint): Second point

    Returns:
        float: Euclidean distance between a and b
    """
    return hypot(*[i - j for i, j in zip(a, b, strict=True)])


def distance_inf(a, b) -> float:
    """Calculate Chebyshev (maximum) distance between two points.

    Also known as L∞ distance or chessboard distance.

    Args:
        a (nPoint): First point
        b (nPoint): Second point

    Returns:
        float: Maximum absolute difference between coordinates
    """
    return max(abs(i - j) for i, j in zip(a, b, strict=True))


def isclose_prec(a, b) -> bool:
    """Python's isclose with given precision.

    Args:
        a: first value
        b: second value

    Returns:
        bool: is two values are close
    """
    if isinstance(a, mp.mpf | mp.mpc):
        return mp.almosteq(a, b)

    return isclose(a, b, rel_tol=PRECISION)


def signum(x) -> Literal[-1, 1, 0]:
    """Calculate the sign of a number.

    Returns:
        {-1, 1, 0}: -1 if x < 0; 0 if x > 0; and 0 otherwise
    """
    if isinstance(x, mp.mpf):
        return mp.sign(x)

    if x < 0:
        return -1

    if x > 0:
        return 1

    return 0
