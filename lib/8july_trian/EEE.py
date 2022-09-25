import sys

import numpy as np
from Iterate import Worker
from Plotter import Plotter
from Point import Point2, Point3
from Utility import save_plot

cnt = 2**14

worker = Worker()
worker.vertices = [\
    Point3(2, 0, 1),
    Point3(4, 2, 1),
    Point3(4, -2, 1)]
xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)
worker.projective = 1
worker.m = worker.generate_m()
worker.coloring = True
worker.vertices_colors = ['#ff00ff', '#0000ff', '#008000']
worker.double_mid = True
worker.xmin, worker.xmax = xmin, xmax
worker.ymin, worker.ymax = ymin, ymax

x, y, colors = worker.clean(*worker.work(cnt, rel=1))

plotter = Plotter(x, y)
plotter.set_x_range(xmin, xmax)
plotter.set_y_range(ymin, ymax)
plotter.colors = colors
plotter.plot()

# x, y, colors = worker.clean(*worker.work(cnt))
#
# file_name = 'EEE'
# for i in worker.vertices:
#     file_name += f'_{i.x},{i.y},{i.z}'
#
# save_plot(\
#     x = x,
#     y = y,
#     file_name = f'{file_name}.png',
#     xlims = (xmin, xmax),
#     ylims = (ymin, ymax),
#     colors = colors,
#     A = worker.vertices)

# for rel in np.linspace(0.01, 3, num = 5, endpoint = False):
#     x, y, colors = worker.clean(*worker.work(cnt, rel = rel))
#
#     file_name = f'{rel:.2f}_EEE'
#     for i in worker.vertices:
#         file_name += f'_{i.x},{i.y},{i.z}'
#
#     # print(x, y, colors, sep = '\n')
#
#     save_plot(\
#         x = x,
#         y = y,
#         file_name = f'{file_name}.png',
#         xlims = (xmin, xmax),
#         ylims = (ymin, ymax),
#         colors = colors,
#         A = worker.vertices)
