import tkinter as tk
from tkinter import ttk
import numpy as np
from speaker_calibration.gui.view.gui_utils import spinbox_row


class SettingsWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        # Loads some configuration parameters regarding the layout of the widgets in the window
        init_settings = np.loadtxt("config/settings_window_init.csv", dtype=str, delimiter=",", skiprows=1)

        # Configuration of the window
        self.geometry("300x600")
        self.resizable(0, 0)
        self.iconbitmap("docs/img/favicon.ico")
        # The window is only closed when the application closes
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        # Hides the window
        self.withdraw()
        # Configures columns of the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initializes the spinboxes arrays
        self.settings_values = np.zeros(init_settings.shape[0], dtype=object)
        self.labels = np.zeros(init_settings.shape[0], dtype=object)
        self.spinboxes = np.zeros(init_settings.shape[0], dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(init_settings.shape[0] + 1):
            self.grid_rowconfigure(i, weight=1)
            if i < init_settings.shape[0]:
                self.labels[i], self.settings_values[i], self.spinboxes[i] = spinbox_row(
                    self,
                    init_settings[i, 0],
                    float(init_settings[i, 1]),
                    float(init_settings[i, 1]),
                    float(init_settings[i, 2]),
                    float(init_settings[i, 3]),
                    i,
                    int(init_settings[i, 4]),
                    int(init_settings[i, 5]),
                )

        # Configures the row containing the combobox it is possible to choose the type of sound to use in a calibration
        self.sound_type = tk.StringVar(self, "Noise")
        self.sound_type_label = ttk.Label(self, text="Sound Type")
        self.sound_type_label.grid(row=self.spinboxes.size, column=0, sticky="e")
        self.sound_type_cb = ttk.Combobox(self, width=10, justify="center", textvariable=self.sound_type, state="disabled", values=["Noise", "Pure Tones"])
        self.sound_type_cb.grid(row=self.spinboxes.size, column=1, sticky="w")
