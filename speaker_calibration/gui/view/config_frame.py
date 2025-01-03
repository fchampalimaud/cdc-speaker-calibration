import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.view.hardware_frame import HardwareFrame
from speaker_calibration.gui.view.plot_config_frame import PlotConfigFrame


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

        # button
        self.run_button = ttk.Button(self, text="Run")
        self.run_button.grid(row=4, column=0, pady=5)
