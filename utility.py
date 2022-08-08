import matplotlib.pyplot as plt
import numpy as np


def save_plot(x: np.ndarray,
              y: np.ndarray,
              file_name: str,
              xlims: (float, float),
              ylims: (float, float),
              colors: np.ndarray,
              vertices=None):
    if len(x) < 1000:
        return

    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().add_patch(plt.Circle((0, 0), 1, fill=False, color='red'))
    plt.xlim(*xlims)
    plt.ylim(*ylims)

    vertices = [k.to_Point2() for k in vertices]
    for k in range(len(vertices)):
        x_values = [vertices[k].x, vertices[(k + 1) % len(vertices)].x]
        y_values = [vertices[k].y, vertices[(k + 1) % len(vertices)].y]

        plt.plot(x_values, y_values, c='black', linewidth=1)

    plt.scatter(x, y, c=colors, s=1/2, edgecolors='none')

    plt.savefig(f'{file_name}', dpi=300)

    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
