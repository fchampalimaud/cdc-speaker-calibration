import numpy as np
from scipy.signal import welch
from classes import Signal


def psd_calibration(
    sound_duration: float,
    fs: float,
    amplification: float = 1,
    ramp_time: float = 0.005,
    fs_adc: float = 192000,
    time_constant: float = None,
    mic_factor: float = None,
    reference_pressure=0.00002,
):
    """
    Calculates the power spectral density calibration factor to be used with the setup being calibrated.

    Parameters
    ----------
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.

    Returns
    -------
    inverse_filter : numpy.ndarray
        the power spectral density calibration factor.
    signal : Signal
        the Signal object used for the PSD calibration.
    """
    # Generates the noise and upload it to the soundcard
    signal = Signal(sound_duration, fs, amplification=amplification, ramp_time=ramp_time, mic_factor=mic_factor, reference_pressure=reference_pressure)

    # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
    signal.load_sound()
    signal.record_sound(fs_adc)

    freq, psd = welch(
        signal.recorded_sound[int(0.1 * signal.recorded_sound.size) : int(0.9 * signal.recorded_sound.size)],
        fs=fs_adc,
        nperseg=time_constant * fs_adc,
    )
    inverse_filter = 1 / np.sqrt(psd)
    inverse_filter = np.stack((freq, inverse_filter), axis=1)

    return inverse_filter, signal, psd
