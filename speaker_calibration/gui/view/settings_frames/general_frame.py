import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.view.gui_utils import spinbox_row
import numpy as np


class GeneralFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # Loads some configuration parameters regarding the layout of the widgets in the window
        init = np.loadtxt(
            "config/frames/general_init.csv", dtype=str, delimiter=",", skiprows=1
        )

        # Configures columns of the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Configures the row containing the combobox it is possible to choose the type of sound to use in a calibration
        self.sound_type = tk.StringVar(self, "Noise")
        self.sound_type_label = ttk.Label(self, text="Sound Type")
        self.sound_type_label.grid(row=0, column=0, sticky="e")
        self.sound_type_cb = ttk.Combobox(
            self,
            width=10,
            justify="center",
            textvariable=self.sound_type,
            state="disabled",
            values=["Noise", "Pure Tones"],
        )
        self.sound_type_cb.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        # Initializes the spinboxes arrays
        self.variables = np.zeros(init.shape[0], dtype=object)
        self.labels = np.zeros(init.shape[0], dtype=object)
        self.spinboxes = np.zeros(init.shape[0], dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(init.shape[0]):
            self.grid_rowconfigure(i + 1, weight=1)
            self.labels[i], self.variables[i], self.spinboxes[i] = spinbox_row(
                self,
                init[i, 0],
                float(init[i, 1]),
                float(init[i, 1]),
                float(init[i, 2]),
                float(init[i, 3]),
                i + 1,
                int(init[i, 4]),
                int(init[i, 5]),
            )
