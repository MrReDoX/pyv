# TODO
# Рисовать точку за точкой?
# status bar?
# Iterate.py: x -> xs, y -> ys

# https://pyqtgraph.readthedocs.io/en/latest/parametertree/parametertypes.html

import itertools
import json
import os
import sys
import threading
from math import ceil, inf, pi
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtGui, QtWidgets

from iterate import Worker
from point import Point2, Point3


# format: "(x, y)"
def parse_m(data: str) -> Point2:
    if not data:
        return Point2(inf, inf)

    data = data.strip().replace(' ', '')[1:-1]
    data = list(map(float, data.split(',')))

    return Point2(data[0], data[1])


# format: "(x_1:y_1:z_1)\n(x_2:y_2:z_2)\n\dots\n(x_n:y_n:z_n)"
def parse_vertices(data: str) -> list:
    data = data.strip().replace(' ', '').replace(',', '.').split('\n')

    # remove ( and )
    data = [i[1:-1] for i in data]

    # make triples (x, y, z)
    data = [tuple(map(float, i.split(':'))) for i in data]

    return [Point3(x, y, z) for (x, y, z) in data]


# format: "#HEX1, #HEX2, ..., #HEX3"
def parse_colors(data: str) -> list:
    if not data:
        return []

    # remove spaces, etc
    data = data.strip().replace(' ', '').split(',')

    return [f'{i}' for i in data]


# format: "xmin, xmax, ymin, ymax"
def parse_limits(data: str) -> (float, float, float, float):
    if not data:
        return (inf, inf, inf, inf)

    data = data.strip().replace(' ', '').split(',')

    return tuple(float(i) for i in data)


class Application:
    def __init__(self):
        pg.setConfigOptions(antialias=True)
        self.app = pg.mkQApp('pyv')

        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle('pyv')

        children = [
            Parameter.create(name='Вершины', type='text', value='(2:0:1)\n(4:2:1)\n(4:-2:1)'),
            dict(name='Стартовая точка', type='str', value=''),
            dict(name='Цвета точек', type='str', value='#0000ff, #008000, #781f19'),
            dict(name='Случайные цвета', type='bool', value=False),
            dict(name='lambda', type='float', value=1.0),
            dict(name='projective', type='float', value=1.0),
            dict(name='Рисовать вторую середину', type='bool', value=False),
            dict(name='Пределы', type='str', value=''),
            dict(name='Угадывать пределы', type='bool', value=False),
            dict(name='Угадывать пределы (включить абсолют)', type='bool', value=True),
            dict(name='Рисовать границы', type='bool', value=True),
            dict(name='Ширина границ', type='float', value=1.0),
            dict(name='Рисовать абсолют', type='bool', value=True),
            dict(name='Цвет абсолюта', type='str', value='#ff0000'),
            dict(name='Количество точек', type='str', value='2**14'),
            dict(name='Размер точки', type='float', value=1.0),
            dict(name='Тип репера', type='int', value=1),
            Parameter.create(name='Checker', type='file')
        ]

        # TODO: ширина линий вокруг треугольника
        # ширина линий абсолюта
        # размер точек
        children_exp = [
            dict(name='dpi', type='int', value=600)
        ]

        self.params = Parameter.create(name='Параметры', type='group', children=children)
        self.params_exp = Parameter.create(name='Экспорт', type='group', children=children_exp)
        param_tree = ParameterTree(showHeader=False)
        param_tree.addParameters(self.params)
        param_tree.addParameters(self.params_exp)

        self.win = pg.GraphicsLayoutWidget(show=False)
        self.canvas= self.win.addPlot()
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


        btn_plot = QtWidgets.QPushButton("Plot")
        btn_export = QtWidgets.QPushButton("Export")

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
                xmin, xmax, ymin, ymax = self.worker.guess_limits(contains_absolute = True)

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

            tmp = [i.to_point2() for i in self.worker.vertices + [self.worker.vertices[0]]]
            for cur, nex in itertools.pairwise(tmp):
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
                circle = pg.PlotCurveItem(np.cos(points), np.sin(points), pen = pg.mkPen(color), skipFiniteCheck = True)
                self.canvas.addItem(circle)

            if self.worker.frame_type == 2:
                # Абсолют — гипербола yx - 1 = 0
                # 0 не содержится
                left = xmin - 2
                right = xmax + 2
                cnt = ceil(abs(right - left) / 0.01)

                if left * right > 0:
                    # xs = np.linspace(xmin, xmax, ceil(abs(xmax - xmin) / 0.1))
                    xs = np.linspace(left, right, cnt)
                else:
                    # xmin * xmax < 0, значит, ноль содержится
                    # xs = np.linspace(xmin, bad_point, ceil(abs(xmin - bad_point) / 0.1))
                    # np.append(xs, np.linspace(bad_point, xmax, ceil(abs(xmax - bad_point) / 0.1)))

                    xs = np.linspace(0.1, right, cnt)
                    ys = list(map(lambda x: 1 / x, xs))
                    hyperbole = pg.PlotCurveItem(xs, ys, pen = pg.mkPen(color), skipFiniteCheck = True)
                    self.canvas.addItem(hyperbole)

                    xs = np.linspace(left, -0.1, cnt)

                ys = list(map(lambda x: 1 / x, xs))

                hyperbole = pg.PlotCurveItem(xs, ys, pen = pg.mkPen(color), skipFiniteCheck = True)
                self.canvas.addItem(hyperbole)


    def plot(self):
        self.main_window.setWindowTitle('pyv BUSY')
        self.win.clear()

        self.read_config()

        relation = self.params.child('lambda').value()
        cnt = eval(self.params.child("Количество точек").value())

        # run in separate thread
        plot_thread = threading.Thread(target = self.worker.work,
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
        self.main_window.setWindowTitle('pyv EXPORTING')

        plt.gca().set_aspect('equal', adjustable='box')

        if self.params.child('Рисовать абсолют').value():
            color = 'red'
            if val := self.params.child('Цвет абсолюта').value():
                color = val

            if self.worker.frame_type == 1:
                plt.gca().add_patch(plt.Circle((0, 0), 1, fill=False, color=color, linewidth=0.25))

            if self.worker.frame_type == 2:
                # Абсолют — гипербола yx - 1 = 0
                # 0 не содержится
                left = self.worker.xmin - 2
                right = self.worker.xmax + 2
                cnt = ceil(abs(right - left) / 0.01)

                if left * right > 0:
                    # xs = np.linspace(xmin, xmax, ceil(abs(xmax - xmin) / 0.1))
                    xs = np.linspace(left, right, cnt)
                else:
                    # xmin * xmax < 0, значит, ноль содержится
                    # xs = np.linspace(xmin, bad_point, ceil(abs(xmin - bad_point) / 0.1))
                    # np.append(xs, np.linspace(bad_point, xmax, ceil(abs(xmax - bad_point) / 0.1)))

                    xs = np.linspace(0.1, right, cnt)
                    ys = list(map(lambda x: 1 / x, xs))
                    plt.plot(xs, ys, c=color, linewidth=0.25)

                    xs = np.linspace(left, -0.1, cnt)

                ys = list(map(lambda x: 1 / x, xs))
                plt.plot(xs, ys, c=color, linewidth=0.25)

        plt.xlim(self.worker.xmin - 2, self.worker.xmax + 2)
        plt.ylim(self.worker.ymin - 2, self.worker.ymax + 2)

        if self.params.child('Рисовать границы').value():
            width = 1.0
            if value := self.params.child('Ширина границ').value():
                width = value / 4

            tmp = [i.to_point2() for i in self.worker.vertices + [self.worker.vertices[0]]]
            for cur, nex in itertools.pairwise(tmp):
                plt.plot([cur.x, nex.x], [cur.y, nex.y], c='black', linewidth=0.25)

        size = 1.0
        # if val := params.child('Размер точки').value():
        #     size = val

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self.main_window,
            caption='Выберите файл',
            directory=os.getcwd(),
        )

        # _, file_extension = os.path.splitext(path)

        file_name = os.path.basename(path)

        if not file_name:
            self.main_window.setWindowTitle('pyv DONE')

            return

        dpi = 600
        if val := self.params_exp.child('dpi').value():
            dpi = val

        # TODO: add option to enable, disable axis
        plt.axis('off')

        plt.scatter(self.worker.x, self.worker.y, c=self.worker.colors, s=size/4, edgecolors='none')
        plt.savefig(path, dpi=dpi)

        plt.close()
        plt.cla()
        plt.clf()

        self.main_window.setWindowTitle('pyv DONE')


    def export_conf(self):
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
