import numpy as np
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

    # Calculates the power spectral density calibration factor to be used with the setup being calibrated
    calibration_factor = 1 / signal.fft
    calibration_factor = np.stack((signal.freq_array, calibration_factor), axis=1)

    return calibration_factor, signal
