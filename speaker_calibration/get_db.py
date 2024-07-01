import numpy as np
from classes import Hardware, InputParameters, Signal


def get_db(att_array: np.ndarray, sound_duration: float, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray):
    """
    Returns the parameters needed to calculate the dB calibration.

    Parameters
    ----------
    att_array : numpy.ndarray
        the array containing the the attenuation to apply to the sound.
    sound_duration : float
        the duration of the sound (s).
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    calibration_factor : numpy.ndarray
        the power spectral density calibration factor.

    Returns
    -------
    db_spl : numpy.ndarray
        the array containing the dB SPL values calculated for the signal.
    db_fft : numpy.ndarray
        the array containing the dB SPL values calculated from the fft of each signal.
    signals : numpy.ndarray
        the array containing the signals used.
    """
    # Initialization of the output arrays
    signals = np.zeros(att_array.size, dtype=Signal)
    db_spl = np.zeros(att_array.size)
    db_fft = np.zeros(att_array.size)

    for i in range(att_array.size):
        # Generates the noise and upload it to the soundcard
        signals[i] = Signal(
            sound_duration,
            hardware,
            input_parameters,
            filter=True,
            calibrate=True,
            calibration_factor=calibration_factor,
            attenuation=att_array[i],
        )

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        signals[i].load_sound()
        signals[i].record_sound(input_parameters, filter=True)

        # Calculates the fft of the recorded sound
        signals[i].db_spl_calculation(input_parameters)

        db_spl[i] = signals[i].db_spl
        db_fft[i] = signals[i].db_fft

        print("Attenuation factor: " + str(att_array[i]))
        print("dB SPL after calibration: " + str(db_spl[i]))
        print("dB SPL after calibration: " + str(db_fft[i]))

    return db_spl, db_fft, signals
