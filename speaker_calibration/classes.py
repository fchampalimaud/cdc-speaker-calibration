import numpy as np
import yaml


class InputParameters:
    """
    A class containing the input parameters used for the calibration.

    Attributes
    ----------
    fs_adc : int
        sampling frequency of the ADC (Hz).
    sound_duration_psd : float
        duration of the sound used to flatten the power spectral density - PSD - of the equipment (s) ??.
    sound_duration_db : float
        duration of the sounds used to calibrate the amplitude response of the equipment (s) ??.
    sound_duration_test : float
        duration of the sounds used to test the calibration (s).
    ramp_time : float
        ramp time of the sound (s).
    reference_pressure : float
        reference pressure (Pa).
    mic_factor : float
        factor of the microphone (V/Pa).
    att_min : float
        minimum speaker attenuation value (log).
    att_max : float
        maximum speaker attenuation value (log).
    att_steps : int
        number of attenuation steps.
    smooth_window : int
        number of bins of the moving average smoothing window.
    time_constant : float
        duration of each division of the original signal that is used to compute the PSD (s). Used in the function `fft_intervals`.
    freq_min : float
        minimum frequency to consider to pass band.
    freq_max : float
        maximum frequency to consider to pass band.
    freq_high : float
        cutoff frequency of the high pass filter applied to the recorded signal (Hz).
    freq_low : float
        cutoff frequency of the low pass filter applied to the recorded signal (Hz).
    amplification : float
        NOTE: change to .85 for calibration of headphones!
    """

    fs_adc: int
    sound_duration_psd: float
    sound_duration_db: float
    sound_duration_test: float
    ramp_time: float
    reference_pressure: float
    mic_factor: float
    att_min: float
    att_max: float
    att_steps: int
    smooth_window: int
    time_constant: float
    freq_min: float
    freq_max: float
    freq_high: float
    freq_low: float
    amplification: float

    def __init__(self):
        # Loads the content of the YAML file into a dictionary
        with open("config/settings.yml", "r") as file:
            settings_dict = yaml.safe_load(file)

        # Updates the attributes of the object based on the dictionary generated from the YAML file
        self.__dict__.update(settings_dict)

        # Initializes new attributes based on the loaded ones
        self.log_att = np.linspace(self.att_min, self.att_max, self.att_steps)
        self.att_factor = 10**self.log_att


class Hardware:
    """
    A class used to represent the equipment being calibrated.

    Attributes
    ----------
    harp_soundcard : bool
        indicates whether the soundcard being calibrated is a Harp device or not.
    soundcard_com : str
        indicates the COM number the soundcard corresponds to in the computer used for the calibration. The string should be of the format "COM?", in which "?" is the COM number.
    soundcard_id : str
        the ID of the soundcard. If the soundcard is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    fs_sc : int
        the sampling frequency of the soundcard (Hz).
    harp_audio_amp : bool
        indicates whether the audio amplifier used in the calibration is a Harp device or not.
    audio_amp_id : str
        the ID of the audio amplifier. If the audio amplifier is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    speaker_id : int
        the ID number of the speaker being calibrated (StC).
    """

    harp_soundcard: bool
    soundcard_com: str
    soundcard_id: str
    fs_sc: int
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int

    def __init__(self):
        # Loads the content of the YAML file into a dictionary
        with open("config/hardware.yml", "r") as file:
            hardware_dict = yaml.safe_load(file)

        # Updates the attributes of the object based on the dictionary generated from the YAML file
        self.__dict__.update(hardware_dict)
