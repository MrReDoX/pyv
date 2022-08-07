import sys

import numpy as np
from Point import Point2, Point3

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot


def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(not (x < 2))
    conds.append(not (x + y - 4 > 0))
    conds.append(not (x - y - 4 > 0))

    return all(conds)

cnt = 2**16

xmin, xmax = -2.5, 5
ymin, ymax = -1.5, 1.5

worker = Worker()
worker.set_As(\
    Point3(4, 0, 1),
    Point3(1.2, 0.7, 1),
    Point3(1.2, -0.7, 1)
)
worker.set_projective(1)
#worker.set_checker(check)
worker.enable_convex_trick()
#worker.set_m(3, 0)
worker.generate_m()
worker.enable_basic_coloring()
worker.set_colors('#ff00ff', '#0000ff', '#008000')
worker.gen_double_mid()
worker.set_x_limits(xmin, xmax)
worker.set_y_limits(ymin, ymax)

x, y, colors = worker.clean(*worker.work1(cnt))

worker.set_colors('black', 'black', 'black')
x1, y1, colors1 = worker.clean(*worker.work(2**13))

x = np.append(x, x1)
y = np.append(y, y1)
colors = np.append(colors, colors1)

plotter = Plotter(x, y)

plotter.set_x_range(xmin, xmax)
plotter.set_y_range(ymin, ymax)
plotter.set_colors(colors)
# plotter.plot()

file_name = 'EHH'
for i in worker.get_As():
    file_name += f'_{i.x},{i.y},{i.z}'

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
