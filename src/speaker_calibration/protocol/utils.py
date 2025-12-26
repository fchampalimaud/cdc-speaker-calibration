import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional

from scipy.signal import butter, sosfilt

from speaker_calibration.config import (
    NoiseProtocolSettings,
    Paths,
    PureToneProtocolSettings,
)
from speaker_calibration.recording import RecordingDevice
from speaker_calibration.sound import RecordedSound
from speaker_calibration.soundcards import SoundCard


class Protocol(ABC):
    def __init__(
        self,
        settings: NoiseProtocolSettings | PureToneProtocolSettings,
        soundcard: SoundCard,
        adc: RecordingDevice,
        output_path: Path,
        paths: Paths,
        callback: Optional[Callable] = None,
    ):
        self.settings = settings
        self.soundcard = soundcard
        self.adc = adc
        self.output_path = output_path
        self.paths = paths
        self.callback = callback

    @abstractmethod
    def sound_sweep(self):
        pass

    def record_sound(
        self,
        filename: Path,
        duration: float,
        amplitude: float = 1,
        filter: bool = False,
    ) -> RecordedSound:
        """
        Records the sounds.

        Parameters
        ----------
        filename : Path
            The path to the file to which the sound will be saved to and from which the sound is upload from (in case a Harp SoundCard is used).
        duration : float
            The duration of the sound (s).
        filter : bool, optional
            Indicates whether the acquired signal should be filtered or not.

        Returns
        -------
        sound : Sound
            The recorded sound.
        """
        # Create the result list to pass to the recording thread
        result = []

        # Create the start event and the threads that will play and record the sound
        start_event = threading.Event()
        play_thread = threading.Thread(
            target=self.soundcard.play,
            kwargs={"amplitude": amplitude, "start_event": start_event},
        )
        record_thread = threading.Thread(
            target=self.adc.record_signal,
            args=[duration],
            kwargs={
                "start_event": start_event,
                "result": result,
                "filename": filename,
            },
        )

        # Start both threads
        record_thread.start()
        play_thread.start()

        # Activates the event in order to synchronize the sound being played with the acquisition
        time.sleep(0.1)
        start_event.set()
        record_thread.join()

        # Filter the acquired signal if desired
        if filter:
            sos = butter(
                32,
                [self.settings.filter.min_freq, self.settings.filter.max_freq],
                btype="bandpass",
                output="sos",
                fs=self.adc.fs,
            )
            result[0].signal = sosfilt(sos, result[0].signal)

        return result[0]
