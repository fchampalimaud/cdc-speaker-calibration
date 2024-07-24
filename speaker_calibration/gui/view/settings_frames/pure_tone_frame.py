from tkinter import ttk
import numpy as np
from speaker_calibration.gui.view.gui_utils import spinbox_row


class PureToneFrame(ttk.LabelFrame):
    def __init__(self, container, text="Pure Tone Calibration"):
        super().__init__(container, text=text)

        # Loads some configuration parameters regarding the layout of the widgets in the window
        init = np.loadtxt("config/pure_tone_init.csv", dtype=str, delimiter=",", skiprows=1)

        # Configures columns of the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initializes the spinboxes arrays
        self.variables = np.zeros(init.shape[0], dtype=object)
        self.labels = np.zeros(init.shape[0], dtype=object)
        self.spinboxes = np.zeros(init.shape[0], dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(init.shape[0]):
            self.grid_rowconfigure(i, weight=1)
            self.labels[i], self.variables[i], self.spinboxes[i] = spinbox_row(
                self,
                init[i, 0],
                float(init[i, 1]),
                float(init[i, 1]),
                float(init[i, 2]),
                float(init[i, 3]),
                i,
                int(init[i, 4]),
                int(init[i, 5]),
            )
