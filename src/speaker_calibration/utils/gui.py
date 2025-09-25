from typing import Literal

import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from scipy.signal import freqz

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

    def generate_plots(
        self, count: int, heatmap: bool = False, data=np.zeros((1, 1, 3))
    ):
        self.ax.clear()
        self.plot = []
        if not heatmap:
            for i in range(count):
                (plot,) = self.ax.plot([], [])
                self.plot.append(plot)
        else:
            plot = self.ax.imshow(data, cmap="viridis", interpolation="nearest")
            self.plot.append(plot)
            self.fig.colorbar(self.plot[0], ax=self.ax)


class Plot:
    def __init__(
        self,
        plot_type: Literal[
            "Data",
            "Signals",
            "Inverse Filter",
            "Inverse Filter Signal",
        ] = "Data",
        calib_type: Literal["Noise", "Pure Tones"] = "Noise",
        num_amp: int = 2,
        num_freqs: int = 1,
    ):
        self.calib_type = calib_type
        self.plot_type = plot_type
        self.plot = MatplotlibWidget()
        self.init_array(num_amp, num_freqs)

    def init_array(self, num_amp: int = 2, num_freqs: int = 1):
        self.amp_index = 0
        self.freq_index = 0

        if self.calib_type == "Noise" and self.plot_type == "Data":
            self.data = np.zeros((num_amp, 2))
        elif self.calib_type == "Noise" and self.plot_type == "Signals":
            self.data = np.zeros((num_amp, 2), dtype=Sound)
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter":
            self.data = np.zeros((1, 2))
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter Signal":
            self.data = np.zeros((2), dtype=Sound)
        elif self.calib_type == "Pure Tones" and self.plot_type == "Data":
            self.data = np.zeros((num_amp, num_freqs, 3))
        elif self.calib_type == "Pure Tones" and self.plot_type == "Signals":
            self.data = np.zeros((num_amp, num_freqs, 2), dtype=Sound)

    def generate_plots(self, calib_type: Literal["Noise", "Pure Tones"]):
        self.calib_type = calib_type

        if self.calib_type == "Noise" and self.plot_type == "Data":
            self.plot.generate_plots(2)
        elif self.calib_type == "Noise" and self.plot_type == "Signals":
            self.plot.generate_plots(2)
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter":
            self.plot.generate_plots(1)
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter Signal":
            self.plot.generate_plots(2)
        elif self.calib_type == "Pure Tones" and self.plot_type == "Data":
            self.plot.generate_plots(1, True, self.data)
        elif self.calib_type == "Pure Tones" and self.plot_type == "Signals":
            self.plot.generate_plots(2)

    def add_data(self, is_predata: bool, *args):
        if self.calib_type == "Noise" and self.plot_type == "Data":
            if is_predata:
                self.data[:, 0] = args[0]
            else:
                self.data[args[0], 1] = args[2].calculate_db_spl()
        elif self.calib_type == "Noise" and self.plot_type == "Signals":
            self.data[args[0], 0] = args[1]
            self.data[args[0], 1] = args[2]
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter":
            freq, response = freqz(args[0], 1, 192000)
            filter = np.column_stack((freq, response))
            self.data = filter
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter Signal":
            self.data[0] = args[1]
            self.data[1] = args[2]
        elif self.calib_type == "Pure Tones" and self.plot_type == "Data":
            if is_predata:
                self.data[:, :, 0:2] = args[0]
            else:
                self.data[args[0], args[1], 2] = args[4]
        elif self.calib_type == "Pure Tones" and self.plot_type == "Signals":
            self.data[args[0], args[1], 0] = args[2]
            self.data[args[0], args[1], 1] = args[3]

        self.draw_data()

    def draw_data(self):
        if self.calib_type == "Noise" and self.plot_type == "Data":
            self.plot.plot[0].set_data(self.data[:, 0], self.data[:, 1])
        elif self.calib_type == "Noise" and self.plot_type == "Signals":
            recording = self.data[self.amp_index, 1]
            freq, fft = recording.fft_welch(0.005)
            self.plot.plot[0].set_data(freq, fft)
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter":
            self.plot.plot[0].set_data(self.data[:, 0], self.data[:, 1])
        elif self.calib_type == "Noise" and self.plot_type == "Inverse Filter Signal":
            self.plot.plot[0].set_data(self.data[0].time, self.data[0].signal)
            self.plot.plot[1].set_data(self.data[1].time, self.data[1].signal)
        elif self.calib_type == "Pure Tones" and self.plot_type == "Data":
            self.plot.plot[0].set_data(self.data[:, :, 2])
            self.plot.plot[0].autoscale()
        elif self.calib_type == "Pure Tones" and self.plot_type == "Signals":
            signal = self.data[self.amp_index, self.freq_index, 0]
            recording = self.data[self.amp_index, self.freq_index, 1]
            self.plot.plot[0].set_data(signal.time, signal.signal)
            self.plot.plot[1].set_data(recording.time, recording.signal)

        self.plot.ax.relim()
        self.plot.ax.autoscale_view()
        self.plot.canvas.draw()

    def update_indexes(self, amp_index: int, freq_index: int):
        self.amp_index = amp_index
        self.freq_index = freq_index

        self.draw_data()
