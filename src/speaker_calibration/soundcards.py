import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Literal, Optional

from pydantic.types import StringConstraints
from pyharp.device import Device
from pyharp.messages import HarpMessage
from typing_extensions import Annotated

from speaker_calibration.utils.decorators import validate_range


class SoundCard(ABC):
    """
    The class representing an abstract soundcard from which to implement specific ones.

    Attributes
    ----------
    fs : float | int
        The sampling frequency of the soundcard.
    """

    fs: float | int

    def __init__(self, fs: float | int):
        self.fs = fs

    @abstractmethod
    def play(self):
        """
        Plays a sound. _This is the abstract method to be implemented for the specific soundcards that derive from this abstract class._
        """
        pass


class HarpSoundCard(SoundCard):
    """
    This class is an implementation of the SoundCard class for the Harp SoundCard.

    Attributes
    ----------
    device : Device
        The Harp device object responsible for the serial communication with the device.
    """

    device: Device

    def __init__(
        self,
        serial_port: Annotated[
            str, StringConstraints(pattern=r"^((COM\d+)|(/dev/ttyUSB\d+))$")
        ],
        fs: Literal[96000, 192000] = 192000,
    ):
        super().__init__(fs)
        self.device = Device(serial_port)

    @validate_range("index", 2, 31)
    def play(self, index: int = 2, start_event: Optional[threading.Event] = None):
        """
        Plays a sound from the Harp SoundCard.

        Parameters
        ----------
        index : int, optional
            The index in which the sound is stored.
        start_event : threading.Event, optional
            A thread event used to synchronize the start of the sound with the start of the recording. If `start_event` is not provided, the sound will play as soon as possible.
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
            The path to the file containing the sound to be uploaded to the Harp SoundCard.
        index : int, optional
            The index in which the sound will be stored.
        """
        while True:
            output = os.popen(
                "cmd /c .\\assets\\toSoundCard.exe "
                + filename
                + " "
                + str(index)
                + " 0 "
                + str(self.fs)
            ).read()

            if "Bandwidth: " in output:
                break
            print(output)
            time.sleep(3)


# TODO
# class ComputerSoundCard(SoundCard):
