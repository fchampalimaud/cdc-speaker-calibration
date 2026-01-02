from PySide6.QtWidgets import (
    QGroupBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QFormLayout,
    QLineEdit,
)


class ADCLayout(QGroupBox):
    WIDGETS_WIDTH = 85
    LABEL_WIDTH = 170

    def __init__(self):
        super().__init__("ADC")

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

        self.setLayout(form)
        self.on_adc_changed(True)

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
