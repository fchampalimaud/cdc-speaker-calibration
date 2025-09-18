import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Literal, Optional

import numpy as np
from multipledispatch import dispatch
from pydantic.types import StringConstraints
from pyharp.device import Device
from pyharp.messages import HarpMessage
from typing_extensions import Annotated

from speaker_calibration.sound import Sound


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


@dispatch(Sound, str, speaker_side=str)
def create_sound_file(
    signal: Sound,
    filename: str,
    speaker_side: Literal["both", "left", "right"] = "both",
) -> None:
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal : Sound
        The signal to be written to the .bin file.
    filename : str
        The name of the .bin file.
    speaker_side : Literal["both", "left", "right"], optional
        Whether the sound plays in both speakers or in a single one. Possible values: "both", "left" or "right.
    """
    # Transform the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1

    if speaker_side == "both":
        wave_left = amplitude24bits * signal.signal
        wave_right = amplitude24bits * signal.signal
    elif speaker_side == "left":
        wave_left = amplitude24bits * signal.signal
        wave_right = 0 * signal.signal
    else:
        wave_left = 0 * signal.signal
        wave_right = amplitude24bits * signal.signal

    # Group the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Write the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)


@dispatch(Sound, Sound, str)
def create_sound_file(
    signal_left: Sound,
    signal_right: Sound,
    filename: str,
) -> None:
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal_left : Sound
        The signal to be written to the .bin file that is going to be played by the left speaker.
    signal_right : Sound
        The signal to be written to the .bin file that is going to be played by the right speaker.
    filename : str
        The name of the .bin file.
    """
    # Transform the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1
    wave_left = amplitude24bits * signal_left.signal
    wave_right = amplitude24bits * signal_right.signal

    # Group the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Write the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)


# TODO
# class ComputerSoundCard(SoundCard):
