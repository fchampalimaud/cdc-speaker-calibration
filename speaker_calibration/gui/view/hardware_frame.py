import tkinter as tk
from tkinter import ttk
from speaker_calibration.gui.view.gui_utils import get_ports
from pyharp.device import Device
from pyharp.messages import HarpMessage
from serial.serialutil import SerialException
from tkinter.messagebox import showwarning


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

        self.soundcard_com = tk.StringVar(self, "COMx")
        self.port_cb = ttk.Combobox(self.port_frame, width=8, justify="center", textvariable=self.soundcard_com)
        self.port_cb.grid(column=1, row=0, sticky="w")
        self.port_cb["state"] = "readonly"
        self.port_cb["values"] = get_ports()
        self.port_cb.bind("<<ComboboxSelected>>", self.connect_soundcard)

        self.fs_frame = tk.Frame(self.par_frame)
        self.fs_frame.grid(column=1, row=0, padx=10)

        self.fs_label = ttk.Label(self.fs_frame, text="Sampling Frequency (Hz)")
        self.fs_label.grid(column=0, row=0, sticky="e")

        self.fs_sc = tk.IntVar(self, 192000)
        self.fs_cb = ttk.Combobox(self.fs_frame, width=8, justify="center", textvariable=self.fs_sc, state="readonly", values=[96000, 192000])
        self.fs_cb.grid(column=1, row=0, sticky="w")

        self.soundcard_frame = tk.Frame(self)
        self.soundcard_frame.grid(column=0, row=1, pady=5)

        self.harp_soundcard = tk.IntVar(self, 1)
        self.harp_soundcard_cb = ttk.Checkbutton(self.soundcard_frame, text="Harp SoundCard", variable=self.harp_soundcard)
        self.harp_soundcard_cb.grid(column=0, row=0, padx=5)
        self.harp_soundcard_cb["state"] = tk.DISABLED

        self.sc_id_frame = tk.Frame(self.soundcard_frame)
        self.sc_id_frame.grid(column=1, row=0, padx=5)

        self.sc_id_label = tk.Label(self.sc_id_frame, text="SoundCard ID")
        self.sc_id_label.grid(column=0, row=0, sticky="e")

        self.sc_id_text = ttk.Entry(self.sc_id_frame, width=15, state="disabled")
        self.sc_id_text.grid(column=1, row=0, sticky="w")

        self.harp_amp_frame = tk.Frame(self)
        self.harp_amp_frame.grid(column=0, row=2, pady=5)

        self.harp_audio_amp = tk.IntVar(self, 1)
        self.harp_amp_cb = ttk.Checkbutton(self.harp_amp_frame, text="Harp Amp", variable=self.harp_audio_amp)
        self.harp_amp_cb.grid(column=0, row=0, padx=5)
        self.harp_amp_cb["state"] = tk.DISABLED

        self.amp_id_frame = tk.Frame(self.harp_amp_frame)
        self.amp_id_frame.grid(column=1, row=0, padx=5)

        self.amp_id_label = tk.Label(self.amp_id_frame, text="Amp ID")
        self.amp_id_label.grid(column=0, row=0, sticky="e")

        self.amp_id_text = ttk.Entry(self.amp_id_frame, width=15, state="disabled")
        self.amp_id_text.grid(column=1, row=0, sticky="w")

        # ID frame
        self.id_frame = tk.Frame(self)
        self.id_frame.grid(column=0, row=3, pady=5)

        self.speaker_frame = tk.Frame(self.id_frame)
        self.speaker_frame.grid(column=0, row=0, padx=10)

        self.speaker_id_label = ttk.Label(self.speaker_frame, text="Speaker ID")
        self.speaker_id_label.grid(column=0, row=0, sticky="e")

        self.speaker_id = tk.IntVar(self, 0)
        self.speaker_id_sb = ttk.Spinbox(self.speaker_frame, from_=0, to=1000, increment=1, textvariable=self.speaker_id, width=5, justify="center")
        self.speaker_id_sb.grid(column=1, row=0, sticky="w")

        self.setup_frame = tk.Frame(self.id_frame)
        self.setup_frame.grid(column=1, row=0, padx=10)

        self.setup_id_label = ttk.Label(self.setup_frame, text="Setup ID")
        self.setup_id_label.grid(column=0, row=0, sticky="e")

        self.setup_id = tk.IntVar(self, 0)
        self.setup_id_sb = ttk.Spinbox(self.setup_frame, from_=0, to=1000, increment=1, textvariable=self.setup_id, width=5, justify="center")
        self.setup_id_sb.grid(column=1, row=0, sticky="w")

    def connect_soundcard(self, event):
        if hasattr(self, "soundcard"):
            self.soundcard.disconnect()

        if self.soundcard_com.get() == "Refresh":
            self.port_cb["values"] = get_ports()
            self.soundcard_com.set("COMx")
            return

        try:
            self.soundcard = Device(self.soundcard_com.get())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
            else:
                showwarning("Warning", "This is not a Harp Soundcard.")
                self.soundcard.disconnect()
        except SerialException:
            showwarning("Warning", "This is not a Harp device.")
            self.soundcard_com.set("COMx")
