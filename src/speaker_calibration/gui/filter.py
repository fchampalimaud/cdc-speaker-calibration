from PySide6.QtWidgets import QGroupBox, QFormLayout, QLabel, QCheckBox, QSpinBox


class FilterLayout(QGroupBox):
    WIDGETS_WIDTH = 85
    LABEL_WIDTH = 170

    def __init__(self):
        super().__init__("Filter")
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

        self.setLayout(form)

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
