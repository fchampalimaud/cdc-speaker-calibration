import os
import threading
from abc import ABC, abstractmethod
from typing import Literal, Optional

from pyharp.device import Device
from pyharp.messages import HarpMessage

from speaker_calibration.utils.decorators import validate_range


class SoundCard(ABC):
    fs: float

    def __init__(self, fs):
        self.fs = fs

    @abstractmethod
    def play(self):
        pass


class HarpSoundCard(SoundCard):
    device: Device

    def __init__(self, com_port: str, fs: Literal[96000, 192000] = 192000):
        super().__init__(fs)
        self.device = Device(com_port)

    @validate_range("index", 2, 31)
    def play(self, index: int = 2, start_event: Optional[threading.Event] = None):
        """
        Plays a sound from the Harp SoundCard.

        Parameters
        ----------
        index : int, optional
            the index in which the sound is stored.
        start_event : threading.Event, optional
            a thread event used to synchronize the start of the sound with the start of the recording. If `start_event` is not provided, the sound will play as soon as possible.
        """
        # Wait for the event if it exists
        if start_event is not None:
            start_event.wait()
        # Play the sound
        self.device.send(HarpMessage.WriteU16(32, index).frame, False)

    @validate_range("index", 2, 31)
    def load_sound(self, filename, index: int = 2):
        """
        Loads the sound to the Harp SoundCard.

        Parameters
        ----------
        filename : str
            the path to the file containing the sound to be uploaded to the Harp SoundCard.
        index : int, optional
            the index in which the sound will be stored.
        """
        os.system(
            "cmd /c .\\assets\\toSoundCard.exe "
            + filename
            + " "
            + str(index)
            + " 0 "
            + str(self.fs)
        )


# TODO
# class ComputerSoundCard(SoundCard):
