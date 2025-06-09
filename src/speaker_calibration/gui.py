import sys
from typing import Literal

from pyharp.device import Device, HarpMessage
from PySide6.QtCore import QObject, Qt, QThread, QThreadPool, Signal, Slot
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
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from serial import SerialException
from speaker_calibration.protocol import Calibration
from speaker_calibration.settings import (
    CalibrationSettings,
    ComputerSoundCard,
    Filter,
    Freq,
    HarpSoundCard,
    InverseFilter,
    Moku,
    NiDaq,
    Settings,
    TestCalibration,
)
from speaker_calibration.utils.gui import Plot, get_ports


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
        self.generate_inverse_filter_layout()
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

        form.addRow("Harp SoundCard", self.is_harp)
        form.addRow(self.serial_port_l, self.serial_port)
        form.addRow(self.fs_harp_l, self.fs_harp)
        form.addRow(self.fs_computer_l, self.fs_computer)

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
        self.amplitude.setValue(1)
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

    def generate_inverse_filter_layout(self):
        self.inverse_filter_gb = QGroupBox("Inverse Filter")
        form = QFormLayout()

        self.inverse_filter_l = QLabel("Determine Filter")
        self.inverse_filter_l.setFixedWidth(self.LABEL_WIDTH)
        self.inverse_filter = QCheckBox()
        self.inverse_filter.setChecked(True)
        self.inverse_filter.stateChanged.connect(self.on_inverse_filter_changed)

        self.if_duration_l = QLabel("Sound Duration (s)")
        self.if_duration_l.setFixedWidth(self.LABEL_WIDTH)
        self.if_duration = QDoubleSpinBox()
        self.if_duration.setSingleStep(0.01)
        self.if_duration.setMinimum(0)
        self.if_duration.setDecimals(3)
        self.if_duration.setSingleStep(0.005)
        self.if_duration.setValue(30)
        self.if_duration.setFixedWidth(self.WIDGETS_WIDTH)

        self.time_const_l = QLabel("Time Constant (s)")
        self.time_const = QDoubleSpinBox()
        self.time_const.setMinimum(0)
        self.time_const.setDecimals(3)
        self.time_const.setSingleStep(0.005)
        self.time_const.setValue(0.005)
        self.time_const.setFixedWidth(self.WIDGETS_WIDTH)

        form.addRow(self.inverse_filter_l, self.inverse_filter)
        form.addRow(self.if_duration_l, self.if_duration)
        form.addRow(self.time_const_l, self.time_const)

        self.inverse_filter_gb.setLayout(form)
        self.layout.addWidget(self.inverse_filter_gb)

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
        self.calib_duration.setValue(15)
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
        self.min_att.setValue(0)
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
        self.test_duration.setValue(5)
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
        self.max_db.setValue(70)
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
            self.inverse_filter_gb.show()
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
            self.inverse_filter_gb.hide()
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
            self.test_min_freq_l.show()
            self.test_min_freq.show()
            self.test_max_freq_l.show()
            self.test_max_freq.show()
            self.test_freq_steps_l.show()
            self.test_freq_steps.show()
            self.adjustSize()

    def on_inverse_filter_changed(self, state):
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
        if self.serial_port.currentText() == "Refresh":
            self.serial_port.clear()
            self.serial_port.addItems(get_ports())
            return

        try:
            self.soundcard = Device(self.serial_port.currentText())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
                self.soundcard.disconnect()

            else:
                # showwarning("Warning", "This is not a Harp Soundcard.")
                self.serial_port.setCurrentIndex(-1)
                self.soundcard.disconnect()
        except SerialException:
            self.serial_port.setCurrentIndex(-1)
            # showwarning("Warning", "This is not a Harp device.")


class PlotLayout(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.create_dictionary()
        self.generate_selection()

        self.setLayout(self.layout)

        self.thread_pool = QThreadPool.globalInstance()

    def create_dictionary(self):
        self.plots = {
            "Calibration Data": Plot(),
            "Calibration Signals": Plot(),
            "Test Data": Plot(),
            "Test Signals": Plot(),
            "Inverse Filter": Plot(),
            "Inverse Filter Signal": Plot(),
        }

        self.fig = QStackedWidget()
        self.fig.addWidget(self.plots["Calibration Data"].plot)
        self.fig.addWidget(self.plots["Calibration Signals"].plot)
        self.fig.addWidget(self.plots["Test Data"].plot)
        self.fig.addWidget(self.plots["Test Signals"].plot)
        self.fig.addWidget(self.plots["Inverse Filter"].plot)
        self.fig.addWidget(self.plots["Inverse Filter Signal"].plot)
        self.layout.addWidget(self.fig)

    def generate_selection(self):
        layout = QHBoxLayout()

        self.plot_l = QLabel("Plot: ")
        self.plot_selection = QComboBox()
        # self.plot_selection.currentIndexChanged.connect(self.switch_plots)

        self.intensity_index_l = QLabel("Plot Index: ")
        self.intensity_index = QSpinBox()
        self.intensity_index.valueChanged.connect(self.draw_data)

        self.frequency_index_l = QLabel("Frequency Index: ")
        self.frequency_index = QSpinBox()

        self.original = QRadioButton("Original Signal")
        self.recorded = QRadioButton("Recorded Sound")
        self.both = QRadioButton("Both")
        self.both.setChecked(True)

        layout.addWidget(self.plot_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.plot_selection)
        layout.addWidget(self.intensity_index_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.intensity_index)
        layout.addWidget(self.frequency_index_l, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.frequency_index)
        layout.addWidget(self.original, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.recorded, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.both, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addLayout(layout)

    def reset_figures(
        self, calib_type: Literal["Noise", "Pure Tones"], num_amp, num_freqs, num_db
    ):  # TODO: add test num_freqs
        while self.plot_selection.count() > 0:
            self.plot_selection.removeItem(0)

        if calib_type == "Noise":
            self.plot_selection.addItems(self.plots.keys())
        else:
            self.plot_selection.addItems(self.plots.keys()[:-2])

        for key in self.plots:
            self.plots[key].generate_plots(key, calib_type)
            self.plots[key].init_array(key, calib_type, num_amp, num_freqs, num_db)

    def draw_data(self):
        match self.plot_selection.currentText():
            case "Calibration Data":
                self.plots["Calibration Data"].plot.plot[0].set_data(
                    self.plots["Calibration Data"].data[:, 0],
                    self.plots["Calibration Data"].data[:, 1],
                )
                self.plots["Calibration Data"].plot.ax.relim()
                self.plots["Calibration Data"].plot.ax.autoscale_view()
                self.plots["Calibration Data"].plot.canvas.draw()
            case "Calibration Signals":
                index = self.intensity_index.value()
                self.plots["Calibration Signals"].plot.plot[0].set_data(
                    self.plots["Calibration Signals"].data[index, 0].time,
                    self.plots["Calibration Signals"].data[index, 0].signal,
                )
                self.plots["Calibration Signals"].plot.plot[1].set_data(
                    self.plots["Calibration Signals"].data[index, 1].time,
                    self.plots["Calibration Signals"].data[index, 1].signal,
                )
                self.plots["Calibration Signals"].plot.ax.relim()
                self.plots["Calibration Signals"].plot.ax.autoscale_view()
                self.plots["Calibration Signals"].plot.canvas.draw()
            case "Test Data":
                self.plots["Test Data"].plot.plot[0].set_data(
                    self.plots["Test Data"].data[:, 0],
                    self.plots["Test Data"].data[:, 1],
                )
                self.plots["Test Data"].plot.ax.relim()
                self.plots["Test Data"].plot.ax.autoscale_view()
                self.plots["Test Data"].plot.canvas.draw()
            case "Test Signals":
                index = self.intensity_index.value()
                self.plots["Test Signals"].plot.plot[0].set_data(
                    self.plots["Test Signals"].data[index, 0].time,
                    self.plots["Test Signals"].data[index, 0].signal,
                )
                self.plots["Test Signals"].plot.plot[1].set_data(
                    self.plots["Test Signals"].data[index, 1].time,
                    self.plots["Test Signals"].data[index, 1].signal,
                )
                self.plots["Test Signals"].plot.ax.relim()
                self.plots["Test Signals"].plot.ax.autoscale_view()
                self.plots["Test Signals"].plot.canvas.draw()
            case "Inverse Filter":
                self.plots["Inverse Filter"].plot.plot[0].set_data(
                    self.plots["Inverse Filter"].data[:, 0],
                    self.plots["Inverse Filter"].data[:, 1],
                )
                self.plots["Inverse Filter"].plot.ax.relim()
                self.plots["Inverse Filter"].plot.ax.autoscale_view()
                self.plots["Inverse Filter"].plot.canvas.draw()
            case "Inverse Filter Signal":
                self.plots["Inverse Filter Signal"].plot.plot[0].set_data(
                    self.plots["Inverse Filter Signal"].data[0].time,
                    self.plots["Inverse Filter Signal"].data[0].signal,
                )
                self.plots["Inverse Filter Signal"].plot.plot[1].set_data(
                    self.plots["Inverse Filter Signal"].data[1].time,
                    self.plots["Inverse Filter Signal"].data[1].signal,
                )
                self.plots["Inverse Filter Signal"].plot.ax.relim()
                self.plots["Inverse Filter Signal"].plot.ax.autoscale_view()
                self.plots["Inverse Filter Signal"].plot.canvas.draw()

    def calibration_callback(self, code: str, *args):
        if code == "Inverse Filter":
            self.plots["Inverse Filter"].data = args[0]
            self.plots["Inverse Filter Signal"].data[0] = args[1]
            self.plots["Inverse Filter Signal"].data[1] = args[2]
        elif code == "Pre-calibration":
            self.plots["Calibration Data"].data[:, 0] = args[0]
        elif code == "Calibration":
            self.plots["Calibration Data"].data[args[0], 1] = args[3]
            self.plots["Calibration Signals"].data[args[0], 0] = args[1]
            self.plots["Calibration Signals"].data[args[0], 1] = args[2]
        elif code == "Pre-test":
            self.plots["Test Data"].data[:, 0] = args[0]
        elif code == "Test":
            self.plots["Test Data"].data[args[0], 1] = args[3]
            self.plots["Test Signals"].data[args[0], 0] = args[1]
            self.plots["Test Signals"].data[args[0], 1] = args[2]

        self.draw_data()


class ApplicationWindow(QMainWindow):
    work_requested = Signal()

    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.setCentralWidget(self._main)

        layout = QHBoxLayout(self._main)

        self.plot = PlotLayout()
        self.settings_layout = SettingsLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.settings_layout)
        scroll_area.setFixedWidth(320)

        self.settings_layout.run.clicked.connect(self.run_calibration)
        self.plot.plot_selection.currentIndexChanged.connect(self.switch_plots)

        layout.addWidget(self.plot)
        layout.addWidget(scroll_area)

        self.showMaximized()

    def run_calibration(self):
        freq = Freq(
            min_freq=self.settings_layout.min_freq.value(),
            max_freq=self.settings_layout.max_freq.value(),
        )

        filt = Filter(
            filter_input=self.settings_layout.filter_input.isChecked(),
            filter_acquisition=self.settings_layout.filter_acquisition.isChecked(),
            min_value=self.settings_layout.min_freq_filt.value(),
            max_value=self.settings_layout.max_freq_filt.value(),
        )

        inverse_filter = InverseFilter(
            determine_filter=self.settings_layout.inverse_filter.isChecked(),
            sound_duration=self.settings_layout.if_duration.value(),
            time_constant=self.settings_layout.time_const.value(),
        )

        calib_freq = Freq(
            min_freq=self.settings_layout.calib_min_freq.value(),
            max_freq=self.settings_layout.calib_max_freq.value(),
            num_freqs=self.settings_layout.calib_freq_steps.value(),
        )

        calibration = CalibrationSettings(
            calibrate=self.settings_layout.calibrate.isChecked(),
            sound_duration=self.settings_layout.calib_duration.value(),
            freq=calib_freq,
            att_min=self.settings_layout.min_att.value(),
            att_max=self.settings_layout.max_att.value(),
            att_steps=self.settings_layout.att_steps.value(),
        )

        test_freq = Freq(
            min_freq=self.settings_layout.test_min_freq.value(),
            max_freq=self.settings_layout.test_max_freq.value(),
            num_freqs=self.settings_layout.test_freq_steps.value(),
        )

        test = TestCalibration(
            test=self.settings_layout.test.isChecked(),
            sound_duration=self.settings_layout.test_duration.value(),
            freq=test_freq,
            db_min=self.settings_layout.min_db.value(),
            db_max=self.settings_layout.max_db.value(),
            db_steps=self.settings_layout.db_steps.value(),
        )

        if self.settings_layout.is_harp.isChecked():
            soundcard = HarpSoundCard(
                com_port=self.settings_layout.serial_port.currentText(),
                fs=int(self.settings_layout.fs_harp.currentText()),
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

        self.settings = Settings(
            sound_type=self.settings_layout.sound_type.currentText(),
            mic_factor=self.settings_layout.mic_factor.value(),
            reference_pressure=self.settings_layout.reference_pressure.value(),
            ramp_time=self.settings_layout.ramp_time.value(),
            amplitude=self.settings_layout.amplitude.value(),
            freq=freq,
            filter=filt,
            inverse_filter=inverse_filter,
            calibration=calibration,
            test_calibration=test,
            is_harp=self.settings_layout.is_harp.isChecked(),
            soundcard=soundcard,
            adc_device=self.settings_layout.adc.currentText(),
            adc=adc,
            output_dir="output",
        )

        self.plot.reset_figures(
            self.settings_layout.sound_type.currentText(),
            num_amp=self.settings_layout.att_steps.value(),
            num_freqs=1,  # FIXME
            num_db=self.settings_layout.db_steps.value(),
        )

        self.worker_thread = QThread()
        self.worker = Worker(self.settings, self.plot.calibration_callback)
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.on_task_finished)
        self.work_requested.connect(self.worker.run)
        self.worker_thread.start()

        self.work_requested.emit()

        self.settings_layout.run.setEnabled(False)

    def switch_plots(self, index=None):
        match self.plot.plot_selection.currentText():
            case "Calibration Data":
                self.plot.fig.setCurrentIndex(0)
                self.plot.intensity_index.setMaximum(0)
            case "Calibration Signals":
                self.plot.fig.setCurrentIndex(1)
                self.plot.intensity_index.setMaximum(
                    self.settings.calibration.att_steps - 1
                )
            case "Test Data":
                self.plot.fig.setCurrentIndex(2)
                self.plot.intensity_index.setMaximum(0)
            case "Test Signals":
                self.plot.fig.setCurrentIndex(3)
                self.plot.intensity_index.setMaximum(
                    self.settings.calibration.db_steps - 1
                )
            case "Inverse Filter":
                self.plot.fig.setCurrentIndex(4)
                self.plot.intensity_index.setMaximum(0)
            case "Inverse Filter Signal":
                self.plot.fig.setCurrentIndex(5)
                self.plot.intensity_index.setMaximum(0)
        self.plot.intensity_index.setValue(0)
        self.plot.draw_data()

    def on_task_finished(self):
        self.settings_layout.run.setEnabled(True)
        self.worker_thread.quit()

    def closeEvent(self, event):
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


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
