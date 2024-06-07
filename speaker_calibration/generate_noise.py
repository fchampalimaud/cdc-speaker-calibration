import numpy as np
from scipy.signal import butter, sosfilt


def generate_noise(
    fs: int,
    duration: float,
    head_phone_amp: float = 0.85,
    ramp_time: float = 0.005,
    filter: bool = False,
    freq_min: float = 20,
    freq_max: float = 20000,
    calibrate: bool = False,
    calibration_factor: np.ndarray = np.zeros((1, 2)),
    truncate: bool = True,
):
    """
    Generates a gaussian random noise.

    Parameters
    ----------
    fs : int
        sampling frequency of the signal being generated (Hz).
    duration : float
        duration of the signal generated (s).
    head_phone_amp : float, optional
        amplification factor of the speakers.
    ramp_time : float, optional
        ramp time of the signal (s).
    filter : bool, optional
        whether to filter the signal.
    freq_min : float, optional
        minimum frequency to consider to pass band.
    freq_max : float, optional
        maximum frequency to consider to pass band.
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
    # Generates the base signal
    n_samples = int(fs * duration)
    signal = 0.2 * np.random.randn(n_samples)  # We don't want more than 1 hence rescale by 0.2

    # Applies a 3th-order butterworth band-pass filter to the signal
    if filter:
        sos = butter(3, [freq_min, freq_max], btype="bandpass", output="sos", fs=fs)
        signal = sosfilt(sos, signal)

    # Uses the calibration factor to flatten the power spectral density of the signal according to the electronics characteristics
    if calibrate:
        freq_vector = np.fft.rfftfreq(duration * fs, d=1 / fs)
        calibration_interp = np.interp(
            freq_vector, calibration_factor[:, 0], 0.5 * calibration_factor.shape[0] * calibration_factor[:, 1]
        )  # TODO: understand why 0.5 * calibration_factor.shape[0] * calibration_factor[:, 1]
        calibrated_noise = np.fft.irfft(np.multiply(np.fft.rfft(signal), calibration_interp), n=fs * duration)
        signal = calibrated_noise * 0.2 / np.sqrt(np.mean(calibrated_noise**2))

    # Truncates the signal between -1 and 1
    if truncate:
        signal[signal > 1 | signal < -1] = 0

    # Applies a ramp at the beginning and at the end of the signal and the input amplification factor
    ramp_samples = np.floor(fs * ramp_time)
    ramp = (0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))) ** 2
    ramped_signal = np.concatenate((ramp, np.ones(n_samples - ramp_samples * 2), np.flip(ramp)), axis=None)
    signal = head_phone_amp * np.multiply(signal, ramped_signal)

    return signal


def create_sound_file(signal: np.ndarray, filename: str):
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal : numpy.ndarray
        the signal to be written to the .bin file.
    filename : str
        the name of the .bin file.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.pow(2, 31) - 1
    wave_left = amplitude24bits * signal
    wave_right = amplitude24bits * signal

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)
