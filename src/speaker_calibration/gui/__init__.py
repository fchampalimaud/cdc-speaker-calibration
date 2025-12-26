import ctypes
import sys
from typing import Literal, Optional

import nidaqmx
from harp.devices.soundcard import SoundCard as HSC
from harp.protocol.exceptions import HarpTimeoutError
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
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from serial import SerialException

from speaker_calibration.__main__ import main
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
)
from speaker_calibration.gui.utils import (
    EQFilterPlot,
    NoiseDataPlot,
    NoiseSignalsPlot,
    PureTonesDataPlot,
    PureTonesSignalsPlot,
    get_ports,
)

myappid = "fchampalimaud.cdc.speaker_calibration"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class SettingsLayout(QWidget):
    WIDGETS_WIDTH = 85
    LABEL_WIDTH = 170

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.generate_soundcard_layout()
        self.generate_adc_layout()
        self.generate_filter_layout()
        self.generate_protocol_layout()
        self.generate_eq_filter_layout()
        self.generate_calibration_layout()
        self.generate_test_layout()

        self.run = QPushButton("Run")
        self.layout.addWidget(self.run)

        self.setLayout(self.layout)

        self.on_is_harp_changed(True)
        self.on_adc_changed(True)
        self.on_sound_type_changed(0)

    def generate_soundcard_layout(self):
        soundcard_gb = QGroupBox("Soundcard")
        form = QFormLayout()

        self.is_harp = QCheckBox()
        self.is_harp.setChecked(True)
        self.is_harp.stateChanged.connect(self.on_is_harp_changed)

        self.serial_port_l = QLabel("Serial Port")
        self.serial_port_l.setFixedWidth(self.LABEL_WIDTH)
        self.serial_port = QComboBox()
        self.serial_port.setPlaceholderText("COMx")
        self.serial_port.addItems(get_ports())
        self.serial_port.setFixedWidth(self.WIDGETS_WIDTH)
        self.serial_port.currentIndexChanged.connect(self.connect_soundcard)

        self.fs_harp_l = QLabel("Sampling Frequency (Hz)")
        self.fs_harp = QComboBox()
        self.fs_harp.addItems(["96000", "192000"])
        self.fs_harp.setCurrentIndex(1)
        self.fs_harp.setFixedWidth(self.WIDGETS_WIDTH)

        self.fs_computer_l = QLabel("Sampling Frequency (Hz)")
        self.fs_computer_l.setFixedWidth(self.LABEL_WIDTH)
        self.fs_computer = QSpinBox()
        self.fs_computer.setRange(1, 48000)
        self.fs_computer.setValue(48000)
        self.fs_computer.setFixedWidth(self.WIDGETS_WIDTH)

        self.speaker_l = QLabel("Speaker")
        self.speaker_l.setFixedWidth(self.LABEL_WIDTH)
        self.speaker = QComboBox()
        self.speaker.addItems(["Left", "Right"])
        self.speaker.setCurrentIndex(0)
        self.speaker.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow("Harp SoundCard", self.is_harp)
        form.addRow(self.serial_port_l, self.serial_port)
        form.addRow(self.fs_harp_l, self.fs_harp)
        form.addRow(self.fs_computer_l, self.fs_computer)
        form.addRow(self.speaker_l, self.speaker)

        soundcard_gb.setLayout(form)
        self.layout.addWidget(soundcard_gb)

    def generate_adc_layout(self):
        adc_gb = QGroupBox("ADC")
        form = QFormLayout()

        self.adc_l = QLabel("ADC")
        self.adc_l.setFixedWidth(self.LABEL_WIDTH)
        self.adc = QComboBox()
        self.adc.addItems(["NI-DAQ", "Moku:Go"])
        self.adc.setCurrentIndex(0)
        self.adc.setFixedWidth(self.WIDGETS_WIDTH)
        self.adc.currentIndexChanged.connect(self.on_adc_changed)

        self.fs_adc = QSpinBox()
        self.fs_adc.setRange(1, 250000)
        self.fs_adc.setValue(250000)
        self.fs_adc.setFixedWidth(self.WIDGETS_WIDTH)

        self.device_id_l = QLabel("Device ID")
        self.device_id_l.setFixedWidth(self.LABEL_WIDTH)
        self.device_id = QSpinBox()
        self.device_id.setMinimum(1)
        self.device_id.setFixedWidth(self.WIDGETS_WIDTH)

        self.address_l = QLabel("Device Address")
        self.address = QLineEdit()

        self.channel = QSpinBox()
        self.channel.setRange(0, 7)
        self.channel.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.adc_l, self.adc)
        form.addRow("ADC Sampling Frequency (Hz)", self.fs_adc)
        form.addRow(self.device_id_l, self.device_id)
        form.addRow(self.address_l, self.address)
        form.addRow("Channel", self.channel)

        adc_gb.setLayout(form)
        self.layout.addWidget(adc_gb)

    def generate_filter_layout(self):
        filter_gb = QGroupBox("Filter")
        form = QFormLayout()

        self.filter_input_l = QLabel("Filter Input")
        self.filter_input_l.setFixedWidth(self.LABEL_WIDTH)
        self.filter_input = QCheckBox()
        self.filter_input.setChecked(True)
        self.filter_input.stateChanged.connect(self.on_filter_changed)

        self.filter_acquisition = QCheckBox()
        self.filter_acquisition.setChecked(True)
        self.filter_acquisition.stateChanged.connect(self.on_filter_changed)

        self.min_freq_filt_l = QLabel("Minimum Frequency (Hz)")
        self.min_freq_filt_l.setFixedWidth(self.LABEL_WIDTH)
        self.min_freq_filt = QSpinBox()
        self.min_freq_filt.setRange(0, 80000)
        self.min_freq_filt.setValue(5000)
        self.min_freq_filt.setFixedWidth(self.WIDGETS_WIDTH)

        self.max_freq_filt_l = QLabel("Maximum Frequency (Hz)")
        self.max_freq_filt = QSpinBox()
        self.max_freq_filt.setRange(0, 80000)
        self.max_freq_filt.setValue(20000)
        self.max_freq_filt.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.filter_input_l, self.filter_input)
        form.addRow("Filter Acquisition", self.filter_acquisition)
        form.addRow(self.min_freq_filt_l, self.min_freq_filt)
        form.addRow(self.max_freq_filt_l, self.max_freq_filt)

        filter_gb.setLayout(form)
        self.layout.addWidget(filter_gb)

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

        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0, 1)
        self.amplitude.setValue(0.9)
        self.amplitude.setSingleStep(0.01)
        self.amplitude.setFixedWidth(self.WIDGETS_WIDTH)

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
        form.addRow("Amplitude", self.amplitude)
        form.addRow("Ramp Time (s)", self.ramp_time)
        form.addRow(self.min_freq_l, self.min_freq)
        form.addRow(self.max_freq_l, self.max_freq)
        form.addRow("Microphone Factor (V/Pa)", self.mic_factor)
        form.addRow("Reference Pressure (Pa)", self.reference_pressure)

        protocol_gb.setLayout(form)
        self.layout.addWidget(protocol_gb)

    def generate_eq_filter_layout(self):
        self.eq_filter_gb = QGroupBox("EQ Filter")
        form = QFormLayout()

        self.eq_filter_l = QLabel("Determine Filter")
        self.eq_filter_l.setFixedWidth(self.LABEL_WIDTH)
        self.eq_filter = QCheckBox()
        self.eq_filter.setChecked(True)
        self.eq_filter.stateChanged.connect(self.on_eq_filter_changed)

        self.if_duration_l = QLabel("Sound Duration (s)")
        self.if_duration_l.setFixedWidth(self.LABEL_WIDTH)
        self.if_duration = QDoubleSpinBox()
        self.if_duration.setSingleStep(0.01)
        self.if_duration.setMinimum(0)
        self.if_duration.setDecimals(3)
        self.if_duration.setSingleStep(0.005)
        self.if_duration.setValue(15)
        self.if_duration.setFixedWidth(self.WIDGETS_WIDTH)

        self.time_const_l = QLabel("Time Constant (s)")
        self.time_const = QDoubleSpinBox()
        self.time_const.setMinimum(0)
        self.time_const.setDecimals(3)
        self.time_const.setSingleStep(0.005)
        self.time_const.setValue(0.100)
        self.time_const.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.eq_filter_l, self.eq_filter)
        form.addRow(self.if_duration_l, self.if_duration)
        form.addRow(self.time_const_l, self.time_const)

        self.eq_filter_gb.setLayout(form)
        self.layout.addWidget(self.eq_filter_gb)

    def generate_calibration_layout(self):
        calibrate_gb = QGroupBox("Calibrate")
        form = QFormLayout()

        self.calibrate_l = QLabel("Calibrate")
        self.calibrate_l.setFixedWidth(self.LABEL_WIDTH)
        self.calibrate = QCheckBox()
        self.calibrate.setChecked(True)
        self.calibrate.stateChanged.connect(self.on_calibration_changed)

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
        self.att_steps.setValue(15)
        self.att_steps.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.calibrate_l, self.calibrate)
        form.addRow(self.calib_duration_l, self.calib_duration)
        form.addRow(self.calib_min_freq_l, self.calib_min_freq)
        form.addRow(self.calib_max_freq_l, self.calib_max_freq)
        form.addRow(self.calib_freq_steps_l, self.calib_freq_steps)
        form.addRow(self.min_att_l, self.min_att)
        form.addRow(self.max_att_l, self.max_att)
        form.addRow(self.att_steps_l, self.att_steps)

        calibrate_gb.setLayout(form)
        self.layout.addWidget(calibrate_gb)

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
        self.db_steps.setValue(5)
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
        self.layout.addWidget(test_gb)

    def on_is_harp_changed(self, state):
        if state:
            self.serial_port.setVisible(True)
            self.serial_port_l.setVisible(True)
            self.fs_harp.setVisible(True)
            self.fs_harp_l.setVisible(True)
            self.fs_computer.setVisible(False)
            self.fs_computer_l.setVisible(False)
            # self.adjustSize()
        else:
            self.serial_port.setVisible(False)
            self.serial_port_l.setVisible(False)
            self.fs_harp.setVisible(False)
            self.fs_harp_l.setVisible(False)
            self.fs_computer.setVisible(True)
            self.fs_computer_l.setVisible(True)
            # self.adjustSize()

    def on_adc_changed(self, index):
        if self.adc.currentText() == "NI-DAQ":
            self.device_id_l.show()
            self.device_id.show()
            self.address_l.hide()
            self.address.hide()
            self.fs_adc.setRange(1, 250000)
            self.fs_adc.setValue(250000)
            self.channel.setRange(0, 7)
            self.channel.setValue(1)
            self.adjustSize()
        else:
            self.device_id_l.hide()
            self.device_id.hide()
            self.address_l.show()
            self.address.show()
            self.fs_adc.setRange(1, 500000)
            self.fs_adc.setValue(500000)
            self.channel.setRange(1, 2)
            self.channel.setValue(1)
            self.adjustSize()

    def on_filter_changed(self, state):
        if self.filter_input.isChecked() or self.filter_acquisition.isChecked():
            self.min_freq_filt_l.show()
            self.min_freq_filt.show()
            self.max_freq_filt_l.show()
            self.max_freq_filt.show()
            self.adjustSize()
        else:
            self.min_freq_filt_l.hide()
            self.min_freq_filt.hide()
            self.max_freq_filt_l.hide()
            self.max_freq_filt.hide()
            self.adjustSize()

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
        else:
            self.eq_filter_gb.hide()
            self.min_freq_l.hide()
            self.min_freq.hide()
            self.max_freq_l.hide()
            self.max_freq.hide()
            if self.calibrate.isChecked():
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

    def on_eq_filter_changed(self, state):
        if state:
            self.if_duration_l.setVisible(True)
            self.if_duration.setVisible(True)
            self.time_const_l.setVisible(True)
            self.time_const.setVisible(True)
            self.adjustSize()
        else:
            self.if_duration_l.setVisible(False)
            self.if_duration.setVisible(False)
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
            self.test_min_freq_l.setVisible(True)
            self.test_min_freq.setVisible(True)
            self.test_max_freq_l.setVisible(True)
            self.test_max_freq.setVisible(True)
            self.test_freq_steps_l.setVisible(True)
            self.test_freq_steps.setVisible(True)
            self.min_db_l.setVisible(True)
            self.min_db.setVisible(True)
            self.max_db_l.setVisible(True)
            self.max_db.setVisible(True)
            self.db_steps_l.setVisible(True)
            self.db_steps.setVisible(True)
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

    def connect_soundcard(self, index):
        if (
            self.serial_port.currentText() == "Refresh"
            or self.serial_port.currentText() == ""
        ):
            self.serial_port.setCurrentIndex(-1)
            self.serial_port.clear()
            self.serial_port.addItems(get_ports())
            return

        try:
            soundcard = HSC(self.serial_port.currentText())
            soundcard.disconnect()
        except HarpTimeoutError:
            self.serial_port.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp device.")
        except SerialException:
            self.serial_port.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp device.")
        except Exception:
            self.serial_port.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp Soundcard.")


class PlotLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.fig = QStackedWidget()
        self.layout.addWidget(self.fig)

        # self.create_dictionary()
        self.generate_selection()

        self.setLayout(self.layout)

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
        self.plot_selection = QComboBox()

        self.amp_index_l = QLabel("Plot Index: ")
        self.amp_index = QSpinBox()

        self.freq_index_l = QLabel("Frequency Index: ")
        self.freq_index = QSpinBox()

        self.original = QRadioButton("Original Signal")
        self.recorded = QRadioButton("Recorded Sound")
        self.both = QRadioButton("Both")
        self.both.setChecked(True)

        layout.addWidget(self.plot_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.plot_selection)
        layout.addWidget(self.amp_index_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.amp_index)
        layout.addWidget(self.freq_index_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.freq_index)
        layout.addWidget(self.original, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.recorded, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.both, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addLayout(layout)

    def calibration_callback(self, code: str, *args):
        if code == "EQ Filter":
            self.plots["EQ Filter"].add_data(*args)
        elif code == "Pre-calibration":
            self.plots["Calibration Data"].add_xx(*args)
        elif code == "Calibration":
            self.plots["Calibration Data"].add_point(
                args[0], args[1].calculate_db_spl()
            )
            self.plots["Calibration Signals"].plot_signal(args[1])
        elif code == "Pre-test":
            self.plots["Test Data"].add_xx(*args, True)
        elif code == "Test":
            self.plots["Test Data"].add_point(args[0], args[1].calculate_db_spl())
            self.plots["Test Signals"].plot_signal(args[1])


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
        self.settings_layout = SettingsLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.settings_layout)
        scroll_area.setFixedWidth(320)

        self.settings_layout.run.clicked.connect(self.run_calibration)
        self.plot.plot_selection.currentIndexChanged.connect(self.switch_plots)
        # self.plot.amp_index.valueChanged.connect(self.update_indexes)
        # self.plot.freq_index.valueChanged.connect(self.update_indexes)

        layout.addWidget(self.plot)
        layout.addWidget(scroll_area)

        self.showMaximized()

    def run_calibration(self):
        filt = Filter(
            filter_input=self.settings_layout.filter_input.isChecked(),
            filter_acquisition=self.settings_layout.filter_acquisition.isChecked(),
            min_freq=self.settings_layout.min_freq_filt.value(),
            max_freq=self.settings_layout.max_freq_filt.value(),
        )

        eq_filter = EQFilter(
            # determine_filter=self.settings_layout.eq_filter.isChecked(),
            sound_duration=self.settings_layout.if_duration.value(),
            time_constant=self.settings_layout.time_const.value(),
            amplitude=self.settings_layout.amplitude.value(),
        )

        calibration = Calibration(
            # calibrate=self.settings_layout.calibrate.isChecked(),
            sound_duration=self.settings_layout.calib_duration.value(),
            min_amp=self.settings_layout.min_att.value(),
            max_amp=self.settings_layout.max_att.value(),
            amp_steps=self.settings_layout.att_steps.value(),
        )

        test = Test(
            # test=self.settings_layout.test.isChecked(),
            sound_duration=self.settings_layout.test_duration.value(),
            min_db=self.settings_layout.min_db.value(),
            max_db=self.settings_layout.max_db.value(),
            db_steps=self.settings_layout.db_steps.value(),
        )

        protocol = NoiseProtocolSettings(
            min_freq=self.settings_layout.calib_min_freq.value(),
            max_freq=self.settings_layout.calib_max_freq.value(),
            mic_factor=self.settings_layout.mic_factor.value(),
            reference_pressure=self.settings_layout.reference_pressure.value(),
            ramp_time=self.settings_layout.ramp_time.value(),
            eq_filter=eq_filter,
            calibration=calibration,
            test=test,
        )

        if self.settings_layout.is_harp.isChecked():
            if self.settings_layout.serial_port.currentText() == "":
                QMessageBox.warning(
                    self,
                    "Warning",
                    "The Harp SoundCard is not connected. Please turn it on.",
                )
                return

            soundcard = HarpSoundCard(
                serial_port=self.settings_layout.serial_port.currentText(),
                fs=int(self.settings_layout.fs_harp.currentText()),
                speaker=self.settings_layout.speaker.currentText(),
            )
        else:
            soundcard = ComputerSoundCard(
                soundcard_name="",  # FIXME
                fs=self.settings_layout.fs_computer.value(),
            )

        if self.settings_layout.adc.currentText() == "NI-DAQ":
            adc = NiDaq(
                fs=self.settings_layout.fs_adc.value(),
                device_id=self.settings_layout.device_id.value(),
                channel=self.settings_layout.channel.value(),
            )
        else:
            adc = Moku(
                fs=self.settings_layout.fs_adc.value(),
                address=self.settings_layout.address.text(),
                channel=self.settings_layout.channel.value(),
            )

        self.settings = Config(
            soundcard=soundcard,
            adc=adc,
            filter=filt,
            protocol=protocol,
            paths=Paths(output="output"),
        )

        if (
            self.settings_layout.adc.currentText() == "NI-DAQ"
            and not self.nidaqmx_available()
        ):
            QMessageBox.warning(
                self, "Warning", "The NI-DAQ is not connected. Please turn it on."
            )
            return

        self.plot.create_dictionary(
            self.settings_layout.sound_type.currentText(),
            num_amp=self.settings_layout.att_steps.value(),
            num_freqs=self.settings_layout.calib_freq_steps.value(),
            num_db=self.settings_layout.db_steps.value(),
            num_test_freqs=self.settings_layout.test_freq_steps.value(),
            min_freq=self.settings_layout.min_freq_filt.value(),
            max_freq=self.settings_layout.max_freq_filt.value(),
        )

        self.worker_thread = QThread()
        self.worker = Worker(self.settings, self.plot.calibration_callback)
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.on_task_finished)
        self.work_requested.connect(self.worker.run)
        self.worker_thread.start()

        self.work_requested.emit()

        self.settings_layout.run.setEnabled(False)

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
                self.plot.amp_index.setMaximum(0)
                self.plot.freq_index.setMaximum(0)
            case "Calibration Signals":
                self.plot.fig.setCurrentIndex(1)
                self.plot.amp_index.setMaximum(self.settings.calibration.amp_steps - 1)
                self.plot.freq_index.setMaximum(
                    self.settings.calibration.freq.num_freqs - 1
                )
            case "Test Data":
                self.plot.fig.setCurrentIndex(2)
                self.plot.amp_index.setMaximum(0)
                self.plot.freq_index.setMaximum(0)
            case "Test Signals":
                self.plot.fig.setCurrentIndex(3)
                self.plot.amp_index.setMaximum(
                    self.settings.test_calibration.db_steps - 1
                )
                self.plot.freq_index.setMaximum(
                    self.settings.test_calibration.freq.num_freqs - 1
                )
            case "EQ Filter":
                self.plot.fig.setCurrentIndex(4)
                self.plot.amp_index.setMaximum(0)
                self.plot.freq_index.setMaximum(0)
        self.plot.amp_index.setValue(0)
        self.plot.freq_index.setValue(0)

    # def update_indexes(self, index=None):
    #     plot = self.plot.plots[self.plot.plot_selection.currentText()]
    #     plot.update_indexes(self.plot.amp_index.value(), self.plot.freq_index.value())

    def on_task_finished(self):
        self.settings_layout.run.setEnabled(True)
        self.worker_thread.quit()

    def closeEvent(self, event):
        if hasattr(self, "worker_thread"):
            self.worker_thread.quit()
        event.accept()  # Accept the close event


class Worker(QObject):
    finished = Signal()

    def __init__(self, settings, calibration_callback):
        super(Worker, self).__init__()
        self.settings = settings
        self.calibration_callback = calibration_callback

    @Slot()
    def run(self):
        Calibration(self.settings, self.calibration_callback)
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
