import tkinter as tk
from tkinter import ttk
import numpy as np
from speaker_calibration.gui.view.gui_utils import SpinboxesFrame


class PureToneFrame(ttk.LabelFrame):
    def __init__(self, container, text="Pure Tone Calibration"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

        self.labels = np.array(["Calibrate", "Test Calibration"])
        self.variables = np.zeros(2, dtype=object)
        self.checkboxes = np.zeros(2, dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(2):
            self.variables[i] = tk.IntVar(self, 1)
            self.checkboxes[i] = ttk.Checkbutton(
                self,
                text=self.labels[i],
                variable=self.variables[i],
                onvalue="1",
                offvalue="0",
            )
            self.checkboxes[i].grid(row=i, column=0, pady=5)

        self.calibration = SpinboxesFrame(
            self, "config/frames/pt_calibration_init.csv", "Calibration"
        )
        self.calibration.grid(column=0, row=3, padx=5, pady=5)

        self.test = SpinboxesFrame(
            self, "config/frames/pt_test_init.csv", "Test Calibration"
        )
        self.test.grid(column=0, row=4, padx=5, pady=5)
