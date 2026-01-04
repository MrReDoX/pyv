"""Main program module. Builds GUI and run program."""

# TODO(tensorix): Fix checker messages
# TODO(tensorix): Add binaries: windows, linux, mac
# TODO(tensorix): Switch to uv
# TODO(tensorix): Add translation

import itertools
import json
import sys
from math import ceil, inf, pi
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt.QtGui import QAction
from pyqtgraph.Qt.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from seval import safe_eval

from Constants import FRAME_FIRST_TYPE, FRAME_SECOND_TYPE
from Exporter import Exporter2D
from Iterate2D import Worker2D
from Iterate3D import Worker3D
from Point import Point, Point3


def parse_m(data: str) -> Point3:
    """Parse point data from text box in format (x:y:z).

    Args:
        data (str): data from the text box

    Returns:
        Point3: parsed point

    """
    if not data:
        return Point3(inf, inf, inf)

    data = data.strip().replace(' ', '')[1:-1]
    listed = list(map(float, data.split(':')))

    return Point3(*listed)


def parse_vertices(data: str) -> list:
    """Parse vertices data from text box in format.

        (x1:y1:z1)
        (x2:y2:z2)
            .
            .
            .
        (xn:yn:zn)

    Args:
        data (str): data from the text box

    Returns:
        list: list of parsed vertices of type Point3 or nPoint

    """
    improved_data = data.strip().replace(' ', '').replace(',', '.').split('\n')

    # remove ( and )
    listed = [i[1:-1] for i in improved_data]

    # make triples (x, y, z)
    paired = [tuple(map(float, i.split(':'))) for i in listed]

    number_of_coords_in_plane = 3

    if len(paired[0]) == number_of_coords_in_plane:
        return [Point3(x, y, z) for (x, y, z) in paired]

    return [Point(x, y, z, w) for (x, y, z, w) in paired]


def parse_colors(data: str) -> list:
    """Parse colors data from text box in format #HEX1, #HEX2, ...

    Args:
        data (str): data from the text box

    Returns:
        list: list of strings in format ['#HEX1', '#HEX2', ...]

    """
    if not data:
        return []

    # remove spaces, etc
    improved_data = data.strip().replace(' ', '').split(',')

    return [f'{i}' for i in improved_data]


def parse_limits(data: str) -> tuple[float, float, float, float]:
    """Parse limits data from text box in format "xmin, xmax, ymin, ymax".

    Args:
        data (str): data from the text box

    Returns:
        Tuple[float, float, float, float]: xmin, xmax, ymin, ymax for plotter

    """
    if not data:
        return (-inf, inf, -inf, inf)

    improved_data = data.strip().replace(' ', '').split(',')

    return tuple(float(i) for i in improved_data)


class Application:
    """Main class that builds GUI."""

    def __init__(self):
        self.init_app()
        self.init_main_window()
        self.init_params()
        self.init_canvas()

        self.init_menu()
        self.init_buttons_and_layout()
        self.init_tabs_and_splitter()

        self.main_window.showMaximized()

        self.worker = Worker2D()
        self.worker_3d = Worker3D()

    def init_app(self):
        pg.setConfigOptions(antialias=True)
        self.app = pg.mkQApp('pyv')

    def init_main_window(self):
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle('pyv')

    def init_params(self):
        with Path('params.json').open(encoding='utf-8') as f:
            config = json.load(f)

        def parse_param_list(param_list):
            parsed = []
            for item in param_list:
                if item['type'] == 'list' and 'limits' in item:
                    limits = item.pop('limits')
                    p = Parameter.create(**item)
                    p.setLimits(limits)
                    parsed.append(p)
                else:
                    parsed.append(item)
            return parsed

        self.params = Parameter.create(
            name='Параметры',
            type='group',
            children=parse_param_list(config['Параметры']),
        )

        self.params_exp = Parameter.create(
            name='Экспорт',
            type='group',
            children=parse_param_list(config['Экспорт']),
        )

        self.param_tree = ParameterTree(showHeader=False)
        self.param_tree.addParameters(self.params)
        self.param_tree.addParameters(self.params_exp)

    def init_canvas(self):
        background_color = 'w'
        is_aspect_locked = True
        aspect = 1.0

        # 2d
        self.graphics_widget_2d = pg.PlotWidget(background=background_color)
        self.canvas_2d = self.graphics_widget_2d.getPlotItem()
        self.canvas_2d.setAspectLocked(is_aspect_locked, aspect)

        # 3d
        # self.graphics_widget_3d =\
        #   gl.GLViewWidget(rotationMethod='quaternion')
        self.graphics_widget_3d = gl.GLViewWidget()
        self.graphics_widget_3d.setBackgroundColor(background_color)

        # points
        self.scatter_2d = pg.ScatterPlotItem()
        self.scatter_3d = gl.GLScatterPlotItem()
        self.scatter_3d.setGLOptions('translucent')

        self.canvas_2d.addItem(self.scatter_2d)
        self.graphics_widget_3d.addItem(self.scatter_3d)

    def init_menu(self):
        action_export = QAction(self.main_window)
        action_export.setObjectName('actionExport')
        action_export.setText('Экспортировать')
        action_export.triggered.connect(self.export_conf)

        action_import = QAction(self.main_window)
        action_import.setObjectName('actionImport')
        action_import.setText('Импортировать')
        action_import.triggered.connect(self.import_conf)

        menu = self.main_window.menuBar()
        conf = menu.addMenu('Конфигурация')
        conf.addAction(action_export)
        conf.addAction(action_import)

    def init_buttons_and_layout(self):
        self.btn_plot = QPushButton('Plot')
        self.btn_plot.setShortcut('Ctrl+Return')

        self.btn_export = QPushButton('Export')

        self.btn_plot.clicked.connect(self.plot_2d)
        self.btn_export.clicked.connect(self.export_2d)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_plot)
        button_layout.addWidget(self.btn_export)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.param_tree)
        main_layout.addLayout(button_layout)

        self.params_and_buttons_widget = QWidget()
        self.params_and_buttons_widget.setLayout(main_layout)

    def init_tabs_and_splitter(self):
        # 2d, 3d tab on the bottom
        tab_widget = QTabWidget()
        tab_widget.addTab(self.graphics_widget_2d, '2d')
        tab_widget.addTab(self.graphics_widget_3d, '3d')
        tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        tab_widget.currentChanged.connect(
            lambda: self.tab_changed(
                        tab_widget,
                        self.btn_plot,
                        self.btn_export,
                    ),
        )

        splitter = QSplitter()
        splitter.addWidget(tab_widget)
        splitter.addWidget(self.params_and_buttons_widget)

        self.main_window.setCentralWidget(splitter)

    def read_config(self):
        """Read GUI settings and write them to variables."""
        self.worker.vertices = parse_vertices(
            self.params.child('Вершины').value(),
        )

        xmin, xmax, ymin, ymax = parse_limits(
            self.params.child('Пределы').value(),
        )
        if not self.params.child('Пределы').value():
            xmin, xmax, ymin, ymax = self.worker.guess_limits()

            include_absolute = self.params.child(
                'Угадывать пределы (включить абсолют)',
            ).value()
            if include_absolute:
                xmin, xmax, ymin, ymax =\
                    self.worker.guess_limits(contains_absolute=True)

        self.worker.xmin, self.worker.xmax = xmin, xmax
        self.worker.ymin, self.worker.ymax = ymin, ymax

        self.canvas_2d.setXRange(xmin, xmax)
        self.canvas_2d.setYRange(ymin, ymax)

        self.worker.prepare_shapely_checker()

        self.worker.start_point =\
            parse_m(self.params.child('Стартовая точка').value())
        if not self.params.child('Стартовая точка').value():
            self.worker.start_point = self.worker.gen_start_point()

        self.worker.prepare_polygon_checker()

        self.worker.coloring = False
        if val := self.params.child('Цвета точек').value():
            self.worker.vertices_colors = parse_colors(val)

        if not self.params.child('Цвета точек').value():
            self.worker.vertices_colors =\
                ['#000000'] * len(self.worker.vertices)

        if self.params.child('Случайные цвета').value():
            self.worker.vertices_colors = self.worker.gen_random_colors()

        self.worker.inside = self.params.child('Рисовать точки внутри').value()
        # self.worker.double_mid =\
        #     self.params.child('Рисовать вторую середину').value()

        if val := self.params.child('Стратегия').value():
            strategy_path = Path(val)
            # Добавляем родительскую директорию в sys.path
            sys.path.append(str(strategy_path.parent))
            # Импортируем модуль
            module = __import__(strategy_path.stem)
            self.worker.strategy = module.strategy

        if self.params.child('Рисовать границы').value():
            width = 3.0
            if val := self.params.child('Ширина границ').value():
                width = val

            vertices = [*self.worker.vertices, self.worker.vertices[0]]
            for_pairing = [i.to_lower_dimension() for i in vertices]

            for cur, nex in itertools.pairwise(for_pairing):
                self.canvas_2d.plot([cur[1], nex[1]],
                                    [cur[2], nex[2]],
                                    pen=pg.mkPen('#000000',
                                    width=width))

        if val := self.params.child('Тип репера').value():
            self.worker.frame_type = val

        if self.params.child('Рисовать абсолют').value():
            color = '#ff0000'
            if val := self.params.child('Цвет абсолюта').value():
                color = val

            if self.worker.frame_type == FRAME_FIRST_TYPE:
                # Absolute is a circle
                points = np.linspace(0, 2 * pi, num=2**7)

                circle = self.canvas_2d.plot()
                circle.setData(np.cos(points),
                               np.sin(points),
                               pen=pg.mkPen(color),
                               skipFiniteCheck=True)

            if self.worker.frame_type == FRAME_SECOND_TYPE:
                # Absolute is a hyperbola yx-1=0
                left = xmin - 2
                right = xmax + 2
                cnt = ceil(abs(right - left) / 0.01)

                if left * right > 0:
                    x_coords = np.linspace(left, right, cnt)
                else:
                    # xmin * xmax < 0, значит, ноль содержится
                    x_coords = np.linspace(0.1, right, cnt)
                    y_coords = [1 / x for x in x_coords]
                    hyperbole = pg.PlotCurveItem(x_coords,
                                                 y_coords,
                                                 pen=pg.mkPen(color),
                                                 skipFiniteCheck=True)
                    self.canvas_2d.addItem(hyperbole)

                    x_coords = np.linspace(left, -0.1, cnt)

                y_coords = [1 / x for x in x_coords]

                hyperbole = pg.PlotCurveItem(x_coords,
                                             y_coords,
                                             pen=pg.mkPen(color),
                                             skipFiniteCheck=True)
                self.canvas_2d.addItem(hyperbole)

            d = {'shapely & polygon': self.worker.checker,
                 'shapely': self.worker.shapely_default_checker,
                 'polygon': self.worker.polygon_default_checker}

            self.worker.checker = d[self.params.child('Алгоритм').value()]

    def plot_2d(self, rel=None, export_function=None):
        """Run chaos game and plot with ScatterPlot.

        Args:
            rel (_type_, optional): relation for segment division.
                Defaults to None.
            export_function (_type_, optional): export right after the plot.
                Defaults to None.

        """
        self.main_window.setWindowTitle('pyv PLOTTING')
        self.canvas_2d.clear()
        self.canvas_2d.addItem(self.scatter_2d)

        # To avoid
        # RuntimeError: wrapped C/C++ object of type Worker has been deleted
        del self.worker

        self.worker = Worker2D()
        self.read_config()

        if not rel:
            values = self.params.child('lambda').value()
            values = values.replace(' ', '').split(',')

            rel = float(values[0])

        cnt = safe_eval(self.params.child('Количество итераций').value())

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

            if export_function:
                export_function(x, y, colors, rel)

        # Run in separate thread
        self.worker.args = (cnt,)
        self.worker.kwargs = {'rel': rel}
        self.worker.signals.result.connect(work_finished)

        self.worker.threadpool.start(self.worker)

    def plot_3d(self):
        """Run chaos game and plot with GLScatterPlot."""
        self.main_window.setWindowTitle('pyv PLOTTING')

        self.graphics_widget_3d.clear()
        self.graphics_widget_3d.addItem(self.scatter_3d)

        self.worker_3d = Worker3D()
        self.worker_3d.vertices =\
            parse_vertices(self.params.child('Вершины').value())
        self.worker_3d.start_point = Point(1, 1, 1)
        self.worker_3d.start_point = self.worker_3d.gen_start_point()
        self.worker_3d.vertices_colors = self.worker_3d.gen_random_colors()

        # draw boundary
        lowers = [v.to_lower_dimension().to_list()
                  for v in self.worker_3d.vertices]
        edges = set()
        for tri in self.worker_3d.hull.simplices:
            # tri — индекс 3 вершин треугольника
            edges.add(tuple(sorted([tri[0], tri[1]])))
            edges.add(tuple(sorted([tri[1], tri[2]])))
            edges.add(tuple(sorted([tri[2], tri[0]])))

        for v1, v2 in edges:
            line_pts = np.array([lowers[v1], lowers[v2]])
            line = gl.GLLinePlotItem(pos=line_pts,
                                     color=(0, 0, 0, 1),
                                     width=2,
                                     antialias=True)
            self.graphics_widget_3d.addItem(line)

        # lower = [i.to_lower_dimension().to_tuple()
        #          for i in self.worker_3d.vertices]
        # lower += [lower[-1]]
        # for cur, nex in zip(lower, lower[1:]):
        #     # print(np.shape(np.array([cur, nex])))

        #     line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
        #                              color=pg.glColor('k'),
        #                              width=5,
        #                              antialias=True)

        #     self.graphics_widget_3d.addItem(line)
        # lower_first = lower[:4]
        # lower_first += [lower_first[0]]
        # for cur, nex in zip(lower_first, lower_first[1:]):
        #     line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
        #                              color=pg.glColor('k'),
        #                              width=5,
        #                              antialias=True)

        #     self.graphics_widget_3d.addItem(line)

        # lower_second = lower[4:]
        # lower_second += [lower_second[0]]
        # for cur, nex in zip(lower_second, lower_second[1:]):
        #     line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
        #                              color=pg.glColor('k'),
        #                              width=5,
        #                              antialias=True)

        #     self.graphics_widget_3d.addItem(line)

        # for cur, nex in zip(lower[:4], lower[4:]):
        #     line = gl.GLLinePlotItem(pos=np.array([cur, nex]),
        #                              color=pg.glColor('k'),
        #                              width=5,
        #                              antialias=True)

        #     self.graphics_widget_3d.addItem(line)

        # draw absolute
        mesh_data = gl.MeshData.sphere(rows=128, cols=128)
        sphere = gl.GLMeshItem(meshdata=mesh_data,
                               smooth=True,
                               color=pg.glColor('r'))
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

        relation = float(self.params.child('lambda').value())
        cnt = safe_eval(self.params.child('Количество итераций').value())

        size = 1.0
        if val := self.params.child('Размер точки').value():
            size = val

        def work_finished(x, y, z, colors):
            # if len(x) < 1000:
            #     self.plot_3d()

            #     return

            colors = np.array([pg.glColor(i) for i in colors])

            data = np.column_stack((x, y, z))

            self.scatter_3d.setData(pos=data,
                                    color=colors,
                                    size=10 * size,
                                    pxMode=True)

            self.main_window.setWindowTitle('pyv DONE')

        # run in separate thread
        self.worker_3d.args = (cnt,)
        self.worker_3d.kwargs = {'rel': relation}
        self.worker_3d.signals.result.connect(work_finished)
        self.worker_3d.threadpool.start(self.worker_3d)

    def export_2d(self):
        """Export image to file with matplotlib."""
        self.main_window.setWindowTitle('pyv EXPORTING')

        def plot_finished(x, y, colors, rel):
            self.main_window.setWindowTitle('pyv EXPORTING')

            exporter = Exporter2D(
                self.worker,
                self.params,
                self.params_exp,
                x,
                y,
                colors,
                lamb=rel,
            )
            # exporter.args = (self.worker, self.params, self.params_exp,
            #                  x, y, colors, rel)
            exporter.kwargs = {}
            exporter.signals.finished.connect(work_finished)

            exporter.threadpool.start(exporter)

        def work_finished():
            self.main_window.setWindowTitle('pyv DONE')

            if relations:
                self.plot_2d(rel=relations.pop(),
                             export_function=plot_finished)

        values = self.params.child('lambda').value()
        values = values.replace(' ', '').split(',')
        relations = set(map(float, values))

        self.plot_2d(rel=relations.pop(), export_function=plot_finished)

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
        default_name = ''

        for i in self.worker.vertices:
            default_name += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'

        default_name = default_name.lstrip('_') + '.json'

        filt = 'Json File (*.json)'
        path, _ = QFileDialog.getSaveFileName(
            parent=self.main_window,
            caption='Choose file',
            directory=str(Path.cwd() / default_name),
            filter=filt,
        )

        if not path:
            return

        if not path.endswith('.json'):
            path += '.json'

        data = {
            'Параметры': self.params.saveState()['children'],
            'Экспорт': self.params_exp.saveState()['children'],
        }

        with Path(path).open(mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def import_conf(self):
        """Read parameters trees from the JSON file."""
        filt = 'Json File (*.json)'
        path, _ = QFileDialog.getOpenFileName(
            parent=self.main_window,
            caption='Choose file',
            directory=str(Path.cwd()),
            filter=filt,
        )

        if not path:
            return

        with Path(path).open(encoding='utf-8') as f:
            data = json.load(f)

        self.params.restoreState({
            'children': data['Параметры'],
        })

        self.params_exp.restoreState({
            'children': data['Экспорт'],
        })

    def tab_changed(self, tab_widget, button_plot, button_export):
        """Switch plot and export signals, when switch between tabs.

        Args:
            tab_widget (_type_): tab we are actually on
            button_plot (_type_): plot button
            button_export (_type_): export button

        """
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
    app = Application()
    pg.exec()
