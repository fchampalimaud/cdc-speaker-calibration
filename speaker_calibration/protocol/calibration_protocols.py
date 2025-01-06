import numpy as np
from speaker_calibration.protocol.classes import Signal
from speaker_calibration.settings.hardware import Hardware
from speaker_calibration.settings.input_settings import Settings
from speaker_calibration.protocol.calibration_steps import psd_calibration, get_db
import time


def noise_calibration(
    hardware: Hardware,
    input: Settings,
    inverse_filter: np.ndarray = None,
    calibration_parameters: np.ndarray = None,
    callback: callable = None,
):
    """
    Performs the speaker calibration with white noise.

    Parameters
    ----------
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    input : Settings
        the object containing the input parameters used for the calibration.
    inverse_filter : numpy.ndarray, optional
        the inverse filter to apply to the calibration and test signals that flattens the frequency spectrum of the recorded sound for the equipment being calibrated.
    calibration_parameters : numpy.ndarray, optional
        an array of size 2 in which index-0 is the slope and index-1 is the intercept of the calibration curve.
    callback : callable, optional
        a function which is used to send messages to other parts of the code (for example: to interact with a GUI architecture).

    Returns
    -------
    inverse_filter : numpy.ndarray
        the inverse filter that flattens the frequency spectrum of the recorded sound for the equipment being calibrated.
    calibration_parameters : numpy.ndarray
        an array of size 2 in which index-0 is the slope and index-1 is the intercept of the calibration curve.
    """

    if input.noise["calculate_filter"]:
        # Calculates the inverse filter which flattens the frequency spectrum of the recorded sound for the equipment being calibrated
        inverse_filter, psd_signal = psd_calibration(
            input.noise["psd"]["duration"],
            hardware.fs_sc,
            input.amplification,
            input.ramp_time,
            input.fs_adc,
            input.noise["psd"]["time_constant"],
            input.mic_factor,
            input.reference_pressure,
        )
        if callback is not None:
            callback([inverse_filter, psd_signal], "Inverse Filter")

    if input.noise["calibrate"]:
        # Generates an array with different attenuation factors
        log_att = np.linspace(
            input.noise["calibration"]["att_min"],
            input.noise["calibration"]["att_max"],
            input.noise["calibration"]["att_steps"],
        )
        att_factor = 10**log_att

        if callback is not None:
            callback([log_att], "Pre-calibration")

        # Calculates the dB SPL values for different attenuation factors
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
        calibration_parameters = np.polyfit(log_att, db_spl, 1)
        print("Slope: " + str(calibration_parameters[0]))
        print("Intercept: " + str(calibration_parameters[1]))

    if input.noise["test_calibration"]:
        # Defines attenuation factors to test the calibration curve
        att_test = np.linspace(
            input.noise["test"]["db_min"],
            input.noise["test"]["db_max"],
            input.noise["test"]["db_steps"],
        )

        if callback is not None:
            callback([att_test], "Pre-test")

        att_test = (att_test - calibration_parameters[1]) / calibration_parameters[0]
        att_test = 10**att_test

        # Tests the calibration curve with the test attenuation factors
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

    return inverse_filter, calibration_parameters


def pure_tone_calibration(hardware: Hardware, input: Settings):
    """
    Performs the speaker calibration with pure tones.

    Parameters
    ----------
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    input_parameters : Settings
        the object containing the input parameters used for the calibration.

    Returns
    -------
    freq_array : numpy.ndarray
        the array containing the frequencies to be used in the calibration.
    db_array : numpy.ndarray
        the array containing the dB SPL values calculated for each pure tone.
    """
    # Initializes the array containing the frequencies to be used in the calibration and a zero-initialized array for the respective dB SPL values
    freq_array = np.logspace(
        np.log10(input.freq_min),
        np.log10(input.freq_max),
        input.pure_tones["calibration"]["num_freqs"],
    )
    attenuations = np.linspace(0.1, 1, 5)
    db_array = np.zeros((input.pure_tones["calibration"]["num_freqs"], 5))

    # Calculates the frequency response of the system
    for i in range(input.pure_tones["calibration"]["num_freqs"]):
        print("Frequency (Hz): " + str(freq_array[i]))
        for j in range(5):
            print("Attenuation: " + str(input.amplification * attenuations[j]))
            signal = Signal(
                input.pure_tones["calibration"]["duration"],
                hardware.fs_sc,
                sound_type=input.sound_type,
                amplification=input.amplification * attenuations[j],
                ramp_time=input.ramp_time,
                freq=freq_array[i],
                mic_factor=input.mic_factor,
                reference_pressure=input.reference_pressure,
            )
            time.sleep(1)
            signal.load_sound()
            signal.record_sound(input.fs_adc)
            signal.db_spl_calculation()
            print("dB SPL: " + str(signal.db_spl))
            db_array[i, j] = signal.db_spl

    np.savetxt("output/pure_tones.csv", db_array, delimiter=",")

    return freq_array, db_array
