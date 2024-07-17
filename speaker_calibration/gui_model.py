import numpy as np

from classes import InputParameters, Hardware, Signal


class SpeakerCalibrationModel:
    def __init__(self):
        self.input_parameters = InputParameters()
        self.hardware_config = Hardware()
        self.inverse_filter = None
        self.calibration_parameters = np.zeros(2)
        self.psd_signal = np.zeros(2, dtype=np.ndarray)
        self.calibration_signals = None
        self.calibration_data = None
        self.test_signals = None
        self.test_data = None
