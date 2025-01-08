import tkinter as tk
from tkinter import ttk
from speaker_calibration.utils.gui_utils import (
    LabeledCombobox,
    LabeledSpinbox,
    Checkbox,
)


class SettingsWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.iconbitmap("docs/img/favicon.ico")
        # The window is only closed when the application closes
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        # Makes window non-resizable
        self.resizable(False, False)
        # Hides the window
        self.withdraw()
        # Configures columns of the window
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)

        self.sound_type = LabeledCombobox(
            self,
            "Sound Type",
            row=0,
            columnspan=2,
            value_list=["Noise", "Pure Tones"],
            default_value="Noise",
            combobox_width=10,
            sticky="e",
        )
        self.sound_type.bind(self.change_frame)

        self.reference_pressure = LabeledSpinbox(
            self,
            "Reference Pressure (Pa)",
            default_value=0.00002,
            from_=0.000001,
            to=1,
            increment=0.000005,
            row=1,
            sticky="e",
        )

        self.ramp_time = LabeledSpinbox(
            self,
            "Ramp Time (s)",
            default_value=0.005,
            from_=0.005,
            to=1,
            increment=0.005,
            row=2,
            sticky="e",
        )

        self.amplification = LabeledSpinbox(
            self,
            "Amplification",
            default_value=1,
            from_=0,
            to=1,
            increment=0.01,
            row=3,
            sticky="e",
        )

        self.freq_frame = FreqFrame(self)
        self.freq_frame.grid(row=4, column=0, padx=5, pady=5)

        self.filter_frame = FilterFrame(self)
        self.filter_frame.grid(row=5, column=0, padx=5, pady=5)

        self.inverse_filter = InverseFilterFrame(self)
        self.inverse_filter.grid(row=6, column=0, padx=5, pady=5)

        self.calibration = CalibrationFrame(self)
        self.calibration.grid(row=7, column=0, padx=5, pady=5)

        self.test_calibration = TestCalibrationFrame(self)
        self.test_calibration.grid(row=8, column=0, padx=5, pady=5)

    def change_frame(self, event=None):
        if self.sound_type.get() == "Noise":
            self.inverse_filter.grid(
                row=6,
                column=0,
                padx=5,
                pady=5,
            )
        else:
            self.inverse_filter.grid_forget()


class FilterFrame(ttk.LabelFrame):
    def __init__(self, container, text="Filter"):
        super().__init__(container, text=text)

        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)

        self.filter_input = Checkbox(
            self,
            "Filter Input",
            row=0,
            column=0,
            default_value=True,
            command=self.change_frame,
        )

        self.filter_acquisition = Checkbox(
            self,
            "Filter Acquisition",
            row=1,
            column=0,
            default_value=True,
            command=self.change_frame,
        )

        self.min_value = LabeledSpinbox(
            self,
            "Minimum Frequency (Hz)",
            default_value=5000,
            from_=0,
            to=80000,
            increment=0.1,
            row=2,
            column=0,
            sticky="e",
        )

        self.max_value = LabeledSpinbox(
            self,
            "Maximum Frequency (Hz)",
            default_value=20000,
            from_=0,
            to=80000,
            increment=0.1,
            row=3,
            column=0,
            sticky="e",
        )

    def change_frame(self, event=None):
        if self.filter_input.get() or self.filter_acquisition.get():
            self.min_value.grid(
                row=2,
                column=0,
                padx=5,
                pady=5,
            )
            self.max_value.grid(
                row=3,
                column=0,
                padx=5,
                pady=5,
            )
        else:
            self.min_value.grid_forget()
            self.max_value.grid_forget()


class FreqFrame(ttk.LabelFrame):
    def __init__(self, container, text="Frequency Range"):
        super().__init__(container, text=text)

        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.num_freqs = LabeledSpinbox(
            self,
            "Number of Frequencies",
            default_value=10,
            from_=0,
            to=100,
            increment=1,
            row=0,
            column=0,
            sticky="e",
        )

        self.min_value = LabeledSpinbox(
            self,
            "Minimum Frequency (Hz)",
            default_value=5000,
            from_=0,
            to=80000,
            increment=0.1,
            row=1,
            column=0,
            sticky="e",
        )

        self.max_value = LabeledSpinbox(
            self,
            "Maximum Frequency (Hz)",
            default_value=20000,
            from_=0,
            to=80000,
            increment=0.1,
            row=2,
            column=0,
            sticky="e",
        )


class InverseFilterFrame(ttk.LabelFrame):
    def __init__(self, container, text="Inverse Filter"):
        super().__init__(container, text=text)

        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.determine_filter = Checkbox(
            self,
            "Calculate Filter",
            row=0,
            column=0,
            default_value=True,
            command=self.change_frame,
        )

        self.sound_duration = LabeledSpinbox(
            self,
            "Sound Duration (s)",
            default_value=30,
            from_=0.01,
            to=60,
            increment=0.01,
            row=1,
            column=0,
            sticky="e",
        )

        self.time_constant = LabeledSpinbox(
            self,
            "Time Constant (s)",
            default_value=0.005,
            from_=0.001,
            to=10,
            increment=0.001,
            row=2,
            column=0,
            sticky="e",
        )

    def change_frame(self, event=None):
        if self.determine_filter.get():
            self.sound_duration.grid(
                row=1,
                column=0,
                padx=5,
                pady=5,
            )
            self.time_constant.grid(
                row=2,
                column=0,
                padx=5,
                pady=5,
            )
        else:
            self.sound_duration.grid_forget()
            self.time_constant.grid_forget()


class CalibrationFrame(ttk.LabelFrame):
    def __init__(self, container, text="Calibration"):
        super().__init__(container, text=text)

        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)

        self.calibrate = Checkbox(
            self,
            "Calibrate",
            row=0,
            column=0,
            default_value=True,
            command=self.change_frame,
        )

        self.sound_duration = LabeledSpinbox(
            self,
            "Sound Duration (s)",
            default_value=15,
            from_=0.01,
            to=60,
            increment=0.01,
            row=1,
            column=0,
            sticky="e",
        )

        self.att_min = LabeledSpinbox(
            self,
            "Minimum Attenuation",
            default_value=0,
            from_=-10,
            to=0,
            increment=0.1,
            row=2,
            column=0,
            sticky="e",
        )

        self.att_max = LabeledSpinbox(
            self,
            "Maximum Attenuation",
            default_value=-1,
            from_=-10,
            to=0,
            increment=0.1,
            row=3,
            column=0,
            sticky="e",
        )

        self.att_steps = LabeledSpinbox(
            self,
            "Steps",
            default_value=15,
            from_=1,
            to=100,
            increment=1,
            row=4,
            column=0,
            sticky="e",
        )

    def change_frame(self, event=None):
        if self.calibrate.get():
            self.sound_duration.grid(
                row=1,
                column=0,
                padx=5,
                pady=5,
            )
            self.att_min.grid(
                row=2,
                column=0,
                padx=5,
                pady=5,
            )
            self.att_max.grid(
                row=3,
                column=0,
                padx=5,
                pady=5,
            )
            self.att_steps.grid(
                row=4,
                column=0,
                padx=5,
                pady=5,
            )
        else:
            self.sound_duration.grid_forget()
            self.att_min.grid_forget()
            self.att_max.grid_forget()
            self.att_steps.grid_forget()


class TestCalibrationFrame(ttk.LabelFrame):
    def __init__(self, container, text="Calibration"):
        super().__init__(container, text=text)

        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)

        self.test = Checkbox(
            self,
            "Test Calibration",
            row=0,
            column=0,
            default_value=True,
            command=self.change_frame,
        )

        self.sound_duration = LabeledSpinbox(
            self,
            "Sound Duration (s)",
            default_value=5,
            from_=0.01,
            to=60,
            increment=0.01,
            row=1,
            column=0,
            sticky="e",
        )

        self.db_min = LabeledSpinbox(
            self,
            "Minimum dB SPL",
            default_value=30,
            from_=0,
            to=200,
            increment=0.1,
            row=2,
            column=0,
            sticky="e",
        )

        self.db_max = LabeledSpinbox(
            self,
            "Maximum dB SPL",
            default_value=70,
            from_=0,
            to=200,
            increment=0.1,
            row=3,
            column=0,
            sticky="e",
        )

        self.db_steps = LabeledSpinbox(
            self,
            "Steps",
            default_value=5,
            from_=1,
            to=100,
            increment=1,
            row=4,
            column=0,
            sticky="e",
        )

    def change_frame(self, event=None):
        if self.test.get():
            self.sound_duration.grid(
                row=1,
                column=0,
                padx=5,
                pady=5,
            )
            self.db_min.grid(
                row=2,
                column=0,
                padx=5,
                pady=5,
            )
            self.db_max.grid(
                row=3,
                column=0,
                padx=5,
                pady=5,
            )
            self.db_steps.grid(
                row=4,
                column=0,
                padx=5,
                pady=5,
            )
        else:
            self.sound_duration.grid_forget()
            self.db_min.grid_forget()
            self.db_max.grid_forget()
            self.db_steps.grid_forget()
