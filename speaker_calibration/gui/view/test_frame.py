import tkinter as tk
from tkinter import ttk
import numpy as np


class TestFrame(ttk.LabelFrame):
    def __init__(self, container, text="Test Calibration"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)

        self.lim_frame = tk.Frame(self)
        self.lim_frame.grid(column=0, row=0, pady=5)

        self.min_frame = tk.Frame(self.lim_frame)
        self.min_frame.grid(column=0, row=0, padx=10)

        self.min_label = ttk.Label(self.min_frame, text="Min dB")
        self.min_label.grid(column=0, row=0, sticky="e")

        self.min_var = tk.StringVar(self, "40.0")
        self.min_sb = ttk.Spinbox(self.min_frame, from_=0, to=100, increment=0.1, textvariable=self.min_var, width=10, justify="center")
        self.min_sb.grid(column=1, row=0, sticky="w")

        self.max_frame = tk.Frame(self.lim_frame)
        self.max_frame.grid(column=1, row=0, padx=10)

        self.max_label = ttk.Label(self.max_frame, text="Max dB")
        self.max_label.grid(column=0, row=0, sticky="e")

        self.max_var = tk.StringVar(self, "60.0")
        self.max_sb = ttk.Spinbox(self.max_frame, from_=0, to=100, increment=0.1, textvariable=self.max_var, width=10, justify="center")
        self.max_sb.grid(column=1, row=0, sticky="w")

        self.steps_frame = tk.Frame(self)
        self.steps_frame.grid(column=0, row=1, pady=5)

        self.steps_label = ttk.Label(self.steps_frame, text="Steps")
        self.steps_label.grid(column=0, row=0, sticky="e")

        self.steps_var = tk.IntVar(self, 15)
        self.steps_sb = ttk.Spinbox(self.steps_frame, from_=0, to=50, increment=1, textvariable=self.steps_var, width=10, justify="center")
        self.steps_sb.grid(column=1, row=0, sticky="w")

        self.par_frame = tk.Frame(self)
        self.par_frame.grid(column=0, row=2, pady=5)

        self.slope_frame = tk.Frame(self.par_frame)
        self.slope_frame.grid(column=0, row=0, padx=10)

        self.slope_label = ttk.Label(self.slope_frame, text="Slope")
        self.slope_label.grid(column=0, row=0, sticky="e")

        self.slope = tk.StringVar(self, "70.00")
        self.slope_sb = ttk.Spinbox(self.slope_frame, from_=-500, to=500, increment=0.01, textvariable=self.slope, width=10, justify="center")
        self.slope_sb.grid(column=1, row=0, sticky="w")

        self.intercept_frame = tk.Frame(self.par_frame)
        self.intercept_frame.grid(column=1, row=0, padx=10)

        self.intercept_label = ttk.Label(self.intercept_frame, text="Intercept")
        self.intercept_label.grid(column=0, row=0, sticky="e")

        self.intercept = tk.StringVar(self, "20.00")
        self.intercept_sb = ttk.Spinbox(self.intercept_frame, from_=-500, to=500, increment=0.01, textvariable=self.intercept, width=10, justify="center")
        self.intercept_sb.grid(column=1, row=0, sticky="w")

        self.test_button = ttk.Button(self, text="Load Fit Parameters", command=self.open_fit_parameters)
        self.test_button.grid(column=0, row=3, pady=5)

        self.inverse_filter_frame = tk.Frame(self)
        self.inverse_filter_frame.grid(column=0, row=4, pady=5)

        self.inverse_filter_button = ttk.Button(self.inverse_filter_frame, text="Load Filter", command=self.open_calibration_factor)
        self.inverse_filter_button.grid(column=0, row=0)

        self.inverse_filter_var = tk.StringVar(self, "No Filter")
        self.inverse_filter_label = ttk.Label(self.inverse_filter_frame, textvariable=self.inverse_filter_var)
        self.inverse_filter_label.grid(column=1, row=0)

    def open_fit_parameters(self):
        filename = tk.filedialog.askopenfilename()
        fit_parameters = np.loadtxt(filename, delimiter=",")

        if fit_parameters.size == 2:
            self.slope.set(fit_parameters[0])
            self.intercept.set(fit_parameters[1])

    def open_calibration_factor(self):
        filename = tk.filedialog.askopenfilename()
        self.calibration_factor = np.loadtxt(filename, delimiter=",")

        self.inverse_filter_var.set("Filter Loaded")
