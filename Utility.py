import numpy as np


def save_plot(x: np.ndarray,
              y: np.ndarray,
              file_name: str,
              xlims: (float, float),
              ylims: (float, float),
              colors: np.ndarray,
              A=list()):
    from math import ceil, log

    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure

    if file_name.find('eps') != -1:
        return

    print(len(x), len(y))
    if len(x) < 1000:
        return

    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().add_patch(plt.Circle((0, 0), 1, fill=False, color='red'))
    plt.xlim(*xlims)
    plt.ylim(*ylims)

    # plt.gcf().set_size_inches((6.4 * 2.5, 4.8 * 2.5))
    # plt.gcf().set_size_inches((12.8, 7.2))
    # plt.gcf().set_size_inches((12.8 * 1.5, 9.6 * 1.5))

    A = [k.to_Point2() for k in A]
    for k in range(len(A)):
        x_values = [A[k].x, A[(k + 1) % len(A)].x]
        y_values = [A[k].y, A[(k + 1) % len(A)].y]

        plt.plot(x_values, y_values, c='black', linewidth=1)

    # plt.scatter(x, y, c = colors, s = 1, alpha = 0.1)
    # plt.scatter(x, y, c = colors, s = 2**(-int(ceil((log(1200))))))
    # plt.scatter(x, y, c = colors, s = 1e-6)
    plt.scatter(x, y, c=colors, s=1/2, edgecolors='none')

    # about dpi: https://stackoverflow.com/questions/13714454/specifying-and-saving-a-figure-with-exact-size-in-pixels
    # plt.savefig(f'{file_name}', dpi = 1200)
    plt.savefig(f'{file_name}', dpi=300)

    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()

