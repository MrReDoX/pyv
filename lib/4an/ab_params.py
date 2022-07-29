import sys

from Point import (
    Point2,
    Point3,
)

from Iterate import Worker

import matplotlib.pyplot as plt

from math import sqrt

A, B = map(float, input('A, B: ').split())

def check(p: Point2):
    global A
    global B

    conds = list()

    x = p.x
    y = p.y

    conds.append(not (x + sqrt(B * B - 1) * y - B > 0))
    conds.append(not (x - sqrt(A * A - 1) * y - A < 0))
    conds.append(not (x + sqrt(A * A - 1) * y - A < 0))
    conds.append(not (x - sqrt(B * B - 1) * y - B > 0))

    return all(conds)

worker = Worker()

frst = A * sqrt(B * B - 1) + B * sqrt(A * A - 1)
thrd = sqrt(A * A - 1) + sqrt(B * B - 1)

worker.set_As(\
    Point3(A, 0, 1),
    Point3(frst, B - A, thrd),
    Point3(B, 0, 1),
    Point3(frst, A - B, thrd)
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

filename = 'a_b_param'
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
