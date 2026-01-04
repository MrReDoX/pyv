from cmath import exp
from math import pi

c = complex(100, 100)
r = 10
n = 6

points = [c + r**2 * exp(1j * (2 * pi * k) / n) for k in range(n)]

for z in points:
    print(f'({z.real:.2f}:{z.imag:.2f}:1)')
