import tkinter as tk
from tkinter import ttk
import numpy as np
from speaker_calibration.gui.view.settings_frames.noise.psd_frame import PSDFrame
from speaker_calibration.gui.view.settings_frames.noise.calibration_frame import CalibrationFrame
from speaker_calibration.gui.view.settings_frames.noise.test_frame import TestFrame


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
            self.checkboxes[i] = ttk.Checkbutton(self, text=self.labels[i], variable=self.variables[i], onvalue="1", offvalue="0")
            self.checkboxes[i].grid(row=i, column=0, pady=5)

        self.psd = PSDFrame(self)
        self.psd.grid(column=0, row=3, padx=5, pady=5)

        self.calibration = CalibrationFrame(self)
        self.calibration.grid(column=0, row=4, padx=5, pady=5)

        self.test = TestFrame(self)
        self.test.grid(column=0, row=5, padx=5, pady=5)
