import os
import time

import numpy as np
from classes import Hardware, InputParameters
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from scipy.signal import butter, sosfilt
from pyharp.device import Device
from pyharp.messages import HarpMessage


def db_calibration(device: Device, input_parameters: InputParameters, hardware: Hardware, calibration_factor: np.ndarray, signal_bef_cal: np.ndarray):
    """
    Lorem ipsum.

    Parameters
    ----------

    Returns
    -------
    """
    # Initialization of the output arrays
    db_spl_aft_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    db_spl_bef_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    filtered_signal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    fft_aft_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    rms_sound_aft_cal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    signal_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    rms_fft_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)
    db_fft_array = np.zeros(input_parameters.att_steps, dtype=np.ndarray)

    for i in range(input_parameters.att_steps):
        # Generate the noise and upload it to the soundcard
        signal = generate_noise(
            fs=hardware.fs_sc,
            duration=input_parameters.sound_duration_db,
            head_phone_amp=input_parameters.amplification * input_parameters.att_factor[i],
            filter=True,
            freq_low=input_parameters.freq_min,
            freq_high=input_parameters.freq_max,
            calibrate=True,
            calibration_factor=calibration_factor,
        )
        create_sound_file(signal, "sound.bin")
        os.system("cmd /c toSoundCard.exe sound.bin 2 0 " + str(hardware.soundcard_fs))  # TODO: add toSoundCard.exe to the project

        # Play the sound throught the soundcard and recorded it with the microphone + DAQ system
        device.send(HarpMessage.WriteU16(32, 2).frame, False)
        time.sleep(input_parameters.sound_duration_psd)
        rec_signal = np.zeros(1000)  # TODO: Record sound

        sos = butter(3, [input_parameters.freq_high, input_parameters.freq_low], btype="bandpass", output="sos", fs=input_parameters.adc_fs)
        filtered_signal = sosfilt(sos, rec_signal)

        fft_aft_cal, f_vec_h, n_int, int_samp, rms = fft_intervals(filtered_signal, input_parameters.time_cons, input_parameters.adc_fs, input_parameters.smooth_window)

        sig_aft_cal_pascal = filtered_signal[0.1 * filtered_signal.size : 0.9 * filtered_signal.size] / input_parameters.mic_fac
        sig_bef_cal_pascal = signal_bef_cal[0.1 * signal_bef_cal.size : 0.9 * signal_bef_cal.size] / input_parameters.mic_fac

        rms_sound_aft_cal = np.sqrt(np.mean(sig_aft_cal_pascal**2))
        rms_sound_bef_cal = np.sqrt(np.mean(sig_bef_cal_pascal**2))

        rms_fft = rms / input_parameters.mic_fac

        db_spl_aft_cal = 20 * np.log10(rms_sound_aft_cal / input_parameters.ref)
        db_spl_bef_cal = 20 * np.log10(rms_sound_bef_cal / input_parameters.ref)
        db_fft = 20 * np.log10(rms_fft / input_parameters.ref)

        print("Attenuation factor: " + str(input_parameters.att_fac[i]))
        print("dB SPL after calibration: " + str(db_spl_aft_cal))
        print("dB SPL after calibration: " + str(db_spl_bef_cal))

        db_spl_aft_cal_array[i] = db_spl_aft_cal
        db_spl_bef_cal_array[i] = db_spl_bef_cal
        filtered_signal_array[i] = filtered_signal
        fft_aft_cal_array[i] = fft_aft_cal
        rms_sound_aft_cal_array[i] = rms_sound_aft_cal
        signal_array[i] = signal
        rms_fft_array[i] = rms_fft
        db_fft_array[i] = db_fft

    return db_spl_aft_cal_array, db_spl_bef_cal_array, filtered_signal_array, fft_aft_cal_array, rms_sound_aft_cal_array, signal_array, rms_fft_array, db_fft_array
