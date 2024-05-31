import numpy as np


class Hardware:
    harp_soundcard: bool
    soundcard_id: str
    soundcard_fs: int = 192000  # SoundCard Sampling Frequency (Hz)
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int


class InputParameters:
    # These parameters are from the Calibrate.m  file
    adc_fs: int = 250000  # ADC Sampling Frequency (Hz)
    s_dur_cal: float = 30  # total duration of sound played for calibration (s)
    s_dur_db: float = 15  # total duration of sound played for dB estimation (s)
    s_dur_st: float = 5  # total duration of sound played for st (??) estimation (s)
    ramp_time: float = 0.005  # ramp time (s)
    ref: float = 20e-6  # self.reference pressure (Pa) TODO: ask
    mic_fac: float = 10  # factor on the mic (V/Pa)
    att_min: float = 0.65  # minimum speaker attenuation value (log)
    att_steps: int = 15  # number of attenuation steps
    att_max: float = 0.1  # maximum speaker attenuation value (log)
    smooth_window: int = 1  # smoothing window fft (number of bins)
    time_cons: float = 0.025  # time cons to estimate the psd (s)
    # TODO: clarify difference between the types of frequencies
    freq_min: float = 5000  # minimum frequency to consider to pass band
    freq_max: float = 20000  # maximum frequency to consider to pass band
    freq_high: float = 4500  # freq. for high pass filter after recording
    freq_low: float = 25000  # freq. for low pass filter after recording
    amp: float = 0.8  # NOTE: change to .85 for calibration of headphones!

    def __init__(self):
        # These parameters are from the runCalibration2.m file
        self.log_att = np.linspace(self.att_min, self.att_max, self.att_steps)
        self.att_fac = 10**self.log_att

        self.n_samp_sc_cal = self.s_dur_cal * self.fs_sc  # number of sound samples for Sound Card (calibration)
        self.n_samp_ai_cal = self.s_dur_cal * self.fs_ai  # number of sound samples for National Instruments (calibration)
        self.time_sc_cal = np.arange(1, self.n_samp_sc_cal + 1) / self.fs_sc  # time vector for Sound Card (s) (calibration)
        self.time_ai_cal = np.arange(1, self.n_samp_ai_cal + 1) / self.fs_ai  # time vector for National Instruments (s) (calibration)
        self.f_vec_sc_cal = (np.arange(self.n_samp_sc_cal) / self.n_samp_sc_cal) * self.fs_sc  # frequency vector for Sound Card (calibration)
        self.f_vec_ai_cal = (np.arange(self.n_samp_ai_cal) / self.n_samp_ai_cal) * self.fs_ai  # frequency vector for National Instruments (calibration)

        self.n_samp_sc_db = self.s_dur_db * self.fs_sc  # number of sound samples for Sound Card (dB estimation)
        self.n_samp_ai_db = self.s_dur_db * self.fs_ai  # number of sound samples for National Instruments (dB estimation)
        self.time_sc_db = np.arange(1, self.n_samp_sc_db + 1) / self.fs_sc  # time vector for Sound Card (s) (dB estimation)
        self.time_ai_db = np.arange(1, self.n_samp_ai_db + 1) / self.fs_ai  # time vector for National Instruments (s) (dB estimation)
        self.f_vec_sc_db = (np.arange(self.n_samp_sc_db) / self.n_samp_sc_db) * self.fs_sc  # frequency vector for Sound Card (dB estimation)
        self.f_vec_ai_db = (np.arange(self.n_samp_ai_db) / self.n_samp_ai_db) * self.fs_ai  # frequency vector for National Instruments (dB estimation)

        self.n_samp_sc_st = self.s_dur_st * self.fs_sc  # number of sound samples for Sound Card (dB estimation)
        self.n_samp_ai_st = self.s_dur_st * self.fs_ai  # number of sound samples for National Instruments (dB estimation)
        self.time_sc_st = np.arange(1, self.n_samp_sc_st + 1) / self.fs_sc  # time vector for Sound Card (s) (dB estimation)
        self.time_ai_st = np.arange(1, self.n_samp_ai_st + 1) / self.fs_ai  # time vector for National Instruments (s) (dB estimation)
        self.f_vec_sc_st = (np.arange(self.n_samp_sc_st - 1) / self.n_samp_sc_st) * self.fs_sc  # frequency vector for Sound Card (dB estimation)
        self.f_vec_ai_st = (np.arange(self.n_samp_ai_st - 1) / self.n_samp_ai_st) * self.fs_ai  # frequency vector for National Instruments (dB estimation)


if __name__ == "__main__":
    print("Hello World!")

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
# TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)


# TODO: install pyharp
# device = Device("COM19")
# n_points = 5  # used to be 30
# duration = 10  # seconds
# fs = 192000  # samples per second

# for x in range(0, n_points):
#     sound_filename = "sound_" + str(x) + ".bin"
#     wave_int = generate_noise(sound_filename, fs=fs, duration=duration, write_file=True)

#     # loads the .bin file to index 2 of the soundcard
#     os.system("cmd /c toSoundCard.exe sound_" + str(x) + ".bin 2 0 " + str(fs))

#     # sends the PlaySoundOrFrequency message to the soundcard to play the noise at index 2 (message address: 32)
#     device.send(HarpMessage.WriteU16(32, 2).frame, False)
#     time.sleep(duration)

# device.disconnect()
