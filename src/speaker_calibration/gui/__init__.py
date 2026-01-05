import ctypes
import sys
from typing import Literal, Optional

import nidaqmx
from PySide6.QtCore import QObject, Qt, QThread, QThreadPool, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from speaker_calibration.__main__ import run_calibration
from speaker_calibration.config import (
    Calibration,
    ComputerSoundCard,
    Config,
    EQFilter,
    Filter,
    HarpSoundCard,
    Moku,
    NiDaq,
    NoiseProtocolSettings,
    Paths,
    Test,
    PureToneProtocolSettings,
    PureToneCalibration,
    PureToneTest,
)
from speaker_calibration.gui.soundcard import SoundCardLayout
from speaker_calibration.gui.adc import ADCLayout
from speaker_calibration.gui.filter import FilterLayout
from speaker_calibration.gui.utils import (
    EQFilterPlot,
    NoiseDataPlot,
    NoiseSignalsPlot,
    PureTonesDataPlot,
    PureTonesSignalsPlot,
)

myappid = "fchampalimaud.cdc.speaker_calibration"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class SettingsLayout(QWidget):
    WIDGETS_WIDTH = 85
    LABEL_WIDTH = 170

    def __init__(self):
        super().__init__()

        self.vlayout = QVBoxLayout()

        self.sc = SoundCardLayout()
        self.vlayout.addWidget(self.sc)

        self.adc = ADCLayout()
        self.vlayout.addWidget(self.adc)

        self.filter = FilterLayout()
        self.vlayout.addWidget(self.filter)

        self.generate_protocol_layout()
        self.generate_eq_filter_layout()
        self.generate_calibration_layout()
        self.generate_test_layout()

        self.run = QPushButton("Run")
        self.vlayout.addWidget(self.run)

        self.setLayout(self.vlayout)

        self.on_sound_type_changed(0)

    def generate_protocol_layout(self):
        protocol_gb = QGroupBox("Protocol")
        form = QFormLayout()

        self.sound_type_l = QLabel("Sound Type")
        self.sound_type_l.setFixedWidth(self.LABEL_WIDTH)
        self.sound_type = QComboBox()
        self.sound_type.addItems(["Noise", "Pure Tones"])
        self.sound_type.setCurrentIndex(0)
        self.sound_type.setFixedWidth(self.WIDGETS_WIDTH)
        self.sound_type.currentIndexChanged.connect(self.on_sound_type_changed)

        self.ramp_time = QDoubleSpinBox()
        self.ramp_time.setMinimum(0)
        self.ramp_time.setDecimals(3)
        self.ramp_time.setSingleStep(0.005)
        self.ramp_time.setValue(0.005)
        self.ramp_time.setFixedWidth(self.WIDGETS_WIDTH)

        self.min_freq_l = QLabel("Minimum Frequency (Hz)")
        self.min_freq = QSpinBox()
        self.min_freq.setRange(0, 80000)
        self.min_freq.setValue(5000)
        self.min_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.max_freq_l = QLabel("Maximum Frequency (Hz)")
        self.max_freq = QSpinBox()
        self.max_freq.setRange(0, 80000)
        self.max_freq.setValue(20000)
        self.max_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.mic_factor = QDoubleSpinBox()
        self.mic_factor.setDecimals(5)
        self.mic_factor.setSingleStep(0.00001)
        self.mic_factor.setValue(0.41887)

        self.reference_pressure = QDoubleSpinBox()
        self.reference_pressure.setDecimals(6)
        self.reference_pressure.setValue(0.00002)
        self.reference_pressure.setSingleStep(0.000005)

        form.addRow(self.sound_type_l, self.sound_type)
        form.addRow("Ramp Time (s)", self.ramp_time)
        form.addRow(self.min_freq_l, self.min_freq)
        form.addRow(self.max_freq_l, self.max_freq)
        form.addRow("Microphone Factor (V/Pa)", self.mic_factor)
        form.addRow("Reference Pressure (Pa)", self.reference_pressure)

        protocol_gb.setLayout(form)
        self.vlayout.addWidget(protocol_gb)

    def generate_eq_filter_layout(self):
        self.eq_filter_gb = QGroupBox("EQ Filter")
        form = QFormLayout()

        self.eq_duration_l = QLabel("Sound Duration (s)")
        self.eq_duration_l.setFixedWidth(self.LABEL_WIDTH)
        self.eq_duration = QDoubleSpinBox()
        self.eq_duration.setSingleStep(0.01)
        self.eq_duration.setMinimum(0)
        self.eq_duration.setDecimals(3)
        self.eq_duration.setSingleStep(0.005)
        self.eq_duration.setValue(15)
        self.eq_duration.setFixedWidth(self.WIDGETS_WIDTH)

        self.time_const_l = QLabel("Time Constant (s)")
        self.time_const = QDoubleSpinBox()
        self.time_const.setMinimum(0)
        self.time_const.setDecimals(3)
        self.time_const.setSingleStep(0.005)
        self.time_const.setValue(0.100)
        self.time_const.setFixedWidth(self.WIDGETS_WIDTH)

        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0, 1)
        self.amplitude.setValue(0.9)
        self.amplitude.setSingleStep(0.01)
        self.amplitude.setFixedWidth(self.WIDGETS_WIDTH)

        self.min_boost_db = QDoubleSpinBox()
        self.min_boost_db.setRange(-100, 100)
        self.min_boost_db.setValue(-24)
        self.min_boost_db.setSingleStep(0.1)
        self.min_boost_db.setFixedWidth(self.WIDGETS_WIDTH)

        self.max_boost_db = QDoubleSpinBox()
        self.max_boost_db.setRange(-100, 100)
        self.max_boost_db.setValue(12)
        self.max_boost_db.setSingleStep(0.1)
        self.max_boost_db.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.eq_duration_l, self.eq_duration)
        form.addRow(self.time_const_l, self.time_const)
        form.addRow("Amplitude", self.amplitude)
        form.addRow("Min Boost dB", self.min_boost_db)
        form.addRow("Max Boost dB", self.max_boost_db)

        self.eq_filter_gb.setLayout(form)
        self.vlayout.addWidget(self.eq_filter_gb)

    def generate_calibration_layout(self):
        calibrate_gb = QGroupBox("Calibration")
        form = QFormLayout()

        self.calib_duration_l = QLabel("Sound Duration (s)")
        self.calib_duration_l.setFixedWidth(self.LABEL_WIDTH)
        self.calib_duration = QDoubleSpinBox()
        self.calib_duration.setSingleStep(0.01)
        self.calib_duration.setMinimum(0)
        self.calib_duration.setDecimals(3)
        self.calib_duration.setSingleStep(0.005)
        self.calib_duration.setValue(10)
        self.calib_duration.setFixedWidth(self.WIDGETS_WIDTH)

        self.calib_min_freq_l = QLabel("Minimum Frequency (Hz)")
        self.calib_min_freq = QSpinBox()
        self.calib_min_freq.setRange(0, 80000)
        self.calib_min_freq.setValue(5000)
        self.calib_min_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.calib_max_freq_l = QLabel("Maximum Frequency (Hz)")
        self.calib_max_freq = QSpinBox()
        self.calib_max_freq.setRange(0, 80000)
        self.calib_max_freq.setValue(20000)
        self.calib_max_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.calib_freq_steps_l = QLabel("Frequency Steps")
        self.calib_freq_steps = QSpinBox()
        self.calib_freq_steps.setMinimum(0)
        self.calib_freq_steps.setValue(10)
        self.calib_freq_steps.setFixedWidth(self.WIDGETS_WIDTH)

        self.min_att_l = QLabel("Minimum Attenuation")
        self.min_att = QDoubleSpinBox()
        self.min_att.setSingleStep(0.01)
        self.min_att.setRange(-10, 0)
        self.min_att.setValue(-0.1)
        self.min_att.setFixedWidth(self.WIDGETS_WIDTH)

        self.max_att_l = QLabel("Maximum Attenuation")
        self.max_att = QDoubleSpinBox()
        self.max_att.setSingleStep(0.01)
        self.max_att.setRange(-10, 0)
        self.max_att.setValue(-1)
        self.max_att.setFixedWidth(self.WIDGETS_WIDTH)

        self.att_steps_l = QLabel("Attenuation Steps")
        self.att_steps = QSpinBox()
        self.att_steps.setMinimum(2)
        self.att_steps.setValue(12)
        self.att_steps.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.calib_duration_l, self.calib_duration)
        form.addRow(self.calib_min_freq_l, self.calib_min_freq)
        form.addRow(self.calib_max_freq_l, self.calib_max_freq)
        form.addRow(self.calib_freq_steps_l, self.calib_freq_steps)
        form.addRow(self.min_att_l, self.min_att)
        form.addRow(self.max_att_l, self.max_att)
        form.addRow(self.att_steps_l, self.att_steps)

        calibrate_gb.setLayout(form)
        self.vlayout.addWidget(calibrate_gb)

    def generate_test_layout(self):
        test_gb = QGroupBox("Test Calibration")
        form = QFormLayout()

        self.test_l = QLabel("Test")
        self.test_l.setFixedWidth(self.LABEL_WIDTH)
        self.test = QCheckBox()
        self.test.setChecked(True)
        self.test.stateChanged.connect(self.on_test_changed)

        self.test_duration_l = QLabel("Sound Duration (s)")
        self.test_duration_l.setFixedWidth(self.LABEL_WIDTH)
        self.test_duration = QDoubleSpinBox()
        self.test_duration.setSingleStep(0.01)
        self.test_duration.setMinimum(0)
        self.test_duration.setDecimals(3)
        self.test_duration.setSingleStep(0.005)
        self.test_duration.setValue(10)
        self.test_duration.setFixedWidth(self.WIDGETS_WIDTH)

        self.test_min_freq_l = QLabel("Minimum Frequency (Hz)")
        self.test_min_freq = QSpinBox()
        self.test_min_freq.setRange(0, 80000)
        self.test_min_freq.setValue(5000)
        self.test_min_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.test_max_freq_l = QLabel("Maximum Frequency (Hz)")
        self.test_max_freq = QSpinBox()
        self.test_max_freq.setRange(0, 80000)
        self.test_max_freq.setValue(20000)
        self.test_max_freq.setFixedWidth(self.WIDGETS_WIDTH)

        self.test_freq_steps_l = QLabel("Frequency Steps")
        self.test_freq_steps = QSpinBox()
        self.test_freq_steps.setMinimum(2)
        self.test_freq_steps.setValue(10)
        self.test_freq_steps.setFixedWidth(self.WIDGETS_WIDTH)

        self.min_db_l = QLabel("Minimum dB SPL")
        self.min_db = QDoubleSpinBox()
        self.min_db.setSingleStep(0.01)
        self.min_db.setMinimum(0)
        self.min_db.setValue(30)
        self.min_db.setFixedWidth(self.WIDGETS_WIDTH)

        self.max_db_l = QLabel("Maximum dB SPL")
        self.max_db = QDoubleSpinBox()
        self.max_db.setSingleStep(0.01)
        self.max_db.setMinimum(0)
        self.max_db.setValue(68)
        self.max_db.setFixedWidth(self.WIDGETS_WIDTH)

        self.db_steps_l = QLabel("dB SPL Steps")
        self.db_steps = QSpinBox()
        self.db_steps.setMinimum(2)
        self.db_steps.setValue(7)
        self.db_steps.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.test_l, self.test)
        form.addRow(self.test_duration_l, self.test_duration)
        form.addRow(self.test_min_freq_l, self.test_min_freq)
        form.addRow(self.test_max_freq_l, self.test_max_freq)
        form.addRow(self.test_freq_steps_l, self.test_freq_steps)
        form.addRow(self.min_db_l, self.min_db)
        form.addRow(self.max_db_l, self.max_db)
        form.addRow(self.db_steps_l, self.db_steps)

        test_gb.setLayout(form)
        self.vlayout.addWidget(test_gb)

    def on_sound_type_changed(self, index):
        if self.sound_type.currentText() == "Noise":
            self.eq_filter_gb.show()
            self.min_freq_l.show()
            self.min_freq.show()
            self.max_freq_l.show()
            self.max_freq.show()
            self.calib_min_freq_l.hide()
            self.calib_min_freq.hide()
            self.calib_max_freq_l.hide()
            self.calib_max_freq.hide()
            self.calib_freq_steps_l.hide()
            self.calib_freq_steps.hide()
            self.test_min_freq_l.hide()
            self.test_min_freq.hide()
            self.test_max_freq_l.hide()
            self.test_max_freq.hide()
            self.test_freq_steps_l.hide()
            self.test_freq_steps.hide()
            self.adjustSize()
            self.min_att.setRange(-10, 0)
            self.min_att.setValue(-0.1)
            self.max_att.setRange(-10, 0)
            self.max_att.setValue(-1)
        else:
            self.eq_filter_gb.hide()
            self.min_freq_l.hide()
            self.min_freq.hide()
            self.max_freq_l.hide()
            self.max_freq.hide()
            self.calib_min_freq_l.show()
            self.calib_min_freq.show()
            self.calib_max_freq_l.show()
            self.calib_max_freq.show()
            self.calib_freq_steps_l.show()
            self.calib_freq_steps.show()
            if self.test.isChecked():
                self.test_min_freq_l.show()
                self.test_min_freq.show()
                self.test_max_freq_l.show()
                self.test_max_freq.show()
                self.test_freq_steps_l.show()
                self.test_freq_steps.show()
            self.adjustSize()
            self.min_att.setRange(0, 1)
            self.min_att.setValue(0.1)
            self.max_att.setRange(0, 1)
            self.max_att.setValue(1)

    def on_eq_filter_changed(self, state):
        if state:
            self.eq_duration_l.setVisible(True)
            self.eq_duration.setVisible(True)
            self.time_const_l.setVisible(True)
            self.time_const.setVisible(True)
            self.adjustSize()
        else:
            self.eq_duration_l.setVisible(False)
            self.eq_duration.setVisible(False)
            self.time_const_l.setVisible(False)
            self.time_const.setVisible(False)
            self.adjustSize()

    def on_calibration_changed(self, state):
        if state:
            self.calib_duration_l.setVisible(True)
            self.calib_duration.setVisible(True)
            self.min_att_l.setVisible(True)
            self.min_att.setVisible(True)
            self.max_att_l.setVisible(True)
            self.max_att.setVisible(True)
            self.att_steps_l.setVisible(True)
            self.att_steps.setVisible(True)
            self.adjustSize()
            if self.sound_type.currentText() == "Pure Tones":
                self.calib_min_freq_l.setVisible(True)
                self.calib_min_freq.setVisible(True)
                self.calib_max_freq_l.setVisible(True)
                self.calib_max_freq.setVisible(True)
                self.calib_freq_steps_l.setVisible(True)
                self.calib_freq_steps.setVisible(True)
        else:
            self.calib_duration_l.setVisible(False)
            self.calib_duration.setVisible(False)
            self.calib_min_freq_l.setVisible(False)
            self.calib_min_freq.setVisible(False)
            self.calib_max_freq_l.setVisible(False)
            self.calib_max_freq.setVisible(False)
            self.calib_freq_steps_l.setVisible(False)
            self.calib_freq_steps.setVisible(False)
            self.min_att_l.setVisible(False)
            self.min_att.setVisible(False)
            self.max_att_l.setVisible(False)
            self.max_att.setVisible(False)
            self.att_steps_l.setVisible(False)
            self.att_steps.setVisible(False)
            self.adjustSize()

    def on_test_changed(self, state):
        if state:
            self.test_duration_l.setVisible(True)
            self.test_duration.setVisible(True)
            self.min_db_l.setVisible(True)
            self.min_db.setVisible(True)
            self.max_db_l.setVisible(True)
            self.max_db.setVisible(True)
            self.db_steps_l.setVisible(True)
            self.db_steps.setVisible(True)
            if self.sound_type.currentText() == "Pure Tones":
                self.test_min_freq_l.setVisible(True)
                self.test_min_freq.setVisible(True)
                self.test_max_freq_l.setVisible(True)
                self.test_max_freq.setVisible(True)
                self.test_freq_steps_l.setVisible(True)
                self.test_freq_steps.setVisible(True)
            self.adjustSize()
        else:
            self.test_duration_l.setVisible(False)
            self.test_duration.setVisible(False)
            self.test_min_freq_l.setVisible(False)
            self.test_min_freq.setVisible(False)
            self.test_max_freq_l.setVisible(False)
            self.test_max_freq.setVisible(False)
            self.test_freq_steps_l.setVisible(False)
            self.test_freq_steps.setVisible(False)
            self.min_db_l.setVisible(False)
            self.min_db.setVisible(False)
            self.max_db_l.setVisible(False)
            self.max_db.setVisible(False)
            self.db_steps_l.setVisible(False)
            self.db_steps.setVisible(False)
            self.adjustSize()


class PlotLayout(QWidget):
    WIDGETS_WIDTH = 160
    LABEL_WIDTH = 30

    def __init__(self):
        super().__init__()

        self.vlayout = QVBoxLayout()

        self.fig = QStackedWidget()
        self.vlayout.addWidget(self.fig)

        # self.create_dictionary()
        self.generate_selection()

        self.setLayout(self.vlayout)

        self.thread_pool = QThreadPool.globalInstance()

    def create_dictionary(
        self,
        type: Literal["Noise", "Pure Tones"],
        num_amp: Optional[int] = None,
        num_freqs: Optional[int] = None,
        num_db: Optional[int] = None,
        num_test_freqs: Optional[int] = None,
        min_freq=None,
        max_freq=None,
    ):
        while self.plot_selection.count() > 0:
            self.plot_selection.removeItem(0)

        while self.fig.count() > 0:
            self.fig.removeWidget(self.fig.currentWidget())

        if type == "Noise":
            self.plots = {
                "Calibration Data": NoiseDataPlot(num_amp),
                "Calibration Signals": NoiseSignalsPlot(min_freq, max_freq),
                "Test Data": NoiseDataPlot(num_db),
                "Test Signals": NoiseSignalsPlot(min_freq, max_freq),
                "EQ Filter": EQFilterPlot(),
            }
            self.fig.addWidget(self.plots["Calibration Data"].figure)
            self.fig.addWidget(self.plots["Calibration Signals"].figure)
            self.fig.addWidget(self.plots["Test Data"].figure)
            self.fig.addWidget(self.plots["Test Signals"].figure)
            self.fig.addWidget(self.plots["EQ Filter"].figure)
        else:
            self.plots = {
                "Calibration Data": PureTonesDataPlot(num_amp, num_freqs),
                "Calibration Signals": PureTonesSignalsPlot(num_amp, num_freqs),
                "Test Data": PureTonesDataPlot(num_db, num_test_freqs),
                "Test Signals": PureTonesSignalsPlot(num_db, num_test_freqs),
            }
            self.fig.addWidget(self.plots["Calibration Data"].figure)
            self.fig.addWidget(self.plots["Calibration Signals"].figure)
            self.fig.addWidget(self.plots["Test Data"].figure)
            self.fig.addWidget(self.plots["Test Signals"].figure)

        self.plot_selection.addItems(self.plots.keys())

    def generate_selection(self):
        layout = QHBoxLayout()

        self.plot_l = QLabel("Plot: ")
        self.plot_l.setFixedWidth(self.LABEL_WIDTH)
        self.plot_selection = QComboBox()
        self.plot_selection.setFixedWidth(self.WIDGETS_WIDTH)

        layout.addWidget(self.plot_l)
        layout.addWidget(self.plot_selection, alignment=Qt.AlignmentFlag.AlignLeft)

        self.vlayout.addLayout(layout)

    def calibration_callback(self, code: str, *args):
        if code == "EQ Filter":
            self.plots["EQ Filter"].add_data(*args)
        elif code == "Pre-calibration":
            self.plots["Calibration Data"].add_xx(*args)
        elif code == "Noise Calibration":
            self.plots["Calibration Data"].add_point(
                args[0], args[1].calculate_db_spl()
            )
            self.plots["Calibration Signals"].plot_signal(args[1])
        elif code == "Pure Tone Calibration":
            self.plots["Calibration Data"].add_point(
                args[0], args[1], args[3].calculate_db_spl()
            )
            self.plots["Calibration Signals"].add_signal(
                args[0], args[1], args[2], args[3]
            )
        elif code == "Pre-test":
            self.plots["Test Data"].add_xx(*args, True)
        elif code == "Noise Test":
            self.plots["Test Data"].add_point(args[0], args[1].calculate_db_spl())
            self.plots["Test Signals"].plot_signal(args[1])
        elif code == "Pure Tone Test":
            self.plots["Test Data"].add_point(
                args[0], args[1], args[3].calculate_db_spl()
            )
            self.plots["Test Signals"].add_signal(args[0], args[1], args[2], args[3])


class ApplicationWindow(QMainWindow):
    work_requested = Signal()

    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.setWindowTitle("Speaker Calibration")
        self.setWindowIcon(QIcon("docs/img/favicon.ico"))

        layout = QHBoxLayout(self._main)

        self.plot = PlotLayout()
        self.config = SettingsLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.config)
        scroll_area.setFixedWidth(320)

        self.config.run.clicked.connect(self.run_calibration)
        self.plot.plot_selection.currentIndexChanged.connect(self.switch_plots)

        layout.addWidget(self.plot)
        layout.addWidget(scroll_area)

        self.showMaximized()

    def run_calibration(self):
        if self.config.sc.is_harp.isChecked():
            if self.config.sc.serial_port.currentText() == "":
                QMessageBox.warning(
                    self,
                    "Warning",
                    "The Harp SoundCard is not connected. Please turn it on.",
                )
                return

            soundcard = HarpSoundCard(
                serial_port=self.config.sc.serial_port.currentText(),
                fs=int(self.config.sc.fs_harp.currentText()),
                speaker=self.config.sc.convert_speaker(),
            )
        else:
            soundcard = ComputerSoundCard(
                soundcard_name="",  # FIXME
                fs=self.config.sc.serial_port.fs_computer.value(),
                speaker=self.config.sc.convert_speaker(),
            )

        match self.config.adc.adc.currentText():
            case "NI-DAQ":
                if not self.nidaqmx_available():
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "The NI-DAQ is not connected. Please turn it on.",
                    )
                    return

                adc = NiDaq(
                    fs=self.config.adc.fs_adc.value(),
                    device_id=self.config.adc.device_id.value(),
                    channel=self.config.adc.channel.value(),
                )
            case "Moku":
                adc = Moku(
                    fs=self.config.adc.fs_adc.value(),
                    address=self.config.adc.address.text(),
                    channel=self.config.adc.channel.value(),
                )

        filt = Filter(
            filter_input=self.config.filter.filter_input.isChecked(),
            filter_acquisition=self.config.filter.filter_acquisition.isChecked(),
            min_freq=self.config.filter.min_freq_filt.value(),
            max_freq=self.config.filter.max_freq_filt.value(),
        )

        match self.config.sound_type.currentText():
            case "Noise":
                eq_filter = EQFilter(
                    sound_duration=self.config.eq_duration.value(),
                    time_constant=self.config.time_const.value(),
                    amplitude=self.config.amplitude.value(),
                    min_boost_db=self.config.min_boost_db.value(),
                    max_boost_db=self.config.max_boost_db.value(),
                )

                calibration = Calibration(
                    sound_duration=self.config.calib_duration.value(),
                    min_amp=self.config.min_att.value(),
                    max_amp=self.config.max_att.value(),
                    amp_steps=self.config.att_steps.value(),
                )

                if self.config.test.isChecked():
                    test = Test(
                        sound_duration=self.config.test_duration.value(),
                        min_db=self.config.min_db.value(),
                        max_db=self.config.max_db.value(),
                        db_steps=self.config.db_steps.value(),
                    )
                else:
                    test = None

                protocol = NoiseProtocolSettings(
                    min_freq=self.config.min_freq.value(),
                    max_freq=self.config.max_freq.value(),
                    mic_factor=self.config.mic_factor.value(),
                    reference_pressure=self.config.reference_pressure.value(),
                    ramp_time=self.config.ramp_time.value(),
                    eq_filter=eq_filter,
                    calibration=calibration,
                    test=test,
                    filter=filt,
                )
            case "Pure Tones":
                calibration = PureToneCalibration(
                    sound_duration=self.config.calib_duration.value(),
                    min_freq=self.config.calib_min_freq.value(),
                    max_freq=self.config.calib_max_freq.value(),
                    freq_steps=self.config.calib_freq_steps.value(),
                    min_amp=self.config.min_att.value(),
                    max_amp=self.config.max_att.value(),
                    amp_steps=self.config.att_steps.value(),
                )

                if self.config.test.isChecked():
                    test = PureToneTest(
                        sound_duration=self.config.test_duration.value(),
                        min_freq=self.config.test_min_freq.value(),
                        max_freq=self.config.test_max_freq.value(),
                        freq_steps=self.config.test_freq_steps.value(),
                        min_db=self.config.min_db.value(),
                        max_db=self.config.max_db.value(),
                        db_steps=self.config.db_steps.value(),
                    )
                else:
                    test = None

                protocol = PureToneProtocolSettings(
                    mic_factor=self.config.mic_factor.value(),
                    reference_pressure=self.config.reference_pressure.value(),
                    ramp_time=self.config.ramp_time.value(),
                    calibration=calibration,
                    test=test,
                    filter=filt,
                )

        self.settings = Config(
            soundcard=soundcard,
            adc=adc,
            protocol=protocol,
            paths=Paths(output="output"),
        )

        self.plot.create_dictionary(
            self.config.sound_type.currentText(),
            num_amp=self.config.att_steps.value(),
            num_freqs=self.config.calib_freq_steps.value(),
            num_db=self.config.db_steps.value(),
            num_test_freqs=self.config.test_freq_steps.value(),
            min_freq=self.config.filter.min_freq_filt.value(),
            max_freq=self.config.filter.max_freq_filt.value(),
        )

        self.worker_thread = QThread()
        self.worker = Worker(self.settings, self.plot.calibration_callback)
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.on_task_finished)
        self.work_requested.connect(self.worker.run)
        self.worker_thread.start()

        self.work_requested.emit()

        self.config.run.setEnabled(False)

    def nidaqmx_available(self) -> bool:
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(
                    "Dev1/ai0", min_val=-10.0, max_val=10.0
                )
                task.read()
            return True
        except Exception:
            return False

    def switch_plots(self, index=None):
        match self.plot.plot_selection.currentText():
            case "Calibration Data":
                self.plot.fig.setCurrentIndex(0)
            case "Calibration Signals":
                self.plot.fig.setCurrentIndex(1)
            case "Test Data":
                self.plot.fig.setCurrentIndex(2)
            case "Test Signals":
                self.plot.fig.setCurrentIndex(3)
            case "EQ Filter":
                self.plot.fig.setCurrentIndex(4)

    def on_task_finished(self):
        self.config.run.setEnabled(True)
        self.worker_thread.quit()

    def closeEvent(self, event):
        if hasattr(self, "worker_thread"):
            self.worker_thread.quit()
        event.accept()  # Accept the close event


class Worker(QObject):
    finished = Signal()

    def __init__(self, config, calibration_callback):
        super(Worker, self).__init__()
        self.config = config
        self.calibration_callback = calibration_callback

    @Slot()
    def run(self):
        run_calibration(self.config, self.calibration_callback)
        self.finished.emit()


def main():
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
