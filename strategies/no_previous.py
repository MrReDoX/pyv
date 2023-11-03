from random import choice


# Choose random except previous
def strategy(verticies: list, prev: list) -> int:
    good = verticies
    if prev:
        good = [i for i in verticies if i != prev[-1]]

    return choice(good)
