from pathlib import Path
from typing import Callable, Optional, cast

import numpy as np
from scipy.signal import butter, firwin2, freqz_sos

from speaker_calibration.config import NoiseProtocolSettings, Paths
from speaker_calibration.protocol.utils import Protocol
from speaker_calibration.recording import RecordingDevice
from speaker_calibration.sound import RecordedSound, WhiteNoise
from speaker_calibration.soundcards import HarpSoundCard, SoundCard, create_sound_file
from speaker_calibration.utils import SweepType


class NoiseProtocol(Protocol):
    def __init__(
        self,
        settings: NoiseProtocolSettings,
        soundcard: SoundCard,
        adc: RecordingDevice,
        output_path: Path,
        paths: Paths,
        callback: Optional[Callable] = None,
    ):
        super().__init__(settings, soundcard, adc, output_path, paths, callback)

        # Calculate the EQ filter
        if self.paths.eq_filter is None:
            self.eq_filter = self.calculate_eq_filter()

            # Save EQ filter
            np.save(self.output_path / "eq_filter.npy", self.eq_filter)

            # Send EQ filter and signals to the interface
            if self.callback is not None:
                self.callback("EQ Filter", self.eq_filter)
        else:
            self.eq_filter = np.load(self.paths.eq_filter)

        # Perform the calibration
        if self.paths.eq_filter is None or self.paths.calibration is None:
            # Generate the amplitude values to be used in the calibration
            log_amp = np.linspace(
                cast(float, self.settings.calibration.min_amp),
                cast(float, self.settings.calibration.max_amp),
                cast(int, self.settings.calibration.amp_steps),
            )

            # Send amplitudes to be used to the interface
            if self.callback is not None:
                self.callback("Pre-calibration", log_amp)

            # Generate and play the sounds for every amplitude value
            self.sounds = self.sound_sweep(
                log_amp, cast(float, self.settings.calibration.sound_duration)
            )

            db_spl = [sound.db_spl for sound in self.sounds]

            # Calculate the calibration parameters
            self.calibration_parameters = np.polyfit(log_amp, db_spl, 1)

            # Save the calibration parameters
            np.save(
                self.output_path / "calibration_parameters.npy",
                self.calibration_parameters,
            )
        else:
            self.calibration_parameters = np.load(self.paths.calibration)

        # Test the calibration
        if self.settings.test is not None:
            # Generate the dB values to be used in the calibration test
            db_test = np.linspace(
                cast(float, self.settings.test.min_db),
                cast(float, self.settings.test.max_db),
                cast(int, self.settings.test.db_steps),
            )

            # Send the desired dB values
            if self.callback is not None:
                self.callback("Pre-test", db_test)

            # Use the calibration parameters and the dB array to generate the correspondent amplitude values that will be used in the calibration test
            att_test = (
                db_test - self.calibration_parameters[1]
            ) / self.calibration_parameters[0]

            # Test the calibration curve with the test amplitude factors
            self.test_sounds = self.sound_sweep(
                att_test,
                cast(float, self.settings.test.sound_duration),
                type=SweepType.TEST,
            )

    def calculate_eq_filter(self):
        signal = WhiteNoise(
            cast(float, self.settings.eq_filter.sound_duration),
            self.soundcard.fs,
            self.settings.eq_filter.amplitude,
            self.settings.ramp_time,
            filter=True,
            freq_min=self.settings.min_freq,
            freq_max=self.settings.max_freq,
        )

        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            sound_path = self.output_path / "sounds" / "eq_filter_sound.bin"
            create_sound_file(signal, sound_path)
            self.soundcard.load_sound(filename=sound_path)

        # Play the sound from the soundcard and record it with the microphone + DAQ system
        rec_path = self.output_path / "sounds" / "eq_filter_rec.npy"
        recorded_sound = self.record_sound(
            rec_path, cast(float, self.settings.eq_filter.sound_duration)
        )

        resampled_sound = RecordedSound.resample(recorded_sound, self.soundcard.fs)

        freq, fft = resampled_sound.fft_welch(self.settings.eq_filter.time_constant)
        transfer_function = 1 / (fft + 1e-10)

        mean_gain = np.mean(
            transfer_function[
                (freq >= self.settings.min_freq) & (freq <= self.settings.max_freq)
            ]
        )

        transfer_function /= mean_gain

        min_boost_linear = 10 ** (self.settings.eq_filter.min_boost_db / 20)
        max_boost_linear = 10 ** (self.settings.eq_filter.max_boost_db / 20)

        transfer_function[transfer_function < min_boost_linear] = min_boost_linear
        transfer_function[transfer_function > max_boost_linear] = max_boost_linear

        sos = butter(
            32,
            [self.settings.min_freq, self.settings.max_freq],
            btype="bandpass",
            output="sos",
            fs=self.soundcard.fs,
        )

        w, h = freqz_sos(sos, fs=self.soundcard.fs)
        new_h = np.interp(freq, w, np.abs(h))
        response = np.multiply(transfer_function, abs(new_h))
        final_filter = firwin2(4097, freq, response, fs=self.soundcard.fs)

        return final_filter

    def sound_sweep(
        self,
        amp_array: np.ndarray,
        duration: float,
        type: SweepType = SweepType.CALIBRATION,
    ):
        """
        Plays sounds with different amplitudes and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        amp_array : np.ndarray
            The array containing the amplitude levels to be used in the different sounds.
        duration : float
            The duration of the sounds (s).
        type : SweepType, optional
            Indicates whether this function is being run in the calibration or in the test of a calibration

        Returns
        -------
        db_spl : numpy.ndarray
            The array containing the measured dB SPL values for each amplification value.
        sounds : numpy.ndarray
            The array containing both the original and acquired signals for each amplification value.
        """
        # Initialization of the output arrays
        sounds = np.zeros(amp_array.size, dtype=RecordedSound)

        # Generate the noise
        signal = WhiteNoise(
            duration,
            self.soundcard.fs,
            1,  # FIXME
            self.settings.ramp_time,
            self.settings.filter.filter_input,
            cast(float, self.settings.filter.min_freq),
            cast(float, self.settings.filter.max_freq),
            self.eq_filter,
            noise_type="gaussian",  # FIXME
        )

        # Save the generated noise
        match type:
            case SweepType.CALIBRATION:
                filename = self.output_path / "sounds" / "calibration_sound.bin"
                rec_file = "calibration"
                code = "Noise Calibration"
            case SweepType.TEST:
                filename = self.output_path / "sounds" / "test_sound.bin"
                rec_file = "test"
                code = "Noise Test"

        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            create_sound_file(signal, filename)
            self.soundcard.load_sound(filename)

        for i in range(amp_array.size):
            # Play the sound from the soundcard and record it with the microphone + DAQ system
            rec_path = self.output_path / "sounds" / (rec_file + "_" + str(i) + ".npy")
            sounds[i] = self.record_sound(
                rec_path,
                duration,
                10 ** (amp_array[i]),
                self.settings.filter.filter_acquisition,
            )

            # Calculate the intensity in dB SPL
            sounds[i].calculate_db_spl(self.settings.mic_factor)

            # Send information regarding the current noise to the interface
            if self.callback is not None:
                self.callback(code, i, sounds[i])

        return sounds
