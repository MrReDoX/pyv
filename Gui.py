# TODO
# Кнопка Export
# Запоминать результаты вычислений для ускорения работы
# Кнопка сохранить текущую конфигурацию
# Кнопка checker, которая позволяет установить текущий checker
# Переделать вершины в class pyqtgraph.parametertree.parameterTypes.ListParameter(**opts)[
# или на class pyqtgraph.parametertree.parameterTypes.TextParameter(**opts)
# Рисовать точку за точкой?
# Дерево параметров Export
# Выбрать формат для экспорта списком: eps, png...
# dpi для экспорта

# https://pyqtgraph.readthedocs.io/en/latest/parametertree/parametertypes.html

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

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

# format: "(x_1:y_1:z_1),(x_2:y_2:z_2),\dots,(x_n:y_n:z_n)"
def parse_vertices(data: str) -> list:
    data = data.strip().replace(' ', '').split(',')

    # remove ( and )
    data = [i[1:-1] for i in data]

    # make triples (x, y, z)
    data = [tuple(map(float, i.split(':'))) for i in data]

    return [Point3(x, y, z) for (x, y, z) in data]


# format: "HEX1, HEX2, ..., HEX3"
def parse_colors(data: str) -> list:
    if not data:
        return list()

    # remove spaces, etc
    data = data.strip().replace(' ', '').split(',')

    return [f'#{i}' for i in data]


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

    worker.m = parse_m(params.child('Стартовая точка').value())
    if not params.child('Стартовая точка').value():
        worker.m = worker.generate_m()

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

    cnt = eval(params.child('Количество точек').value())

    x, y, colors = worker.clean(*worker.work(cnt, rel=relation))

    size = 1.0
    if val := params.child('Размер точки').value():
        size = val

    canvas.addItem(pg.ScatterPlotItem(x=x, y=y, size=size, brush=colors))

    main_window.setWindowTitle('pyv DONE')


def save():
    pass


def export():
    import matplotlib.pyplot as plt

    global x, y, colors
    global worker

    main_window.setWindowTitle('pyv EXPORTING')

    print(worker.xmin, worker.xmax, worker.ymin, worker.ymax)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().add_patch(plt.Circle((0, 0), 1, fill=False, color='red'))
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
    if val := params.child('Размер точки').value():
        size = val

    plt.scatter(x, y, c=colors, s=size/2, edgecolors='none')
    plt.savefig('export.png', dpi=600)

    plt.close()
    plt.cla()
    plt.clf()

    main_window.setWindowTitle('pyv DONE')


pg.setConfigOptions(antialias=True)

app = pg.mkQApp('pyv')

# Create window with ImageView widget
main_window = QtWidgets.QMainWindow()
# win.showFullScreen()
# win.resize(800,800)
main_window.setWindowTitle('pyv')

children = [
    dict(name='Вершины', type='str', value='(2:0:1),(4:2:1),(4:-2:1)'),
    dict(name='Стартовая точка', type='str', value=''),
    dict(name='Цвета точек', type='str', value='0000ff, 008000, 781f19'),
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
    dict(name='Размер точки', type='float', value=1.0)
]

params = pg.parametertree.Parameter.create(name='Параметры', type='group', children=children)
param_tree = pg.parametertree.ParameterTree(showHeader=False)
param_tree.setParameters(params)

win = pg.GraphicsLayoutWidget(show=False)
canvas = win.addPlot()
canvas.setAspectLocked(True, 1.0)

win.setBackground('w')

tmp = np.linspace(0, 2 * math.pi, num=200)
circle = pg.PlotCurveItem(np.cos(tmp), np.sin(tmp), pen = pg.mkPen('#ff0000'))
canvas.addItem(circle)


btn_plot = QtWidgets.QPushButton("Plot")
btn_save = QtWidgets.QPushButton("Save")
btn_export = QtWidgets.QPushButton("Export")

# connect plot to thread
btn_plot.clicked.connect(plot)
btn_save.clicked.connect(save)
btn_export.clicked.connect(export)
# plot_thread = threading.Thread(target=plot)
# btn_plot.clicked.connect(plot_thread.start)
# btn_reset.clicked.connect(reset)

button_layout = QtWidgets.QHBoxLayout()
button_layout.addWidget(btn_plot)
button_layout.addWidget(btn_save)
button_layout.addWidget(btn_export)

main_layout = QtWidgets.QVBoxLayout()
main_layout.addWidget(param_tree)
main_layout.addLayout(button_layout)

widget = QtWidgets.QWidget()
widget.setLayout(main_layout)


splitter = QtWidgets.QSplitter()
splitter.addWidget(win)
splitter.addWidget(widget)


# layout = QtWidgets.QGridLayout()
# layout.addWidget(win, 0, 0, 1, 1)
# layout.addWidget(QtWidgets.QSplitter
# layout.addWidget(param_tree, 0, 1, 1, 2)
# layout.setColumnMinimumWidth(2, 500)
# layout.addWidget(btn_plot, 1, 1)
# layout.addWidget(btn_reset, 1, 2)

main_window.setCentralWidget(splitter)

# widget = QtWidgets.QWidget(win)
# main_window.setCentralWidget(widget)
# widget.setLayout(splitter)

main_window.showMaximized()

# layout.showMaximized()
# layout.show()

# splitter = QtWidgets.QSplitter()
# splitter.addWidget(param_tree)
# splitter.addWidget(points)
#
# splitter.showMaximized()
# splitter.show()

worker = None
x, y, colors = None, None, None

if __name__ == '__main__':
    pg.exec()
