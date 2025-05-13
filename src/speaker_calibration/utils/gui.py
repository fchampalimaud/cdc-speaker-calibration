from typing import Literal

import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
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
    def __init__(self):
        super().__init__()
        self.fig = Figure(figsize=(5, 3))
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)
        self.layout = QVBoxLayout()
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def generate_plots(self, count: int, heatmap: bool = False):
        self.ax.clear()
        if not heatmap:
            self.plot = []
            for i in range(count):
                (line,) = self.ax.plot([], [])
                self.plot.append(line)
        else:
            self.plot = self.ax.imshow(np.zeros((1, 1, 3)))


class Plot:
    def __init__(
        self,
        array_type: Literal[
            "Calibration",
            "Signals",
            "Inverse Filter",
            "Inverse Filter Signal",
        ] = "Calibration",
        calib_type: Literal["Noise", "Pure Tones"] = "Noise",
        num_amp: int = 2,
        num_freqs: int = 1,
    ):
        self.plot = MatplotlibWidget()
        self.init_array(array_type, calib_type, num_amp, num_freqs)

    def init_array(
        self,
        array_type: Literal[
            "Calibration",
            "Signals",
            "Inverse Filter",
            "Inverse Filter Signal",
        ],
        calib_type: Literal["Noise", "Pure Tones"],
        num_amp: int = 2,
        num_freqs: int = 1,
        num_db: int = 2,
    ):
        if calib_type == "Noise" and array_type == "Calibration Data":
            self.data = np.zeros((num_amp, 2))
        elif calib_type == "Noise" and array_type == "Calibration Signals":
            self.data = np.zeros((num_amp, 2), dtype=Sound)
        if calib_type == "Noise" and array_type == "Test Data":
            self.data = np.zeros((num_db, 2))
        elif calib_type == "Noise" and array_type == "Test Signals":
            self.data = np.zeros((num_db, 2), dtype=Sound)
        elif calib_type == "Noise" and array_type == "Inverse Filter":
            self.data = np.zeros((1, 2))
        elif calib_type == "Noise" and array_type == "Inverse Filter Signal":
            self.data = np.zeros((2), dtype=Sound)
        elif calib_type == "Pure Tones" and array_type == "Calibration Data":
            self.data = np.zeros((num_amp, num_freqs, 3))
        elif calib_type == "Pure Tones" and array_type == "Calibration Signals":
            self.data = np.zeros((num_amp, num_freqs, 2), dtype=Sound)
        elif calib_type == "Pure Tones" and array_type == "Test Data":
            self.data = np.zeros((num_db, num_freqs, 3))
        elif calib_type == "Pure Tones" and array_type == "Test Signals":
            self.data = np.zeros((num_db, num_freqs, 2), dtype=Sound)

    def generate_plots(
        self,
        plot_type: Literal[
            "Calibration",
            "Signals",
            "Inverse Filter",
            "Inverse Filter Signal",
        ],
        calib_type: Literal["Noise", "Pure Tones"],
    ):
        if calib_type == "Noise" and plot_type == "Calibration Data":
            self.plot.generate_plots(2)
        elif calib_type == "Noise" and plot_type == "Calibration Signals":
            self.plot.generate_plots(2)
        elif calib_type == "Noise" and plot_type == "Test Data":
            self.plot.generate_plots(2)
        elif calib_type == "Noise" and plot_type == "Test Signals":
            self.plot.generate_plots(2)
        elif calib_type == "Noise" and plot_type == "Inverse Filter":
            self.plot.generate_plots(1)
        elif calib_type == "Noise" and plot_type == "Inverse Filter Signal":
            self.plot.generate_plots(2)
        elif calib_type == "Pure Tones" and plot_type == "Calibration Data":
            self.plot.generate_plots(1, True)
        elif calib_type == "Pure Tones" and plot_type == "Calibration Signals":
            self.plot.generate_plots(2)
        elif calib_type == "Pure Tones" and plot_type == "Test Data":
            self.plot.generate_plots(1, True)
        elif calib_type == "Pure Tones" and plot_type == "Test Signals":
            self.plot.generate_plots(2)
