from pathlib import Path
from typing import Literal, Optional

import numpy as np
from multipledispatch import dispatch
from scipy.signal import butter, lfilter, sosfilt, welch
from scipy.signal.windows import flattop

from speaker_calibration.utils.decorators import greater_than, validate_range


class Sound:
    """
    The class representing a sound.

    Attributes
    ----------
    signal : numpy.ndarray
        The 1D array containing the signal itself.
    time : Optional[numpy.ndarray]
        The 1D array containing the time axis of the signal.
    """

    signal: np.ndarray
    fs: float
    time: Optional[np.ndarray]

    def __init__(
        self,
        signal: np.ndarray,
        fs: float,
        time: Optional[np.ndarray] = None,
    ):
        self._signal = signal
        self._fs = fs
        self._time = time
        self._duration = signal.size / fs

    @property
    def signal(self):
        return self._signal

    @property
    def fs(self):
        return self._fs

    @property
    def time(self):
        return self._time

    @property
    def duration(self):
        return self._duration

    def save(self, filename: Path):
        if self.time is not None:
            sound_array = np.stack((self.time, self.signal), axis=1)
        else:
            sound_array = self.signal

        np.save(filename, sound_array)


class WhiteNoise(Sound):
    def __init__(
        self,
        duration,
        fs,
        amplitude: float = 1,
        ramp_time: float = 0.005,
        filter: bool = False,
        freq_min: float = 5000,
        freq_max: float = 20000,
        eq_filter: Optional[np.ndarray] = None,
        noise_type: Literal["gaussian", "uniform"] = "gaussian",
    ):
        self._amplitude = amplitude
        self._ramp_time = ramp_time
        self._type = noise_type

        noise = self._generate_noise(
            duration,
            fs,
            filter,
            freq_min,
            freq_max,
            eq_filter,
        )

        super().__init__(noise, fs, np.linspace(0, duration, int(fs * duration)))

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def ramp_time(self):
        return self._ramp_time

    @property
    def type(self):
        return self._type

    def _generate_noise(
        self,
        duration,
        fs,
        filter: bool = False,
        freq_min: float = 5000,
        freq_max: float = 20000,
        eq_filter: Optional[np.ndarray] = None,
    ):
        # Calculate the number of samples of the signal
        num_samples = int(fs * duration)

        # Generate the base white noise (either gaussian or uniform)
        if self.type == "gaussian":
            # The gaussian samples are rescaled so that 99% of the samples are between -1 and 1
            signal = 1 / 3 * np.random.randn(num_samples)
        else:
            signal = np.random.uniform(low=-1.0, high=1.0, size=num_samples)

        # Calculate the RMS of the original signal to be used in a future normalization
        rms_original_signal = np.sqrt(np.mean(signal**2))

        # Use the calibration factor to flatten the power spectral density of the signal according to the electronics characteristics
        if eq_filter is not None:
            signal = lfilter(eq_filter, 1, signal)

        # Applies a 16th-order butterworth band-pass filter to the signal
        if filter:
            sos = butter(
                32, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs
            )
            signal = sosfilt(sos, signal)

        # Normalize the signal
        signal = signal / np.sqrt(np.mean(signal**2)) * rms_original_signal

        # Truncate the signal between -1 and 1
        signal = self.amplitude * signal
        signal[(signal < -1)] = -1
        signal[(signal > 1)] = 1

        # Apply a ramp at the beginning and at the end of the signal and the input amplitude factor
        ramp_samples = int(np.floor(fs * self.ramp_time))
        ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
        ramped_signal = np.concatenate(
            (ramp, np.ones(num_samples - ramp_samples * 2), np.flip(ramp)), axis=None
        )

        return np.multiply(signal, ramped_signal)


class PureTone(Sound):
    def __init__(
        self,
        duration: float,
        fs: int,
        freq: float,
        phase: float = 0,
        amplitude: float = 1,
        ramp_time: float = 0.005,
    ):
        self._freq = freq
        self._phase = phase
        self._amplitude = amplitude
        self._ramp_time = ramp_time

        # Sinusoidal signal generation
        time = np.linspace(0, duration, int(fs * duration))
        signal = amplitude * np.sin(2 * np.pi * freq * time + phase)

        # Apply a ramp at the beginning and at the end of the signal
        ramp_samples = int(np.floor(fs * ramp_time))
        ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
        ramped_signal = np.concatenate(
            (ramp, np.ones(time.size - ramp_samples * 2), np.flip(ramp)), axis=None
        )

        super().__init__(np.multiply(signal, ramped_signal), fs, time)

    @property
    def freq(self):
        return self._freq

    @property
    def phase(self):
        return self._phase

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def ramp_time(self):
        return self._ramp_time
