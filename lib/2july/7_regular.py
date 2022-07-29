import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot

import numpy as np

# number of verticies
n = 7

# generate roots of unity
angles = [1j * 2 * np.pi * k / n for k in range(n)]
p = -3j + np.exp(angles)

points = [Point3(np.imag(k), np.real(k), 1) for k in p]

print(*points, sep = '\n')

cnt = 2**16

# xmin, xmax = 0, 4.5
# ymin, ymax = -1, 1.5

xmin, xmax = 0, 6.5
ymin, ymax = -2.5, 2.5

worker = Worker()
worker.set_As(*points)
xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)
worker.set_projective(1)
#worker.set_checker(check)
worker.enable_convex_trick()
#worker.set_m(3, 0)
worker.generate_m()
# worker.enable_basic_coloring()
# worker.set_colors('#08aab0', '#fd70f4', '#8b4907', '#cc8cf6')
# worker.gen_double_mid()
worker.set_x_limits(xmin, xmax)
worker.set_y_limits(ymin, ymax)

x, y, colors = worker.clean(*worker.work1(cnt))

# worker.set_colors('black', 'black', 'black', 'black')
# x1, y1, colors1 = worker.clean(*worker.work(2**14))
#
# x = np.append(x, x1)
# y = np.append(y, y1)
# colors = np.append(colors, colors1)

plotter = Plotter(x, y)

plotter.set_x_range(xmin, xmax)
plotter.set_y_range(ymin, ymax)
plotter.set_colors(colors)
# plotter.plot()

file_name = '7_regular'
for i in worker.get_As():
    file_name += f'_{i.x:.1f},{i.y:.1f},{i.z:.1f}'

save_plot(\
    x = x,
    y = y,
    file_name = f'{file_name}.png',
    xlims = (xmin, xmax),
    ylims = (ymin, ymax),
    colors = colors,
    A = worker.get_As())

save_plot(\
    x = x,
    y = y,
    file_name = f'{file_name}.eps',
    xlims = (xmin, xmax),
    ylims = (ymin, ymax),
    colors = colors,
    A = worker.get_As())
