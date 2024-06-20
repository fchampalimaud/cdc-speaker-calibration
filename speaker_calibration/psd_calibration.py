import numpy as np
from scipy.signal import welch
from classes import Hardware, InputParameters, Signal


def psd_calibration(hardware: Hardware, input_parameters: InputParameters):
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
    calibration_factor : numpy.ndarray
        the power spectral density calibration factor.
    signal : Signal
        the Signal object used for the PSD calibration.
    """
    # Generates the noise and upload it to the soundcard
    signal = Signal(input_parameters.sound_duration_psd, hardware, input_parameters)

    # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
    signal.load_sound()
    signal.record_sound(input_parameters)

    # Calculates the fft of the recorded sound
    signal.fft_calculation(input_parameters)
    signal.db_spl_calculation(input_parameters)

    freq, psd = welch(
        signal.recorded_sound[int(0.1 * signal.recorded_sound.size) : int(0.9 * signal.recorded_sound.size)],
        fs=input_parameters.fs_adc,
        nperseg=input_parameters.time_constant * input_parameters.fs_adc,
    )
    calibration_factor = 1 / np.sqrt(psd)
    calibration_factor = np.stack((freq, calibration_factor), axis=1)
    # psd_welch_interp = np.interp(freq, f, psd_welch)
    # cal_factor_welch = cal_factor_welch / (2 * np.sqrt(signal.size))

    return calibration_factor, signal
