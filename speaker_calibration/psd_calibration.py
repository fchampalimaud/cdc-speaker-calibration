import os
import time
import numpy as np
from pyharp.device import Device
from classes import Hardware, InputParameters
from generate_noise import generate_noise, create_sound_file
from fft_intervals import fft_intervals
from pyharp.messages import HarpMessage


def psd_calibration(device: Device, input_parameters: InputParameters, hardware: Hardware):
    """
    Lorem ipsum.

    Parameters
    ----------

    Returns
    -------
    """
    signal = generate_noise(fs=hardware.fs_sc, duration=input_parameters.sound_duration_psd)
    create_sound_file(signal, "sound.bin")
    # TODO: add toSoundCard.exe to the project
    os.system("cmd /c toSoundCard.exe sound.bin 2 0 " + str(hardware.fs_sc))

    device.send(HarpMessage.WriteU16(32, 2).frame, False)
    time.sleep(input_parameters.sound_duration_psd)

    # TODO: Record sound
    rec_signal = np.zeros(1000)

    fft_bef_cal, f_vec, n_int, int_samp, rms = fft_intervals(rec_signal, input_parameters.time_constant, input_parameters.fs_adc, input_parameters.smooth_window)

    cal_factor = 1 / fft_bef_cal

    return cal_factor, f_vec, rec_signal, fft_bef_cal
