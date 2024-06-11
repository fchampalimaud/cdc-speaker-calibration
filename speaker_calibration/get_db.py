import numpy as np
from classes import Hardware, InputParameters, Signal
from pyharp.device import Device


def get_db(att_array: np.ndarray, sound_duration: float, device: Device, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray):
    """
    Returns the parameters needed to calculate the dB calibration.

    Parameters
    ----------
    att_array : numpy.ndarray
        # TODO
    sound_duration : float
        # TODO
    device : Device
        the initialized (Harp) Sound Card. This object allows to send and receive messages to and from the device.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    calibration_factor : numpy.ndarray
        the power spectral density calibration factor.

    Returns
    -------
    db_spl : numpy.ndarray
        # TODO
    db_fft : numpy.ndarray
        # TODO
    signals : numpy.ndarray
        # TODO
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
        signals[i].load_sound(hardware)
        signals[i].record_sound(device, input_parameters)

        # Calculates the fft of the recorded sound
        signals[i].fft_calculation(input_parameters)
        signals[i].db_spl_calculation(input_parameters)

        db_spl[i] = signals[i].db_spl
        db_fft[i] = signals[i].db_fft

        print("Attenuation factor: " + str(att_array[i]))
        print("dB SPL after calibration: " + str(db_spl[i]))

    return db_spl, db_fft, signals  # StC
