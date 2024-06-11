import numpy as np
from classes import Hardware, InputParameters, Signal
from pyharp.device import Device


def db_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray, signal_bef_cal: Signal):
    """
    Returns the parameters needed to calculate the dB calibration.

    Parameters
    ----------
    device : Device
        the initialized (Harp) Sound Card. This object allows to send and receive messages to and from the device.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    calibration_factor : numpy.ndarray
        the power spectral density calibration factor.
    signal_bef_cal : numpy.ndarray
        the sound recorded before the power spectral density (PSD) calibration.

    Returns
    -------
    db_spl_aft_cal_array : numpy.ndarray
        the dB values calculated for each attenuation factor (dB).
    db_spl_bef_cal_array : numpy.ndarray
        the dB value calculated for the sound recorded before the power spectral density (PSD) calibration (dB).
    filtered_signal_array : numpy.ndarray
        the sounds recorded during the dB calibration.
    fft_aft_cal_array : numpy.ndarray
        the fft's of the sounds recorded during the dB calibration.
    rms_sound_aft_cal_array : numpy.ndarray
        the RMS of the sounds recorded during the dB calibration.
    signal_array : numpy.ndarray
        the signals generated for the dB calibration
    rms_fft_array : numpy.ndarray
        the RMS of the fft's of the sounds recorded during the dB calibration.
    db_fft_array : numpy.ndarray
        # TODO
    """
    # Initialization of the output arrays
    signals = np.zeros(input_parameters.att_steps, dtype=Signal)
    db_spl = np.zeros(input_parameters.att_steps)

    signal_bef_cal.db_spl_calculation(input_parameters)

    for i in range(input_parameters.att_steps):
        # Generates the noise and upload it to the soundcard
        signals[i] = Signal(
            input_parameters.sound_duration_db,
            hardware,
            input_parameters,
            filter=True,
            calibrate=True,
            calibration_factor=calibration_factor,
            attenuation=input_parameters.att_factor[i],
        )

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        signals[i].load_sound(hardware)
        signals[i].record_sound(device, input_parameters)

        # Calculates the fft of the recorded sound
        signals[i].fft_calculation(input_parameters)
        signals[i].db_spl_calculation(input_parameters)
        db_spl[i] = signals[i].db_spl

        print("Attenuation factor: " + str(input_parameters.att_factor[i]))
        print("dB SPL after calibration: " + str(db_spl[i]))
        print("dB SPL before calibration: " + str(signal_bef_cal.db_spl))

    return db_spl, signals  # StC
