# pyv

Chaos game simulator. Interface is done with pyqtgraph, exporting with matplotlib. So be aware exporting result is not the same as you see on your screen. The reason for this is matplotlib is very slow for real time complex (=with color, many points) plot, so embedding it in interface would cause perfomance issues.

**Disclaimer**: I am not a programmer, so this product is not the result of sophisticated coder contemplation. I don't know how to maintain git repository, don't know how to use branches for productive development etc. My python knowledge may not be the its greatest. I haven't worked with Qt translation features so program is straight russian language.

# Installation

Use `uv`:
```console
$ uv sync
```

# Running the Application

```console
$ uv run python src/Gui.py
```
Press "Plot" and contemplate.

![PyV Interface](pyv.png)

# Issues

1. Formats of parameters are in the comments of appropariate methods parse_something in `gui.py`.

# regular $n$-gon

Build regular $n$-gon with center in $c$ and radius $r$

```python
from cmath import exp
from math import pi

c = complex(0, -3)
r = 2
n = 7

points = [c + r**2 * exp(1j * (2 * pi * k) / n) for k in range(n)]

for z in points:
    print(f'({z.real:.2f}:{z.imag:.2f}:1)')
```
