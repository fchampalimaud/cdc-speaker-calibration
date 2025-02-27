import os

import numpy as np
from speaker_calibration.protocol.generate_sound import (
    create_sound_file,
    generate_noise,
    generate_pure_tone,
)
from scipy.signal import butter, sosfilt
from speaker_calibration.protocol.record_sound import record_sound_nidaq


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
    freq_min : float
        minimum frequency to consider to pass band.
    freq_max : float
        maximum frequency to consider to pass band.
    fs_adc : float
        sampling frequency of the ADC (Hz).
    recorded_sound : numpy.ndarray
        the recorded signal.
    reference_pressure : float
        reference pressure (Pa).
    mic_factor : float
        factor of the microphone (V/Pa).
    db_spl : float
        the dB SPL of the signal.
    db_fft : float
        the dB SPL of the signal calculated from the fft.
    """

    signal: np.ndarray
    fs: float
    duration: float
    freq_min: float
    freq_max: float
    fs_adc: float
    recorded_sound: np.ndarray
    reference_pressure: float
    mic_factor: float
    db_spl: float
    db_fft: float

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
            self.signal = generate_pure_tone(
                freq, duration, fs, amplification, ramp_time
            )

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
        os.system(
            "cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(int(self.fs))
        )

    def record_sound(
        self,
        fs_adc: float = 192000,
        filter: bool = False,
        freq_min: float = None,
        freq_max: float = None,
    ):
        """
        Plays the signal in the soundcard and records it with a microphone + DAQ system.

        Parameters
        ----------
        fs_adc : float, optional
            sampling frequency of the ADC (Hz).
        filter : bool, optional
            whether to filter the signal.
        freq_min : float, optional
            minimum frequency to consider to pass band.
        freq_max : float, optional
            maximum frequency to consider to pass band.
        """
        self.fs_adc = fs_adc
        self.recorded_sound = record_sound_nidaq(self.fs_adc, self.duration)

        if filter:
            if freq_min is not None:
                self.freq_min = freq_min
            if freq_max is not None:
                self.freq_max = freq_max

            sos = butter(
                3,
                [self.freq_min, self.freq_max],
                btype="bandpass",
                output="sos",
                fs=self.fs_adc,
            )
            self.recorded_sound = sosfilt(sos, self.recorded_sound)

    def db_spl_calculation(
        self, mic_factor: float = None, reference_pressure: float = None
    ):
        """
        Calculates the dB SPL of the recorded signal.

        Parameters
        ----------
        mic_factor : float, optional
            factor of the microphone (V/Pa).
        reference_pressure : float, optional
            reference pressure (Pa).
        """

        if mic_factor is not None:
            self.mic_factor = mic_factor
        if reference_pressure is not None:
            self.reference_pressure = reference_pressure

        signal_pascal = (
            self.recorded_sound[
                int(0.1 * self.recorded_sound.size) : int(
                    0.9 * self.recorded_sound.size
                )
            ]
            / self.mic_factor
        )
        rms = np.sqrt(np.mean(signal_pascal**2))
        self.db_spl = 20 * np.log10(rms / self.reference_pressure)

    def db_fft_calculation(
        self, mic_factor: float = None, reference_pressure: float = None
    ):
        """
        Calculates the dB SPL of the recorded signal from the fft.

        Parameters
        ----------
        mic_factor : float, optional
            factor of the microphone (V/Pa).
        reference_pressure : float, optional
            reference pressure (Pa).
        """
        if mic_factor is not None:
            self.mic_factor = mic_factor
        if reference_pressure is not None:
            self.reference_pressure = reference_pressure

        fft = np.abs(np.fft.fft(self.recorded_sound)) ** 2
        rms_fft = np.sqrt(np.sum(fft) / (fft.size**2 * self.mic_factor**2))
        self.db_fft = 20 * np.log10(rms_fft / self.reference_pressure)

    def execute_protocol(
        self, fs_adc: float = 192000, filter: bool = True, mic_factor=None
    ):
        """
        Calls the remaining methods (load_sound, record_sound, db_spl_calculation, db_fft_calculation).

        Parameters
        ----------
        fs_adc : float, optional
            sampling frequency of the ADC (Hz).
        filter : bool, optional
            whether to filter the signal.
        mic_factor : float, optional
            factor of the microphone (V/Pa).
        """
        if mic_factor is not None:
            self.mic_factor = mic_factor

        if not hasattr(self.mic_factor):
            raise ValueError("mic_factor must have a non-None value")

        self.load_sound()
        self.record_sound(fs_adc=fs_adc, filter=filter)
        self.db_spl_calculation()
        self.db_fft_calculation()
