import numpy as np


def generate_noise(fs: int = 192000, duration: float = 1, head_phone_amp: float = 0.85, ramp_time: float = 0.005, truncated: bool = True):
    """
    Lorem ipsum.

    Parameters
    ----------

    Returns
    -------
    """
    number_samples = int(fs * duration)
    random_sample = 0.2 * np.random.randn(number_samples)  # We don't want more than 1 hence rescale by 0.2

    if truncated:
        random_sample[random_sample > 1 | random_sample < -1] = 0

    nr = np.floor(fs * ramp_time)
    r = (0.5 * (1 - np.cos(np.linspace(0, np.pi, nr)))) ** 2
    ramped = np.concatenate((r, np.ones(number_samples - nr * 2), np.flip(r)), axis=None)
    signal = head_phone_amp * np.multiply(random_sample, ramped)

    return signal

    # f_vec_sc_h = np.fft.rfftfreq(input_parameters.sound_duration_db * hardware.fs_sc, d = 1 / hardware.fs_sc)
    # int_samp = input_parameters.time_constant * input_parameters.fs_adc

    # f_interp = np.interp(f_vec_sc_h, f_vec, 0.5 * int_samp * cal_factor)
    # freq_to_use = f_vec_sc_h[f_vec_sc_h > input_parameters.freq_min & f_vec_sc_h < input_parameters.freq_max]

    # n5Hz = 50
    # fix = (0.5 * (1 - np.cos(np.linspace(0, np.pi, n5Hz)))) ** 2

    # freq_to_use[input_parameters.s_dur_db * input_parameters.freq_min - n5Hz + 2 : input_parameters.s_dur_db * input_parameters.freq_min + 1] = fix
    # freq_to_use[input_parameters.s_dur_db * input_parameters.freq_max + 1 : input_parameters.s_dur_db * input_parameters.freq_max + n5Hz] = np.flip(fix)

    # noise_cal = np.fft.irfft(np.multiply(np.multiply(np.fft.rfft(signal), f_interp), freq_to_use), n = input_parameters.sound_duration_db * hardware.fs_sc)

    # noise_vec = noise_cal * 0.2 / np.sqrt(np.mean(noise_cal**2))


def create_sound_file(signal: np.ndarray, filename: str):
    """
    Lorem ipsum.

    Parameters
    ----------
    """
    amplitude24bits = np.pow(2, 31) - 1
    wave_left = amplitude24bits * signal
    wave_right = amplitude24bits * signal

    stereo = np.stack((wave_left, wave_right), axis=1)

    wave_int = stereo.astype(np.int32)

    with open(filename, "wb") as f:
        wave_int.tofile(f)
