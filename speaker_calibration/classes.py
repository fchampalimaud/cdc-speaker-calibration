import numpy as np
import yaml


class InputParameters:
    """
    A class containing the input parameters used for the calibration.

    ...
    Attributes
    ----------
    fs_adc : int
        the sampling frequency of the ADC (Hz).
    sound_duration_psd : float
        duration of the sound used to flatten the power spectral density - PSD - of the equipment (s) ??.
    sound_duration_db : float
        duration of the sounds used to calibrate the amplitude response of the equipment (s) ??.
    sound_duration_test : float
        duration of the sounds used to test the calibration (s).
    ramp_time : float
        ramp time of the sound (s).
    ref : float
        lorem ipsum
    mic_fac : float
        lorem ipsum
    att_min : float
        lorem ipsum
    att_steps : int
        lorem ipsum
    att_max : float
        lorem ipsum
    smooth_window : int
        lorem ipsum
    time_cons : float
        lorem ipsum
    freq_min : float
        lorem ipsum
    freq_max : float
        lorem ipsum
    freq_high : float
        lorem ipsum
    freq_low : float
        lorem ipsum
    amp : float
        lorem ipsum
    """

    fs_adc: int = 250000  # ADC Sampling Frequency (Hz)
    sound_duration_psd: float = 30  # total duration of sound played for calibration (s)
    sound_duration_db: float = 15  # total duration of sound played for dB estimation (s)
    sound_duration_test: float = 5  # total duration of sound played for st (??) estimation (s)
    ramp_time: float = 0.005  # ramp time (s)
    ref: float = 20e-6  # self.reference pressure (Pa) TODO: ask
    mic_fac: float = 10  # factor on the mic (V/Pa)
    att_min: float = -0.65  # minimum speaker attenuation value (log)
    att_steps: int = 15  # number of attenuation steps
    att_max: float = -0.1  # maximum speaker attenuation value (log)
    smooth_window: int = 1  # smoothing window fft (number of bins)
    time_cons: float = 0.025  # time cons to estimate the psd (s)
    # TODO: clarify difference between the types of frequencies
    freq_min: float = 5000  # minimum frequency to consider to pass band
    freq_max: float = 20000  # maximum frequency to consider to pass band
    freq_high: float = 4500  # freq. for high pass filter after recording
    freq_low: float = 25000  # freq. for low pass filter after recording
    amp: float = 0.8  # NOTE: change to .85 for calibration of headphones!

    def __init__(self, **args):
        with open("config/settings.yml", "r") as file:
            settings_dict = yaml.safe_load(file)
        self.__dict__.update(settings_dict)
        self.log_att = np.linspace(self.att_min, self.att_max, self.att_steps)
        self.att_fac = 10**self.log_att

        #     # These parameters are from the runCalibration2.m file

    #     self.n_samp_ai_cal = self.s_dur_cal * self.fs_ai  # number of sound samples for National Instruments (calibration)

    #     self.n_samp_ai_db = self.s_dur_db * self.fs_ai  # number of sound samples for National Instruments (dB estimation)
    #     self.time_sc_db = np.arange(1, self.n_samp_sc_db + 1) / self.fs_sc  # time vector for Sound Card (s) (dB estimation)
    #     self.time_ai_db = np.arange(1, self.n_samp_ai_db + 1) / self.fs_ai  # time vector for National Instruments (s) (dB estimation)
    #     self.f_vec_sc_db = (np.arange(self.n_samp_sc_db) / self.n_samp_sc_db) * self.fs_sc  # frequency vector for Sound Card (dB estimation)
    #     self.f_vec_ai_db = (np.arange(self.n_samp_ai_db) / self.n_samp_ai_db) * self.fs_ai  # frequency vector for National Instruments (dB estimation)

    #     self.n_samp_ai_st = self.s_dur_st * self.fs_ai  # number of sound samples for National Instruments (dB estimation)
    #     self.time_sc_st = np.arange(1, self.n_samp_sc_st + 1) / self.fs_sc  # time vector for Sound Card (s) (dB estimation)
    #     self.time_ai_st = np.arange(1, self.n_samp_ai_st + 1) / self.fs_ai  # time vector for National Instruments (s) (dB estimation)
    #     self.f_vec_sc_st = (np.arange(self.n_samp_sc_st - 1) / self.n_samp_sc_st) * self.fs_sc  # frequency vector for Sound Card (dB estimation)
    #     self.f_vec_ai_st = (np.arange(self.n_samp_ai_st - 1) / self.n_samp_ai_st) * self.fs_ai  # frequency vector for National Instruments (dB estimation)


class Hardware:
    """
    A class used to represent the equipment being calibrated.

    ...
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
    fs_sc: int = 192000
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int

    def __init__(self):
        # Loads the content of the YAML file into a dictionary
        with open("config/hardware.yml", "r") as file:
            hardware_dict = yaml.safe_load(file)

        # Updates the attributes of the object based on the dictionary generated from the YAML file
        self.__dict__.update(hardware_dict)
