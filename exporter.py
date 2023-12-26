"""Module responsible for 2d export."""

import itertools
import os
from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from pyqtgraph.Qt.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal,
                                 pyqtSlot)


class ExporterSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    '''
    finished = pyqtSignal()


class Exporter2D(QRunnable):
    """Class managing matplotlib export"""
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = ()
        self.kwargs = {}
        self.signals = ExporterSignals()

        self.params = None
        self.params_exp = None

    @pyqtSlot()
    def run(self):
        """QThread magic."""
        self.export_2d(*self.args, **self.kwargs)

        self.signals.finished.emit()

    def export_2d(self, worker, params, params_exp, x, y, colors, lamb):
        """Export image file with matplotlib."""
        plt.gca().set_aspect('equal', adjustable='box')

        if params.child('Рисовать абсолют').value():
            color = 'red'
            if val := params.child('Цвет абсолюта').value():
                color = val

            linewidth = 0.25
            if val := params_exp.child('Ширина линий абсолюта').value():
                linewidth = val

            if worker.frame_type == 1:
                par = {'color': color, 'linewidth': linewidth}
                theta = np.linspace(0, 2 * np.pi, 2**14)
                x_coords = np.cos(theta)
                y_coords = np.sin(theta)
                plt.plot(x_coords, y_coords, **par)

            if worker.frame_type == 2:
                # Абсолют — гипербола yx - 1 = 0
                # 0 не содержится
                left = worker.xmin - 2
                right = worker.xmax + 2
                cnt = ceil(abs(right - left) / 0.01)

                if left * right > 0:
                    x_coords = np.linspace(left, right, cnt)
                else:
                    # xmin * xmax < 0, значит, ноль содержится

                    x_coords = np.linspace(0.01, right, cnt)
                    y_coords = list(map(lambda x: 1 / x, x_coords))
                    plt.plot(x_coords, y_coords, c=color, linewidth=linewidth)

                    x_coords = np.linspace(left, -0.01, cnt)

                y_coords = list(map(lambda x: 1 / x, x_coords))
                plt.plot(x_coords, y_coords, c=color, linewidth=linewidth)

        if params.child('Рисовать границы').value():
            width = 0.25
            if value := params_exp.child('Ширина границ').value():
                width = value

            vertices = worker.vertices + [worker.vertices[0]]
            for_pairing = [i.to_point2() for i in vertices]

            for cur, nex in itertools.pairwise(for_pairing):
                plt.plot([cur.x, nex.x],
                         [cur.y, nex.y],
                         c='black',
                         linewidth=width)

        size = 1.0
        if val := params_exp.child('Размер точки').value():
            size = val

        directory = os.getcwd()
        if value := params_exp.child('Директория по умолчанию').value():
            directory = value

        file_name = params_exp.child('Имя файла').value()
        while (left_idx := file_name.find('$')) != -1:
            right_idx = file_name.find('$', left_idx + 1)

            # slice without $
            command = file_name[left_idx + 1:right_idx]

            ans = ''
            if command == 'color':
                ans = 'bw'
                if params.child('Случайные цвета').value()\
                        or params.child('Цвета точек').value():
                    ans = 'colored'

            elif command == 'lambda':
                ans = f'{lamb:.2f}'
            elif command == 'verticies':
                for i in worker.vertices:
                    ans += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'

            file_name = file_name[:left_idx] + ans + file_name[right_idx + 1:]

        if file_name[0] == '_':
            file_name = file_name[1:]

        while file_name.find('__') != -1:
            file_name = file_name.replace('__', '_')

        if not file_name:
            return

        dpi = 600
        if val := params_exp.child('dpi').value():
            dpi = val

        value = params_exp.child('Рисовать оси').value()
        yes_or_no = {False: 'off', True: 'on'}
        plt.axis(yes_or_no[value])

        rasterized = params_exp.child('Растеризовать').value()

        plt.scatter(x,
                    y,
                    c=colors,
                    s=size,
                    edgecolors='none',
                    rasterized=rasterized)
        plt.savefig(f'{directory}/{file_name}', dpi=dpi)

        plt.close()
        plt.cla()
        plt.clf()
