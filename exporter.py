import itertools
import os
from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from pyqtgraph.Qt.QtCore import *
from pyqtgraph.Qt.QtGui import *
from pyqtgraph.Qt.QtWidgets import *


class ExporterSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object, object, object)


class Exporter2D(QRunnable):
    def __init__(self):
        # For threading
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = None
        self.kwargs = None
        self.signals = ExporterSignals()

        self.params = None
        self.params_exp = None

    @pyqtSlot()
    def run(self):
        self.export_2d(*self.args, **self.kwargs)

        self.signals.finished.emit()

    def export_2d(self, worker, params, params_exp, x, y, colors):
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
                theta = np.linspace(0, 2 * np.pi, 2**10)
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

        plt.xlim(worker.xmin - 2, worker.xmax + 2)
        plt.ylim(worker.ymin - 2, worker.ymax + 2)

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

        file_name = ''

        if params.child('Случайные цвета').value() or params.child('Цвета точек').value():
            file_name += 'colored_'

        if params_exp.child('Количество точек в имя файла').value():
            file_name += f'_{params.child("Количество точек").value()}'

        if params_exp.child('Параметр \\lambda в имя файла').value():
            file_name += f'_{params.child("lambda").value()}'

        for i in worker.vertices:
            file_name += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'

        if file_name[0] == '_':
            file_name = file_name[1:]

        while file_name.find('__') != -1:
            file_name = file_name.replace('__', '_')

        if val := params_exp.child('Имя файла').value():
            file_name = val

        extension = 'eps'
        if value := params_exp.child('Расширение по умолчанию').value():
            extension = value

        # directory += f'/{file_name}.{extension}'

        # path, _ = QtWidgets.QFileDialog.getSaveFileName(
        #     parent=main_window,
        #     caption='Выберите файл',
        #     directory=directory
        # )

        # directory, file_name = os.path.split(path)
        # print(directory)
        # print(file_name)

        if not file_name:
            # main_window.setWindowTitle('pyv DONE')

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
        plt.savefig(f'{directory}/{file_name}.{extension}', dpi=dpi)

        plt.close()
        plt.cla()
        plt.clf()

        # self.main_window.setWindowTitle('pyv DONE')
