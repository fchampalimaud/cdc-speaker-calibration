import tkinter as tk
from tkinter import ttk
from configuration_window import ConfigurationWindow
from hardware_frame import HardwareFrame
from pyharp.device import Device
from pyharp.messages import HarpMessage
from serial.serialutil import SerialException
from test_frame import TestFrame
import numpy as np
from main import noise_calibration


class OptionsFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.config_window = ConfigurationWindow()

        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, justify="center", textvariable=self.combobox_var)
        self.combobox.grid(column=0, row=1)
        self.combobox["values"] = ("PSD Signal", "Inverse Filter", "Calibration Signals", "Calibration Curve", "Test Signals", "Test Plot")

        # button
        self.config_button = ttk.Button(self, text="Open Configuration Window", command=self.config_window.deiconify)
        self.config_button.grid(column=0, row=2)

        # label
        self.hardware_frame = HardwareFrame(self)
        self.hardware_frame.grid(column=0, row=3)

        self.hardware_frame.port_cb.bind("<<ComboboxSelected>>", self.connect_soundcard)

        self.test_frame = TestFrame(self)
        self.test_frame.grid(column=0, row=4)

        self.run_frame = ttk.LabelFrame(self)
        self.run_frame.grid(column=0, row=5)

        for i in range(3):
            self.run_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.run_frame.grid_rowconfigure(i, weight=1)

        self.sf_var = tk.IntVar(self.run_frame, 1)
        self.run_cb_sf = ttk.Checkbutton(self.run_frame, text="Speaker Filter", variable=self.sf_var, onvalue="1", offvalue="0")
        self.run_cb_sf.grid(row=0, column=0, pady=5, padx=5)
        self.cc_var = tk.IntVar(self.run_frame, 1)
        self.run_cb_cc = ttk.Checkbutton(self.run_frame, text="Calibration Curve", variable=self.cc_var)
        self.run_cb_cc.grid(row=0, column=1, pady=5, padx=5)
        self.tc_var = tk.IntVar(self.run_frame, 1)
        self.run_cb_tc = ttk.Checkbutton(self.run_frame, text="Test Calibration", variable=self.tc_var)
        self.run_cb_tc.grid(row=0, column=2, pady=5, padx=5)

        # button
        self.run_button = ttk.Button(self.run_frame, text="Run", command=self.run_calibration)
        self.run_button.grid(row=1, column=1, pady=5)

    def connect_soundcard(self, event):
        if hasattr(self, "soundcard"):
            self.soundcard.disconnect()

        try:
            self.soundcard = Device(self.hardware_frame.port_var.get())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
        except SerialException:
            print("This is not a Harp device.")

    def run_calibration(self):
        self.config_window.load_input_parameters()
        self.calibration_factor, self.fit_parameters = noise_calibration(
            float(self.hardware_frame.fs_var.get()),
            self.config_window.input_parameters,
            self.calibration_factor if hasattr(self, "calibration_factor") else None,
            np.array([float(self.test_frame.slope_var.get()), float(self.test_frame.intercept_var.get())]),
            float(self.test_frame.min_var.get()),
            float(self.test_frame.max_var.get()),
            self.test_frame.steps_var.get(),
            self.sf_var.get(),
            self.cc_var.get(),
            self.tc_var.get(),
        )

        np.savetxt(
            "output/calibration_factor_speaker" + str(self.hardware_frame.speaker_var.get()) + "_setup" + str(self.hardware_frame.setup_var.get()) + ".csv",
            self.calibration_factor,
            delimiter=",",
            fmt="%f",
        )
        np.savetxt(
            "output/fit_parameters_speaker" + str(self.hardware_frame.speaker_var.get()) + "_setup" + str(self.hardware_frame.setup_var.get()) + ".csv",
            self.fit_parameters,
            delimiter=",",
            fmt="%f",
        )
