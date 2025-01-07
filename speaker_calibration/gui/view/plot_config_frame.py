from tkinter import ttk
from speaker_calibration.utils.gui_utils import (
    LabeledSpinbox,
    LabeledCombobox,
    Checkbox,
)


class PlotConfigFrame(ttk.LabelFrame):
    def __init__(self, container, text="Plot Configuration"):
        super().__init__(container, text=text)

        for i in range(2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        plot_list = [
            "PSD Signal",
            "Inverse Filter",
            "Calibration Signals",
            "Calibration Data",
            "Test Signals",
            "Test Data",
        ]

        self.plot = LabeledCombobox(self, "Plot", 0, value_list=plot_list)

        self.plot.combobox.bind("<<ComboboxSelected>>", self.change_frame)

        self.frames = [NoiseSignalFrame(self), PureToneSignalFrame(self)]

    def change_frame(self, event=None):
        if self.plot.get() == "PSD Signal":
            self.frames[0].grid(column=0, row=1)
            self.frames[1].grid_forget()
        elif self.plot.get() == "Inverse Filter":
            self.frames[1].grid(column=0, row=1)
            self.frames[0].grid_forget()


class NoiseSignalFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        for i in range(2):
            self.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.grid_rowconfigure(i, weight=1)

        self.signal_index = LabeledSpinbox(
            self, "Signal Index", 0, 0, 0, 1, 0, columnspan=2
        )

        self.show_signal = Checkbox(self, "Original Signal", 1, 0, default_value=True)
        self.show_recording = Checkbox(self, "Recorded Sound", 1, 1, default_value=True)


class PureToneSignalFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        for i in range(2):
            self.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.frequency_index = LabeledSpinbox(
            self, "Frequency Index", 0, 0, 0, 1, 0, columnspan=2
        )
        self.amplitude_index = LabeledSpinbox(
            self, "Amplitude Index", 0, 0, 0, 1, 1, columnspan=2
        )

        self.show_signal = Checkbox(self, "Original Signal", 2, 0, default_value=True)
        self.show_recording = Checkbox(self, "Recorded Sound", 2, 1, default_value=True)
