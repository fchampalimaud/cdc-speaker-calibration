from PySide6.QtWidgets import (
    QGroupBox,
    QCheckBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QFormLayout,
    QMessageBox,
)
from harp.devices.soundcard import SoundCard as HSC
from harp.protocol.exceptions import HarpTimeoutError
from speaker_calibration.gui.utils import get_ports
from speaker_calibration.utils import Speaker
from serial import SerialException


class SoundCardLayout(QGroupBox):
    WIDGETS_WIDTH = 85
    LABEL_WIDTH = 170

    def __init__(self):
        super().__init__("SoundCard")

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

        self.setLayout(form)

        self.on_is_harp_changed(True)

    def on_is_harp_changed(self, state):
        if state:
            self.serial_port.setVisible(True)
            self.serial_port_l.setVisible(True)
            self.fs_harp.setVisible(True)
            self.fs_harp_l.setVisible(True)
            self.fs_computer.setVisible(False)
            self.fs_computer_l.setVisible(False)
        else:
            self.serial_port.setVisible(False)
            self.serial_port_l.setVisible(False)
            self.fs_harp.setVisible(False)
            self.fs_harp_l.setVisible(False)
            self.fs_computer.setVisible(True)
            self.fs_computer_l.setVisible(True)

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

    def convert_speaker(self):
        match self.speaker.currentText():
            case "Left":
                return Speaker.LEFT
            case "Right":
                return Speaker.RIGHT
