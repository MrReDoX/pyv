# pyv

Chaos game simulator. Interface is done with pyqtgraph, exporting with matplotlib. So be aware exporting result is not the same as you see on your screen. The reason for this is matplotlib is very slow for real time complex (=with color, many points) plot, so embedding it in interface would cause perfomance issues.

**Disclaimer**: I am not a programmer, so this product is not the result of sophisticated coder contemplation. I don't know how to maintain git repository, don't know how to use branches for productive development etc. My python knowledge may not be the its greatest. I haven't worked with Qt translation features so program is straight russian language.

# Install

I think dependices are these: [numpy](https://numpy.org/install/), [pyqtgraph](https://www.pyqtgraph.org/), python 3.10.9. I am working with the latest versions aviable for Arch Linux, other version haven't been tested.

# Run

Just do `python gui.py`. Press plot and contemplate.

# Issues

1. Always use plot before exporting.
2. Formats of parameters are in the comments of appropariate methods parse_something in `gui.py`.

# regular $ n $-gon

Build regular $ n $-gon with appropriate output

```
import cmath
import math

c = complex(0, -3)
n = 7

points = [c + 2 * cmath.exp(1j * (2 * math.pi * k) / n) for k in range(n)]

for z in points:
    print(f'({z.real:.2f}:{z.imag:.2f}:1)')
```
