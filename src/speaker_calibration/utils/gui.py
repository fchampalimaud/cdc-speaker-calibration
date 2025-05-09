import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


class MatplotlibWidget(QWidget):
    def __init__(self, figure):
        super().__init__()
        self.fig = figure
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)
        self.layout = QVBoxLayout()
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def add_plots(self, count: int, heatmap: bool = False):
        self.ax.clear()
        if not heatmap:
            self.plot = []
            for i in range(count):
                self.plot.append(self.ax.plot([0], [0]))
        else:
            self.plot = self.ax.imshow(np.zeros((1, 1, 3)))
