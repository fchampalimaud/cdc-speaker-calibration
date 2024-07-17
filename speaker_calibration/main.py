import numpy as np
from classes import Hardware, InputParameters, Signal
from get_db import get_db
from psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage


def noise_calibration(
    fs,
    input_parameters: InputParameters,
    hardware: Hardware,
    calibration_factor: np.ndarray = None,
    fit_parameters: np.ndarray = None,
    min_db: float = 40,
    max_db: float = 60,
    test_steps: int = 5,
    speaker_filter: bool = True,
    calibration_curve: bool = True,
    test_calibration: bool = True,
    callback=None,
):
    """
    Performs the speaker calibration with white noise.

    Parameters
    ----------
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    """

    # Calibrates the hardware in power spectral density (PSD)
    if speaker_filter:
        calibration_factor, psd_signal, psd = psd_calibration(fs, input_parameters)
        if callback is not None:
            callback([calibration_factor, psd_signal], "Inverse Filter")

    if calibration_curve:
        # Calculates the dB SPL values for different attenuation factors
        att_factor = np.linspace(input_parameters.att_min, input_parameters.att_max, input_parameters.att_steps)
        att_factor = 10**att_factor
        db_spl, db_fft, signals = get_db(att_factor, input_parameters.sound_duration_db, fs, input_parameters, calibration_factor, callback, "Calibration")

        # Fits the dB SPL vs logarithmic attenuation to a straight line
        fit_parameters = np.polyfit(input_parameters.log_att, db_spl, 1)
        print("Slope: " + str(fit_parameters[0]))
        print("Intercept: " + str(fit_parameters[1]))

    if test_calibration:
        # Defines new attenuation factors to test the fit performed
        tdB = np.linspace(min_db, max_db, test_steps)
        att_test = (tdB - fit_parameters[1]) / fit_parameters[0]
        att_test = 10**att_test

        # Tests the fit with the new attenuation factors
        db_spl_test, db_fft_test, signals_test = get_db(att_test, input_parameters.sound_duration_test, fs, input_parameters, calibration_factor, callback, "Test")

    return calibration_factor, fit_parameters


def pure_tone_calibration(hardware: Hardware, input_parameters: InputParameters):
    """
    Performs the speaker calibration with pure tones.

    Parameters
    ----------
    device : Device
        the object representing the Harp Soundcard.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    """
    # Frequency response of the system
    freq_array = np.logspace(np.log10(1), np.log10(80000), 100)
    db_array = np.zeros(100)
    for i in range(100):
        print("Frequency (Hz): " + str(freq_array[i]))
        signal = Signal(1, hardware, input_parameters, freq=freq_array[i])
        # time.sleep(1)
        signal.load_sound()
        # time.sleep(1)
        signal.record_sound(input_parameters)
        signal.db_spl_calculation(input_parameters)
        db_array[i] = signal.db_spl

    np.savetxt("output/calibration.txt", db_array)


# TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)
if __name__ == "__main__":
    # Reads the input parameters and hardware characteristics and initialize the Harp SoundCard
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # Choice of calibration type
    if input_parameters.sound_type == "noise":
        noise_calibration(hardware, input_parameters)
    elif input_parameters.sound_type == "pure tone":
        pure_tone_calibration(device, hardware, input_parameters)

    device.disconnect()
