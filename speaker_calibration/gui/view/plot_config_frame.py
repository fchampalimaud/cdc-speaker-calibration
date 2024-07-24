import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.view.gui_utils import spinbox_row


class PlotConfigFrame(ttk.LabelFrame):
    def __init__(self, container, text="Plot Configuration"):
        super().__init__(container, text=text)

        for i in range(2):
            self.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)

        self.plot_label = ttk.Label(self, text="Plot")
        self.plot_label.grid(row=0, column=0, padx=5, pady=5)

        self.plot_var = tk.StringVar()
        self.plot_cb = ttk.Combobox(self, justify="center", textvariable=self.plot_var, state="readonly")
        self.plot_cb.grid(column=0, row=1)
        self.plot_cb["values"] = ["PSD Signal", "Inverse Filter", "Calibration Signals", "Calibration Data", "Test Signals", "Test Data"]
        self.plot_cb.grid(row=0, column=1, padx=5, pady=5)

        _, self.calibration_signal_var, self.calibration_signal = spinbox_row(self, "Calibration Signal", 0, 0, 0, 1, 1, spinbox_width=10, int_value=1)

        _, self.test_signal_var, self.test_signal = spinbox_row(self, "Test Signal", 0, 0, 0, 1, 2, spinbox_width=10, int_value=1)

        self.signal = tk.IntVar(self, 1)
        self.signal_cb = ttk.Checkbutton(self, text="Original Signal", variable=self.signal, onvalue="1", offvalue="0")
        self.signal_cb.grid(row=3, column=0, padx=5, pady=5)

        self.recorded_sound = tk.IntVar(self, 1)
        self.recorded_sound_cb = ttk.Checkbutton(self, text="Recorded Sound", variable=self.recorded_sound, onvalue="1", offvalue="0")
        self.recorded_sound_cb.grid(row=3, column=1, padx=5, pady=5)
