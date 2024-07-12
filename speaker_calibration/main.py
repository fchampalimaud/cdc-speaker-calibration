import matplotlib.pyplot as plt
import numpy as np
from classes import Hardware, InputParameters, Signal
from get_db import get_db
from psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage


def noise_calibration(fs, input_parameters: InputParameters):
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
    calibration_factor, psd_signal, psd = psd_calibration(fs, input_parameters)

    # Calculates the dB SPL values for different attenuation factors
    db_spl, db_fft, signals = get_db(input_parameters.att_factor, input_parameters.sound_duration_db, fs, input_parameters, calibration_factor)

    # Fits the dB SPL vs logarithmic attenuation to a straight line
    fit_parameters = np.polyfit(input_parameters.log_att, db_spl, 1)
    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    # # Defines new attenuation factors to test the fit performed
    # tdB = np.arange(65, 50, -5)
    # att_test = (tdB - fit_parameters[1]) / fit_parameters[0]
    # att_test = 10**att_test

    # # Tests the fit with the new attenuation factors
    # db_spl_test, db_fft_test, signals_test = get_db(att_test, input_parameters.sound_duration_test, hardware, input_parameters, calibration_factor)

    return calibration_factor, fit_parameters


def pure_tone_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters):
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

    # Attenuation test
    # 1000 Hz Pure Tone
    signal = Signal(1, hardware, input_parameters, freq=1000)
    signal.load_sound()
    signal.record_sound(input_parameters)
    signal.db_spl_calculation(input_parameters)
    print("dB SPL original signal: " + str(signal.db_spl))

    plt.show()


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
