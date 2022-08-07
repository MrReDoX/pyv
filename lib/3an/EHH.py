from Point import Point2, Point3

from Iterate import Worker
from Plotter import Plotter
from Utility import save_plot


def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(not (x > 4))
    conds.append(not (x - 2 * y - 2 < 0))
    conds.append(not (x + 2 * y - 2 < 0))

    return all(conds)

cnt = 2**15
xmin, xmax = -2, 6
ymin, ymax = -2, 6

worker = Worker()
worker.set_As(\
    Point3(2, 0, 1),
    Point3(4, -1, 1),
    Point3(4, 1, 1)
)

worker.set_projective(1)
# worker.set_checker(check)
worker.enable_convex_trick()
# worker.set_m(3, 0)
worker.generate_m()
worker.enable_basic_coloring()
worker.set_colors('r', 'g', 'b')
worker.gen_double_mid()
worker.set_x_limits(xmin, xmax)
worker.set_y_limits(ymin, ymax)

x, y = worker.work(cnt)

plotter = Plotter(x, y)

plotter.set_x_range(xmin, xmax)
plotter.set_y_range(ymin, ymax)
plotter.set_colors(worker.get_colors())
# plotter.plot()

file_name = 'EHH'
for i in worker.get_As():
    file_name += f'_{i.x},{i.y},{i.z}'

save_plot(\
    x = x,
    y = y,
    file_name = f'{file_name}.svg',
    xlims = (xmin, xmax),
    ylims = (ymin, ymax),
    colors = worker.get_colors())
