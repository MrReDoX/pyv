from random import choice


# Odd indexes (0, 1, 2, 3, 4, 5, ... -> 1, 3, 5, 7, ...)
def strategy(verticies: list, prev: list) -> int:
    excluded = verticies[1::2]

    return choice(excluded)
