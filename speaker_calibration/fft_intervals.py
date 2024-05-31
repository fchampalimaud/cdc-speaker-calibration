import numpy as np
from scipy.ndimage import uniform_filter1d


# TODO: Search Welch's Method because of the way the power gets divided across bins (that's why the signal is divided in n intervals)
def fft_intervals(signal, time_cons, fs_ai, smooth_fac):
    n_int = np.floor(signal.size / (time_cons * fs_ai))  # number of intervals
    int_samp = time_cons * fs_ai  # interval in samples

    fft_int = np.zeros(int_samp, n_int - 9)

    for i in range(5, n_int - 4):
        sig_fft = signal[i * int_samp + 1 : (i + 1) * int_samp]  # interval to consider
        fft_int[:, i] = np.abs(np.fft.fft(sig_fft)) ** 2  # abs value signal

    f_vec = fs_ai * np.arange(int_samp) / int_samp  # frequency vector
    fft_av = np.sqrt(np.mean(fft_int, 2))  # take the mean of all intervals

    # single-sided spectrum

    f_vec_h = f_vec[1 : f_vec.size // 2 + 1]
    fft_av = fft_av[1 : f_vec.size // 2 + 1]
    fft_av = uniform_filter1d(fft_av, smooth_fac)

    freq1 = 2500
    freq2 = 35000

    n1 = np.floor(freq1 * time_cons) + 1
    n2 = np.floor(freq2 * time_cons) + 1

    # f_vec_h_rat = f_vec_h(n1:n2)
    # N = n2-n1 + 1

    sum_fft = 2 * sum(fft_int[n1:n2, :]) / int_samp
    rms_fft = np.sqrt(sum_fft / int_samp)

    RMS = np.mean(rms_fft, 2)

    return fft_av, f_vec_h, n_int, int_samp, RMS
