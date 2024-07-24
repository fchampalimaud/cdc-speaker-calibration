import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.view.hardware_frame import HardwareFrame
from speaker_calibration.gui.view.plot_config_frame import PlotConfigFrame
import numpy as np


class ConfigFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        # button
        self.settings_button = ttk.Button(self, text="Open Settings Window")
        self.settings_button.grid(column=0, row=1)

        self.plot_config = PlotConfigFrame(self)
        self.plot_config.grid(column=0, row=2)

        # label
        self.hardware_frame = HardwareFrame(self)
        self.hardware_frame.grid(column=0, row=3)

        self.run_frame = ttk.LabelFrame(self)
        self.run_frame.grid(column=0, row=4)

        for i in range(1):
            self.run_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.run_frame.grid_rowconfigure(i, weight=1)

        self.par_frame = tk.Frame(self.run_frame)
        self.par_frame.grid(column=0, row=0, pady=5)

        self.slope_frame = tk.Frame(self.par_frame)
        self.slope_frame.grid(column=0, row=0, padx=10)

        self.slope_label = ttk.Label(self.slope_frame, text="Slope")
        self.slope_label.grid(column=0, row=0, sticky="e")

        self.slope = tk.StringVar(self.run_frame, "70.00")
        self.slope_sb = ttk.Spinbox(self.slope_frame, from_=-500, to=500, increment=0.01, textvariable=self.slope, width=10, justify="center")
        self.slope_sb.grid(column=1, row=0, sticky="w")

        self.intercept_frame = tk.Frame(self.par_frame)
        self.intercept_frame.grid(column=1, row=0, padx=10)

        self.intercept_label = ttk.Label(self.intercept_frame, text="Intercept")
        self.intercept_label.grid(column=0, row=0, sticky="e")

        self.intercept = tk.StringVar(self.run_frame, "20.00")
        self.intercept_sb = ttk.Spinbox(self.intercept_frame, from_=-500, to=500, increment=0.01, textvariable=self.intercept, width=10, justify="center")
        self.intercept_sb.grid(column=1, row=0, sticky="w")

        self.test_button = ttk.Button(self.run_frame, text="Load Fit Parameters", command=self.open_fit_parameters)
        self.test_button.grid(column=0, row=1, pady=5)

        self.inverse_filter_frame = tk.Frame(self.run_frame)
        self.inverse_filter_frame.grid(column=0, row=2, pady=5)

        self.inverse_filter_button = ttk.Button(self.inverse_filter_frame, text="Load Filter")
        self.inverse_filter_button.grid(column=0, row=0)

        self.inverse_filter_var = tk.StringVar(self.run_frame, "No Filter")
        self.inverse_filter_label = ttk.Label(self.inverse_filter_frame, textvariable=self.inverse_filter_var)
        self.inverse_filter_label.grid(column=1, row=0)

        # button
        self.run_button = ttk.Button(self.run_frame, text="Run")
        self.run_button.grid(row=3, column=0, pady=5)

    def open_fit_parameters(self):
        filename = tk.filedialog.askopenfilename()
        fit_parameters = np.loadtxt(filename, delimiter=",")

        if fit_parameters.size == 2:
            self.slope.set(fit_parameters[0])
            self.intercept.set(fit_parameters[1])
