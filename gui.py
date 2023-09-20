"""Main program module. Builds GUI and run program."""

import itertools
import json
import os
import sys
from math import ceil, inf, pi
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtGui, QtWidgets

from iterate import Worker
from iterate_3d import Worker3D
from point import Point2, Point3, nPoint


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

    if len(paired[0]) == 3:
        return [Point3(x, y, z) for (x, y, z) in paired]

    # for k in [-0.1, -0.2, -0.3, -0.4, -0.5]:
    #     # t = [nPoint(x + k, y + k, z + k, w) for (x, y, z, w) in paired]
    #     tp = []
    #     for x, y, z, w in paired:
    #         xp = round(x + k, 2)
    #         yp = round(y + k, 2)
    #         zp = round(z + k, 2)
    #         tp.append((xp, yp, zp, 1.0))
    #     print(*tp, sep='\n')
    #     print()


    return [nPoint(x, y, z, w) for (x, y, z, w) in paired]


#def parse_vertices_3d(data: str) -> list:
#    """Parse vertices data from text box in format "(x1:y1:z1:w1)\n..."""
#    improved_data = data.strip().replace(' ', '').replace(',', '.').split('\n')
#
#    # remove ( and )
#    listed = [i[1:-1] for i in improved_data]
#
#    # make triples (x, y, z)
#    paired = [tuple(map(float, i.split(':'))) for i in listed]
#
#    print(len(paired[0]))
#
#    return [nPoint(x, y, z, w) for (x, y, z, w) in paired]


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
            {'name': 'Стартовая точка', 'type': 'str', 'value': ''},
            {'name': 'Цвета точек', 'type': 'str', 'value': '#00406b, #008000, #781f19'},
            {'name': 'Случайные цвета', 'type': 'bool', 'value': False},
            {'name': 'lambda', 'type': 'float', 'value': 1.0},
            {'name': 'projective', 'type': 'float', 'value': 1.0},
            {'name': 'Рисовать вторую середину', 'type': 'bool', 'value': False},
            {'name': 'Пределы', 'type': 'str', 'value': ''},
            {'name': 'Угадывать пределы', 'type': 'bool', 'value': False},
            {'name': 'Угадывать пределы (включить абсолют)', 'type': 'bool', 'value': True},
            {'name': 'Рисовать границы', 'type': 'bool', 'value': True},
            {'name': 'Ширина границ', 'type': 'float', 'value': 1.0},
            {'name': 'Рисовать абсолют', 'type': 'bool', 'value': True},
            {'name': 'Цвет абсолюта', 'type': 'str', 'value': '#000000'},
            {'name': 'Количество точек', 'type': 'str', 'value': '2**14'},
            {'name': 'Размер точки', 'type': 'float', 'value': 1.0},
            {'name': 'Тип репера', 'type': 'int', 'value': 1},
            Parameter.create(name='Checker', type='file')
        ]

        children_exp = [
            {'name': 'dpi', 'type': 'int', 'value': 600},
            {'name': 'Имя файла', 'type': 'str', 'value': ''},
            {'name': 'Директория по умолчанию', 'type': 'str', 'value': os.getcwd()},
            {'name': 'Расширение по умолчанию', 'type': 'str', 'value': 'eps'},
            {'name': 'Ширина линий абсолюта', 'type': 'float', 'value': 0.25},
            {'name': 'Ширина границ', 'type': 'float', 'value': 0.25},
            {'name': 'Размер точки', 'type': 'float', 'value': 0.25},
            {'name': 'Рисовать оси', 'type': 'bool', 'value': False},
            {'name': 'Параметр \\lambda в имя файла', 'type': 'bool', 'value': False},
            {'name': 'Количество точек в имя файла', 'type': 'bool', 'value': False},
            {'name': 'Растеризовать', 'type': 'bool', 'value': True}
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

        self.graphics_widget_2d = pg.PlotWidget(background='w')
        self.canvas_2d = self.graphics_widget_2d.getPlotItem()
        self.canvas_2d.setAspectLocked(True, 1.0)

        # self.graphics_widget_3d = gl.GLViewWidget(rotationMethod='quaternion')
        self.graphics_widget_3d = gl.GLViewWidget()
        self.graphics_widget_3d.setBackgroundColor('w')

        self.scatter_2d = pg.ScatterPlotItem()
        self.scatter_3d = gl.GLScatterPlotItem()
        self.scatter_3d.setGLOptions('translucent')

        self.canvas_2d.addItem(self.scatter_2d)
        self.graphics_widget_3d.addItem(self.scatter_3d)

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
        btn_plot.setShortcut('Ctrl+Return')

        btn_export = QtWidgets.QPushButton('Export')

        btn_plot.clicked.connect(self.plot_2d)
        btn_export.clicked.connect(self.export_2d)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(btn_plot)
        button_layout.addWidget(btn_export)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(param_tree)
        main_layout.addLayout(button_layout)

        params_and_buttons_widget = QtWidgets.QWidget()
        params_and_buttons_widget.setLayout(main_layout)

        # 2d, 3d tab on the bottom
        tab_widget = QtWidgets.QTabWidget()
        # tab_widget.addTab(self.graphics_widget_2d, '2d')
        tab_widget.addTab(self.graphics_widget_2d, '2d')
        tab_widget.addTab(self.graphics_widget_3d, '3d')
        # tab_widget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        tab_widget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        tab_widget.currentChanged.connect(lambda: self.tab_changed(tab_widget,
                                                                   btn_plot,
                                                                   btn_export))

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(tab_widget)
        splitter.addWidget(params_and_buttons_widget)

        self.main_window.setCentralWidget(splitter)
        self.main_window.showMaximized()

        self.worker = Worker()
        self.worker_3d = Worker3D()

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

        self.canvas_2d.setXRange(xmin, xmax)
        self.canvas_2d.setYRange(ymin, ymax)

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
                self.canvas_2d.plot([cur.x, nex.x],
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
                # circle = pg.PlotCurveItem(np.cos(points),
                #                           np.sin(points),
                #                           pen=pg.mkPen(color),
                #                           skipFiniteCheck=True)

                circle = self.canvas_2d.plot()
                circle.setData(np.cos(points),
                               np.sin(points),
                               pen=pg.mkPen(color),
                               skipFiniteCheck=True)

                # self.canvas_2d.addItem(circle, row=0, col=0)

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
                    self.canvas_2d.addItem(hyperbole)

                    x_coords = np.linspace(left, -0.1, cnt)

                y_coords = list(map(lambda x: 1 / x, x_coords))

                hyperbole = pg.PlotCurveItem(x_coords,
                                             y_coords,
                                             pen=pg.mkPen(color),
                                             skipFiniteCheck=True)
                self.canvas_2d.addItem(hyperbole)

    def plot_2d(self):
        """Run chaos game and plot with ScatterPlot."""
        self.main_window.setWindowTitle('pyv BUSY')
        # self.canvas_2d.clear()

        # To avoid
        # RuntimeError: wrapped C/C++ object of type Worker has been deleted
        self.worker = Worker()
        self.read_config()

        relation = self.params.child('lambda').value()
        cnt = eval(self.params.child("Количество точек").value())

        size = 1.0
        if val := self.params.child('Размер точки').value():
            size = val

        def work_finished(x, y, colors):
            x, y, colors = self.worker.clean(x, y, colors)

            self.scatter_2d.setData(x=x,
                                    y=y,
                                    size=size,
                                    brush=colors)

            self.main_window.setWindowTitle('pyv DONE')

        # run in separate thread
        self.worker.args=(cnt,)
        self.worker.kwargs={'rel': relation}
        self.worker.signals.result.connect(work_finished)
        self.worker.threadpool.start(self.worker)

    # TODO:
    # 1. draw parallelepiped
    # 2. parse_vertices round
    def plot_3d(self):
        """Run chaos game and plot with GLScatterPlot."""
        self.main_window.setWindowTitle('pyv BUSY')

        self.graphics_widget_3d.clear()
        self.graphics_widget_3d.addItem(self.scatter_3d)

        self.worker_3d = Worker3D()
        self.worker_3d.vertices = parse_vertices(self.params.child('Вершины').value())
        self.worker_3d.start_point = nPoint(1, 1, 1)
        self.worker_3d.start_point = self.worker_3d.gen_start_point()
        self.worker_3d.vertices_colors = self.worker_3d.gen_random_colors()

        # draw boundary
        lower = [i.to_lower_dimension().to_tuple() for i in self.worker_3d.vertices]
        # lower += [lower[-1]]
        # for cur, nex in zip(lower, lower[1:]):
        #     # print(np.shape(np.array([cur, nex])))

        #     line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
        #                              color=pg.glColor('k'),
        #                              width=5,
        #                              antialias=True)

        #     self.graphics_widget_3d.addItem(line)
        lower_first = lower[:4]
        lower_first += [lower_first[0]]
        for cur, nex in zip(lower_first, lower_first[1:]):
             line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
                                      color=pg.glColor('k'),
                                      width=5,
                                      antialias=True)

             self.graphics_widget_3d.addItem(line)

        lower_second = lower[4:]
        lower_second += [lower_second[0]]
        for cur, nex in zip(lower_second, lower_second[1:]):
             line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
                                      color=pg.glColor('k'),
                                      width=5,
                                      antialias=True)

             self.graphics_widget_3d.addItem(line)

        for cur, nex in zip(lower[:4], lower[4:]):
             line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
                                      color=pg.glColor('k'),
                                      width=5,
                                      antialias=True)

             self.graphics_widget_3d.addItem(line)

        # draw absolute
        mesh_data = gl.MeshData.sphere(rows=128, cols=128)
        sphere = gl.GLMeshItem(meshdata=mesh_data, smooth=True, color=pg.glColor('r'))
        self.graphics_widget_3d.addItem(sphere)

        # create three grids, add each to the view
        xgrid = gl.GLGridItem(color=(0, 0, 0, 255))
        ygrid = gl.GLGridItem(color=(0, 0, 0, 255))
        zgrid = gl.GLGridItem(color=(0, 0, 0, 255))
        self.graphics_widget_3d.addItem(xgrid)
        self.graphics_widget_3d.addItem(ygrid)
        self.graphics_widget_3d.addItem(zgrid)
        # rotate x and y grids to face the correct direction
        xgrid.rotate(90, 0, 1, 0)
        ygrid.rotate(90, 1, 0, 0)

        relation = self.params.child('lambda').value()
        cnt = eval(self.params.child("Количество точек").value())

        size = 1.0
        if val := self.params.child('Размер точки').value():
            size = val

        def work_finished(x, y, z, colors):
            if len(x) < 1000:
                self.plot_3d()

                return

            colors = np.array(list(map(pg.glColor, colors)))
            # colors = np.array([pg.glColor(i) for i in colors])

            x = x[:, np.newaxis]
            y = y[:, np.newaxis]
            z = z[:, np.newaxis]

            data = np.hstack((x, y, z))

            print(np.shape(data))
            print(np.shape(colors))
            print('\n')

            self.scatter_3d.setData(pos=data,
                                    color=colors,
                                    size=5 * size,
                                    pxMode=True)

            self.main_window.setWindowTitle('pyv DONE')

        # run in separate thread
        self.worker_3d.args=(cnt,)
        self.worker_3d.kwargs={'rel': relation}
        self.worker_3d.signals.result.connect(work_finished)
        self.worker_3d.threadpool.start(self.worker_3d)

    def export_2d(self):
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

        file_name = ''

        if self.params_exp.child('Количество точек в имя файла').value():
            file_name += f'{self.params.child("Количество точек").value()}'

        if self.params_exp.child('Параметр \\lambda в имя файла').value():
            file_name += f'_{self.params.child("lambda").value()}'

        for i in self.worker.vertices:
            file_name += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'
        # file_name = file_name[1:]

        if file_name[0] == '_':
            file_name = file_name[1:]

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

    def export_3d(self):
        """TODO."""
        filename = 'test.png'

        # №1
        # d = self.graphics_widget_3d.renderToArray((1000, 1000))
        # pg.makeQImage(d).save(filename, quality=100)

        # № 2
        # grabs current
        self.graphics_widget_3d.grabFramebuffer().save(filename)

        # № 3
        # matplotlib?


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

    def tab_changed(self, tab_widget, button_plot, button_export):
        """Switch plot and export signals, when switch between tabs."""
        button_plot.disconnect()
        button_export.disconnect()

        # idx == 0 — 2d
        # idx == 1 — 3d
        choice = [{'plot': self.plot_2d, 'export': self.export_2d},
                  {'plot': self.plot_3d, 'export': self.export_3d}]

        idx = tab_widget.currentIndex()

        button_plot.clicked.connect(choice[idx]['plot'])
        button_export.clicked.connect(choice[idx]['export'])


if __name__ == '__main__':
    # p4 = nPoint(1, 2, 3, 4)
    # print(p4)

    app = Application()
    pg.exec()
