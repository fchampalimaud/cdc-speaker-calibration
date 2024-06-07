import math

# from struct import *
import os
import time

import numpy as np

# import matplotlib.pyplot as plt
from pyharp.device import Device
from pyharp.messages import HarpMessage  # , MessageType

# from threading import Thread, current_thread
# from multiprocessing import Process, current_process


def generate_noise(
    filename,
    fs=192000,  # number of samples per second (standard)
    duration=1,  # seconds
    write_file=False,
):
    head_phone_amp = 0.85
    amplitude24bits = math.pow(2, 31) - 1
    ramp_time = 0.005
    number_samples = int(duration / (1 / fs))
    rand_samp = 0.2 * np.random.randn(
        number_samples
    )  # We don't want more than 1 hence rescale by 0.2

    nr = math.floor(fs * ramp_time)
    r = (0.5 * (1 - np.cos(np.linspace(0, math.pi, nr)))) ** 2
    ramped = np.concatenate(
        (r, np.ones(number_samples - nr * 2), np.flip(r)), axis=None
    )
    sig = head_phone_amp * np.multiply(rand_samp, ramped)

    wave_left = amplitude24bits * sig
    wave_right = amplitude24bits * sig

    stereo = np.stack((wave_left, wave_right), axis=1)

    wave_int = stereo.astype(np.int32)

    if write_file:
        with open(filename, "wb") as f:
            wave_int.tofile(f)

    return wave_int.flatten()


if __name__ == "__main__":
    device = Device("COM19")
    n_points = 5  # used to be 30
    duration = 10  # seconds
    fs = 192000  # samples per second

    for x in range(0, n_points):
        sound_filename = "sound_" + str(x) + ".bin"
        wave_int = generate_noise(
            sound_filename, fs=fs, duration=duration, write_file=True
        )

        # loads the .bin file to index 2 of the soundcard
        os.system("cmd /c toSoundCard.exe sound_" + str(x) + ".bin 2 0 " + str(fs))

        # sends the PlaySoundOrFrequency message to the soundcard to play the noise at index 2 (message address: 32)
        device.send(HarpMessage.WriteU16(32, 2).frame, False)
        time.sleep(duration)

    device.disconnect()
