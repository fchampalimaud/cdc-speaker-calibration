import numpy as np


def generate_noise(fs=192000, duration=1, head_phone_amp=0.85, ramp_time=0.005, truncated=True):
    number_samples = int(duration / (1 / fs))
    random_sample = 0.2 * np.random.randn(number_samples)  # We don't want more than 1 hence rescale by 0.2

    if truncated:
        random_sample[random_sample > 1 | random_sample < -1] = 0

    nr = np.floor(fs * ramp_time)
    r = (0.5 * (1 - np.cos(np.linspace(0, np.pi, nr)))) ** 2
    ramped = np.concatenate((r, np.ones(number_samples - nr * 2), np.flip(r)), axis=None)
    signal = head_phone_amp * np.multiply(random_sample, ramped)

    return signal


def create_sound_file(signal, filename):
    amplitude24bits = np.pow(2, 31) - 1
    wave_left = amplitude24bits * signal
    wave_right = amplitude24bits * signal

    stereo = np.stack((wave_left, wave_right), axis=1)

    wave_int = stereo.astype(np.int32)

    with open(filename, "wb") as f:
        wave_int.tofile(f)
