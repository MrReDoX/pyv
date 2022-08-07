import sys
from math import pi, sqrt
from random import shuffle, uniform
from time import sleep

import numpy as np
from Point import Point2, Point3

from Iterate import Worker
# from Plotter import Plotter
from Utility import save_plot

# number of verticies
n = 8

# generate roots of unity
angles = [1j * 2 * pi * k / n for k in range(n)]

cnt = 2**14

# xmin, xmax = 0, 4.5
# ymin, ymax = -1, 1.5

xmin, xmax = -10, 10
ymin, ymax = -10, 10

r = 100
r_actual = r / 2

translate = [r, -r, r + 1j * r, -r + 1j * r, r - 1j * r, -r - 1j * r]

rng = np.random.default_rng()

for rel in np.linspace(0.01, 1, num = len(translate), endpoint = False):
    worker = Worker()
    worker.projective = 1
    #worker.set_checker(check)
    #worker.set_m(3, 0)
    worker.coloring = True
    # worker.set_colors('#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51')
    # worker.gen_double_mid()

    p = rng.choice(translate) + r_actual * np.exp(angles)
    points = [Point3(round(np.imag(k), 3), round(np.real(k), 3), 1) for k in p]
    worker.vertices = points
    xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = False)
    worker.m = worker.generate_m()
    worker.vertices_colors = worker.get_random_colors()

    worker.xmin, worker.xmax = xmin, xmax
    worker.ymin, worker.ymax = ymin, ymax

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
