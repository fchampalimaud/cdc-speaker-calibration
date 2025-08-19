from pathlib import Path
from typing import Literal, Optional

import numpy as np
from multipledispatch import dispatch
from scipy.signal import butter, lfilter, sosfilt

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
    inverse_filter : Optional[numpy.ndarray]
        The 1D array containing the inverse filter of the signal.
    """

    signal: np.ndarray
    time: Optional[np.ndarray]
    inverse_filter: Optional[np.ndarray]

    def __init__(
        self,
        signal: np.ndarray,
        time: Optional[np.ndarray] = None,
        inverse_filter: Optional[np.ndarray] = None,
    ):
        self.signal = signal
        self.time = time
        self.inverse_filter = inverse_filter

    def save(self, filename: Path):
        if self.time is not None:
            sound_array = np.stack((self.time, self.signal), axis=1)
        else:
            sound_array = self.signal

        np.save(filename, sound_array)


@greater_than("duration", 0)
@greater_than("fs", 0)
@validate_range("amplitude", 0, 1)
@greater_than("ramp_time", 0)
@validate_range("freq_min", 0, 80000)
@validate_range("freq_max", 0, 80000)
def white_noise(
    duration: float,
    fs: int,
    amplitude: float = 1,
    ramp_time: float = 0.005,
    filter: bool = True,
    freq_min: float = 0,
    freq_max: float = 80000,
    inverse_filter: Optional[np.ndarray] = None,
    noise_type: Literal["gaussian", "uniform"] = "gaussian",
) -> Sound:
    """
    Generates a white noise.

    Parameters
    ----------
    duration : float
        Duration of the signal generated (s).
    fs : int
        Sampling frequency of the signal being generated (Hz).
    amplitude : float, optional
        Amplitude factor of the speakers.
    ramp_time : float, optional
        Ramp time of the signal (s).
    filter : bool, optional
        Whether to filter the signal or not.
    freq_min : float, optional
        Minimum frequency to consider to pass band (Hz).
    freq_max : float, optional
        Maximum frequency to consider to pass band (Hz).
    inverse_filter : Optional[np.ndarray], optional
        The inverse filter to be used to flatten the power spectral density of the sound played by the speakers.
    noise_type : Literal["gaussian", "uniform"], optional
        Whether the generated white noise should be gaussian or uniform.

    Returns
    -------
    white_noise : Sound
        The generated white noise.
    """
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
    if inverse_filter is not None:
        signal = lfilter(inverse_filter, 1, signal)

    # Applies a 16th-order butterworth band-pass filter to the signal
    if filter:
        sos = butter(16, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs)
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

    return white_noise


@greater_than("duration", 0)
@greater_than("fs", 0)
@validate_range("amplitude", 0, 1)
@greater_than("ramp_time", 0)
def pure_tone(
    duration: float,
    fs: int,
    freq: float,
    phase: float = 0,
    amplitude: float = 1,
    ramp_time: float = 0.005,
) -> Sound:
    """
    Generates a pure tone.

    Parameters
    ----------
    duration : float
        Duration of the signal generated (s).
    fs : int
        Sampling frequency of the signal being generated (Hz).
    freq : float
        Frequency of the sinusoidal signal (Hz).
    phase : float, optional
        Phase of the sinusoidal signal.
    amplitude : float, optional
        Amplitude of the sinusoidal signal.
    ramp_time : float, optional
        Ramp time of the signal (s).

    Returns
    -------
    pure_tone : Sound
        The generated pure tone.
    """
    # Sinusoidal signal generation
    t = np.linspace(0, duration, int(fs * duration))
    signal = amplitude * np.sin(2 * np.pi * freq * t + phase)

    # Apply a ramp at the beginning and at the end of the signal
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate(
        (ramp, np.ones(t.size - ramp_samples * 2), np.flip(ramp)), axis=None
    )
    pure_tone = Sound(np.multiply(signal, ramped_signal), t)

    return pure_tone


# TODO: add docstring
def log_chirp(
    duration: float,
    fs: int,
    freq_min: float,
    freq_max: float,
    phase: float = 0,
    amplitude: float = 1,
    ramp_time: float = 0.005,
):
    # Calculate helper parameter
    log_param = duration / np.log(freq_max / freq_min)

    # Generate signal
    time = np.linspace(0, duration, int(fs * duration))
    signal = amplitude * np.sin(
        2 * np.pi * freq_min * log_param * (np.exp(time / log_param) - 1) + phase
    )

    # Apply ramp
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = np.linspace(0, 1, ramp_samples) ** 2
    ramped_signal = np.concatenate(
        (ramp, np.ones(time.size - ramp_samples * 2), np.flip(ramp)), axis=None
    )
    signal = np.multiply(signal, ramped_signal)

    # Calculate inverse filter
    inverse_filter = np.flip(signal) * np.exp(-time / log_param)

    # Create Sound object
    chirp = Sound(signal, time, inverse_filter)

    return chirp


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


def calculate_db_spl(
    sound: Sound,
    mic_factor: float,
    reference_pressure: float = 0.00002,
    domain: Literal["time", "freq"] = "time",
):
    """
    Calculates the dB SPL of the recorded signal.

    Parameters
    ----------
    sound : Sound
        The sound from which the dB SPL calculation will be performed.
    mic_factor : float
        Factor of the microphone (V/Pa).
    reference_pressure : float, optional
        Reference pressure (Pa).
    domain : Literal["time", "freq"], optional
        Indicates whether the dB SPL calculation should be performed in the time or in the frequency domain.
    """
    # Remove the beginning and end of the acquisition
    signal = sound.signal[int(0.1 * sound.signal.size) : int(0.9 * sound.signal.size)]

    # Calculate dB SPL either in the time or in the frequency domain
    if domain == "time":
        signal_pascal = signal / mic_factor
        rms = np.sqrt(np.mean(signal_pascal**2))
        db_spl = 20 * np.log10(rms / reference_pressure)
    else:
        fft = np.abs(np.fft.fft(signal)) ** 2
        rms = np.sqrt(np.sum(fft) / (fft.size**2 * mic_factor**2))
        db_spl = 20 * np.log10(rms / reference_pressure)

    return db_spl
