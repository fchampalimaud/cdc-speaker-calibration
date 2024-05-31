import numpy as np


def generate_noise(filename, fs=192000, duration=1, head_phone_amp=0.85, ramp_time=0.005, write_file=False, truncated=True):
    number_samples = int(duration / (1 / fs))
    rand_samp = 0.2 * np.random.randn(number_samples)  # We don't want more than 1 hence rescale by 0.2

    if truncated:
        rand_samp[rand_samp > 1 | rand_samp < -1] = 0

    nr = np.floor(fs * ramp_time)
    r = (0.5 * (1 - np.cos(np.linspace(0, np.pi, nr)))) ** 2
    ramped = np.concatenate((r, np.ones(number_samples - nr * 2), np.flip(r)), axis=None)
    sig = head_phone_amp * np.multiply(rand_samp, ramped)

    return sig


# TODO: left and right channel to input in the soundcard
# amplitude24bits = np.pow(2, 31) - 1
# wave_left = amplitude24bits * sig
# wave_right = amplitude24bits * sig

# stereo = np.stack((wave_left, wave_right), axis=1)

# wave_int = stereo.astype(np.int32)

# if write_file:
#     with open(filename, "wb") as f:
#         wave_int.tofile(f)

# return wave_int.flatten()
