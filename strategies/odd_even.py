from random import choice


# Even -> Odd -> Even -> Odd
def strategy(verticies: list, prev: list) -> int:
    if not prev:
        return choice(verticies)
       
    if verticies.index(prev[-1]) % 2 == 0:
        return choice(verticies[1::2])
    
    return choice(verticies[::2])
