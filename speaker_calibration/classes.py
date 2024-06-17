import os

import numpy as np
import yaml
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from scipy.signal import butter, sosfilt

# from record_sound import record_sound


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


class Signal:
    """
    A class containing a generated signal and every operation performed over it (load, record, fft, dB calculation, etc).

    Attributes
    ----------
    signal : numpy.ndarray
        the generated signal.
    fs : float
        the sampling frequency of the signal (Hz).
    duration : float
        the duration of the signal (s).
    recorded_sound : numpy.ndarray
        the recorded signal.
    rms : float
        the root mean square (RMS) of the signal (s).
    db_spl : float
        the dB SPL of the signal.
    fft : numpy.ndarray
        the fft of the signal.
    rms_fft : float
        the root mean square (RMS) of the signal (s) calculated from the fft.
    db_fft : float
        the dB SPL of the signal calculated from the fft.
    freq_array : numpy.ndarray
        the frequency array which corresponds to the fft of the signal (Hz).
    """

    signal: np.ndarray
    fs: float
    duration: float
    recorded_sound: np.ndarray
    rms: float
    db_spl: float
    fft: np.ndarray
    rms_fft: float
    db_fft: float
    freq_array: np.ndarray

    def __init__(
        self,
        duration: float,
        hardware: Hardware,
        input_parameters: InputParameters,
        filter: bool = False,
        calibrate: bool = False,
        calibration_factor: np.ndarray = np.zeros((1, 2)),
        attenuation: float = 1,
    ):
        # Generates the signal
        self.signal = generate_noise(
            hardware.fs_sc,
            duration,
            input_parameters.amplification * attenuation,
            input_parameters.ramp_time,
            filter,
            input_parameters.freq_min,
            input_parameters.freq_max,
            calibrate,
            calibration_factor,
        )

        # Inputs the sampling frequency and duration of the signal
        self.fs = hardware.fs_sc
        self.duration = duration

    def load_sound(self):
        """
        Loads the sound to the (Harp) Sound Card.
        """
        create_sound_file(self.signal, "sound.bin")
        os.system("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(self.fs))

    def record_sound(self, input_parameters: InputParameters, filter: bool = False):
        """
        Plays the signal in the soundcard and records it with a microphone + DAQ system.

        Parameters
        ----------
        input_parameters : InputParameters
            the object containing the input parameters used for the calibration.
        filter : bool, optional
            whether to filter the signal.
        """
        # self.recorded_sound, _ = record_sound(input_parameters.fs_adc, self.duration)
        self.recorded_sound = self.signal

        if filter:
            sos = butter(3, [input_parameters.freq_high, input_parameters.freq_low], btype="bandpass", output="sos", fs=input_parameters.fs_adc)
            self.recorded_sound = sosfilt(sos, self.recorded_sound)

    def db_spl_calculation(self, input_parameters: InputParameters):
        """
        Calculates the dB SPL of the recorded signal.

        Parameters
        ----------
        input_parameters : InputParameters
            the object containing the input parameters used for the calibration.
        """
        signal_pascal = self.recorded_sound[int(0.1 * self.recorded_sound.size) : int(0.9 * self.recorded_sound.size)] / input_parameters.mic_factor
        self.rms = np.sqrt(np.mean(signal_pascal**2))
        self.db_spl = 20 * np.log10(self.rms / input_parameters.reference_pressure)

        # TODO: Organize this code
        fft = np.abs(np.fft.fft(self.recorded_sound)) ** 2
        self.rms_fft = np.sqrt(np.sum(fft) / (fft.size**2 * input_parameters.mic_factor**2))
        self.db_fft = 20 * np.log10(self.rms_fft / input_parameters.reference_pressure)

    def fft_calculation(self, input_parameters: InputParameters):
        """
        Calculates the fft of the recorded signal.

        Parameters
        ----------
        input_parameters : InputParameters
            the object containing the input parameters used for the calibration.
        """
        self.fft, self.freq_array, self.rms_fft = fft_intervals(
            self.recorded_sound[int(0.1 * self.recorded_sound.size) : int(0.9 * self.recorded_sound.size)],
            input_parameters.time_constant,
            input_parameters.fs_adc,
            input_parameters.smooth_window,
        )
        self.db_fft = 20 * np.log10(self.rms_fft / input_parameters.reference_pressure)
