import tkinter as tk

# from speaker_calibration.gui.view.gui_utils import spinbox_row
from speaker_calibration.gui.view.settings_frames.general_frame import GeneralFrame
from speaker_calibration.gui.view.settings_frames.noise_frame import NoiseFrame
from speaker_calibration.gui.view.gui_utils import SpinboxesFrame


class SettingsWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        # Configuration of the window
        # self.geometry("350x850")
        # self.resizable(0, 0)
        self.iconbitmap("docs/img/favicon.ico")
        # The window is only closed when the application closes
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        # Hides the window
        self.withdraw()
        # Configures columns of the window
        self.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.general = GeneralFrame(self)
        self.general.grid(column=0, row=0)

        # separator = ttk.Separator(self, orient="horizontal")
        # separator.grid(column=0, row=1)

        self.noise = NoiseFrame(self)
        self.noise.grid(column=0, row=1)

        # separator = ttk.Separator(self, orient="horizontal")
        # separator.grid(column=0, row=3)

        self.pure_tone = SpinboxesFrame(
            self, "config/frames/pure_tone_init.csv", "Pure Tone Calibration"
        )
        self.pure_tone.grid(column=0, row=2)
