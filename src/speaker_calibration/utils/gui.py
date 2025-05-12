from typing import Literal

import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from speaker_calibration.sound import Sound


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
                (line,) = self.ax.plot([], [])
                self.plot.append(line)
        else:
            self.plot = self.ax.imshow(np.zeros((1, 1, 3)))


class PlotData:
    def __init__(
        self,
        type: Literal["Noise", "Pure Tones"],
        num_amp: int,
        num_freq: int,
        num_db: int,
    ):
        if type == "Noise":
            self.inverse_filter = None
            self.psd_signal = np.zeros(2, dtype=Sound)
            self.calib = np.zeros((num_amp, 2))
            self.calib_signals = np.zeros((num_amp, 2), dtype=Sound)
            self.test = np.zeros((num_db, 2))
            self.test_signals = np.zeros((num_db, 2), dtype=Sound)
        else:
            self.calib = np.zeros((num_amp, num_freq, 3))
            self.calib_signals = np.zeros((num_amp, num_freq, 2), dtype=Sound)
            self.test = np.zeros((num_db, num_freq, 3))
            self.test_signals = np.zeros((num_db, num_freq, 2), dtype=Sound)
