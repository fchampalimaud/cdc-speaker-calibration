from typing import List

import serial.tools.list_ports
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


class LabeledCombobox(QtWidgets.QWidget):
    def __init__(self, text: str):
        super().__init__()

        self.label = QtWidgets.QLabel(text=text)
        self.label.setAlignment(Qt.AlignCenter)

        self.combobox = QtWidgets.QComboBox()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)
        self.setLayout(self.layout)

    def set_placeholder_text(self, text: str):
        self.combobox.setPlaceholderText(text)

    def add_items(self, items: List[str]):
        self.combobox.addItems(items)

    def connect(self, callback: callable):
        self.combobox.currentIndexChanged.connect(callback)

    def current_text(self):
        return self.combobox.currentText()

    def clear(self):
        return self.combobox.clear()

    def set_current_index(self, index: int):
        self.combobox.setCurrentIndex(index)


class LabeledSpinbox(QtWidgets.QWidget):
    def __init__(self, text: str):
        super().__init__()

        self.label = QtWidgets.QLabel(text=text)
        self.label.setAlignment(Qt.AlignCenter)

        self.spinbox = QtWidgets.QSpinBox()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)

    @property
    def value(self) -> int:
        return self.spinbox.value()

    def set_minimum(self, value: int):
        self.spinbox.setMinimum(value)

    def set_value(self, value: int):
        self.spinbox.setValue(value)

    def set_maximum(self, value: int):
        self.spinbox.setMaximum(value)

    def set_range(self, min: int, max: int):
        self.spinbox.setRange(min, max)


class LabeledDoubleSpinbox(QtWidgets.QWidget):
    def __init__(self, text: str):
        super().__init__()

        self.label = QtWidgets.QLabel(text=text)
        self.label.setAlignment(Qt.AlignCenter)

        self.spinbox = QtWidgets.QDoubleSpinBox()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)

    @property
    def value(self) -> float:
        return self.spinbox.value()

    def set_value(self, value: float):
        self.spinbox.setValue(value)

    def set_minimum(self, value: float):
        self.spinbox.setMinimum(value)

    def set_maximum(self, value: float):
        self.spinbox.setMaximum(value)

    def set_range(self, min: float, max: float):
        self.spinbox.setRange(min, max)

    def set_decimals(self, num_decimals: int):
        self.spinbox.setDecimals(num_decimals)

    def set_single_step(self, value: float):
        self.spinbox.setSingleStep(value)
