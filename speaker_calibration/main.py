import numpy as np
import yaml
from pyharp.device import Device
from psd_calibration import psd_calibration
from db_calibration import db_calibration


class Hardware:
    harp_soundcard: bool
    soundcard_com: str
    soundcard_id: str
    soundcard_fs: int = 192000  # SoundCard Sampling Frequency (Hz)
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int

    def __init__(self, **args):
        self.__dict__.update(args)


class InputParameters:
    # These parameters are from the Calibrate.m  file
    adc_fs: int = 250000  # ADC Sampling Frequency (Hz)
    s_dur_cal: float = 30  # total duration of sound played for calibration (s)
    s_dur_db: float = 15  # total duration of sound played for dB estimation (s)
    s_dur_st: float = 5  # total duration of sound played for st (??) estimation (s)
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
        self.__dict__.update(args)
        self.log_att = np.linspace(self.att_min, self.att_max, self.att_steps)
        self.att_fac = 10**self.log_att

        # def __init__(self):
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


if __name__ == "__main__":
    with open("config/settings.yml", "r") as file:
        settings = yaml.safe_load(file)
    input_parameters = InputParameters(**settings)

    with open("config/hardware.yml", "r") as file:
        hardware_settings = yaml.safe_load(file)
    hardware = Hardware(**hardware_settings)
    device = Device(hardware.soundcard_com)

    # TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)

    cal_factor, f_vec, sig_bef_cal, fft_bef_cal = psd_calibration(device, input_parameters, hardware)

    db_spl_aft_cal = db_calibration()  # unfinished

    fit_parameters = np.polyfit(input_parameters.log_att, db_spl_aft_cal, 1)

    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    device.disconnect()

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
