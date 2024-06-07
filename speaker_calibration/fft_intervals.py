import numpy as np
from scipy.ndimage import uniform_filter1d


# TODO: Search Welch's Method because of the way the power gets divided across bins (that's why the signal is divided in n intervals)
def fft_intervals(signal: np.ndarray, time_constant: float, fs_adc: float, smooth_window: int = 1, freq_min: float = 20, freq_max: float = 20000):
    """
    Calculates the Fast Fourier Transform  (fft) of a signal by dividing it in different intervals and averaging their fft's. This method of calculating the fft makes the fft estimate more accurate.

    Parameters
    ----------
    signal : numpy.ndarray
        the signal whose fft is being calculated.
    time_constant : float
        duration of each division of the original signal that is used to compute the PSD (s).
    fs_adc : float
        sampling frequency of the ADC (Hz).
    smooth_window : int, optional
        number of bins of the moving average smoothing window.
    freq_min : float, optional
        minimum frequency to consider for the root mean square (RMS) calculation (Hz).
    freq_max : float, optional
        maximum frequency to consider for the root mean square (RMS) calculation (Hz).

    Returns
    -------
    fft_average : numpy.ndarray
    freq_vector : numpy.ndarray
    n_intervals : int
    samples_per_interval : int
    rms : float
    """
    # Initialization of interval variables
    samples_per_interval = time_constant * fs_adc
    n_intervals = np.floor(signal.size / (samples_per_interval))
    freq_vector = np.fft.rfft(samples_per_interval)
    fft_intervals = np.zeros((samples_per_interval, n_intervals))

    # Calculates the fft for each interval
    for i in range(n_intervals):
        signal_fft = signal[i * samples_per_interval : (i + 1) * samples_per_interval]
        fft_intervals[:, i] = np.abs(np.fft.rfft(signal_fft)) ** 2

    # Calculates the average fft and applies a moving average smoothing algorithm
    fft_average = np.sqrt(np.mean(fft_intervals, axis=1))
    fft_average = uniform_filter1d(fft_average, smooth_window)

    # Calculates the indexes that delimit the frequencies to consider in the RMS calculation
    i1 = int(freq_min / freq_vector.size)
    i2 = int(freq_max / freq_vector.size)

    # Calculates the RMS of the signal (and not of the signal's fft)
    rms_fft = np.sqrt(2 * np.sum(fft_intervals[i1:i2, :], axis=0) / (samples_per_interval**2))
    rms = np.mean(rms_fft)

    return fft_average, freq_vector, n_intervals, samples_per_interval, rms  # StC
