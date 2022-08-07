import math
import sys

from Point import Point2, Point3

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot


def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(x > 1)
    conds.append(y > 1)

    return all(conds)

cnt = 2**18

xmin, xmax = -2, 100
ymin, ymax = -2, 100

worker = Worker()
worker.set_As(\
    Point3(1, 0, 0),
    Point3(0, 1, 0),
    Point3(1, 1, 1)
)
worker.set_projective(1)
worker.set_checker(check)
# worker.enable_convex_trick()
worker.set_m(2, 2)
# worker.generate_m()
worker.enable_basic_coloring()
worker.set_colors('#ff00ff', '#0000ff', '#008000')
worker.gen_double_mid()
worker.set_x_limits(xmin, xmax)
worker.set_y_limits(ymin, ymax)

# x, y, colors = worker.work(cnt)
x, y, colors = worker.clean(*worker.work(cnt))

plotter = Plotter(x, y)

plotter.set_x_range(xmin, xmax)
plotter.set_y_range(ymin, ymax)
plotter.set_colors(colors)
# plotter.plot()


file_name = 'EPP_1'
for i in worker.get_As():
    file_name += f'_{i.x:.1f},{i.y:.1f},{i.z:.1f}'

save_plot(\
    x = x,
    y = y,
    file_name = f'{file_name}.png',
    xlims = (xmin, xmax),
    ylims = (ymin, ymax),
    colors = colors)

save_plot(\
    x = x,
    y = y,
    file_name = f'{file_name}.eps',
    xlims = (xmin, xmax),
    ylims = (ymin, ymax),
    colors = colors)
