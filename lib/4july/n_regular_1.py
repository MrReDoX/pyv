import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot

import numpy as np

from math import sqrt, pi
from random import shuffle, uniform
from time import sleep

# number of verticies
n = 12

# generate roots of unity
angles = [1j * 2 * pi * k / n for k in range(n)]

cnt = 2**14

# xmin, xmax = 0, 4.5
# ymin, ymax = -1, 1.5

xmin, xmax = -10, 10
ymin, ymax = -10, 10

translate = np.array([3, -3, 3 + 3j, -3 + 3j, 3 - 3j, -3 - 3j, 2.5, -2.5, 2.5 + 2.5j, -2.5 - 2.5j])

rng = np.random.default_rng()

# for rel in np.linspace(0.01, 1, num = len(translate), endpoint = False):
for rel in np.linspace(0.01, 1, num = 10, endpoint = False):
    worker = Worker()
    worker.set_projective(1)
    #worker.set_checker(check)
    worker.enable_convex_trick()
    #worker.set_m(3, 0)
    worker.enable_basic_coloring()
    # worker.set_colors('#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51')
    # worker.gen_double_mid()

    p = rng.choice(translate) + np.exp(angles)
    points = [Point3(round(np.imag(k), 3), round(np.real(k), 3), 1) for k in p]
    worker.set_As(*points)
    xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)
    worker.generate_m()
    worker.set_colors(*worker.get_random_colors())
    worker.set_x_limits(xmin, xmax)
    worker.set_y_limits(ymin, ymax)

    x, y, colors = worker.clean(*worker.work(cnt, rel = rel))
    file_name = f'{rel:.2f}_{len(points)}_regular'
    save_plot(\
        x = x,
        y = y,
        file_name = f'{file_name}.png',
        xlims = (xmin, xmax),
        ylims = (ymin, ymax),
        colors = colors,
        A = points)
