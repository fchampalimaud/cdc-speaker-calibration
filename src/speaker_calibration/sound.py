from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, cast

import numpy as np
from scipy.signal import butter, chirp, lfilter, resample, sosfilt, welch
from scipy.signal.windows import flattop

from speaker_calibration.utils import REFERENCE_PRESSURE


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

    # TODO: rethink this
    @signal.setter
    def signal(self, value: np.ndarray):
        self._signal = value

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
        duration: float,
        fs: float,
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
        signal = cast(np.ndarray, signal)
        signal = signal / np.sqrt(np.mean(signal**2)) * rms_original_signal

        # Truncate the signal between -1 and 1
        signal = self.amplitude * signal
        signal[(signal < -1)] = -1
        signal[(signal > 1)] = 1

        # Apply a ramp at the beginning and at the end of the signal and the input amplitude factor
        signal = _apply_ramp(signal, fs, self.ramp_time)

        return signal


class PureTone(Sound):
    def __init__(
        self,
        duration: float,
        fs: float,
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
        signal = _apply_ramp(signal, fs, self.ramp_time)

        super().__init__(signal, fs, time)

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


class Chirp(Sound):
    def __init__(
        self,
        duration: float,
        fs: float,
        freq_start: float,
        freq_end: float,
        phase: float = 0,
        amplitude: float = 1,
        ramp_time: float = 0.005,
        chirp_type: Literal[
            "linear", "quadratic", "logarithmic", "hyperbolic"
        ] = "logarithmic",
    ):
        self._freq_start = freq_start
        self._freq_end = freq_end
        self._phase = phase
        self._amplitude = amplitude
        self._ramp_time = ramp_time
        self._type = chirp_type

        time = np.linspace(0, duration, int(fs * duration))
        signal = chirp(
            time,
            self.freq_start,
            duration,
            self.freq_end,
            method=self.type,
            phi=self.phase,
        )

        # Apply ramp
        signal = _apply_ramp(signal, fs, self.ramp_time)

        # Calculate inverse filter
        log_param = duration / np.log(self.freq_end / self.freq_start)
        self._inverse_filter = np.flip(signal) * np.exp(-time / log_param)

        super().__init__(signal, fs, time)

    @property
    def freq_start(self):
        return self._freq_start

    @property
    def freq_end(self):
        return self._freq_end

    @property
    def phase(self):
        return self._phase

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def ramp_time(self):
        return self._ramp_time

    @property
    def type(self):
        return self._type

    @property
    def inverse_filter(self):
        return self._inverse_filter


class RecordedSound(Sound):
    def __init__(
        self,
        signal: np.ndarray,
        fs: float,
        time: Optional[np.ndarray] = None,
        mic_factor: Optional[float] = None,
        mic_response: Optional[np.ndarray] = None,
    ):
        super().__init__(signal, fs, time)

        if mic_factor is not None:
            self._mic_factor = mic_factor
        else:
            self._mic_factor = 1

        self._mic_response = mic_response

        self.calculate_db_spl()

    def calculate_db_spl(
        self,
        mic_factor: Optional[float] = None,
        reference_pressure: float = REFERENCE_PRESSURE,
        domain: Literal["time", "freq"] = "time",
    ):
        if mic_factor is not None:
            self.mic_factor = mic_factor

        # Remove the beginning and end of the acquisition
        signal = self.signal[int(0.1 * self.signal.size) : int(0.9 * self.signal.size)]

        # Calculate dB SPL either in the time or in the frequency domain
        if domain == "time":
            signal_pascal = signal / self.mic_factor
            rms = np.sqrt(np.mean(signal_pascal**2))
            self._db_spl = 20 * np.log10(rms / reference_pressure)
        else:
            fft = np.abs(np.fft.fft(signal)) ** 2
            rms = np.sqrt(np.sum(fft) / (fft.size**2 * self.mic_factor**2))
            self._db_spl = 20 * np.log10(rms / reference_pressure)

        return self._db_spl

    # TODO: window?
    def fft_welch(
        self,
        time_cons: float,
        win=None,
        mic_response: Optional[np.ndarray] = None,
    ):
        if mic_response is not None:
            self.mic_response = mic_response

        window = flattop(int(time_cons * self.fs), sym=False)
        win_sum_squared = np.sum(window**2)
        win_sum = np.sum(window)

        self._freq, fft = welch(
            self.signal,
            fs=self.fs,
            window=window,
        )

        power_spectrum = fft * (self.fs * win_sum_squared / 2)
        power_spectrum[0] *= 2

        if self.signal.size % 2 == 0:
            power_spectrum[-1] *= 2

        abs_y_win = np.sqrt(power_spectrum)

        self._fft = (2 / win_sum) * abs_y_win

        return self._freq, self._fft

    @property
    def db_spl(self):
        return self._db_spl

    @property
    def mic_factor(self):
        return self._mic_factor

    @mic_factor.setter
    def mic_factor(self, value: float):
        self._mic_factor = value

    @property
    def mic_response(self):
        return self._mic_response

    @mic_response.setter
    def mic_response(self, value: np.ndarray):
        self._mic_response = value

    @property
    def freq(self):
        self._freq

    @property
    def fft(self):
        self._fft

    @staticmethod
    def resample(sound: RecordedSound, fs: float) -> RecordedSound:
        signal = resample(
            sound.signal,
            int(fs * sound.duration),
        )

        resampled_sound = RecordedSound(
            np.array(signal), fs, sound.signal, sound.mic_factor
        )

        return resampled_sound


def _apply_ramp(signal: np.ndarray, fs: float, ramp_time: float = 0.005):
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = np.linspace(0, 1, ramp_samples) ** 2
    ramp_signal = np.concatenate(
        (ramp, np.ones(signal.size - ramp_samples * 2), np.flip(ramp)), axis=None
    )

    return np.multiply(signal, ramp_signal)
