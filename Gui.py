# TODO
# Экспортирование дерева "Экспорт"
# Рисовать точку за точкой?
# status bar?
# split files

# https://pyqtgraph.readthedocs.io/en/latest/parametertree/parametertypes.html

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.parametertree import Parameter, ParameterTree

import math
import threading

from Iterate import Worker
from Point import Point2, Point3

# format: "(x, y)"
def parse_m(data: str) -> Point2:
    from math import inf

    if not data:
        return Point2(inf, inf)

    data = data.strip().replace(' ', '')[1:-1]
    data = list(map(float, data.split(',')))

    return Point2(data[0], data[1])

# format: "(x_1:y_1:z_1)\n(x_2:y_2:z_2)\n\dots\n(x_n:y_n:z_n)"
def parse_vertices(data: str) -> list:
    data = data.strip().replace(' ', '').split('\n')

    # remove ( and )
    data = [i[1:-1] for i in data]

    # make triples (x, y, z)
    data = [tuple(map(float, i.split(':'))) for i in data]

    return [Point3(x, y, z) for (x, y, z) in data]


# format: "#HEX1, #HEX2, ..., #HEX3"
def parse_colors(data: str) -> list:
    if not data:
        return list()

    # remove spaces, etc
    data = data.strip().replace(' ', '').split(',')

    return [f'{i}' for i in data]


# format: "xmin, xmax, ymin, ymax"
def parse_limits(data: str) -> (float, float, float, float):
    from math import inf

    if not data:
        return (inf, inf, inf, inf)

    data = data.strip().replace(' ', '').split(',')

    return tuple(float(i) for i in data)


def plot():
    global win
    global worker
    global x, y, colors

    main_window.setWindowTitle('pyv BUSY')

    win.clear()

    worker = Worker()
    worker.vertices = parse_vertices(params.child('Вершины').value())

    worker.start_point = parse_m(params.child('Стартовая точка').value())
    if not params.child('Стартовая точка').value():
        worker.start_point = worker.gen_start_point()

    worker.coloring = False
    if colors := params.child('Цвета точек').value():
        worker.coloring = True
        worker.vertices_colors = parse_colors(colors)

    if params.child('Случайные цвета').value():
        worker.coloring = True
        worker.vertices_colors = worker.gen_random_colors()

    relation = params.child('lambda').value()
    worker.projective = params.child('projective').value()
    worker.double_mid = params.child('Рисовать вторую середину').value()

    xmin, xmax, ymin, ymax = parse_limits(params.child('Пределы').value())
    if not params.child('Пределы').value():

        xmin, xmax, ymin, ymax = worker.guess_limits()
        if params.child('Угадывать пределы (включить абсолют)').value():
            xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)

    worker.xmin, worker.xmax = xmin, xmax
    worker.ymin, worker.ymax = ymin, ymax

    canvas = win.addPlot()
    canvas.setAspectLocked(True, 1.0)
    canvas.setXRange(xmin, xmax)
    canvas.setYRange(ymin, ymax)

    if params.child('Рисовать границы').value():
        width = 3.0
        if value := params.child('Ширина границ').value():
            width = value

        tmp = [i.to_Point2() for i in worker.vertices]

        for j in range(len(tmp)):
            x_values = [tmp[j].x, tmp[(j + 1) % len(tmp)].x]
            y_values = [tmp[j].y, tmp[(j + 1) % len(tmp)].y]

            canvas.plot(x_values, y_values, pen=pg.mkPen('#000000', width=3))

    if params.child('Рисовать абсолют').value():
        color = '#ff0000'
        if val := params.child('Цвет абсолюта').value():
            color = val

        points = np.linspace(0, 2 * math.pi, num=200)
        circle = pg.PlotCurveItem(np.cos(points), np.sin(points), pen = pg.mkPen(color))
        canvas.addItem(circle)

    if val := params.child('Checker').value():
        import os
        import sys
        from pathlib import Path

        sys.path.append(os.path.dirname(val))

        module = __import__(Path(val).stem)

        worker.checker = module.checker

    cnt = eval(params.child('Количество точек').value())

    x, y, colors = worker.clean(*worker.work(cnt, rel=relation))

    size = 1.0
    if val := params.child('Размер точки').value():
        size = val

    canvas.addItem(pg.ScatterPlotItem(x=x, y=y, size=size, brush=colors))

    main_window.setWindowTitle('pyv DONE')


def export():
    import os
    import matplotlib.pyplot as plt

    global x, y, colors
    global worker

    main_window.setWindowTitle('pyv EXPORTING')

    plt.gca().set_aspect('equal', adjustable='box')

    if params.child('Рисовать абсолют').value():
        color = 'red'
        if val := params.child('Цвет абсолюта').value():
            color = val

        plt.gca().add_patch(plt.Circle((0, 0), 1, fill=False, color=color))

    plt.xlim(worker.xmin, worker.xmax)
    plt.ylim(worker.ymin, worker.ymax)

    if params.child('Рисовать границы').value():
        width = 1.0
        # if value := params.child('Ширина границ').value():
        #     width = value / 2

        a = [k.to_Point2() for k in worker.vertices]
        for k in range(len(a)):
            x_values = [a[k].x, a[(k + 1) % len(a)].x]
            y_values = [a[k].y, a[(k + 1) % len(a)].y]

            plt.plot(x_values, y_values, c='black', linewidth=width)

    size = 1.0
    # if val := params.child('Размер точки').value():
    #     size = val

    path, fmt = QtWidgets.QFileDialog.getSaveFileName(
        parent=main_window,
        caption='Выберите файл',
        directory=os.getcwd(),
    )

    file_name = os.path.basename(path)

    if not file_name:
        return

    dpi = 600
    if val := params_exp.child('dpi').value():
        dpi = val

    plt.scatter(x, y, c=colors, s=size/2, edgecolors='none')
    plt.savefig(file_name, dpi=dpi)

    plt.close()
    plt.cla()
    plt.clf()

    main_window.setWindowTitle('pyv DONE')


def export_conf():
    import json
    import os

    filt = 'Json File (*.json)'
    path, fmt = QtWidgets.QFileDialog.getSaveFileName(
        parent=main_window,
        caption='Выберите файл',
        directory=os.getcwd(),
        filter=filt,
        initialFilter=filt
    )

    file_name = os.path.basename(path)

    if not file_name:
        return

    if path.find('.json') == -1:
        file_name = file_name + '.json'

    with open(file_name, 'w') as file:
        json.dump(params.saveState(), file)


def import_conf():
    import json
    import os

    filt = 'Json File (*.json)'
    path, fmt = QtWidgets.QFileDialog.getOpenFileName(
        parent=main_window,
        caption='Выберите файл',
        directory=os.getcwd(),
        filter=filt,
        initialFilter=filt
    )

    file_name = os.path.basename(path)

    if file_name:
        params.restoreState(json.load(open(file_name)))

pg.setConfigOptions(antialias=True)

app = pg.mkQApp('pyv')

main_window = QtWidgets.QMainWindow()
main_window.setWindowTitle('pyv')

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
    dict(name='Ширина границ', type='float', value=3.0),
    dict(name='Рисовать абсолют', type='bool', value=True),
    dict(name='Цвет абсолюта', type='str', value='#ff0000'),
    dict(name='Количество точек', type='str', value='2**14'),
    dict(name='Размер точки', type='float', value=1.0),
    Parameter.create(name='Checker', type='file')
]

children_exp = [
    dict(name='dpi', type='int', value=600)
]

params = Parameter.create(name='Параметры', type='group', children=children)
params_exp = Parameter.create(name='Экспорт', type='group', children=children_exp)
param_tree = ParameterTree(showHeader=False)
param_tree.addParameters(params)
param_tree.addParameters(params_exp)

win = pg.GraphicsLayoutWidget(show=False)
canvas = win.addPlot()
canvas.setAspectLocked(True, 1.0)

win.setBackground('w')

tmp = np.linspace(0, 2 * math.pi, num=200)
circle = pg.PlotCurveItem(np.cos(tmp), np.sin(tmp), pen = pg.mkPen('#ff0000'))
canvas.addItem(circle)

action_export = QtWidgets.QAction(main_window)
action_export.setObjectName('actionExport')
action_export.setText('Экспортировать')
action_export.triggered.connect(export_conf)

action_import = QtWidgets.QAction(main_window)
action_import.setObjectName('actionImport')
action_import.setText('Импортировать')
action_import.triggered.connect(import_conf)


menu = main_window.menuBar()
conf = menu.addMenu('Конфигурация')
conf.addAction(action_export)
conf.addAction(action_import)


btn_plot = QtWidgets.QPushButton("Plot")
btn_export = QtWidgets.QPushButton("Export")

btn_plot.clicked.connect(plot)
btn_export.clicked.connect(export)

button_layout = QtWidgets.QHBoxLayout()
button_layout.addWidget(btn_plot)
button_layout.addWidget(btn_export)


main_layout = QtWidgets.QVBoxLayout()
main_layout.addWidget(param_tree)
main_layout.addLayout(button_layout)


widget = QtWidgets.QWidget()
widget.setLayout(main_layout)


splitter = QtWidgets.QSplitter()
splitter.addWidget(win)
splitter.addWidget(widget)


main_window.setCentralWidget(splitter)
main_window.showMaximized()


worker = None
x, y, colors = None, None, None


if __name__ == '__main__':
    pg.exec()
