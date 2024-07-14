import tkinter as tk
from tkinter import ttk
import numpy as np
from gui_utils import spinbox_row
import yaml
from classes import InputParameters


class ConfigurationWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        init_config = np.loadtxt("config/config_window_init.csv", dtype=str, delimiter=",", skiprows=1)

        with open("config/settings.yml", "r") as file:
            settings_dict = yaml.safe_load(file)
        settings_array = list(settings_dict.values())
        self.settings_keys = list(settings_dict.keys())

        self.geometry("300x600")
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
        self.iconbitmap("docs/img/favicon.ico")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.labels = np.zeros(init_config.shape[0], dtype=object)
        self.spinbox_variables = np.zeros(init_config.shape[0], dtype=object)
        self.spinboxes = np.zeros(init_config.shape[0], dtype=object)
        for i in range(init_config.shape[0] + 1):
            self.grid_rowconfigure(i, weight=1)
            if i < init_config.shape[0]:
                self.labels[i], self.spinbox_variables[i], self.spinboxes[i] = spinbox_row(
                    self,
                    init_config[i, 0],
                    float(settings_array[i]),
                    float(init_config[i, 1]),
                    float(init_config[i, 2]),
                    float(init_config[i, 3]),
                    i,
                    int(init_config[i, 4]),
                    int(init_config[i, 5]),
                )

        # sound_type
        self.sound_type_label = ttk.Label(self, text="Sound Type")
        self.sound_type_label.grid(row=self.spinboxes.size, column=0, sticky="e")

        self.sound_var = tk.StringVar(self, settings_array[-1])
        self.sound_type_cb = ttk.Combobox(self, width=10, justify="center", textvariable=self.sound_var)
        self.sound_type_cb.grid(row=self.spinboxes.size, column=1, sticky="w")
        self.sound_type_cb["state"] = "readonly"
        self.sound_type_cb["values"] = ("Noise", "Pure Tones")

    def load_input_parameters(self):
        values = []
        for i in range(self.spinbox_variables.size):
            if isinstance(self.spinbox_variables[i], tk.StringVar):
                values.append(float(self.spinbox_variables[i].get()))
            else:
                values.append(int(self.spinbox_variables[i].get()))
        values.append(self.sound_var.get())

        self.input_parameters = InputParameters(dict(zip(self.settings_keys, values)))
