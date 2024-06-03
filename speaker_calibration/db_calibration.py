import os
import numpy as np
from scipy.signal import butter, sosfilt
from generate_noise import generate_noise, create_sound_file
from fft_intervals import fft_intervals


# TODO: Adapt to return all of the calibration points
# TODO: Organization
def df_calibration(input_parameters, hardware, cal_factor, f_vec, sig_bef_cal):
    for i in range(input_parameters.att_steps):
        signal = generate_noise(fs=hardware.soundcard_fs, duration=input_parameters.s_dur_db)

        f_vec_sc_h = (np.arange(input_parameters.n_samp_sc_db / 2 + 1) / input_parameters.n_samp_sc_db) * hardware.soundcard_fs
        int_samp = input_parameters.time_cons * input_parameters.adc_fs

        f_interp = np.interp(f_vec_sc_h, f_vec, 0.5 * int_samp * cal_factor)
        calibration_to_use = np.concatenate(f_interp, np.flip(f_interp[1:-2]))  # Possible FIXME
        freq_to_use = f_vec_sc_h[f_vec_sc_h > input_parameters.freq_min & f_vec_sc_h < input_parameters.freq_max]

        n5Hz = 50
        fix = (0.5 * (1 - np.cos(np.linspace(0, np.pi, n5Hz)))) ** 2

        freq_to_use[input_parameters.s_dur_db * input_parameters.freq_min - n5Hz + 2 : input_parameters.s_dur_db * input_parameters.freq_min + 1] = fix
        freq_to_use[input_parameters.s_dur_db * input_parameters.freq_max + 1 : input_parameters.s_dur_db * input_parameters.freq_max + n5Hz] = np.flip(fix)

        filter_to_use = np.concatenate(freq_to_use, np.flip(freq_to_use[1:-2]))

        noise_cal = np.fft.ifft(np.multiply(np.multiply(np.fft.fft(signal), calibration_to_use), filter_to_use))

        noise_vec = noise_cal * 0.2 / np.sqrt(np.mean(noise_cal**2))

        # TODO: truncate

        signal = noise_vec

        create_sound_file(signal, "sound.bin")
        # TODO: add toSoundCard.exe to the project
        os.system("cmd /c toSoundCard.exe sound.bin 2 0 " + str(hardware.soundcard_fs))

        # TODO: Record sound
        rec_signal = np.zeros(1000)

        sos = butter(3, [input_parameters.freq_low, input_parameters.freq_high], btype="bandpass", output="sos", fs=input_parameters.adc_fs)
        filtered_signal = sosfilt(sos, rec_signal)

        fft_bef_cal, f_vec_h, n_int, int_samp, rms = fft_intervals(filtered_signal, input_parameters.time_cons, input_parameters.adc_fs, input_parameters.smooth_window)

        sig_aft_cal_pascal = filtered_signal[0.1 * filtered_signal.size : 0.9 * filtered_signal.size] / input_parameters.mic_fac
        sig_bef_cal_pascal = sig_bef_cal[0.1 * sig_bef_cal.size : 0.9 * sig_bef_cal.size] / input_parameters.mic_fac

        rms_sound_aft_cal = np.sqrt(np.mean(sig_aft_cal_pascal**2))
        rms_sound_bef_cal = np.sqrt(np.mean(sig_bef_cal_pascal**2))

        rms_fft = rms / input_parameters.mic_fac

        db_spl_aft_cal = 20 * np.log10(rms_sound_aft_cal / input_parameters.ref)
        db_spl_bef_cal = 20 * np.log10(rms_sound_bef_cal / input_parameters.ref)
        db_fft = 20 * np.log10(rms_fft / input_parameters.ref)

        print("Attenuation factor: " + str(input_parameters.att_fac[i]))
        print("dB SPL after calibration: " + str(db_spl_aft_cal))
        print("dB SPL after calibration: " + str(db_spl_bef_cal))

    return
