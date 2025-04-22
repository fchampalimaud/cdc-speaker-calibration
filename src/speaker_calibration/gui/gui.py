import sys
import time

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator

from speaker_calibration.gui.layouts import (
    AdcLayout,
    FilterLayout,
    ProtocolLayout,
    SoundCardLayout,
)


class SettingsLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.soundcard = SoundCardLayout()
        self.adc = AdcLayout()
        self.filter = FilterLayout()
        self.protocol = ProtocolLayout()

        # FIXME
        self.mic_factor_l = QtWidgets.QLabel("Microphone Factor (V/Pa)")
        self.mic_factor = QtWidgets.QLineEdit()
        self.mic_factor.setValidator(QDoubleValidator())
        self.mic_factor.setText("0.41887")

        # FIXME
        self.reference_pressure_l = QtWidgets.QLabel("Reference Pressure (Pa)")
        self.reference_pressure = QtWidgets.QLineEdit()
        self.reference_pressure.setValidator(QDoubleValidator())
        self.reference_pressure.setText("0.00002")

        self.run = QtWidgets.QPushButton("Run")

        frame = QtWidgets.QFrame()
        frame.setFrameShape(QtWidgets.QFrame.HLine)
        frame.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Organize in layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.soundcard)
        self.layout.addWidget(self.adc)
        self.layout.addWidget(self.filter)
        self.layout.addWidget(self.protocol)

        self.setLayout(self.layout)


class PlotLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        self.layout.addWidget(NavigationToolbar(static_canvas, self))
        self.layout.addWidget(static_canvas)
        # TODO: add plot select

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")

        self.setLayout(self.layout)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)

        layout = QtWidgets.QHBoxLayout(self._main)

        plot_layout = PlotLayout()
        settings_layout = SettingsLayout()
        # settings_layout = SoundCardLayout()

        layout.addWidget(plot_layout)
        layout.addWidget(settings_layout)

        self.showMaximized()

    def _update_ydata(self):
        # Shift the sinusoid as a function of time.
        self.ydata = np.sin(self.xdata + time.time())

    def _update_canvas(self):
        self._line.set_data(self.xdata, self.ydata)
        # It should be safe to use the synchronous draw() method for most drawing
        # frequencies, but it is safer to use draw_idle().
        self._line.figure.canvas.draw_idle()


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
