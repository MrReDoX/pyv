# TODO
# Кнопка Export
# Параметр размер точки
# Рисовать границы
# ? Plot point by point

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

import math
import threading

from Iterate import Worker
from Point import Point3


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
    global busy

    if busy:
        return

    busy = True
    main_window.setWindowTitle('pyv BUSY')

    win.clear()

    worker = Worker()
    worker.vertices = parse_vertices(params.child('Вершины').value())

    worker.m = params.child('Стартовая точка').value()
    if not params.child('Стартовая точка').value():
        worker.m = worker.generate_m()

    worker.coloring = True
    worker.vertices_colors = parse_colors(params.child('Цвета точек').value())
    if not params.child('Цвета точек').value():
        worker.vertices_colors = worker.gen_random_colors()

    relation = params.child('lambda').value()
    worker.projective = params.child('projective').value()
    worker.double_mid = params.child('Рисовать вторую середину').value()

    xmin, xmax, ymin, ymax = parse_limits(params.child('Пределы').value())
    if not params.child('Пределы').value():
        xmin, xmax, ymin, ymax = worker.guess_limits()

        if params.child('Угадывать пределы (включить абсолют)').value():
            xmin, xmax, ymin, ymax = worker.guess_limits(contains_absolute = True)

    canvas = win.addPlot()
    canvas.setAspectLocked(True, 1.0)
    canvas.setXRange(xmin, xmax)
    canvas.setYRange(ymin, ymax)

    if params.child('Рисовать абсолют').value():
        color = params.child('Цвет абсолюта').value()

        points = np.linspace(0, 2 * math.pi, num=10**3)
        circle = pg.PlotCurveItem(np.cos(points), np.sin(points), pen = pg.mkPen(color))
        canvas.addItem(circle)

    cnt = eval(params.child('Количество точек').value())

    x, y, colors = worker.clean(*worker.work(cnt, rel=relation))

    # print(colors)

    # print(x, y, colors)

    # scatter = pg.ScatterPlotItem(size=1, x=x, y=y, brush=colors)
    # canvas.addItem(pg.ScatterPlotItem(size=1, x=x, y=y, brush=colors))
    canvas.addItem(pg.ScatterPlotItem(x=x, y=y, size=1, brush=colors))

    main_window.setWindowTitle('pyv DONE')
    busy = False


pg.setConfigOptions(antialias=True)

app = pg.mkQApp('pyv')

# Create window with ImageView widget
main_window = QtWidgets.QMainWindow()
# win.showFullScreen()
# win.resize(800,800)
main_window.setWindowTitle('pyv')

children = [
    dict(name='Вершины', type='str', value='(2:0:1),(4:2:1),(4:-2:1)'),
    dict(name='Рисовать границы', type='bool', value=False),
    dict(name='Стартовая точка', type='str', value=''),
    dict(name='Цвета точек', type='str', value='0000ff, 008000, 781f19'),
    dict(name='lambda', type='float', value='1.0'),
    dict(name='projective', type='float', value='1.0'),
    dict(name='Рисовать вторую середину', type='bool', value=False),
    dict(name='Пределы', type='str', value=''),
    dict(name='Угадывать пределы', type='bool', value=False),
    dict(name='Угадывать пределы (включить абсолют)', type='bool', value=True),
    dict(name='Рисовать абсолют', type='bool', value=True),
    dict(name='Цвет абсолюта', type='str', value='#ff0000'),
    dict(name='Количество точек', type='str', value='2**14')
]

params = pg.parametertree.Parameter.create(name='Параметры', type='group', children=children)
param_tree = pg.parametertree.ParameterTree(showHeader=False)
param_tree.setParameters(params)

win = pg.GraphicsLayoutWidget(show=False)
canvas = win.addPlot()
canvas.setAspectLocked(True, 1.0)

win.setBackground('w')

tmp = np.linspace(0, 2 * math.pi, num=10**3)
circle = pg.PlotCurveItem(np.cos(tmp), np.sin(tmp), pen = pg.mkPen('#ff0000'))
canvas.addItem(circle)


btn_plot = QtWidgets.QPushButton("Plot")
btn_reset = QtWidgets.QPushButton("Export")

# connect plot to thread
btn_plot.clicked.connect(plot)
# plot_thread = threading.Thread(target=plot)
# btn_plot.clicked.connect(plot_thread.start)
# btn_reset.clicked.connect(reset)

button_layout = QtWidgets.QHBoxLayout()
button_layout.addWidget(btn_plot)
button_layout.addWidget(btn_reset)

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

busy = False

if __name__ == '__main__':
    pg.exec()
