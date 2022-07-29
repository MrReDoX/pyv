import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot

import numpy as np

def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(not (x < 2))
    conds.append(not (x + y - 4 > 0))
    conds.append(not (x - y - 4 > 0))

    return all(conds)

cnt = 2**14

# xmin, xmax = 0, 4.5
# ymin, ymax = -1, 1.5

xmin, xmax = 0, 5
ymin, ymax = -2.5, 2.5

worker = Worker()
worker.set_As(\
    Point3(2, 0, 1),
    Point3(4, 2, 1),
    Point3(4, -2, 1)
)
xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)
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

for rel in np.arange(1.25, 2, 0.25):
    x, y, colors = worker.clean(*worker.work(cnt, rel = rel))

    file_name = f'{rel}_EEE'
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
