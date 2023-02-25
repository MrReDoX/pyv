# pyv

Chaos game simulator

# regular $ n $-gon

Build regular $ n $-gon with appropriate output

```
import math
import cmath

c = complex(0, -3)
n = 7

points = [c + 2 * cmath.exp(1j * (2 * math.pi * k) / n) for k in range(n)]

for z in points:
    print(f'({z.real:.2f}:{z.imag:.2f}:1)')
```

Output:
