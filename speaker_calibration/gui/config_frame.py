import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.hardware_frame import HardwareFrame
from speaker_calibration.gui.test_frame import TestFrame


class ConfigFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, justify="center", textvariable=self.combobox_var, state="readonly")
        self.combobox.grid(column=0, row=1)
        self.combobox["values"] = ["PSD Signal", "Inverse Filter", "Calibration Signals", "Calibration Data", "Test Signals", "Test Data"]

        # button
        self.settings_button = ttk.Button(self, text="Open Settings Window")
        self.settings_button.grid(column=0, row=2)

        # label
        self.hardware_frame = HardwareFrame(self)
        self.hardware_frame.grid(column=0, row=3)

        self.test_frame = TestFrame(self)
        self.test_frame.grid(column=0, row=4)

        self.run_frame = ttk.LabelFrame(self)
        self.run_frame.grid(column=0, row=5)

        for i in range(3):
            self.run_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.run_frame.grid_rowconfigure(i, weight=1)

        self.speaker_filter = tk.IntVar(self.run_frame, 1)
        self.run_cb_sf = ttk.Checkbutton(self.run_frame, text="Speaker Filter", variable=self.speaker_filter, onvalue="1", offvalue="0")
        self.run_cb_sf.grid(row=0, column=0, pady=5, padx=5)
        self.calibration_curve = tk.IntVar(self.run_frame, 1)
        self.run_cb_cc = ttk.Checkbutton(self.run_frame, text="Calibration Curve", variable=self.calibration_curve)
        self.run_cb_cc.grid(row=0, column=1, pady=5, padx=5)
        self.test_calibration = tk.IntVar(self.run_frame, 1)
        self.run_cb_tc = ttk.Checkbutton(self.run_frame, text="Test Calibration", variable=self.test_calibration)
        self.run_cb_tc.grid(row=0, column=2, pady=5, padx=5)

        # button
        self.run_button = ttk.Button(self.run_frame, text="Run")
        self.run_button.grid(row=1, column=1, pady=5)
