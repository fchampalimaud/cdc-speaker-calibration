import os

import numpy as np
import yaml
from speaker_calibration.generate_noise import create_sound_file, generate_noise, generate_pure_tone
from scipy.signal import butter, sosfilt
from speaker_calibration.record_sound import record_sound_nidaq


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
        amplification to be used in the PSD (power spectral density) calibration step.
    sound_type : str
        whether the calibration should be made with pure tones or white noise.
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
    sound_type: str

    def __init__(self):
        # Loads the content of the YAML file into a dictionary
        with open("config/settings.yml", "r") as file:
            settings_dict = yaml.safe_load(file)

        # Updates the attributes of the object based on the dictionary generated from the YAML file
        self.__dict__.update(settings_dict)

    def update(self, settings_dict: dict):
        self.__dict__.update(settings_dict)


class Hardware:
    """
    A class used to represent the equipment being calibrated.

    Attributes
    ----------
    fs_sc : int
        the sampling frequency of the soundcard (Hz).
    harp_soundcard : bool
        indicates whether the soundcard being calibrated is a Harp device or not.
    soundcard_com : str
        indicates the COM number the soundcard corresponds to in the computer used for the calibration. The string should be of the format "COM?", in which "?" is the COM number.
    soundcard_id : str
        the ID of the soundcard. If the soundcard is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    harp_audio_amp : bool
        indicates whether the audio amplifier used in the calibration is a Harp device or not.
    audio_amp_id : str
        the ID of the audio amplifier. If the audio amplifier is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    speaker_id : int
        the ID number of the speaker being calibrated (StC).
    setup_id : int
        the ID number of the setup.
    """

    fs_sc: int
    harp_soundcard: bool
    soundcard_com: str
    soundcard_id: str
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int
    setup_id: int

    def __init__(self):
        self.fs_sc = 192000
        self.harp_soundcard = True
        self.soundcard_com = ""
        self.soundcard_id = ""
        self.harp_audio_amp = True
        self.audio_amp_id = ""
        self.speaker_id = 0
        self.setup_id = 0


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
        fs: float,
        sound_type: str = "Noise",
        amplification: float = 1,
        ramp_time: float = 0.005,
        filter: bool = False,
        freq_min: float = 0,
        freq_max: float = 80000,
        calibrate: bool = False,
        calibration_factor: np.ndarray = np.zeros((1, 2)),
        freq: float = 5000,
        mic_factor: float = None,
        reference_pressure: float = 0.00002,
    ):
        if sound_type == "Noise":
            # Generates the signal
            self.signal = generate_noise(
                duration,
                fs,
                amplification,
                ramp_time,
                filter,
                freq_min,
                freq_max,
                calibrate,
                calibration_factor,
            )
        elif sound_type == "Pure Tone":
            self.signal = generate_pure_tone(freq, amplification, fs, duration, ramp_time)

        # Inputs the sampling frequency and duration of the signal
        self.fs = fs
        self.duration = duration
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.reference_pressure = reference_pressure
        if mic_factor is not None:
            self.mic_factor = mic_factor

    def load_sound(self):
        """
        Loads the sound to the (Harp) Sound Card.
        """
        create_sound_file(self.signal, "sound.bin")
        print("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(int(self.fs)))
        os.system("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(int(self.fs)))

    def record_sound(self, fs_adc: float = 192000, filter: bool = False, freq_min: float = None, freq_max: float = None):
        """
        Plays the signal in the soundcard and records it with a microphone + DAQ system.

        Parameters
        ----------
        input_parameters : InputParameters
            the object containing the input parameters used for the calibration.
        filter : bool, optional
            whether to filter the signal.
        """
        self.recorded_sound = record_sound_nidaq(fs_adc, self.duration)
        # self.recorded_sound = self.signal

        if filter:
            if freq_min is not None:
                self.freq_min = freq_min
            if freq_max is not None:
                self.freq_max = freq_max

            sos = butter(3, [self.freq_min, self.freq_max], btype="bandpass", output="sos", fs=fs_adc)
            self.recorded_sound = sosfilt(sos, self.recorded_sound)

    def db_spl_calculation(self, mic_factor: float = None, reference_pressure: float = None):
        """
        Calculates the dB SPL of the recorded signal.

        Parameters
        ----------
        input_parameters : InputParameters
            the object containing the input parameters used for the calibration.
        """

        if mic_factor is not None:
            self.mic_factor = mic_factor
        self.reference_pressure = reference_pressure

        signal_pascal = self.recorded_sound[int(0.1 * self.recorded_sound.size) : int(0.9 * self.recorded_sound.size)] / self.mic_factor
        self.rms = np.sqrt(np.mean(signal_pascal**2))
        self.db_spl = 20 * np.log10(self.rms / self.reference_pressure)

    def db_fft_calculation(self, mic_factor: float = None, reference_pressure: float = None):
        if mic_factor is not None:
            self.mic_factor = mic_factor
        if reference_pressure is not None:
            self.reference_pressure = reference_pressure

        self.fft = np.abs(np.fft.fft(self.recorded_sound)) ** 2
        self.rms_fft = np.sqrt(np.sum(self.fft) / (self.fft.size**2 * self.mic_factor**2))
        self.db_fft = 20 * np.log10(self.rms_fft / self.reference_pressure)

    def execute_protocol(self, fs_adc: float = 192000, filter: bool = True, mic_factor=None):
        if mic_factor is not None:
            self.mic_factor = mic_factor

        if not hasattr(self.mic_factor):
            raise ValueError("mic_factor must have a non-None value")

        self.load_sound()
        self.record_sound(fs_adc=fs_adc, filter=filter)
        self.db_spl_calculation()
        self.db_fft_calculation()
