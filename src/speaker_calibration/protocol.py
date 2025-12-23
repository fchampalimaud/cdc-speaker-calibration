import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal, Optional, cast

import numpy as np
import yaml
from scipy.interpolate import RBFInterpolator, griddata
from scipy.signal import butter, firwin2, freqz_sos, sosfilt

import speaker_calibration.settings as setts
from speaker_calibration.recording import Moku, NiDaq, RecordingDevice
from speaker_calibration.settings import Settings
from speaker_calibration.sound import PureTone, RecordedSound, Sound, WhiteNoise
from speaker_calibration.soundcards import HarpSoundCard, SoundCard, create_sound_file


class Calibration:
    """
    The calibration class which performs and stores the results from the type of calibration specified in the settings object.

    Attributes
    ----------
    settings : Settings
        the object containing the settings to be used in the calibration protocol
    soundcard : SoundCard
        the object that allows the calibration code to interface with the soundcard used in the calibration
    adc : RecordingDevice
        the object the allows the calibration code to interface with the ADC used in the calibration
    path : Path
        the path to the output file of the current calibration
    callback : Optional[Callable]
        a callback function that allows the calibration code to periodically send data to the user interface with some data based on a keyword
    """

    settings: Settings
    soundcard: SoundCard
    adc: RecordingDevice
    path: Path
    callback: Optional[Callable]

    def __init__(self, settings: Settings, callback: Optional[Callable] = None):
        self.settings = settings
        self.callback = callback

        # Define the path for the output directory for the current calibration
        self.path = (
            Path()
            / self.settings.paths.output
            / datetime.now().strftime("%y%m%d_%H%M%S")
        )
        # Create the output directory structure for the current calibration
        os.makedirs(self.path / "sounds")

        save_settings = self.settings.model_dump(by_alias=True, exclude_unset=True)

        with open(self.path / "config.yml", "w") as file:
            yaml.dump(save_settings, file, default_flow_style=False)

        # Initiate the soundcard to be used in the calibration
        if isinstance(self.settings.soundcard, setts.HarpSoundCard):
            self.soundcard = HarpSoundCard(
                self.settings.soundcard.serial_port, self.settings.soundcard.fs
            )
            # Turn off the speaker that's not going to be calibrated
            if self.settings.soundcard.speaker == "Left":
                self.soundcard.device.write_attenuation_left(0)
                self.soundcard.device.write_attenuation_right(65535)
            else:
                self.soundcard.device.write_attenuation_left(65535)
                self.soundcard.device.write_attenuation_right(0)
        else:
            # TODO: implement interface with computer soundcard
            self.soundcard = None

        # Initiate the ADC to be used in the calibration
        if isinstance(self.settings.adc, setts.NiDaq):
            self.adc = NiDaq(self.settings.adc.device_id, self.settings.adc.fs)
        else:
            self.adc = Moku(self.settings.adc.address, self.settings.adc.fs)

        # Perform the calibration according to the sound type (Noise or Pure Tone)
        if isinstance(self.settings.protocol, setts.NoiseProtocol):
            self.noise_calibration()
        else:
            self.pure_tone_calibration()

    def noise_calibration(self):
        """
        Performs the white noise speaker calibration.
        """
        # Calculate the EQ filter
        if self.settings.paths.eq_filter is None:
            # self.eq_filter, eq_signal, eq_recorded = self.calculate_eq_filter()
            self.eq_filter, eq_signal, eq_recorded = self.calculate_eq_filter()

            # Save EQ filter
            np.save(self.path / "eq_filter.npy", self.eq_filter)

            # Send EQ filter and signals to the interface
            if self.callback is not None:
                self.callback("EQ Filter", self.eq_filter)
        else:
            self.eq_filter = np.load(self.settings.paths.eq_filter)

        # Perform the calibration
        if (
            self.settings.paths.eq_filter is None
            or self.settings.paths.calibration is None
        ):
            # Generate the amplitude values to be used in the calibration
            log_amp = np.linspace(
                cast(float, self.settings.protocol.calibration.min_amp),
                cast(float, self.settings.protocol.calibration.max_amp),
                cast(int, self.settings.protocol.calibration.amp_steps),
            )

            # Send amplitudes to be used to the interface
            if self.callback is not None:
                self.callback("Pre-calibration", log_amp)

            # Generate and play the sounds for every amplitude value
            self.sounds = self.noise_sweep(
                log_amp, cast(float, self.settings.protocol.calibration.sound_duration)
            )

            db_spl = [sound.db_spl for sound in self.sounds]

            # Calculate the calibration parameters
            self.calibration_parameters = np.polyfit(log_amp, db_spl, 1)

            # Save the calibration parameters
            np.save(
                self.path / "calibration_parameters.npy", self.calibration_parameters
            )
        else:
            self.calibration_parameters = np.load(self.settings.paths.calibration)

        # Test the calibration
        if self.settings.protocol.test_calibration is not None:
            # Generate the dB values to be used in the calibration test
            db_test = np.linspace(
                cast(float, self.settings.protocol.test_calibration.min_db),
                cast(float, self.settings.protocol.test_calibration.max_db),
                cast(int, self.settings.protocol.test_calibration.db_steps),
            )

            # Send the desired dB values
            if self.callback is not None:
                self.callback("Pre-test", db_test)

            # Use the calibration parameters and the dB array to generate the correspondent amplitude values that will be used in the calibration test
            att_test = (
                db_test - self.calibration_parameters[1]
            ) / self.calibration_parameters[0]

            # Test the calibration curve with the test amplitude factors
            self.test_sounds = self.noise_sweep(
                att_test,
                cast(float, self.settings.protocol.test_calibration.sound_duration),
                type="Test",
            )

    def pure_tone_calibration(self):
        """
        Performs the pure tone speaker calibration.
        """
        # Perform the calibration
        if self.settings.paths.calibration is None:
            # Generate the array of frequencies to be used in the calibration
            freq = np.linspace(
                self.settings.protocol.calibration.min_freq,
                self.settings.protocol.calibration.max_freq,
                self.settings.protocol.calibration.num_freqs,
            )

            # Generate the array of amplitudes to be used in the calibration
            amp = np.linspace(
                0, 1, self.settings.protocol.calibration.amp_steps
            )  # TODO: check whether it's better to use log spaced amp_array

            # Generate the input calibration array
            freq, amp = np.meshgrid(freq, amp, indexing="ij")
            db = np.zeros(freq.shape)
            calib_array = np.stack((freq, amp, db), axis=2)

            # Send the calibration frequency and amplitude information to the interface
            if self.callback is not None:
                self.callback("Pre-calibration", calib_array[:, :, 0:2])

            # Generate and play the sounds for every frequency and amplitude values
            calib_array, _ = self.pure_tone_sweep(
                calib_array,
                self.settings.protocol.calibration.sound_duration,
                "Calibration",
            )

            # Convert calibration array to 2D array and save it as a CSV file
            calib = calib_array.reshape(calib_array.shape[0] * calib_array.shape[1], 3)
            np.save(
                self.path / "calibration.npy",
                calib,
                delimiter=",",
                fmt="%f",
            )

            amp = amp.reshape(-1)
        else:
            calib = np.load(self.settings.paths.calibration)
            amp = calib[:, 1]

        # Test the calibration
        if self.settings.protocol.test_calibration is not None:
            # Generate the array of frequencies to be used in the calibration test
            test_freq = np.linspace(
                self.settings.test_calibration.freq.min_freq,
                self.settings.test_calibration.freq.max_freq,
                self.settings.test_calibration.freq.num_freqs,
            )

            # Generate the array of dB values to be used in the calibration test
            test_db = np.linspace(
                self.settings.test_calibration.db_min,
                self.settings.test_calibration.db_max,
                self.settings.test_calibration.db_steps,
            )

            test_freq, test_db = np.meshgrid(test_freq, test_db, indexing="ij")

            # Generate the x arrays for the calibration and test to be used in the interpolation
            x_calib = np.stack((freq, db), axis=2).reshape(
                freq.shape[0] * freq.shape[1], 2
            )
            x_test = np.stack((test_freq, test_db), axis=2).reshape(
                test_freq.shape[0] * test_freq.shape[1], 2
            )

            # Perform the interpolation
            # TODO: check whether it's best to use RBFInterpolator
            y = griddata(x_calib, amp, x_test, method="linear")

            # Send the test frequency and dB information to the interface
            if self.callback is not None:
                self.callback("Pre-test", x_test)

            # Generate the test array with the frequencies and amplitudes to be used
            test_array = np.stack(
                (test_freq, y.reshape(freq.shape[0], freq.shape[1]), test_db), axis=2
            )

            # Generate and play the sounds for every frequency and amplitude values
            test_array2, _ = self.pure_tone_sweep(
                test_array, self.settings.test_calibration.sound_duration, "Test"
            )

            # Create the final array with the results from the calibration test
            test = np.stack(
                (
                    test_array[:, :, 0],
                    test_array[:, :, 1],
                    test_array[:, :, 2],
                    test_array2[:, :, 2],
                ),
                axis=2,
            )

            # Save the calibration test results
            np.save(
                self.path / "test_calibration.npy",
                test,
                delimiter=",",
                fmt="%f",
            )

    def calculate_eq_filter(self):
        signal = WhiteNoise(
            cast(float, self.settings.protocol.eq_filter.sound_duration),
            self.settings.soundcard.fs,
            self.settings.protocol.eq_filter.amplitude,
            self.settings.protocol.ramp_time,
            filter=True,
            freq_min=self.settings.protocol.min_freq,
            freq_max=self.settings.protocol.max_freq,
        )

        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            sound_path = self.path / "sounds" / "eq_filter_sound.bin"
            create_sound_file(signal, sound_path)
            self.soundcard.load_sound(filename=sound_path)

        # Play the sound from the soundcard and record it with the microphone + DAQ system
        rec_path = self.path / "sounds" / "eq_filter_rec.npy"
        recorded_sound = self.record_sound(
            rec_path, cast(float, self.settings.protocol.eq_filter.sound_duration)
        )

        resampled_sound = RecordedSound.resample(
            recorded_sound, self.settings.soundcard.fs
        )

        freq, fft = resampled_sound.fft_welch(
            self.settings.protocol.eq_filter.time_constant
        )
        transfer_function = 1 / (fft + 1e-10)

        mean_gain = np.mean(
            transfer_function[
                (freq >= self.settings.protocol.min_freq)
                & (freq <= self.settings.protocol.max_freq)
            ]
        )

        transfer_function /= mean_gain

        min_boost_linear = 10 ** (self.settings.protocol.eq_filter.min_boost_db / 20)
        max_boost_linear = 10 ** (self.settings.protocol.eq_filter.max_boost_db / 20)

        transfer_function[transfer_function < min_boost_linear] = min_boost_linear
        transfer_function[transfer_function > max_boost_linear] = max_boost_linear

        sos = butter(
            32,
            [self.settings.protocol.min_freq, self.settings.protocol.max_freq],
            btype="bandpass",
            output="sos",
            fs=self.settings.soundcard.fs,
        )

        w, h = freqz_sos(sos, fs=self.settings.soundcard.fs)
        new_h = np.interp(freq, w, np.abs(h))
        response = np.multiply(transfer_function, abs(new_h))
        final_filter = firwin2(4097, freq, response, fs=self.settings.soundcard.fs)

        return final_filter, signal, resampled_sound

    def noise_sweep(
        self,
        amp_array: np.ndarray,
        duration: float,
        type: Literal["Calibration", "Test"] = "Calibration",
    ):
        """
        Plays sounds with different amplitudes and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        amp_array : np.ndarray
            The array containing the amplitude levels to be used in the different sounds.
        duration : float
            The duration of the sounds (s).
        type : Literal["Calibration", "Test"], optional
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
            self.settings.soundcard.fs,
            1,  # FIXME
            self.settings.protocol.ramp_time,
            self.settings.filter.filter_input,
            cast(float, self.settings.filter.min_freq),
            cast(float, self.settings.filter.max_freq),
            self.eq_filter,
            noise_type="gaussian",  # FIXME
        )

        # Save the generated noise
        if type == "Calibration":
            filename = self.path / "sounds" / "calibration_sound.bin"
            rec_file = "calibration"
        else:
            filename = self.path / "sounds" / "test_sound.bin"
            rec_file = "test"

        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            create_sound_file(signal, filename)
            self.soundcard.load_sound(filename)

        for i in range(amp_array.size):
            # TODO: non-Harp case not implemented
            if isinstance(self.soundcard, HarpSoundCard):
                if self.settings.soundcard.speaker == "Left":
                    self.soundcard.device.write_attenuation_left(
                        int(-amp_array[i] * 200)
                    )  # x20 because of the 20*log10(x) and x10 due the way this register works (1 LSB = 0.1 dB)
                else:
                    self.soundcard.device.write_attenuation_right(
                        int(-amp_array[i] * 200)
                    )  # x20 because of the 20*log10(x) and x10 due the way this register works (1 LSB = 0.1 dB

            # Play the sound from the soundcard and record it with the microphone + DAQ system
            rec_path = self.path / "sounds" / (rec_file + "_" + str(i) + ".npy")
            sounds[i] = self.record_sound(
                rec_path, duration, self.settings.filter.filter_acquisition
            )

            # Calculate the intensity in dB SPL
            sounds[i].calculate_db_spl(self.settings.protocol.mic_factor)

            # Send information regarding the current noise to the interface
            if self.callback is not None:
                self.callback(type, i, sounds[i])

        return sounds

    def pure_tone_sweep(
        self,
        calib_array: np.ndarray,
        duration: float,
        type: Literal["Calibration", "Test"] = "Calibration",
    ):
        """
        Plays sounds with different amplitudes and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        calib_array : np.ndarray
            The array containing the frequency and amplitude values to be used in the different sounds.
        duration : float
            The duration of the sounds (s).
        type : Literal["Calibration", "Test"], optional
            Indicates whether this function is being run in the calibration or in the test of a calibration

        Returns
        -------
        calib_array : numpy.ndarray
            The array containing the measured dB SPL values for each frequency and amplification values.
        sounds : numpy.ndarray
            The array containing both the original and acquired signals for each frequency and amplification values.
        """
        # Initialization of the output arrays
        sounds = np.zeros((calib_array.shape[0], calib_array.shape[1]), dtype=Sound)

        for i in range(calib_array.shape[0]):
            # Generate the pure tone
            signal = PureTone(
                duration,
                self.settings.soundcard.fs,
                calib_array[i, 0, 0],
                amplitude=calib_array[i, -1, 1],
                ramp_time=self.settings.protocol.ramp_time,
            )

            # Save the generated pure tone
            if type == "Calibration":
                filename = (
                    self.path
                    / "sounds"
                    / (
                        "calibration_sound_"
                        + str(round(calib_array[i, 0, 0]))
                        + "hz.bin"
                    )
                )
            else:
                filename = (
                    self.path
                    / "sounds"
                    / ("test_sound_" + str(round(calib_array[i, 0, 0])) + "hz.bin")
                )

            # Upload the sound to the Harp SoundCard in case one is used
            if isinstance(self.soundcard, HarpSoundCard):
                create_sound_file(signal, filename)
                self.soundcard.load_sound(filename)

            for j in range(calib_array.shape[1]):
                # If amplitude value is NaN skip this sound
                if np.isnan(calib_array[i, j, 1]):
                    calib_array[i, j, 2] = np.nan
                    continue

                # TODO: non-Harp case not implemented
                if isinstance(self.soundcard, HarpSoundCard):
                    if self.settings.soundcard.speaker == "Left":
                        self.soundcard.device.write_attenuation_left(
                            int(-200 * np.log10(calib_array[i, j, 1]))
                        )  # x20 because of the 20*log10(x) and x10 due the way this register works (1 LSB = 0.1 dB)
                    else:
                        self.soundcard.device.write_attenuation_right(
                            int(-200 * np.log10(calib_array[i, j, 1]))
                        )  # x20 because of the 20*log10(x) and x10 due the way this register works (1 LSB = 0.1 dB

                # Play the sound from the soundcard and record it with the microphone + DAQ system
                if type == "Calibration":
                    rec_file = (
                        "calibration_rec_"
                        + str(round(calib_array[i, j, 0]))
                        + "hz_"
                        + str(j)
                        + ".npy"
                    )
                else:
                    rec_file = (
                        "test_rec_"
                        + str(round(calib_array[i, j, 0]))
                        + "hz_"
                        + str(j)
                        + ".npy"
                    )

                sounds[i, j] = self.record_sound(
                    self.path / "sounds" / rec_file,
                    duration,
                    self.settings.filter.filter_acquisition,
                )

                # Calculate the intensity in dB SPL
                calib_array[i, j, 2] = sounds[i, j].calculate_db_spl(
                    self.settings.mic_factor
                )

                # Send information regarding the current pure tone to the interface
                if self.callback is not None:
                    self.callback(type, i, j, signal, sounds[i, j])

        return calib_array, sounds

    def record_sound(
        self,
        filename: Path,
        duration: float,
        filter: bool = False,
    ) -> RecordedSound:
        """
        Records the sounds.

        Parameters
        ----------
        filename : Path
            The path to the file to which the sound will be saved to and from which the sound is upload from (in case a Harp SoundCard is used).
        duration : float
            The duration of the sound (s).
        filter : bool, optional
            Indicates whether the acquired signal should be filtered or not.

        Returns
        -------
        sound : Sound
            The recorded sound.
        """
        # Create the result list to pass to the recording thread
        result = []

        # Create the start event and the threads that will play and record the sound
        start_event = threading.Event()
        play_thread = threading.Thread(
            target=self.soundcard.play, kwargs={"start_event": start_event}
        )
        record_thread = threading.Thread(
            target=self.adc.record_signal,
            args=[duration],
            kwargs={
                "start_event": start_event,
                "result": result,
                "filename": filename,
            },
        )

        # Start both threads
        record_thread.start()
        play_thread.start()

        # Activates the event in order to synchronize the sound being played with the acquisition
        time.sleep(0.1)
        start_event.set()
        record_thread.join()

        # Filter the acquired signal if desired
        if filter:
            sos = butter(
                32,
                [self.settings.filter.min_freq, self.settings.filter.max_freq],
                btype="bandpass",
                output="sos",
                fs=self.adc.fs,
            )
            result[0].signal = sosfilt(sos, result[0].signal)

        return result[0]


def main():
    with open("config/settings.yml", "r") as file:
        data = yaml.safe_load(file)

    settings = Settings(**data)
    Calibration(settings)
