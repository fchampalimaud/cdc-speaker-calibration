from pyharp.device import Device
from pyharp.messages import HarpMessage
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from serial.serialutil import SerialException

from speaker_calibration.utils.gui import LabeledCombobox, LabeledSpinbox, get_ports


class HarpSoundCardLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.serial_port_l = QtWidgets.QLabel("Serial Port")
        self.serial_port = QtWidgets.QComboBox()
        self.serial_port.setPlaceholderText("COMx")
        self.serial_port.addItems(get_ports())
        self.serial_port.currentIndexChanged.connect(self.connect_soundcard)
        # self.serial_port.setMaximumWidth(75)

        self.fs_l = QtWidgets.QLabel("Sampling Frequency (Hz)")
        self.fs = QtWidgets.QComboBox()
        self.fs.addItems(["96000", "192000"])
        self.fs.setCurrentIndex(1)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.serial_port_l, 0, 0)
        self.layout.addWidget(self.serial_port, 0, 1)
        self.layout.addWidget(self.fs_l, 1, 0)
        self.layout.addWidget(self.fs, 1, 1)
        self.setLayout(self.layout)

    def connect_soundcard(self, index):
        if hasattr(self, "soundcard"):
            self.soundcard.disconnect()

        if self.serial_port.current_text() == "Refresh":
            self.serial_port.clear()
            self.serial_port.add_items(get_ports())
            return

        try:
            self.soundcard = Device(self.serial_port.current_text())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
            else:
                # showwarning("Warning", "This is not a Harp Soundcard.")
                self.serial_port.set_current_index(-1)
                self.soundcard.disconnect()
        except SerialException:
            self.serial_port.set_current_index(-1)
            # showwarning("Warning", "This is not a Harp device.")


class ComputerSoundCardLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.fs_l = QtWidgets.QLabel("Sampling Frequency (Hz)")
        self.fs = QtWidgets.QSpinBox()
        self.fs.setRange(1, 48000)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.fs_l, 0, 0)
        self.layout.addWidget(self.fs, 0, 1)
        self.setLayout(self.layout)


class SoundCardLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.is_harp = QtWidgets.QCheckBox("Harp SoundCard")
        self.is_harp.setChecked(True)
        self.is_harp.stateChanged.connect(self.on_is_harp_changed)

        self.harp_soundcard = HarpSoundCardLayout()

        self.computer_soundcard = ComputerSoundCardLayout()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.is_harp, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.harp_soundcard)
        self.layout.addWidget(self.computer_soundcard)
        self.setLayout(self.layout)

        self.on_is_harp_changed(self.is_harp.checkState())

    def on_is_harp_changed(self, state):
        if state:
            self.computer_soundcard.setVisible(False)
            self.harp_soundcard.setVisible(True)
            self.adjustSize()
        else:
            self.harp_soundcard.setVisible(False)
            self.computer_soundcard.setVisible(True)
            self.adjustSize()

    @property
    def fs(self) -> int:
        if self.is_harp.checkState():
            return int(self.harp_soundcard.fs.current_text())
        else:
            return self.computer_soundcard.value()


class AdcLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.adc_l = QtWidgets.QLabel("ADC")
        self.adc = QtWidgets.QComboBox()
        self.adc.addItems(["NI-DAQ", "Moku:Go"])
        self.adc.setCurrentIndex(1)

        self.adc_fs_l = QtWidgets.QLabel("ADC Sampling Frequency (Hz)")
        self.adc_fs = QtWidgets.QSpinBox()
        self.adc_fs.setRange(1, 250000)

        self.device_id_l = QtWidgets.QLabel("Device ID")
        self.device_id = QtWidgets.QSpinBox()
        self.device_id.setMinimum(1)

        # TODO: Moku address

        self.channel_l = QtWidgets.QLabel("Channel")
        self.channel = QtWidgets.QSpinBox()
        self.channel.setRange(0, 7)

        self.adc.currentIndexChanged.connect(self.on_adc_change)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.adc_l, 0, 0)
        self.layout.addWidget(self.adc, 0, 1)
        self.layout.addWidget(self.adc_fs_l, 1, 0)
        self.layout.addWidget(self.adc_fs, 1, 1)
        self.layout.addWidget(self.device_id_l, 2, 0)
        self.layout.addWidget(self.device_id, 2, 1)
        # TODO: Moku address
        self.layout.addWidget(self.channel_l, 4, 0)
        self.layout.addWidget(self.channel, 4, 1)
        self.setLayout(self.layout)

    def on_adc_change(self, index):
        if self.adc.currentText() == "NI-DAQ":
            self.device_id_l.hide()
            self.device_id.hide()
            # TODO: Moku address
            self.adc_fs.setRange(1, 250000)
            self.adc_fs.setValue(250000)
            self.channel.setRange(0, 7)
            self.channel.setValue(1)
            self.adjustSize()
        else:
            self.device_id_l.show()
            self.device_id.show()
            # TODO: Moku address
            self.adc_fs.setRange(1, 500000)
            self.adc_fs.setValue(500000)
            self.channel.setRange(1, 2)
            self.channel.setValue(1)
            self.adjustSize()


class InverseFilterLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.determine_filter = QtWidgets.QCheckBox("Determine Filter")
        self.determine_filter.setChecked(True)
        self.determine_filter.stateChanged.connect(self.on_checkbox_changed)

        self.sound_duration_l = QtWidgets.QLabel("Sound Duration (s)")
        self.sound_duration = QtWidgets.QDoubleSpinBox()
        self.sound_duration.setMinimum(0)
        self.sound_duration.setDecimals(2)
        self.sound_duration.setSingleStep(0.01)
        self.sound_duration.setValue(30)

        self.time_constant_l = QtWidgets.QLabel("Time Constant (s)")
        self.time_constant = QtWidgets.QDoubleSpinBox()
        self.time_constant.setMinimum(0)
        self.time_constant.setDecimals(3)
        self.time_constant.setSingleStep(0.005)
        self.time_constant.setValue(0.005)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(
            self.determine_filter, 0, 0, 1, 2, alignment=Qt.AlignCenter
        )
        self.layout.addWidget(self.sound_duration_l, 1, 0)
        self.layout.addWidget(self.sound_duration, 1, 1)
        self.layout.addWidget(self.time_constant_l, 2, 0)
        self.layout.addWidget(self.time_constant, 2, 1)
        self.setLayout(self.layout)

    def on_checkbox_changed(self, state):
        if state:
            self.sound_duration_l.setVisible(True)
            self.sound_duration.setVisible(True)
            self.time_constant_l.setVisible(True)
            self.time_constant.setVisible(True)
            self.adjustSize()
        else:
            self.sound_duration_l.setVisible(False)
            self.sound_duration.setVisible(False)
            self.time_constant_l.setVisible(False)
            self.time_constant.setVisible(False)
            self.adjustSize()


class CalibrationLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.calibrate = QtWidgets.QCheckBox("Calibrate")
        self.calibrate.setChecked(True)
        self.calibrate.stateChanged.connect(self.on_checkbox_changed)

        self.sound_duration_l = QtWidgets.QLabel("Sound Duration (s)")
        self.sound_duration = QtWidgets.QDoubleSpinBox()
        self.sound_duration.setMinimum(0)
        self.sound_duration.setDecimals(2)
        self.sound_duration.setSingleStep(0.01)
        self.sound_duration.setValue(15)

        self.att_min_l = QtWidgets.QLabel("Minimum Attenuation")
        self.att_min = QtWidgets.QDoubleSpinBox()
        self.att_min.setMaximum(0)
        self.att_min.setDecimals(2)
        self.att_min.setSingleStep(0.01)
        self.att_min.setValue(0)

        self.att_max_l = QtWidgets.QLabel("Maximum Attenuation")
        self.att_max = QtWidgets.QDoubleSpinBox()
        self.att_max.setMaximum(0)
        self.att_max.setDecimals(2)
        self.att_max.setSingleStep(0.01)
        self.att_max.setValue(-1)

        self.att_steps_l = QtWidgets.QLabel("Attenuation Steps")
        self.att_steps = QtWidgets.QSpinBox()
        self.att_steps.setMinimum(2)
        self.att_steps.setValue(15)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.calibrate, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.sound_duration_l, 1, 0)
        self.layout.addWidget(self.sound_duration, 1, 1)
        self.layout.addWidget(self.att_min_l, 2, 0)
        self.layout.addWidget(self.att_min, 2, 1)
        self.layout.addWidget(self.att_max_l, 3, 0)
        self.layout.addWidget(self.att_max, 3, 1)
        self.layout.addWidget(self.att_steps_l, 4, 0)
        self.layout.addWidget(self.att_steps, 4, 1)
        self.setLayout(self.layout)

    def on_checkbox_changed(self, state):
        if state:
            self.sound_duration_l.setVisible(True)
            self.sound_duration.setVisible(True)
            self.att_min_l.setVisible(True)
            self.att_min.setVisible(True)
            self.att_max_l.setVisible(True)
            self.att_max.setVisible(True)
            self.att_steps_l.setVisible(True)
            self.att_steps.setVisible(True)
            self.adjustSize()
        else:
            self.sound_duration_l.setVisible(False)
            self.sound_duration.setVisible(False)
            self.att_min_l.setVisible(False)
            self.att_min.setVisible(False)
            self.att_max_l.setVisible(False)
            self.att_max.setVisible(False)
            self.att_steps_l.setVisible(False)
            self.att_steps.setVisible(False)
            self.adjustSize()


class TestLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.test = QtWidgets.QCheckBox("Test")
        self.test.setChecked(True)
        self.test.stateChanged.connect(self.on_checkbox_changed)

        self.sound_duration_l = QtWidgets.QLabel("Sound Duration (s)")
        self.sound_duration = QtWidgets.QDoubleSpinBox()
        self.sound_duration.setMinimum(0)
        self.sound_duration.setDecimals(2)
        self.sound_duration.setSingleStep(0.01)
        self.sound_duration.setValue(5)
        # self.sound_duration.setFixedWidth(75)

        self.db_min_l = QtWidgets.QLabel("Minimum dB SPL")
        self.db_min = QtWidgets.QDoubleSpinBox()
        self.db_min.setMinimum(0)
        self.db_min.setDecimals(2)
        self.db_min.setSingleStep(0.01)
        self.db_min.setValue(30)

        self.db_max_l = QtWidgets.QLabel("Maximum dB SPL")
        self.db_max = QtWidgets.QDoubleSpinBox()
        self.db_max.setMinimum(0)
        self.db_max.setDecimals(2)
        self.db_max.setSingleStep(0.01)
        self.db_max.setValue(70)

        self.db_steps_l = QtWidgets.QLabel("dB SPL Steps")
        self.db_steps = QtWidgets.QSpinBox()
        self.db_steps.setMinimum(2)
        self.db_steps.setValue(5)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.test, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.sound_duration_l, 1, 0)
        self.layout.addWidget(self.sound_duration, 1, 1)
        self.layout.addWidget(self.db_min_l, 2, 0)
        self.layout.addWidget(self.db_min, 2, 1)
        self.layout.addWidget(self.db_max_l, 3, 0)
        self.layout.addWidget(self.db_max, 3, 1)
        self.layout.addWidget(self.db_steps_l, 4, 0)
        self.layout.addWidget(self.db_steps, 4, 1)
        self.setLayout(self.layout)

    def on_checkbox_changed(self, state):
        if state:
            self.sound_duration_l.setVisible(True)
            self.sound_duration.setVisible(True)
            self.db_min_l.setVisible(True)
            self.db_min.setVisible(True)
            self.db_max_l.setVisible(True)
            self.db_max.setVisible(True)
            self.db_steps_l.setVisible(True)
            self.db_steps.setVisible(True)
            self.adjustSize()
        else:
            self.sound_duration_l.setVisible(False)
            self.sound_duration.setVisible(False)
            self.db_min_l.setVisible(False)
            self.db_min.setVisible(False)
            self.db_max_l.setVisible(False)
            self.db_max.setVisible(False)
            self.db_steps_l.setVisible(False)
            self.db_steps.setVisible(False)
            self.adjustSize()


class ProtocolLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.sound_type_l = QtWidgets.QLabel("Sound Type")
        self.sound_type = QtWidgets.QComboBox()
        self.sound_type.addItems(["Noise", "Pure Tones"])
        self.sound_type.setCurrentIndex(1)

        self.amplitude_l = QtWidgets.QLabel("Amplitude")
        self.amplitude = QtWidgets.QDoubleSpinBox()
        self.amplitude.setRange(0, 1)
        self.amplitude.setDecimals(2)
        self.amplitude.setSingleStep(0.01)
        self.amplitude.setValue(1)

        self.ramp_time_l = QtWidgets.QLabel("Ramp Time (s)")
        self.ramp_time = QtWidgets.QDoubleSpinBox()
        self.ramp_time.setMinimum(0)
        self.ramp_time.setDecimals(3)
        self.ramp_time.setSingleStep(0.005)
        self.ramp_time.setValue(0.005)

        self.min_freq_l = QtWidgets.QLabel("Minimum Frequency (Hz)")
        self.min_freq = QtWidgets.QSpinBox()
        self.min_freq.setRange(0, 80000)
        self.min_freq.setValue(5000)

        self.max_freq_l = QtWidgets.QLabel("Maximum Frequency (Hz)")
        self.max_freq = QtWidgets.QSpinBox()
        self.max_freq.setRange(0, 80000)
        self.max_freq.setValue(20000)

        self.inverse_filter = InverseFilterLayout()
        self.calibration = CalibrationLayout()
        self.test = TestLayout()

        self.sound_type.currentIndexChanged.connect(self.on_sound_type_change)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.sound_type_l, 0, 0)
        self.layout.addWidget(self.sound_type, 0, 1)
        self.layout.addWidget(self.amplitude_l, 1, 0)
        self.layout.addWidget(self.amplitude, 1, 1)
        self.layout.addWidget(self.ramp_time_l, 2, 0)
        self.layout.addWidget(self.ramp_time, 2, 1)
        self.layout.addWidget(self.min_freq_l, 3, 0)
        self.layout.addWidget(self.min_freq, 3, 1)
        self.layout.addWidget(self.max_freq_l, 4, 0)
        self.layout.addWidget(self.max_freq, 4, 1)
        self.layout.addWidget(self.inverse_filter, 5, 0, 1, 2)
        self.layout.addWidget(self.calibration, 6, 0, 1, 2)
        self.layout.addWidget(self.test, 7, 0, 1, 2)
        self.setLayout(self.layout)

    def on_sound_type_change(self, index):
        if self.sound_type.currentText() == "Noise":
            self.inverse_filter.show()
            self.adjustSize()
        else:
            self.inverse_filter.hide()
            self.adjustSize()


class FilterLayout(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.filter_input = QtWidgets.QCheckBox("Filter Input")
        self.filter_input.setChecked(True)
        self.filter_input.stateChanged.connect(self.on_filter_change)

        self.filter_acquisition = QtWidgets.QCheckBox("Filter Acquisition")
        self.filter_acquisition.setChecked(True)
        self.filter_acquisition.stateChanged.connect(self.on_filter_change)

        self.min_freq_l = QtWidgets.QLabel("Minimum Frequency (Hz)")
        self.min_freq = QtWidgets.QSpinBox()
        self.min_freq.setRange(0, 80000)
        self.min_freq.setValue(5000)

        self.max_freq_l = QtWidgets.QLabel("Maximum Frequency (Hz)")
        self.max_freq = QtWidgets.QSpinBox()
        self.max_freq.setRange(0, 80000)
        self.max_freq.setValue(20000)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.filter_input, 0, 0)
        self.layout.addWidget(self.filter_acquisition, 0, 1)
        self.layout.addWidget(self.min_freq_l, 1, 0)
        self.layout.addWidget(self.min_freq, 1, 1)
        self.layout.addWidget(self.max_freq_l, 2, 0)
        self.layout.addWidget(self.max_freq, 2, 1)
        self.setLayout(self.layout)

    def on_filter_change(self, state):
        if self.filter_input.isChecked() or self.filter_acquisition.isChecked():
            self.min_freq_l.show()
            self.min_freq.show()
            self.max_freq_l.show()
            self.max_freq.show()
            self.adjustSize()
        else:
            self.min_freq_l.hide()
            self.min_freq.hide()
            self.max_freq_l.hide()
            self.max_freq.hide()
            self.adjustSize()
