from typing import Literal, Optional

import numpy as np
from multipledispatch import dispatch
from scipy.signal import butter, sosfilt

from speaker_calibration.utils.decorators import greater_than, validate_range


class Sound:
    signal: np.ndarray
    time: Optional[np.ndarray]

    def __init__(self, signal: np.ndarray, time: Optional[np.ndarray] = None):
        self.signal = signal
        self.time = time


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
        duration of the signal generated (s).
    fs : int
        sampling frequency of the signal being generated (Hz).
    amplitude : float, optional
        amplitude factor of the speakers.
    ramp_time : float, optional
        ramp time of the signal (s).
    filter : bool, optional
        whether to filter the signal or not.
    freq_min : float, optional
        minimum frequency to consider to pass band (Hz).
    freq_max : float, optional
        maximum frequency to consider to pass band (Hz).
    inverse_filter : Optional[np.ndarray], optional
        the inverse filter to be used to flatten the power spectral density of the sound played by the speakers.
    noise_type : Literal["gaussian", "uniform"], optional
        whether the generated white noise should be gaussian or uniform.

    Returns
    -------
    white_noise : Sound
        the generated white noise.
    """
    # Calculates the number of samples of the signal
    num_samples = int(fs * duration)

    # Generates the base white noise (either gaussian or uniform)
    if noise_type == "gaussian":
        # The gaussian samples are rescaled so that 99% of the samples are between -1 and 1
        signal = 1 / 3 * np.random.randn(num_samples)
    else:
        signal = np.random.uniform(low=-1.0, high=1.0, size=num_samples)

    # Applies a 3th-order butterworth band-pass filter to the signal
    if filter:
        sos = butter(3, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs)
        signal = sosfilt(sos, signal)

    # Uses the calibration factor to flatten the power spectral density of the signal according to the electronics characteristics
    if inverse_filter is not None:
        freq = np.fft.rfftfreq(int(duration * fs), d=1 / fs)
        calibration_interp = np.interp(freq, inverse_filter[:, 0], inverse_filter[:, 1])
        fft = np.fft.rfft(signal)
        rms_original_signal = np.sqrt(np.mean(signal**2))
        signal = np.fft.irfft(fft * calibration_interp, n=int(fs * duration))
        signal = sosfilt(sos, signal)
        signal = signal / np.sqrt(np.mean(signal**2)) * rms_original_signal

    # Truncates the signal between -1 and 1
    signal[(signal < -1)] = -1
    signal[(signal > 1)] = 1

    # Applies a ramp at the beginning and at the end of the signal and the input amplitude factor
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate(
        (ramp, np.ones(num_samples - ramp_samples * 2), np.flip(ramp)), axis=None
    )
    white_noise = Sound(
        amplitude * np.multiply(signal, ramped_signal),
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
        duration of the signal generated (s).
    fs : int
        sampling frequency of the signal being generated (Hz).
    freq : float
        frequency of the sinusoidal signal (Hz).
    phase : float, optional
        phase of the sinusoidal signal.
    amplitude : float, optional
        amplitude of the sinusoidal signal.
    ramp_time : float, optional
        ramp time of the signal (s).

    Returns
    -------
    pure_tone : Sound
        the generated pure tone.
    """
    # Sinusoidal signal generation
    t = np.linspace(0, duration, int(fs * duration))
    signal = amplitude * np.sin(2 * np.pi * freq * t + phase)

    # Applies a ramp at the beginning and at the end of the signal
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate(
        (ramp, np.ones(t.size - ramp_samples * 2), np.flip(ramp)), axis=None
    )
    pure_tone = Sound(np.multiply(signal, ramped_signal), t)

    return pure_tone


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
        the signal to be written to the .bin file.
    filename : str
        the name of the .bin file.
    speaker_side : Literal["both", "left", "right"], optional
        whether the sound plays in both speakers or in a single one. Possible values: "both", "left" or "right.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
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

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
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
        the signal to be written to the .bin file that is going to be played by the left speaker.
    signal_right : Sound
        the signal to be written to the .bin file that is going to be played by the right speaker.
    filename : str
        the name of the .bin file.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1
    wave_left = amplitude24bits * signal_left.signal
    wave_right = amplitude24bits * signal_right.signal

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
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
        the sound from which the dB SPL calculation will be performed.
    mic_factor : float
        factor of the microphone (V/Pa).
    reference_pressure : float, optional
        reference pressure (Pa).
    domain : Literal["time", "freq"], optional
        indicates whether the dB SPL calculation should be performed in the time or in the frequency domain.
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
