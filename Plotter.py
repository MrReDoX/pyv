import pyqtgraph as pg
import pyqtgraph.exporters

import numpy as np
import math


class Plotter:
    def __init__(self, x: list, y: list):
        self.x = x
        self.y = y

        self.win = pg.GraphicsLayoutWidget(show=False)
        self.canvas = self.win.addPlot()
        self.canvas.setAspectLocked(True, 1.0)

    def set_x_range(self, xmin: float, xmax: float):
        self.canvas.setXRange(xmin, xmax)

    def set_y_range(self, ymin: float, ymax: float):
        self.canvas.setYRange(ymin, ymax)

    def plot(self, save=False):
        pg.setConfigOptions(antialias=True)

        self.win.setBackground('w')

        print(self.colors)

        scatter = pg.ScatterPlotItem(size=1, x=self.x, y=self.y, brush=self.colors)

        points = np.linspace(0, 2 * math.pi, num=10**3)
        circle = pg.PlotCurveItem(np.cos(points), np.sin(points), pen = pg.mkPen('#ff0000'))

        self.canvas.addItem(scatter)
        self.canvas.addItem(circle)

        # doesn't work
        # if save:
        #    #exporter = pg.exporters.ImageExporter(self.win.scene())
        #    exporter = pg.exporters.SVGExporter(self.win.getItem(0, 0))

        #    exporter.export(self.file_name)

        self.win.show()
        pg.exec()

