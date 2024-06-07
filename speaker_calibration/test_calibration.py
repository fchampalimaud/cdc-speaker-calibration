import os

import numpy as np
from classes import Hardware, InputParameters
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from scipy.signal import butter, sosfilt


def test_calibration(hardware: Hardware, input_parameters: InputParameters, cal_factor, slope, intercept):
    tdB = np.arange(70, 20, -5)
    db_spl_test = np.zeros(tdB.size, dtype=np.ndarray)
    db_fft_test = np.zeros(tdB.size, dtype=np.ndarray)

    for i in range(tdB.size):
        att = (tdB[i] - intercept) / slope
        att = 10**att
        print("Target dB: " + str(att))

        # TODO: see noise MATLAB function
        signal = generate_noise(
            fs=hardware.fs_sc,
            duration=input_parameters.sound_duration_test,
            head_phone_amp=input_parameters.amplification * att,
            filter=True,
            freq_low=input_parameters.freq_min,
            freq_high=input_parameters.freq_max,
            calibrate=True,
            cal_factor=cal_factor,
        )

        create_sound_file(signal, "sound.bin")
        # TODO: add toSoundCard.exe to the project
        os.system("cmd /c toSoundCard.exe sound.bin 2 0 " + str(hardware.soundcard_fs))

        # TODO: Record sound
        rec_signal = np.zeros(1000)

        fft_aft_cal, f_vec_h, n_int, int_samp, rms = fft_intervals(rec_signal, input_parameters.time_cons, input_parameters.adc_fs, input_parameters.smooth_window)
        rms_fft = rms / input_parameters.mic_fac
        db_fft = 20 * np.log10(rms_fft / input_parameters.ref)

        sos = butter(3, [input_parameters.freq_low, input_parameters.freq_high], btype="bandpass", output="sos", fs=input_parameters.adc_fs)
        filtered_signal = sosfilt(sos, rec_signal)

        sig_pascal = filtered_signal[0.1 * filtered_signal.size : 0.9 * filtered_signal.size] / input_parameters.mic_fac
        rms_sound = np.sqrt(np.mean(sig_pascal**2))
        db_spl = 20 * np.log10(rms_sound / input_parameters.ref)

        db_spl_test[i] = db_spl
        db_fft_test[i] = db_fft

    return db_spl_test, db_fft_test
