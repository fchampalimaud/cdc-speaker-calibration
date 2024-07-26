import numpy as np
from scipy.signal import butter, sosfilt
from multipledispatch import dispatch


def generate_noise(
    duration: float,
    fs: int,
    amplification: float = 1,
    ramp_time: float = 0.005,
    filter: bool = False,
    freq_min: float = 0,
    freq_max: float = 80000,
    calibrate: bool = False,
    calibration_factor: np.ndarray = np.zeros((1, 2)),
    truncate: bool = True,
):
    """
    Generates a gaussian random noise.

    Parameters
    ----------
    duration : float
        duration of the signal generated (s).
    fs : int
        sampling frequency of the signal being generated (Hz).
    amplification : float, optional
        amplification factor of the speakers.
    ramp_time : float, optional
        ramp time of the signal (s).
    filter : bool, optional
        whether to filter the signal.
    freq_min : float, optional
        minimum frequency to consider to pass band (Hz).
    freq_max : float, optional
        maximum frequency to consider to pass band (Hz).
    calibrate : bool, optional
        whether to use a calibration factor to flatten the power spectral density of the sound played by the speakers.
    calibration_factor : np.ndarray, optional
        the calibration factor to be used to flatten the power spectral density of the sound played by the speakers.
    truncate : bool, optional
        whether to truncate the signal between -1 and 1.

    Returns
    -------
    signal : numpy.ndarray
        the generated gaussian random noise.
    """
    if amplification > 1 and amplification < 0:
        raise ValueError("amplification must be between 0 and 1")

    # Generates the base signal
    n_samples = int(fs * duration)
    signal = 0.2 * np.random.randn(n_samples)  # We don't want more than 1 hence rescale by 0.2

    # Applies a 3th-order butterworth band-pass filter to the signal
    if filter:
        sos = butter(3, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs)
        signal = sosfilt(sos, signal)
        rms_original_signal = np.sqrt(np.mean(signal**2))

    # Uses the calibration factor to flatten the power spectral density of the signal according to the electronics characteristics
    if calibrate:
        freq_vector = np.fft.rfftfreq(duration * fs, d=1 / fs)
        calibration_interp = np.interp(freq_vector, calibration_factor[:, 0], calibration_factor[:, 1])
        fft = np.fft.rfft(signal)
        signal = np.fft.irfft(fft * calibration_interp, n=fs * duration)
        signal = sosfilt(sos, signal)
        signal = signal / np.sqrt(np.mean(signal**2)) * rms_original_signal

    # Truncates the signal between -1 and 1
    if truncate:
        signal[(signal > 1) | (signal < -1)] = 0

    # Applies a ramp at the beginning and at the end of the signal and the input amplification factor
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate((ramp, np.ones(n_samples - ramp_samples * 2), np.flip(ramp)), axis=None)
    signal = amplification * np.multiply(signal, ramped_signal)

    return signal


def generate_pure_tone(freq: float, duration: float, fs: int, amplitude: float = 1, ramp_time: float = 0.005):
    """
    Generates a gaussian random noise.

    Parameters
    ----------
    freq : float
        frequency of the sinusoidal signal (Hz).
    duration : float
        duration of the signal generated (s).
    fs : int
        sampling frequency of the signal being generated (Hz).
    amplitude : float
        amplitude of the sinusoidal signal.
    ramp_time : float, optional
        ramp time of the signal (s).

    Returns
    -------
    signal : numpy.ndarray
        the generated gaussian random noise.
    """
    # Sinusoidal signal generation
    t = np.linspace(0, duration, int(fs * duration))
    signal = amplitude * np.sin(2 * np.pi * freq * t)

    # Applies a ramp at the beginning and at the end of the signal
    ramp_samples = int(np.floor(fs * ramp_time))
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate((ramp, np.ones(t.size - ramp_samples * 2), np.flip(ramp)), axis=None)
    signal = np.multiply(signal, ramped_signal)

    return signal


@dispatch(np.ndarray, str, speaker_side=str)
def create_sound_file(signal: np.ndarray, filename: str, speaker_side: str = "both"):
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal : numpy.ndarray
        the signal to be written to the .bin file.
    filename : str
        the name of the .bin file.
    speaker_side : str
        whether the sound plays in both speakers or in a single one. Possible values: "both", "left" or "right.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1

    if speaker_side == "both":
        wave_left = amplitude24bits * signal
        wave_right = amplitude24bits * signal
    elif speaker_side == "left":
        wave_left = amplitude24bits * signal
        wave_right = 0 * signal
    elif speaker_side == "right":
        wave_left = 0 * signal
        wave_right = amplitude24bits * signal
    else:
        raise ValueError('speaker_side value should be "both", "left" or "right" instead of "%s"' % speaker_side)

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)


@dispatch(np.ndarray, np.ndarray, str, speaker_side=str)
def create_sound_file(signal_left: np.ndarray, signal_right: np.ndarray, filename: str, speaker_side: str = "both"):
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal : numpy.ndarray
        the signal to be written to the .bin file.
    filename : str
        the name of the .bin file.
    speaker_side : str
        whether the sound plays in both speakers or in a single one. Possible values: "both", "left" or "right.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1

    if speaker_side == "both":
        wave_left = amplitude24bits * signal_left
        wave_right = amplitude24bits * signal_right
    elif speaker_side == "left":
        wave_left = amplitude24bits * signal_left
        wave_right = 0 * signal_right
    elif speaker_side == "right":
        wave_left = 0 * signal_left
        wave_right = amplitude24bits * signal_right
    else:
        raise ValueError('speaker_side value should be "both", "left" or "right" instead of "%s"' % speaker_side)

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)
