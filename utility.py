"""Widely used functions
."""

from math import hypot, isclose
from typing import Literal

from constants import PRECISION


def distance(a, b) -> float:
    """Default eucledian distance

    Args:
        a (nPoint): first point
        b (nPoint): second point

    Returns:
        float: eucledian distance between a and b
    """
    return hypot(*[i - j for i, j in zip(a, b)])

def distance_inf(a, b) -> float:
    """max distance

    Args:
        a (nPoint): first point
        b (nPoint): second point

    Returns:
        float: max distance between a and b
    """
    return max(abs(i - j) for i, j in zip(a ,b))

def isclose_prec(a: float, b: float) -> bool:
    """Python's isclose with given precision

    Args:
        a (float): first value
        b (float): second value

    Returns:
        bool: is two values are close
    """
    return isclose(a, b, rel_tol=PRECISION)

def signum(x: float) -> Literal[-1, 1, 0]:
    """Default sgn function

    Returns:
        {-1, 1, 0}: -1 if x < 0; 0 if x > 0; and 0 otherwise
    """
    if x < 0:
        return -1

    if x > 0:
        return 1

    return 0