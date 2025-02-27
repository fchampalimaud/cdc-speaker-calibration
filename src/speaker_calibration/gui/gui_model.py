import numpy as np
import yaml

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
        a two-column array in which the first column is the frequency axis and the second is the filter itself which will be used to flatten the frequency spectrum of the sound being pltesayed by the speaker.
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

    settings: Settings
    hardware: Hardware

    def __init__(self):
        with open("config/hardware.yml", "r") as file:
            hardware = yaml.safe_load(file)
        with open("config/settings.yml", "r") as file:
            settings = yaml.safe_load(file)

        self.settings = Settings(**settings)
        self.hardware = Hardware(**hardware)

    def initialize_data(self):
        self.data = Data(
            sound_type=self.settings.sound_type,
            num_amp=self.settings.sound.calibration.att_steps,
            num_db=self.settings.sound.test_calibration.db_steps,
            num_freq=self.settings.sound.freq.num_freqs,
            fs_sc=self.hardware.soundcard.fs,
            fs_adc=self.hardware.fs_adc,
            calibration_duration=self.settings.sound.calibration.sound_duration,
            test_duration=self.settings.sound.test_calibration.sound_duration,
            inverse_filter_duration=self.settings.sound.inverse_filter.sound_duration,
        )


class Data:
    def __init__(
        self,
        sound_type: str,
        num_amp: int,
        num_db: int,
        fs_sc: int,
        fs_adc: int,
        calibration_duration: float,
        test_duration: float,
        inverse_filter_duration: float = None,
        num_freq: int = None,
    ):
        if sound_type == "Noise":
            self.inverse_filter = InverseFilterData(
                inverse_filter_duration, fs_sc, fs_adc
            )
            self.calibration = CalibrationData(
                sound_type=sound_type,
                num_amp=num_amp,
                duration=calibration_duration,
                fs_sc=fs_sc,
                fs_adc=fs_adc,
            )
            self.test = CalibrationData(
                sound_type=sound_type,
                num_amp=num_db,
                duration=test_duration,
                fs_sc=fs_sc,
                fs_adc=fs_adc,
            )
        elif sound_type == "Pure Tones":
            self.calibration = CalibrationData(
                sound_type=sound_type,
                num_amp=num_amp,
                duration=calibration_duration,
                fs_sc=fs_sc,
                fs_adc=fs_adc,
                num_freq=num_freq,
            )
            self.test = CalibrationData(
                sound_type=sound_type,
                num_amp=num_db,
                duration=test_duration,
                fs_sc=fs_sc,
                fs_adc=fs_adc,
                num_freq=num_freq,
            )


class CalibrationData:
    def __init__(
        self,
        sound_type: str,
        num_amp: int,
        duration: float,
        fs_sc: int,
        fs_adc: int,
        num_freq: int = None,
    ):
        if sound_type == "Noise":
            self.signals = np.zeros((int(fs_sc * duration), num_amp + 1))
            self.recorded_sounds = np.zeros(
                (int(fs_adc * duration + 1000), num_amp + 1)
            )
            self.data = np.zeros((num_amp, 2))
        elif sound_type == "Pure Tones":
            self.signals = np.zeros((int(fs_sc * duration), num_amp + 1, num_freq))
            self.recorded_sounds = np.zeros(
                (int(fs_adc * duration + 1000), num_amp + 1, num_freq)
            )
            self.data = np.zeros((num_amp, num_freq, 3))


class InverseFilterData:
    def __init__(
        self,
        duration: float,
        fs_sc: int,
        fs_adc: int,
    ):
        self.signal = np.zeros((int(fs_sc * duration), 2))
        self.recording = np.zeros((int(fs_adc * duration), 2))
        self.filter = np.zeros((int(fs_adc * duration + 1000 / 2), 2))
