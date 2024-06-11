import os
import time

import numpy as np
from classes import Hardware, InputParameters
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from scipy.signal import butter, sosfilt
from pyharp.device import Device
from pyharp.messages import HarpMessage


def db_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray, signal_bef_cal: np.ndarray):
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
    db_spl_aft_cal_array = np.zeros(input_parameters.att_steps)
    db_spl_bef_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    filtered_signal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    fft_aft_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    rms_sound_aft_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    signal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    rms_fft_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    db_fft_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)

    for i in range(input_parameters.att_steps):
        # Generates the noise and upload it to the soundcard
        signal = generate_noise(
            fs=hardware.fs_sc,
            duration=input_parameters.sound_duration_db,
            head_phone_amp=input_parameters.amplification * input_parameters.att_factor[i],
            filter=True,
            freq_min=input_parameters.freq_min,
            freq_max=input_parameters.freq_max,
            calibrate=True,
            calibration_factor=calibration_factor,
        )
        create_sound_file(signal, "sound.bin")
        os.system("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(hardware.fs_sc))  # TODO: add toSoundCard.exe to the project

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        device.send(HarpMessage.WriteU16(32, 2).frame, False)
        time.sleep(input_parameters.sound_duration_psd)
        recorded_signal = np.ones(1000)  # TODO: Record sound

        # Applies a 3th-order butterworth band-pass filter to the recorded signal
        sos = butter(3, [input_parameters.freq_high, input_parameters.freq_low], btype="bandpass", output="sos", fs=input_parameters.fs_adc)
        filtered_signal = sosfilt(sos, recorded_signal)

        # Calculates the fft of the recorded sound
        fft_aft_cal, freq_vector, n_intervals, samples_per_interval, rms = fft_intervals(
            filtered_signal, input_parameters.time_constant, input_parameters.fs_adc, input_parameters.smooth_window
        )

        sig_aft_cal_pascal = filtered_signal[int(0.1 * filtered_signal.size) : int(0.9 * filtered_signal.size)] / input_parameters.mic_factor
        sig_bef_cal_pascal = signal_bef_cal[int(0.1 * signal_bef_cal.size) : int(0.9 * signal_bef_cal.size)] / input_parameters.mic_factor

        rms_sound_aft_cal = np.sqrt(np.mean(sig_aft_cal_pascal**2))
        rms_sound_bef_cal = np.sqrt(np.mean(sig_bef_cal_pascal**2))

        rms_fft = rms / input_parameters.mic_factor

        db_spl_aft_cal = 20 * np.log10(rms_sound_aft_cal / input_parameters.reference_pressure)
        db_spl_bef_cal = 20 * np.log10(rms_sound_bef_cal / input_parameters.reference_pressure)
        db_fft = 20 * np.log10(rms_fft / input_parameters.reference_pressure)

        print("Attenuation factor: " + str(input_parameters.att_factor[i]))
        print("dB SPL after calibration: " + str(db_spl_aft_cal))
        print("dB SPL before calibration: " + str(db_spl_bef_cal))

        # Updates the output arrays
        db_spl_aft_cal_array[i] = db_spl_aft_cal
        db_spl_bef_cal_array[i] = db_spl_bef_cal
        filtered_signal_array[i] = filtered_signal
        fft_aft_cal_array[i] = fft_aft_cal
        rms_sound_aft_cal_array[i] = rms_sound_aft_cal
        signal_array[i] = signal
        rms_fft_array[i] = rms_fft
        db_fft_array[i] = db_fft

    return db_spl_aft_cal_array, db_spl_bef_cal_array, filtered_signal_array, fft_aft_cal_array, rms_sound_aft_cal_array, signal_array, rms_fft_array, db_fft_array  # StC
