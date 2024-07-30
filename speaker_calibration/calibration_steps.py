import numpy as np
from scipy.signal import welch
from speaker_calibration.classes import Signal, InputParameters, Hardware
from datetime import datetime
import os
import yaml


def psd_calibration(
    sound_duration: float,
    fs: float,
    amplification: float = 1,
    ramp_time: float = 0.005,
    fs_adc: float = 192000,
    time_constant: float = None,
    mic_factor: float = None,
    reference_pressure=0.00002,
):
    """
    Calculates the power spectral density calibration factor to be used with the setup being calibrated.

    Parameters
    ----------
    sound_duration : float
        the duration of the sound (s).
    fs : float
        the sampling frequency of the generated signal (Hz).
    amplification : float, optional
        amplification factor of the speakers.
    ramp_time : float, optional
        ramp time of the sound (s).
    fs_adc : int, optional
        sampling frequency of the ADC (Hz).
    time_constant : float, optional
        duration of each division of the original signal that is used to compute the PSD (s).
    mic_factor : float, optional
        factor of the microphone (V/Pa).
    reference_pressure : float, optional
        reference pressure (Pa).

    Returns
    -------
    inverse_filter : numpy.ndarray
        the inverse filter that flattens the frequency spectrum of the recorded sound for the equipment being calibrated.
    signal : Signal
        the Signal object used for the PSD calibration.
    """
    # Generates the noise and upload it to the soundcard
    signal = Signal(sound_duration, fs, amplification=amplification, ramp_time=ramp_time, mic_factor=mic_factor, reference_pressure=reference_pressure)

    # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
    signal.load_sound()
    signal.record_sound(fs_adc)

    freq, psd = welch(
        signal.recorded_sound[int(0.1 * signal.recorded_sound.size) : int(0.9 * signal.recorded_sound.size)],
        fs=fs_adc,
        nperseg=time_constant * fs_adc,
    )
    inverse_filter = 1 / np.sqrt(psd)
    inverse_filter = np.stack((freq, inverse_filter), axis=1)

    return inverse_filter, signal


def get_db(
    sound_duration: float,
    fs: float,
    att_array: np.ndarray,
    ramp_time: float = 0.005,
    freq_min: float = 0,
    freq_max: float = 80000,
    inverse_filter: np.ndarray = None,
    fs_adc: float = 192000,
    mic_factor: float = None,
    reference_pressure: float = 0.00002,
    callback: callable = None,
    message: str = "Calibration",
):
    """
    Returns the parameters needed to calculate the dB calibration.

    Parameters
    ----------
    sound_duration : float
        the duration of the sound (s).
    fs : float
        the sampling frequency of the generated signal (Hz).
    att_array : numpy.ndarray
        the array containing the the attenuation to apply to the sound.
    ramp_time : float, optional
        ramp time of the sound (s).
    freq_min : float, optional
        minimum frequency to consider to pass band (Hz).
    freq_max : float, optional
        maximum frequency to consider to pass band (Hz).
    inverse_filter : numpy.ndarray, optional
        the inverse filter that flattens the frequency spectrum of the recorded sound for the equipment being calibrated.
    fs_adc : int, optional
        sampling frequency of the ADC (Hz).
    mic_factor : float, optional
        factor of the microphone (V/Pa).
    reference_pressure : float, optional
        reference pressure (Pa).
    callback : callable, optional
        a function which is used to send messages to other parts of the code (for example: to interact with a GUI architecture).
    message: str, optional
        the second argument of the callback function which indicates what operations should be executed over the data received.

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
            fs,
            amplification=att_array[i],
            ramp_time=ramp_time,
            filter=True,
            freq_min=freq_min,
            freq_max=freq_max,
            calibrate=True,
            calibration_factor=inverse_filter,
            mic_factor=mic_factor,
            reference_pressure=reference_pressure,
        )

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        signals[i].load_sound()
        signals[i].record_sound(fs_adc, filter=True)

        # Calculates the fft of the recorded sound
        signals[i].db_spl_calculation()
        db_spl[i] = signals[i].db_spl
        signals[i].db_fft_calculation()
        db_fft[i] = signals[i].db_fft

        print("Attenuation factor: " + str(att_array[i]))
        print("dB SPL after calibration: " + str(db_spl[i]))
        # print("dB SPL after calibration: " + str(db_fft[i]))

        if callback is not None:
            if message == "Calibration":
                callback([signals[i], i], message)
            if message == "Test":
                callback([signals[i], i], message)

    return db_spl, db_fft, signals


def save_data(input: InputParameters, hardware: Hardware, inverse_filter: np.ndarray, calibration_parameters: np.ndarray):
    # TODO: implement case for pure tone calibration
    if input.noise["calculate_filter"] and input.noise["calibrate"]:
        date = datetime.now()
        date_string = "{}_{}".format(date.strftime("%Y%m%d"), date.strftime("%H%M%S"))
        os.makedirs("output/" + date_string, exist_ok=True)

        with open("output/" + date_string + "_settings.yml", "w") as f:
            yaml.dump(input, f)

        with open("output/" + date_string + "_hardware.yml", "w") as f:
            yaml.dump(hardware, f)

        save_string = "speaker" + str(hardware.speaker_id) + "_setup" + str(hardware.setup_id) + ".csv"

        if input.noise["calculate_filter"]:
            np.savetxt(
                "output/" + date_string + "_inverse_filter_" + save_string,
                inverse_filter,
                delimiter=",",
                fmt="%f",
            )

        if input.noise["calibrate"]:
            np.savetxt(
                "output/" + date_string + "_calibration_parameters_" + save_string,
                calibration_parameters,
                delimiter=",",
                fmt="%f",
            )
