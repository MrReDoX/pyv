import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np

def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(not (x < 2))
    conds.append(not (x + y - 4 > 0))
    conds.append(not (x - y - 4 > 0))

    return all(conds)

worker = Worker()

worker.set_As(\
    Point3(2, -2, 1),
    Point3(2, 2, 1),
    Point3(4, 0, 1)
)
worker.set_projective(1)
worker.set_checker(check)
worker.set_m(3, 0)

cnt = 2**17

x, y = worker.work(Point2(3, 0), cnt)

#################
##### PLOT ######
#################

fig = plt.figure()
ax = plt.axes(xlim = (-2, 5), ylim = (-3, 3))
graph = plt.scatter([], [], c = 'black', s = 1, alpha = 0.1)

plt.gca().set_aspect('equal', adjustable = 'box')
plt.gca().add_patch(plt.Circle((0, 0), 1, fill = False))

step = 100

def animate(i):
    graph.set_offsets(np.vstack((x[:step * i + 1], y[:step * i + 1])).T)

    return graph

anim = FuncAnimation(fig, animate, frames = cnt // step)

#anim.save('anim1.mp4', fps = 24, , progress_callback = lambda i, n: print(f'Saving frame {i} of {n}'))

anim.save('test.gif', writer = 'imagemagick', fps = 30, progress_callback = lambda i, n: print(f'Saving frame {i} of {n}'))

#plt.show()

#for i in range(1, cnt + 1, cnt // 25):
#    plt.scatter(x[:i], y[:i], s = 1, alpha = 0.1, color = 'black')
#
#    #plt.get_current_fig_manager().full_screen_toggle()
#    plt.tight_layout()
#
#    plt.xlim(-2, 5)
#    plt.ylim(-3, 3)
#
#    plt.gca().set_aspect('equal', adjustable = 'box')
#    plt.gca().add_patch(plt.Circle((0, 0), 1, fill = False))
#
#    plt.pause(1e-1)

# plt.show()
