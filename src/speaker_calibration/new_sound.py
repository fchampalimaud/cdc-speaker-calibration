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
        self._duration = signal.size / 192000.0

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
        # Calculate the number of samples of the signal
        num_samples = int(fs * duration)

        # Generate the base white noise (either gaussian or uniform)
        if noise_type == "gaussian":
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
        signal = amplitude * signal
        signal[(signal < -1)] = -1
        signal[(signal > 1)] = 1

        # Apply a ramp at the beginning and at the end of the signal and the input amplitude factor
        ramp_samples = int(np.floor(fs * ramp_time))
        ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
        ramped_signal = np.concatenate(
            (ramp, np.ones(num_samples - ramp_samples * 2), np.flip(ramp)), axis=None
        )
        white_noise = Sound(
            np.multiply(signal, ramped_signal),
            np.linspace(0, duration, int(fs * duration)),
        )


# @greater_than("duration", 0)
# @greater_than("fs", 0)
# @validate_range("amplitude", 0, 1)
# @greater_than("ramp_time", 0)
# @validate_range("freq_min", 0, 80000)
# @validate_range("freq_max", 0, 80000)
# def white_noise(
#     duration: float,
#     fs: int,
#     amplitude: float = 1,
#     ramp_time: float = 0.005,
#     filter: bool = True,
#     freq_min: float = 0,
#     freq_max: float = 80000,
#     inverse_filter: Optional[np.ndarray] = None,
#     noise_type: Literal["gaussian", "uniform"] = "gaussian",
# ) -> Sound:
#     """
#     Generates a white noise.

#     Parameters
#     ----------
#     duration : float
#         Duration of the signal generated (s).
#     fs : int
#         Sampling frequency of the signal being generated (Hz).
#     amplitude : float, optional
#         Amplitude factor of the speakers.
#     ramp_time : float, optional
#         Ramp time of the signal (s).
#     filter : bool, optional
#         Whether to filter the signal or not.
#     freq_min : float, optional
#         Minimum frequency to consider to pass band (Hz).
#     freq_max : float, optional
#         Maximum frequency to consider to pass band (Hz).
#     inverse_filter : Optional[np.ndarray], optional
#         The inverse filter to be used to flatten the power spectral density of the sound played by the speakers.
#     noise_type : Literal["gaussian", "uniform"], optional
#         Whether the generated white noise should be gaussian or uniform.

#     Returns
#     -------
#     white_noise : Sound
#         The generated white noise.
#     """
#     # Calculate the number of samples of the signal
#     num_samples = int(fs * duration)

#     # Generate the base white noise (either gaussian or uniform)
#     if noise_type == "gaussian":
#         # The gaussian samples are rescaled so that 99% of the samples are between -1 and 1
#         signal = 1 / 3 * np.random.randn(num_samples)
#     else:
#         signal = np.random.uniform(low=-1.0, high=1.0, size=num_samples)

#     # Calculate the RMS of the original signal to be used in a future normalization
#     rms_original_signal = np.sqrt(np.mean(signal**2))

#     # Use the calibration factor to flatten the power spectral density of the signal according to the electronics characteristics
#     if inverse_filter is not None:
#         signal = lfilter(inverse_filter, 1, signal)

#     # Applies a 16th-order butterworth band-pass filter to the signal
#     if filter:
#         sos = butter(32, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs)
#         signal = sosfilt(sos, signal)

#     # Normalize the signal
#     signal = signal / np.sqrt(np.mean(signal**2)) * rms_original_signal

#     # Truncate the signal between -1 and 1
#     signal = amplitude * signal
#     signal[(signal < -1)] = -1
#     signal[(signal > 1)] = 1

#     # Apply a ramp at the beginning and at the end of the signal and the input amplitude factor
#     ramp_samples = int(np.floor(fs * ramp_time))
#     ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
#     ramped_signal = np.concatenate(
#         (ramp, np.ones(num_samples - ramp_samples * 2), np.flip(ramp)), axis=None
#     )
#     white_noise = Sound(
#         np.multiply(signal, ramped_signal),
#         np.linspace(0, duration, int(fs * duration)),
#     )

#     return white_noise
