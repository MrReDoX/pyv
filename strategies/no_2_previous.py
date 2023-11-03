from random import choice


# Choose random except 2 previous
def strategy(verticies: list, prev: list) -> int:
    good = verticies
    if prev:
        good = [i for i in verticies if i != prev[-1]]

    if len(prev) > 1:
        good = [i for i in good if i != prev[-2]]

    return choice(good)
