import tkinter as tk
from tkinter import ttk
import numpy as np
from speaker_calibration.utils.gui_utils import SpinboxesFrame


class NoiseFrame(ttk.LabelFrame):
    def __init__(self, container, text="Noise Calibration"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

        self.labels = np.array(["Calculate Filter", "Calibrate", "Test Calibration"])
        self.variables = np.zeros(3, dtype=object)
        self.checkboxes = np.zeros(3, dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(3):
            self.variables[i] = tk.IntVar(self, 1)
            self.checkboxes[i] = ttk.Checkbutton(
                self,
                text=self.labels[i],
                variable=self.variables[i],
                onvalue="1",
                offvalue="0",
            )
            self.checkboxes[i].grid(row=i, column=0, pady=5)

        self.psd = SpinboxesFrame(
            self, "config/frames/psd_init.csv", "Filter Calculation"
        )
        self.psd.grid(column=0, row=3, padx=5, pady=5)

        self.calibration = SpinboxesFrame(
            self, "config/frames/calibration_init.csv", "Calibration"
        )
        self.calibration.grid(column=0, row=4, padx=5, pady=5)

        self.test = SpinboxesFrame(
            self, "config/frames/test_init.csv", "Test Calibration"
        )
        self.test.grid(column=0, row=5, padx=5, pady=5)
