import numpy as np
from classes import Hardware, InputParameters, Signal
from pyharp.device import Device


def test_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray, slope: float, intercept: float):
    """
    Tests the calibration curve given by `slope` and `intercept`.

    Parameters
    ----------
    device : Device
        the initialized (Harp) Sound Card. This object allows to send and receive messages to and from the device.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    calibration_factor : numpy.array
        the power spectral density calibration factor.
    slope : float
        the slope of the dB calibration curve.
    intercept : float
        the intercept of the dB calibration curve.

    Returns
    -------
    db_spl_test : numpy.ndarray
        the dB values calculated for each attenuation factor (dB).
    db_fft_test : numpy.ndarray
        # TODO
    """
    tdB = np.arange(70, 50, -10)
    db_spl = np.zeros(tdB.size)
    db_fft = np.zeros(tdB.size)

    for i in range(tdB.size):
        att = (tdB[i] - intercept) / slope
        att = 10**att
        print("Target dB: " + str(att))

        # # Generates the noise and upload it to the soundcard
        signal = Signal(
            input_parameters.sound_duration_test, hardware, input_parameters, filter=True, calibrate=True, calibration_factor=calibration_factor, attenuation=att
        )  # TODO: see noise MATLAB function

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        signal.load_sound(hardware)
        signal.record_sound(device, input_parameters)

        # Calculates the fft of the recorded sound
        signal.fft_calculation(input_parameters)
        signal.db_spl_calculation(input_parameters)

        db_spl[i] = signal.db_spl
        db_fft[i] = signal.db_fft

    return db_spl, db_fft  # StC
