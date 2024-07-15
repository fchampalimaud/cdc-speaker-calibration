import tkinter as tk
from tkinter import ttk
from gui_utils import get_ports


class HardwareFrame(ttk.LabelFrame):
    def __init__(self, container, text="Hardware Settings"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)

        # Parameters Frame
        self.par_frame = tk.Frame(self)
        self.par_frame.grid(column=0, row=0, pady=5)

        self.port_frame = tk.Frame(self.par_frame)
        self.port_frame.grid(column=0, row=0, padx=10)

        self.port_label = ttk.Label(self.port_frame, text="Port")
        self.port_label.grid(column=0, row=0, sticky="e")

        self.port_var = tk.StringVar(self, "COMx")
        self.port_cb = ttk.Combobox(self.port_frame, width=8, justify="center", textvariable=self.port_var)
        self.port_cb.grid(column=1, row=0, sticky="w")
        self.port_cb["state"] = "readonly"
        self.port_cb["values"] = get_ports()

        self.fs_frame = tk.Frame(self.par_frame)
        self.fs_frame.grid(column=1, row=0, padx=10)

        self.fs_label = ttk.Label(self.fs_frame, text="Sampling Frequency (Hz)")
        self.fs_label.grid(column=0, row=0, sticky="e")

        self.fs_var = tk.StringVar(self, "192000")
        self.fs_cb = ttk.Combobox(self.fs_frame, width=8, justify="center", textvariable=self.fs_var)
        self.fs_cb.grid(column=1, row=0, sticky="w")
        self.fs_cb["state"] = "readonly"
        self.fs_cb["values"] = [96000, 192000]

        self.soundcard_frame = tk.Frame(self)
        self.soundcard_frame.grid(column=0, row=1, pady=5)

        self.soundcard_var = tk.IntVar(self, 1)
        self.harp_soundcard_cb = ttk.Checkbutton(self.soundcard_frame, text="Harp SoundCard", variable=self.soundcard_var)
        self.harp_soundcard_cb.grid(column=0, row=0, padx=5)

        self.sc_id_frame = tk.Frame(self.soundcard_frame)
        self.sc_id_frame.grid(column=1, row=0, padx=5)

        self.sc_id_label = tk.Label(self.sc_id_frame, text="SoundCard ID")
        self.sc_id_label.grid(column=0, row=0, sticky="e")

        self.sc_id_text = ttk.Entry(self.sc_id_frame, width=15)
        self.sc_id_text.grid(column=1, row=0, sticky="w")

        self.harp_amp_frame = tk.Frame(self)
        self.harp_amp_frame.grid(column=0, row=2, pady=5)

        self.amp_var = tk.IntVar(self, 1)
        self.harp_amp_cb = ttk.Checkbutton(self.harp_amp_frame, text="Harp Amp", variable=self.amp_var)
        self.harp_amp_cb.grid(column=0, row=0, padx=5)

        self.amp_id_frame = tk.Frame(self.harp_amp_frame)
        self.amp_id_frame.grid(column=1, row=0, padx=5)

        self.amp_id_label = tk.Label(self.amp_id_frame, text="Amp ID")
        self.amp_id_label.grid(column=0, row=0, sticky="e")

        self.amp_id_text = ttk.Entry(self.amp_id_frame, width=15)
        self.amp_id_text.grid(column=1, row=0, sticky="w")

        # ID frame
        self.id_frame = tk.Frame(self)
        self.id_frame.grid(column=0, row=3, pady=5)

        self.speaker_frame = tk.Frame(self.id_frame)
        self.speaker_frame.grid(column=0, row=0, padx=10)

        self.speaker_id_label = ttk.Label(self.speaker_frame, text="Speaker ID")
        self.speaker_id_label.grid(column=0, row=0, sticky="e")

        self.speaker_var = tk.IntVar(self, 0)
        self.speaker_id_sb = ttk.Spinbox(self.speaker_frame, from_=0, to=1000, increment=1, textvariable=self.speaker_var, width=5, justify="center")
        self.speaker_id_sb.grid(column=1, row=0, sticky="w")

        self.setup_frame = tk.Frame(self.id_frame)
        self.setup_frame.grid(column=1, row=0, padx=10)

        self.setup_id_label = ttk.Label(self.setup_frame, text="Setup ID")
        self.setup_id_label.grid(column=0, row=0, sticky="e")

        self.setup_var = tk.IntVar(self, 0)
        self.setup_id_sb = ttk.Spinbox(self.setup_frame, from_=0, to=1000, increment=1, textvariable=self.setup_var, width=5, justify="center")
        self.setup_id_sb.grid(column=1, row=0, sticky="w")
