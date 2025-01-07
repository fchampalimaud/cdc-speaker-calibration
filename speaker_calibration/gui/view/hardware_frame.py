from tkinter import ttk
from speaker_calibration.utils.gui_utils import get_ports
from pyharp.device import Device
from pyharp.messages import HarpMessage
from serial.serialutil import SerialException
from tkinter.messagebox import showwarning
from speaker_calibration.utils.gui_utils import (
    LabeledSpinbox,
    LabeledCombobox,
    Checkbox,
    LabeledEntry,
)


class HardwareFrame(ttk.LabelFrame):
    def __init__(self, container, text="Hardware Settings"):
        super().__init__(container, text=text)

        for i in range(2):
            self.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.is_harp = Checkbox(
            self,
            "Harp SoundCard",
            0,
            0,
            columnspan=2,
            default_value=True,
            command=self.change_frame,
        )

        self.speaker_id = LabeledSpinbox(
            self, "Speaker ID", 0, 0, 1000, 1, row=1, column=0
        )
        self.setup_id = LabeledSpinbox(self, "Setup ID", 0, 0, 1000, 1, row=1, column=1)

        self.frames = [HarpHardwareFrame(self), NonHarpHardwareFrame(self)]
        self.change_frame()

    def change_frame(self, event=None):
        if self.is_harp.get():
            self.frames[0].grid(row=2, column=0, columnspan=2)
            self.frames[1].grid_forget()
        else:
            self.frames[1].grid(row=2, column=0, columnspan=2)
            self.frames[0].grid_forget()


class HarpHardwareFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        for i in range(2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.grid_columnconfigure(i, weight=1)

        self.port = LabeledCombobox(
            self,
            "Port",
            row=0,
            column=0,
            value_list=get_ports(),
            default_value="COMx",
            combobox_width=8,
        )
        self.port.combobox.bind("<<ComboboxSelected>>", self.connect_soundcard)

        self.fs = LabeledCombobox(
            self,
            "Sampling Frequency (Hz)",
            row=0,
            column=1,
            value_list=[96000, 192000],
            default_value=192000,
            combobox_width=8,
        )

        self.soundcard_id = LabeledEntry(self, "SoundCard ID", 1, 0)
        self.audio_amp_id = LabeledEntry(self, "Audio Amplifier ID", 1, 1)

    def connect_soundcard(self, event):
        if hasattr(self, "soundcard"):
            self.soundcard.disconnect()

        if self.port.get() == "Refresh":
            self.port.set_values(get_ports())
            self.port.set("COMx")
            return

        try:
            self.soundcard = Device(self.port.get())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
            else:
                showwarning("Warning", "This is not a Harp Soundcard.")
                self.port.set("COMx")
                self.soundcard.disconnect()
        except SerialException:
            showwarning("Warning", "This is not a Harp device.")
            self.port.set("COMx")


class NonHarpHardwareFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        for i in range(1):
            self.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.grid_columnconfigure(i, weight=1)

        self.port = LabeledCombobox(
            self,
            "SoundCard",
            row=0,
            column=0,
            combobox_width=8,
        )

        self.fs = LabeledSpinbox(
            self,
            "Sampling Frequency (Hz)",
            192000,
            1,
            192000,
            1,
            row=0,
            column=1,
        )
