import numpy as np
import serial.tools.list_ports
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from scipy.signal import freqz

from speaker_calibration.sound import RecordedSound, Sound


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


class EQFilterPlot:
    def __init__(self):
        self.figure = MatplotlibWidget()
        self.init_plot()

    def init_plot(self):
        self.figure.ax.clear()
        (self.plot,) = self.figure.ax.plot([], [])

    def add_data(self, filter):
        freq, response = freqz(filter, 1, 192000)
        self.plot.set_data(freq, 20 * np.log10(response))
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()


class NoiseDataPlot:
    def __init__(self, num_amp: int):
        self.figure = MatplotlibWidget()
        self.data = np.zeros((num_amp, 3))
        self.init_plot()

    def init_plot(self):
        self.figure.ax.clear()
        self.plot = []

        (plot,) = self.figure.ax.plot([], [], "o", color="blue")
        self.plot.append(plot)

        (plot,) = self.figure.ax.plot([], [], "--", color="blue")
        self.plot.append(plot)

    def add_xx(self, xx, is_test=False):
        self.data[:, 0] = xx
        self.plot[0].set_data(self.data[:, 0], self.data[:, 1])

        if is_test:
            self.plot[1].set_data(self.data[:, 0], self.data[:, 0])

        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()

    def add_point(self, index, data):
        self.data[index, 1] = data
        self.plot[0].set_data(self.data[:, 0], self.data[:, 1])
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()

    def add_linear_regression(self, slope, intercept):
        self.data[:, 2] = slope * self.data[:, 0] + intercept
        self.plot[1].set_data(self.data[:, 0], self.data[:, 2])
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()


class NoiseSignalsPlot:
    def __init__(self, min_freq, max_freq):
        self.figure = MatplotlibWidget()
        self.init_plot(min_freq, max_freq)

    def init_plot(self, min_freq, max_freq):
        self.figure.ax.clear()
        self.figure.ax.set_xlim(max(0, min_freq - 10000), max_freq + 10000)

    def plot_signal(self, signal: RecordedSound):
        freq, fft = signal.fft_welch(0.005)
        self.figure.ax.plot(freq, fft)
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()


class PureTonesDataPlot:
    def __init__(self, num_amp: int, num_freqs: int):
        self.figure = MatplotlibWidget()
        self.data = np.zeros((num_amp, num_freqs, 3))
        self.init_plot()

    def init_plot(self):
        data = np.zeros((1, 1, 3))
        self.plot = self.figure.ax.imshow(data, cmap="viridis", interpolation="nearest")
        self.figure.fig.colorbar(self.plot, ax=self.figure.ax)

    def add_xx(self, xx):
        self.data[:, :, 0:2] = xx

    def add_point(self, amp, freq, data):
        self.data[amp, freq, 2] = data
        self.plot.set_data(self.data[:, :, 2])
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()


class PureTonesSignalsPlot:
    def __init__(self, num_amp: int, num_freqs: int):
        self.figure = MatplotlibWidget()
        self.data = np.zeros((num_amp, num_freqs, 2), dtype=RecordedSound)
        self._amp_index = 0
        self._freq_index = 0
        self.init_plot()

    def init_plot(self):
        self.figure.ax.clear()
        self.plot = []
        for i in range(2):
            (plot,) = self.figure.ax.plot([], [])
            self.plot.append(plot)

    def add_signal(self, amp: int, freq: int, signal: Sound, recording: RecordedSound):
        self.data[amp, freq, 0] = signal
        self.data[amp, freq, 1] = recording

    def plot_signal(self):
        if isinstance(
            self.data[self.amp_index, self.freq_index, 0], Sound
        ) and isinstance(self.data[self.amp_index, self.freq_index, 1], RecordedSound):
            self.plot[0].set_data(
                self.data[self.amp_index, self.freq_index, 0].time,
                self.data[self.amp_index, self.freq_index, 0].signal,
            )
            self.plot[1].set_data(
                self.data[self.amp_index, self.freq_index, 1].time,
                self.data[self.amp_index, self.freq_index, 1].signal,
            )
        self.figure.ax.relim()
        self.figure.ax.autoscale_view()
        self.figure.canvas.draw()

    @property
    def amp_index(self):
        return self._amp_index

    @amp_index.setter
    def amp_index(self, value: int):
        self._amp_index = value
        self.plot_signal()

    @property
    def freq_index(self):
        return self._freq_index

    @freq_index.setter
    def freq_index(self, value: int):
        self._freq_index = value
        self.plot_signal()
