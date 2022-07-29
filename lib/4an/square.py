import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker

import matplotlib.pyplot as plt

from math import sqrt

def check(p: Point2):
    conds = list()

    x = p.x
    y = p.y

    conds.append(not (1 > x))
    conds.append(not (x > 3))
    conds.append(not (-2 > y))
    conds.append(not (y > 2))

    return all(conds)

worker = Worker()

worker.set_As(\
    Point3(4, 1, 1),
    Point3(4, -1, 1),
    Point3(2, -1, 1),
    Point3(2, 1, 1)
)

worker.set_projective(1)
# worker.set_checker(check)
# worker.set_m(3, 1)
# worker.enable_random_mid()
worker.enable_convex_trick()
worker.generate_m()

cnt = 2**14

x, y = worker.work1(cnt)

#################
##### PLOT ######
#################

# single plot

plt.gca().set_aspect('equal', adjustable = 'box')
plt.gca().add_patch(plt.Circle((0, 0), 1, fill = False))
# plt.xlim(-5, 10)
# plt.ylim(-2, 10)
# plt.axis('square')

plt.scatter(x, y, c = 'black', s = 1, alpha = 0.1)

filename = 'SQUARE'
for i in worker.get_As():
    filename += f'_{i.x},{i.y},{i.z}'

plt.savefig(f'{filename}.svg')

# multiplot
#for i in range(2):
#    cur = 2**(16 + i)
#
#    plt.subplot(1, 3, i + 1)
#    plt.title(f'{cur}')
#    plt.gca().set_aspect('equal', adjustable = 'box')
#    plt.gca().add_patch(plt.Circle((0, 0), 1, fill = False))
#    plt.scatter(x[:cur], y[:cur], s = 1, alpha = 0.1)

plt.tight_layout()
plt.show()
