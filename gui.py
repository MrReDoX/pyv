"""Main program module. Builds GUI and run program."""

import itertools
import json
import os
import sys
import threading
from math import ceil, inf, pi
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtGui, QtWidgets

from iterate import Worker
from point import Point2, Point3


def parse_m(data: str) -> Point2:
    """Parse point data from text box in format (x, y)."""
    if not data:
        return Point2(inf, inf)

    data = data.strip().replace(' ', '')[1:-1]
    listed = list(map(float, data.split(',')))

    return Point2(listed[0], listed[1])


def parse_vertices(data: str) -> list:
    """Parse vertices data from text box in format "(x1:y1:z1)\n..."""
    improved_data = data.strip().replace(' ', '').replace(',', '.').split('\n')

    # remove ( and )
    listed = [i[1:-1] for i in improved_data]

    # make triples (x, y, z)
    paired = [tuple(map(float, i.split(':'))) for i in listed]

    return [Point3(x, y, z) for (x, y, z) in paired]


# format: "#HEX1, #HEX2, ..., #HEX3"
def parse_colors(data: str) -> list:
    """Parse colors data from text box in format ""#HEX1, #HEX2, ..."""
    if not data:
        return []

    # remove spaces, etc
    improved_data = data.strip().replace(' ', '').split(',')

    return [f'{i}' for i in improved_data]


def parse_limits(data: str) -> Tuple[float, float, float, float]:
    """Parse limits data from text box in format "xmin, xmax, ymin, ymax"."""
    if not data:
        return (inf, inf, inf, inf)

    improved_data = data.strip().replace(' ', '').split(',')

    return tuple(float(i) for i in improved_data)


class Application:
    """Main class that build GUI."""

    def __init__(self):
        pg.setConfigOptions(antialias=True)
        self.app = pg.mkQApp('pyv')

        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle('pyv')

        children = [
            Parameter.create(name='Вершины',
                             type='text',
                             value='(2:0:1)\n(4:2:1)\n(4:-2:1)'),
            dict(name='Стартовая точка', type='str', value=''),
            dict(name='Цвета точек',
                 type='str',
                 value='#0000ff, #008000, #781f19'),
            dict(name='Случайные цвета', type='bool', value=False),
            dict(name='lambda', type='float', value=1.0),
            dict(name='projective', type='float', value=1.0),
            dict(name='Рисовать вторую середину', type='bool', value=False),
            dict(name='Пределы', type='str', value='-2, 5, -3, 6'),
            dict(name='Угадывать пределы', type='bool', value=False),
            dict(name='Угадывать пределы (включить абсолют)',
                 type='bool',
                 value=True),
            dict(name='Рисовать границы', type='bool', value=True),
            dict(name='Ширина границ', type='float', value=1.0),
            dict(name='Рисовать абсолют', type='bool', value=True),
            dict(name='Цвет абсолюта', type='str', value='#ff0000'),
            dict(name='Количество точек', type='str', value='2**14'),
            dict(name='Размер точки', type='float', value=1.0),
            dict(name='Тип репера', type='int', value=1),
            Parameter.create(name='Checker', type='file')
        ]

        children_exp = [
            dict(name='dpi', type='int', value=600),
            dict(name='Имя файла', type='str', value=''),
            dict(name='Директория по умолчанию',
                 type='str',
                 value=os.getcwd()),
            dict(name='Расширение по умолчанию', type='str', value='eps'),
            dict(name='Ширина линий абсолюта', type='float', value=0.25),
            dict(name='Ширина границ', type='float', value=0.25),
            dict(name='Размер точки', type='float', value=0.25),
            dict(name='Рисовать оси', type='bool', value=False),
            dict(name='Параметр \\lambda в имя файла', type='bool', value=False),
            dict(name='Количество точек в имя файла', type='bool', value=False),
            dict(name='Растеризовать', type='bool', value=True)
        ]

        self.params = Parameter.create(name='Параметры',
                                       type='group',
                                       children=children)
        self.params_exp = Parameter.create(name='Экспорт',
                                           type='group',
                                           children=children_exp)
        param_tree = ParameterTree(showHeader=False)
        param_tree.addParameters(self.params)
        param_tree.addParameters(self.params_exp)

        self.win = pg.GraphicsLayoutWidget(show=False)
        self.canvas = self.win.addPlot()
        self.canvas.setAspectLocked(True, 1.0)

        self.win.setBackground('w')

        action_export = QtGui.QAction(self.main_window)
        action_export.setObjectName('actionExport')
        action_export.setText('Экспортировать')
        action_export.triggered.connect(self.export_conf)

        action_import = QtGui.QAction(self.main_window)
        action_import.setObjectName('actionImport')
        action_import.setText('Импортировать')
        action_import.triggered.connect(self.import_conf)

        menu = self.main_window.menuBar()
        conf = menu.addMenu('Конфигурация')
        conf.addAction(action_export)
        conf.addAction(action_import)

        btn_plot = QtWidgets.QPushButton('Plot')
        btn_export = QtWidgets.QPushButton('Export')

        btn_plot.clicked.connect(self.plot)
        btn_export.clicked.connect(self.export)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(btn_plot)
        button_layout.addWidget(btn_export)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(param_tree)
        main_layout.addLayout(button_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.win)
        splitter.addWidget(widget)

        self.main_window.setCentralWidget(splitter)
        self.main_window.showMaximized()

        self.worker = Worker()

    def read_config(self):
        """Read GUI settings and write them to variables."""
        self.worker.vertices = parse_vertices(self.params.child('Вершины').value())

        self.worker.start_point = parse_m(self.params.child('Стартовая точка').value())
        if not self.params.child('Стартовая точка').value():
            self.worker.start_point = self.worker.gen_start_point()

        self.worker.coloring = False
        if val := self.params.child('Цвета точек').value():
            self.worker.coloring = True
            self.worker.vertices_colors = parse_colors(val)

        if self.params.child('Случайные цвета').value():
            self.worker.coloring = True
            self.worker.vertices_colors = self.worker.gen_random_colors()

        self.worker.projective = self.params.child('projective').value()
        self.worker.double_mid = self.params.child('Рисовать вторую середину').value()

        xmin, xmax, ymin, ymax = parse_limits(self.params.child('Пределы').value())
        if not self.params.child('Пределы').value():
            xmin, xmax, ymin, ymax = self.worker.guess_limits()
            if self.params.child('Угадывать пределы (включить абсолют)').value():
                xmin, xmax, ymin, ymax = self.worker.guess_limits(contains_absolute=True)

        self.worker.xmin, self.worker.xmax = xmin, xmax
        self.worker.ymin, self.worker.ymax = ymin, ymax

        self.canvas = self.win.addPlot()
        self.canvas.setAspectLocked(True, 1.0)
        self.canvas.setXRange(xmin, xmax)
        self.canvas.setYRange(ymin, ymax)

        if val := self.params.child('Checker').value():
            sys.path.append(os.path.dirname(val))
            module = __import__(Path(val).stem)

            self.worker.checker = module.checker

        if self.params.child('Рисовать границы').value():
            width = 3.0
            if val := self.params.child('Ширина границ').value():
                width = val

            vertices = self.worker.vertices + [self.worker.vertices[0]]
            for_pairing = [i.to_point2() for i in vertices]

            for cur, nex in itertools.pairwise(for_pairing):
                self.canvas.plot([cur.x, nex.x],
                                 [cur.y, nex.y],
                                 pen=pg.mkPen('#000000',
                                 width=width))

        if val := self.params.child('Тип репера').value():
            self.worker.frame_type = val

        if self.params.child('Рисовать абсолют').value():
            color = '#ff0000'
            if val := self.params.child('Цвет абсолюта').value():
                color = val

            if self.worker.frame_type == 1:
                # Абсолют — окружность
                points = np.linspace(0, 2 * pi, num=100)
                circle = pg.PlotCurveItem(np.cos(points),
                                          np.sin(points),
                                          pen=pg.mkPen(color),
                                          skipFiniteCheck=True)
                self.canvas.addItem(circle)

            if self.worker.frame_type == 2:
                # Абсолют — гипербола yx - 1 = 0
                # 0 не содержится
                left = xmin - 2
                right = xmax + 2
                cnt = ceil(abs(right - left) / 0.01)

                if left * right > 0:
                    x_coords = np.linspace(left, right, cnt)
                else:
                    # xmin * xmax < 0, значит, ноль содержится
                    x_coords = np.linspace(0.1, right, cnt)
                    y_coords = list(map(lambda x: 1 / x, x_coords))
                    hyperbole = pg.PlotCurveItem(x_coords,
                                                 y_coords,
                                                 pen=pg.mkPen(color),
                                                 skipFiniteCheck=True)
                    self.canvas.addItem(hyperbole)

                    x_coords = np.linspace(left, -0.1, cnt)

                y_coords = list(map(lambda x: 1 / x, x_coords))

                hyperbole = pg.PlotCurveItem(x_coords,
                                             y_coords,
                                             pen=pg.mkPen(color),
                                             skipFiniteCheck=True)
                self.canvas.addItem(hyperbole)

    def plot(self):
        """Run chaos game and plot with scatterplot."""
        self.main_window.setWindowTitle('pyv BUSY')
        self.win.clear()

        self.read_config()

        relation = self.params.child('lambda').value()
        cnt = eval(self.params.child("Количество точек").value())

        # run in separate thread
        plot_thread = threading.Thread(target=self.worker.work,
                                       args=(cnt,), kwargs={'rel': relation})
        plot_thread.start()
        plot_thread.join()

        self.worker.clean()

        size = 1.0
        if val := self.params.child('Размер точки').value():
            size = val

        self.canvas.addItem(pg.ScatterPlotItem(x=self.worker.x,
                                               y=self.worker.y,
                                               size=size,
                                               brush=self.worker.colors))

        self.main_window.setWindowTitle('pyv DONE')

    def export(self):
        """Export image file with matplotlib."""
        self.main_window.setWindowTitle('pyv EXPORTING')

        plt.gca().set_aspect('equal', adjustable='box')

        if self.params.child('Рисовать абсолют').value():
            color = 'red'
            if val := self.params.child('Цвет абсолюта').value():
                color = val

            linewidth = 0.25
            if val := self.params_exp.child('Ширина линий абсолюта').value():
                linewidth = val

            if self.worker.frame_type == 1:
                par = {'color': color, 'linewidth': linewidth}
                theta = np.linspace(0, 2 * np.pi, 2**10)
                x_coords = np.cos(theta)
                y_coords = np.sin(theta)
                plt.plot(x_coords, y_coords, **par)

            if self.worker.frame_type == 2:
                # Абсолют — гипербола yx - 1 = 0
                # 0 не содержится
                left = self.worker.xmin - 2
                right = self.worker.xmax + 2
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

        plt.xlim(self.worker.xmin - 2, self.worker.xmax + 2)
        plt.ylim(self.worker.ymin - 2, self.worker.ymax + 2)

        if self.params.child('Рисовать границы').value():
            width = 0.25
            if value := self.params_exp.child('Ширина границ').value():
                width = value

            vertices = self.worker.vertices + [self.worker.vertices[0]]
            for_pairing = [i.to_point2() for i in vertices]

            for cur, nex in itertools.pairwise(for_pairing):
                plt.plot([cur.x, nex.x],
                         [cur.y, nex.y],
                         c='black',
                         linewidth=width)

        size = 1.0
        if val := self.params_exp.child('Размер точки').value():
            size = val

        directory = os.getcwd()
        if value := self.params_exp.child('Директория по умолчанию').value():
            directory = value

        file_name = f''

        if self.params_exp.child('Количество точек в имя файла').value():
            file_name += f'{self.params.child("Количество точек").value()}'

        if self.params_exp.child('Параметр \\lambda в имя файла').value():
            file_name += f'_{self.params.child("lambda").value()}'

            # We don't have add count to file name parameter
            if file_name[0] == '_':
                file_name = file_name[1:]

        for i in self.worker.vertices:
            file_name += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'
        # file_name = file_name[1:]

        if val := self.params_exp.child('Имя файла').value():
            file_name = val

        extension = 'eps'
        if value := self.params_exp.child('Расширение по умолчанию').value():
            extension = value

        directory += f'/{file_name}.{extension}'

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self.main_window,
            caption='Выберите файл',
            directory=directory
        )

        directory, file_name = os.path.split(path)

        if not file_name:
            self.main_window.setWindowTitle('pyv DONE')

            return

        dpi = 600
        if val := self.params_exp.child('dpi').value():
            dpi = val

        value = self.params_exp.child('Рисовать оси').value()
        yes_or_no = {False: 'off', True: 'on'}
        plt.axis(yes_or_no[value])

        rasterized = self.params_exp.child('Растеризовать').value()

        plt.scatter(self.worker.x,
                    self.worker.y,
                    c=self.worker.colors,
                    s=size,
                    edgecolors='none',
                    rasterized=rasterized)
        plt.savefig(f'{directory}/{file_name}', dpi=dpi)

        plt.close()
        plt.cla()
        plt.clf()

        self.main_window.setWindowTitle('pyv DONE')

    def export_conf(self):
        """Write current configuration to the JSON file."""
        filt = 'Json File (*.json)'
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self.main_window,
            caption='Выберите файл',
            directory=os.getcwd(),
            filter=filt,
            initialFilter=filt
        )

        if not path:
            return

        if path.rfind('.json') == -1:
            path += '.json'

        with open(path, 'w', encoding='utf-8') as file:
            json_data = {'params': self.params.saveState(),
                         'params_exp': self.params_exp.saveState()}

            json.dump(json_data, file, indent=4)

    def import_conf(self):
        """Read parameters trees from the JSON file."""
        filt = 'Json File (*.json)'
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.main_window,
            caption='Выберите файл',
            directory=os.getcwd(),
            filter=filt,
            initialFilter=filt
        )

        if not path:
            return

        with open(path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

            self.params.restoreState(json_data['params'])
            self.params_exp.restoreState(json_data['params_exp'])


if __name__ == '__main__':
    app = Application()
    pg.exec()
