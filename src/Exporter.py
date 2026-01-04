"""Module responsible for 2d export."""

import itertools
import re
from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pyqtgraph.Qt.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot

from Constants import FRAME_FIRST_TYPE, FRAME_SECOND_TYPE


def safe_filename(name: str) -> str:
    r"""Sanitize a string to make it safe for use as a filename on most filesystems.

    Replaces any characters that are invalid in filenames on Windows and commonly
    problematic on Unix-like systems (i.e., <, >, :, ", /, \\, |, ?, *) with
    underscores ('_').

    Args:
        name (str): The original string intended to be used as a filename.

    Returns:
        str: A sanitized version of the input string with invalid characters
             replaced by '_'.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', name)


class ExporterSignals(QObject):
    """Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        returns no data
    """

    finished = pyqtSignal()


class Exporter2D(QRunnable):
    """Class managing matplotlib export."""

    def __init__(
            self,
            worker,
            params,
            params_exp,
            x,
            y,
            colors,
            lamb,
        ):
        """Parse params for future exporting."""
        super().__init__()
        self.threadpool = QThreadPool()
        self.args = ()
        self.kwargs = {}
        self.signals = ExporterSignals()

        self.worker = worker
        self.params = params
        self.params_exp = params_exp
        self.x = x
        self.y = y
        self.colors = colors
        self.lamb = lamb

        self.line_width = 0.25
        self.border_width = 0.25
        self.point_size = 1.0
        self.dpi = 600
        self.directory = Path.cwd()
        self.do_plot_axis = 'on'
        self.has_colors = False
        self.rasterized = True

        self.__parse_params()
        self.__parse_file_name()


    @pyqtSlot()
    def run(self):
        """QThread magic."""
        self.export_2d(*self.args, **self.kwargs)

        self.signals.finished.emit()


    def __parse_params(self):
        if val := self.params_exp.child('Размер точки').value():
            self.point_size = val

        if value := self.params_exp.child('Директория по умолчанию').value():
            self.directory = value

        if val := self.params_exp.child('dpi').value():
            self.dpi = val

        self.has_colors = any([
            self.params.child('Случайные цвета').value(),
            self.params.child('Цвета точек').value(),
        ])

        value = self.params_exp.child('Рисовать оси').value()
        yes_or_no = {False: 'off', True: 'on'}
        self.do_plot_axis = yes_or_no[value]
        self.rasterized = self.params_exp.child('Растеризовать').value()


    def __parse_file_name(self):
        file_name = self.params_exp.child('Имя файла').value()

        while (left_idx := file_name.find('$')) != -1:
            right_idx = file_name.find('$', left_idx + 1)

            # slice without $
            command = file_name[left_idx + 1:right_idx]

            ans = ''
            if command == 'color':
                ans = 'bw'
                if self.has_colors:
                    ans = 'colored'

            elif command == 'lambda':
                ans = f'{self.lamb:.2f}'
            elif command == 'verticies':
                for i in self.worker.vertices:
                    ans += f'_({i.x:.1f}:{i.y:.1f}:{i.z:.1f})'

            file_name = file_name[:left_idx] + ans + file_name[right_idx + 1:]

        if file_name[0] == '_':
            file_name = file_name[1:]

        while file_name.find('__') != -1:
            file_name = file_name.replace('__', '_')

        self.file_name = file_name


    def export_2d(self):
        """Export image file with matplotlib."""
        plt.gca().set_aspect('equal', adjustable='box')

        if self.params.child('Рисовать абсолют').value():
            color = 'red'
            if val := self.params.child('Цвет абсолюта').value():
                color = val

            if val := self.params_exp.child('Ширина линий абсолюта').value():
                self.line_width = val

            if self.worker.frame_type == FRAME_FIRST_TYPE:
                par = {'color': color, 'linewidth': self.line_width}
                theta = np.linspace(0, 2 * np.pi, 2**14)
                x_coords = np.cos(theta)
                y_coords = np.sin(theta)
                plt.plot(x_coords, y_coords, **par)

            if self.worker.frame_type == FRAME_SECOND_TYPE:
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
                    y_coords = [1 / x for x in x_coords]
                    plt.plot(x_coords, y_coords, c=color, linewidth=self.line_width)

                    x_coords = np.linspace(left, -0.01, cnt)

                y_coords = [1 / x for x in x_coords]
                plt.plot(x_coords, y_coords, c=color, linewidth=self.line_width)

        if self.params.child('Рисовать границы').value():
            if value := self.params_exp.child('Ширина границ').value():
                self.border_width = value

            vertices = [*self.worker.vertices, self.worker.vertices[0]]
            for_pairing = [i.to_lower_dimension() for i in vertices]

            for cur, nex in itertools.pairwise(for_pairing):
                plt.plot([cur[1], nex[1]],
                         [cur[2], nex[2]],
                         c='black',
                         linewidth=self.border_width)

        if not self.file_name:
            return

        plt.axis(self.do_plot_axis)
        plt.scatter(self.x,
                    self.y,
                    c=self.colors,
                    s=self.point_size,
                    edgecolors='none',
                    rasterized=self.rasterized)

        plt.savefig(f'{self.directory}/{safe_filename(self.file_name)}', dpi=self.dpi)

        plt.close()
        plt.cla()
        plt.clf()
