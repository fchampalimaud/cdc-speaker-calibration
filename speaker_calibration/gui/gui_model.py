import numpy as np

from speaker_calibration.protocol.classes import Signal
from speaker_calibration.settings.hardware import Hardware
from speaker_calibration.settings.input_settings import Settings


class SpeakerCalibrationModel:
    """
    The data model which interacts with the frontend of the application through SpeakerCalibrationController.

    Attributes
    ----------
    input_parameters : Settings
        the object containing the input parameters used for the calibration.
    hardware_config : Hardware
        the object containing information regarding the equipment being calibrated.
    inverse_filter : numpy.ndarray
        a two-column array in which the first column is the frequency axis and the second is the filter itself which will be used to flatten the frequency spectrum of the sound being played by the speaker.
    calibration_parameters : numpy.ndarray
        an array of size 2 in which index-0 is the slope and index-1 is the intercept of the calibration curve.
    psd_signal : numpy.ndarray
        an array of size 2 in which index-0 contains the signal that is loaded to the soundcard and index-1 contains the recording of the signal played by it.
    calibration_signals : numpy.ndarray
        a two-column array in which the first column are the calibration signals loaded to the soundcard and the second column are the recorded sounds.
    calibration_data : numpy.ndarray
        a three-column array in which the first column is the x-axis (logarithmic attenuation levels) and the remaining columns are y-axis (dB SPL values of the calibration signals - in one column the dB are calculated through the time-domain and in the other through the frequency-domain).
    test_signals : numpy.ndarray
        a two-column array in which the first column are the test signals loaded to the soundcard and the second column are the recorded sounds.
    test_data : numpy.ndarray
        a three-column array in which the first column is the x-axis (desired db SPL of the test signals) and the remaining columns are y-axis (real dB SPL values of the test signals - in one column the dB are calculated through the time-domain and in the other through the frequency-domain).
    """

    input_parameters: Settings
    hardware: Hardware
    inverse_filter: np.ndarray
    calibration_parameters: np.ndarray
    psd_signal: Signal
    calibration_signals: np.ndarray
    calibration_data: np.ndarray
    test_signals: np.ndarray
    test_data: np.ndarray

    def __init__(self):
        # self.input_parameters = Settings()
        # self.hardware = Hardware()
        self.input_parameters = None
        self.hardware = None
        self.inverse_filter = None
        self.calibration_parameters = np.zeros(2)
        self.psd_signal = None
        self.calibration_signals = None
        self.calibration_data = None
        self.test_signals = None
        self.test_data = None
