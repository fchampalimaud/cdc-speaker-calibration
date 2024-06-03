import os
import time
import numpy as np
from generate_noise import generate_noise, create_sound_file
from fft_intervals import fft_intervals
from pyharp.messages import HarpMessage
# TODO: import needed classes


def psd_calibration(device, input_parameters, hardware):
    signal = generate_noise(fs=hardware.soundcard_fs, duration=input_parameters.s_dur_cal)
    create_sound_file(signal, "sound.bin")
    # TODO: add toSoundCard.exe to the project
    os.system("cmd /c toSoundCard.exe sound.bin 2 0 " + str(hardware.soundcard_fs))

    device.send(HarpMessage.WriteU16(32, 2).frame, False)
    time.sleep(input_parameters.s_dur_cal)

    # TODO: Record sound
    rec_signal = np.zeros(1000)

    fft_bef_cal, f_vec, n_int, int_samp, rms = fft_intervals(rec_signal, input_parameters.time_cons, input_parameters.adc_fs, input_parameters.smooth_window)

    cal_factor = 1 / fft_bef_cal

    return cal_factor, f_vec, rec_signal, fft_bef_cal
