import numpy as np
from speaker_calibration.classes import Hardware, InputParameters, Signal
from speaker_calibration.get_db import get_db
from speaker_calibration.psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage


def noise_calibration(
    hardware: Hardware,
    input: InputParameters,
    inverse_filter: np.ndarray = None,
    fit_parameters: np.ndarray = None,
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

    if input.noise["calculate_filter"]:
        # Calibrates the hardware in power spectral density (PSD)
        inverse_filter, psd_signal, psd = psd_calibration(
            input.noise["psd"]["duration"],
            hardware.fs_sc,
            input.amplification,
            input.ramp_time,
            input.fs_adc,
            input.time_constant,
            input.mic_factor,
            input.reference_pressure,
        )
        if callback is not None:
            callback([inverse_filter, psd_signal], "Inverse Filter")

    if input.noise["calibrate"]:
        # Calculates the dB SPL values for different attenuation factors
        log_att = np.linspace(
            input.noise["calibration"]["att_min"],
            input.noise["calibration"]["att_max"],
            input.noise["calibration"]["att_steps"],
        )
        att_factor = 10**log_att
        db_spl, db_fft, signals = get_db(
            input.noise["calibration"]["duration"],
            hardware.fs_sc,
            att_factor,
            input.ramp_time,
            input.freq_min,
            input.freq_max,
            inverse_filter,
            input.fs_adc,
            input.mic_factor,
            input.reference_pressure,
            callback,
            "Calibration",
        )

        # Fits the dB SPL vs logarithmic attenuation to a straight line
        fit_parameters = np.polyfit(log_att, db_spl, 1)
        print("Slope: " + str(fit_parameters[0]))
        print("Intercept: " + str(fit_parameters[1]))

    if input.noise["test_calibration"]:
        # Defines new attenuation factors to test the fit performed
        att_test = np.linspace(
            input.noise["test"]["db_min"],
            input.noise["test"]["db_max"],
            input.noise["test"]["db_steps"],
        )
        att_test = (att_test - fit_parameters[1]) / fit_parameters[0]
        att_test = 10**att_test

        # Tests the fit with the new attenuation factors
        db_spl_test, db_fft_test, signals_test = get_db(
            input.noise["test"]["duration"],
            hardware.fs_sc,
            att_test,
            input.ramp_time,
            input.freq_min,
            input.freq_max,
            inverse_filter,
            input.fs_adc,
            input.mic_factor,
            input.reference_pressure,
            callback,
            "Test",
        )

    return inverse_filter, fit_parameters


def pure_tone_calibration(hardware: Hardware, input: InputParameters):
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
    freq_array = np.logspace(np.log10(input.freq_min), np.log10(input.freq_max), input.pure_tones["num_freqs"])
    db_array = np.zeros(input.pure_tones["num_freqs"])
    for i in range(input.pure_tones["num_freqs"]):
        print("Frequency (Hz): " + str(freq_array[i]))
        signal = Signal(
            input.pure_tones["duration"],
            hardware.fs_sc,
            sound_type=input.sound_type,
            amplification=input.amplification,
            ramp_time=input.ramp_time,
            freq=freq_array[i],
            mic_factor=input.mic_factor,
            reference_pressure=input.reference_pressure,
        )
        # time.sleep(1)
        signal.load_sound()
        # time.sleep(1)
        signal.record_sound(input.fs_adc)
        signal.db_spl_calculation()
        db_array[i] = signal.db_spl

    return freq_array, db_array


# TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)
if __name__ == "__main__":
    # Reads the input parameters and hardware characteristics and initialize the Harp SoundCard
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # Choice of calibration type
    if input_parameters.sound_type == "Noise":
        noise_calibration(hardware, input_parameters)
    elif input_parameters.sound_type == "Pure Tone":
        pure_tone_calibration(hardware, input_parameters)

    # TODO: save content

    device.disconnect()
