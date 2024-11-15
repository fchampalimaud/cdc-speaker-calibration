import tkinter as tk
from tkinter import ttk

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
        for i in range(2):
            self.grid_rowconfigure(i, weight=1)

        self.general = GeneralFrame(self)
        self.general.grid(column=0, row=0)

        # separator = ttk.Separator(self, orient="horizontal")
        # separator.grid(column=0, row=1)

        self.frame = ttk.Frame(self)
        self.frame.grid(column=0, row=1)

        self.frames = {}
        self.frames[0] = NoiseFrame(self.frame)
        self.frames[0].grid(column=0, row=0)
        self.frames[1] = SpinboxesFrame(
            self.frame, "config/frames/pure_tone_init.csv", "Pure Tone Calibration"
        )
        self.frames[1].grid(column=0, row=0)

        self.general.sound_type_cb.bind("<<ComboboxSelected>>", self.change_frame)
        self.change_frame()
        # self.noise.grid(column=0, row=1)

        # separator = ttk.Separator(self, orient="horizontal")
        # separator.grid(column=0, row=3)

        # self.pure_tone.grid(column=0, row=2)

    def change_frame(self, event=None):
        if self.general.sound_type.get() == "Noise":
            frame = self.frames[0]
        elif self.general.sound_type.get() == "Pure Tones":
            frame = self.frames[1]

        frame.tkraise()
