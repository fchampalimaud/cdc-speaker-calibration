import tkinter as tk
from tkinter import ttk
import numpy as np


class ConfigurationWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.geometry("300x600")
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
        self.iconbitmap("docs/img/favicon.ico")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for i in range(16):
            self.grid_rowconfigure(i, weight=1)

        # fs_adc
        self.fs_label = ttk.Label(self, text="ADC Sampling Frequency (Hz)")
        self.fs_label.grid(column=0, row=0, sticky="e")

        self.fs_var = tk.IntVar(self, 250000)
        self.fs_sb = ttk.Spinbox(self, from_=0, to=250000, textvariable=self.fs_var, width=10, justify="center")
        self.fs_sb.grid(column=1, row=0, sticky="w")

        # sound_duration_psd
        self.duration_psd_label = ttk.Label(self, text="PSD Calibration Sound Duration (s)")
        self.duration_psd_label.grid(column=0, row=1, sticky="e")

        self.duration_psd_var = tk.IntVar(self, 30)
        self.duration_psd_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_psd_var, width=10, justify="center")
        self.duration_psd_sb.grid(column=1, row=1, sticky="w")

        # sound_duration_db
        self.duration_db_label = ttk.Label(self, text="dB Calibration Sound Duration (s)")
        self.duration_db_label.grid(column=0, row=2, sticky="e")

        self.duration_db_var = tk.IntVar(self, 15)
        self.duration_db_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_db_var, width=10, justify="center")
        self.duration_db_sb.grid(column=1, row=2, sticky="w")

        # sound_duration_test
        self.duration_test_label = ttk.Label(self, text="Test Calibration Sound Duration (s)")
        self.duration_test_label.grid(column=0, row=3, sticky="e")

        self.duration_test_var = tk.IntVar(self, 5)
        self.duration_test_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_test_var, width=10, justify="center")
        self.duration_test_sb.grid(column=1, row=3, sticky="w")

        # ramp_time
        self.ramp_time_label = ttk.Label(self, text="Ramp Time (s)")
        self.ramp_time_label.grid(column=0, row=4, sticky="e")

        self.ramp_time_var = tk.StringVar(self, "0.005")
        self.ramp_time_sb = ttk.Spinbox(self, from_=0.005, to=1, increment=0.005, textvariable=self.ramp_time_var, width=10, justify="center")
        self.ramp_time_sb.grid(column=1, row=4, sticky="w")

        # reference_pressure
        self.pressure_label = ttk.Label(self, text="Reference Pressure (Pa)")
        self.pressure_label.grid(column=0, row=5, sticky="e")

        self.pressure_var = tk.StringVar(self, "0.00002")
        self.pressure_sb = ttk.Spinbox(self, from_=0.000001, to=1, increment=0.000005, textvariable=self.pressure_var, width=10, justify="center")
        self.pressure_sb.grid(column=1, row=5, sticky="w")

        # mic_factor
        self.mic_factor_label = ttk.Label(self, text="Microphone Factor (V/Pa)")
        self.mic_factor_label.grid(column=0, row=6, sticky="e")

        self.mic_factor_var = tk.StringVar(self, "10")
        self.mic_factor_sb = ttk.Spinbox(self, from_=0, to=100, increment=0.1, textvariable=self.mic_factor_var, width=10, justify="center")
        self.mic_factor_sb.grid(column=1, row=6, sticky="w")

        # att_min
        self.att_min_label = ttk.Label(self, text="Minimum Attenuation")
        self.att_min_label.grid(column=0, row=7, sticky="e")

        self.att_min_var = tk.StringVar(self, "0")
        self.att_min_sb = ttk.Spinbox(self, from_=-10, to=0, increment=0.1, textvariable=self.att_min_var, width=10, justify="center")
        self.att_min_sb.grid(column=1, row=7, sticky="w")

        # att_max
        self.att_max_label = ttk.Label(self, text="Maximum Attenuation")
        self.att_max_label.grid(column=0, row=8, sticky="e")

        self.att_max_var = tk.StringVar(self, "-1")
        self.att_max_sb = ttk.Spinbox(self, from_=-10, to=0, increment=0.1, textvariable=self.att_max_var, width=10, justify="center")
        self.att_max_sb.grid(column=1, row=8, sticky="w")

        # att_steps
        self.att_steps_label = ttk.Label(self, text="Attenuation Steps")
        self.att_steps_label.grid(column=0, row=9, sticky="e")

        self.att_steps_var = tk.IntVar(self, 15)
        self.att_steps_sb = ttk.Spinbox(self, from_=1, to=100, textvariable=self.att_steps_var, width=10, justify="center")
        self.att_steps_sb.grid(column=1, row=9, sticky="w")

        # smooth_window
        self.smooth_window_label = ttk.Label(self, text="Smoothing Window")
        self.smooth_window_label.grid(column=0, row=10, sticky="e")

        self.smooth_window_var = tk.IntVar(self, 1)
        self.smooth_window_sb = ttk.Spinbox(self, from_=1, to=100, textvariable=self.smooth_window_var, width=10, justify="center")
        self.smooth_window_sb.grid(column=1, row=10, sticky="w")

        # time_constant
        self.time_constant_label = ttk.Label(self, text="Time Constant (s)")
        self.time_constant_label.grid(column=0, row=11, sticky="e")

        self.time_constant_var = tk.StringVar(self, "0.025")
        self.time_constant_sb = ttk.Spinbox(self, from_=0.001, to=10, increment=0.001, textvariable=self.time_constant_var, width=10, justify="center")
        self.time_constant_sb.grid(column=1, row=11, sticky="w")

        # freq_min
        self.freq_min_label = ttk.Label(self, text="Minimum Frequency (Hz)")
        self.freq_min_label.grid(column=0, row=12, sticky="e")

        self.freq_min_var = tk.StringVar(self, "5000")
        self.freq_min_sb = ttk.Spinbox(self, from_=0, to=80000, increment=0.1, textvariable=self.freq_min_var, width=10, justify="center")
        self.freq_min_sb.grid(column=1, row=12, sticky="w")

        # freq_max
        self.freq_max_label = ttk.Label(self, text="Maximum Frequency (Hz)")
        self.freq_max_label.grid(column=0, row=13, sticky="e")

        self.freq_max_var = tk.StringVar(self, "20000")
        self.freq_max_sb = ttk.Spinbox(self, from_=0, to=80000, increment=0.1, textvariable=self.freq_max_var, width=10, justify="center")
        self.freq_max_sb.grid(column=1, row=13, sticky="w")

        # amplification
        self.amplification_label = ttk.Label(self, text="Amplification")
        self.amplification_label.grid(column=0, row=14, sticky="e")

        self.amplification_var = tk.StringVar(self, "1")
        self.amplification_sb = ttk.Spinbox(self, from_=0, to=1, increment=0.01, textvariable=self.amplification_var, width=10, justify="center")
        self.amplification_sb.grid(column=1, row=14, sticky="w")

        # sound_type
        self.sound_type_label = ttk.Label(self, text="Sound Type")
        self.sound_type_label.grid(column=0, row=15, sticky="e")

        self.sound_var = tk.StringVar(self, "Noise")
        self.sound_type_cb = ttk.Combobox(self, width=10, justify="center", textvariable=self.sound_var)
        self.sound_type_cb.grid(column=1, row=15, sticky="w")
        self.sound_type_cb["state"] = "readonly"
        self.sound_type_cb["values"] = ("Noise", "Pure Tones")
