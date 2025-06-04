import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
from scipy.interpolate import RBFInterpolator, griddata
from scipy.signal import butter, sosfilt, welch

from speaker_calibration.recording import Moku, NiDaq, RecordingDevice
from speaker_calibration.settings import Settings
from speaker_calibration.sound import (
    Sound,
    calculate_db_spl,
    create_sound_file,
    pure_tone,
    white_noise,
)
from speaker_calibration.soundcards import HarpSoundCard, SoundCard


class Calibration:
    soundcard: SoundCard
    adc: RecordingDevice

    def __init__(self, settings: Settings, callback: callable = None):
        self.settings = settings
        self.callback = callback

        self.path = (
            Path() / self.settings.output_dir / datetime.now().strftime("%y%m%d_%H%M%S")
        )
        os.makedirs(self.path / "sounds")

        if self.settings.is_harp:
            self.soundcard = HarpSoundCard(self.settings.soundcard.com_port, 192000)
        else:
            self.soundcard = None

        if self.settings.adc_device == "NI-DAQ":
            self.adc = NiDaq(self.settings.adc.device_id, self.settings.adc.fs)
        else:
            self.adc = Moku(self.settings.adc.address, self.settings.adc.fs)

        if self.settings.sound_type == "Noise":
            self.noise_calibration()
        else:
            self.pure_tone_calibration()

    def noise_calibration(self):
        """
        Performs the white noise speaker calibration.
        """
        # Calculate the inverse filter
        if self.settings.inverse_filter.determine_filter:
            self.inverse_filter, psd_signal, psd_recorded = (
                self.calculate_inverse_filter()
            )
            np.savetxt(
                self.path / "inverse_filter.csv",
                self.inverse_filter,
                delimiter=",",
                fmt="%f",
            )

            if self.callback is not None:
                self.callback(
                    "Inverse Filter", self.inverse_filter, psd_signal, psd_recorded
                )

        # Perform the calibration
        if self.settings.calibration.calibrate:
            # Generate the attenuation values to be used in the calibration
            log_att = np.linspace(
                self.settings.calibration.att_min,
                self.settings.calibration.att_max,
                self.settings.calibration.att_steps,
            )
            att_factor = 10**log_att

            if self.callback is not None:
                self.callback("Pre-calibration", log_att)

            # Generate and play the sounds for every attenuation value
            self.db_spl, self.signals = self.sweep_db(
                att_factor, self.settings.calibration.sound_duration
            )

            # Calculate the calibration parameters
            self.calibration_parameters = np.polyfit(log_att, self.db_spl, 1)
            np.savetxt(
                self.path / "calibration_parameters.csv",
                self.calibration_parameters,
                delimiter=",",
                fmt="%f",
            )

        # Test the calibration
        if self.settings.test_calibration.test:
            # Generate the dB values to be used in the calibration test
            att_test = np.linspace(
                self.settings.test_calibration.db_min,
                self.settings.test_calibration.db_max,
                self.settings.test_calibration.db_steps,
            )

            if self.callback is not None:
                self.callback("Pre-test", att_test)

            # Use the calibration parameters and the dB array to generate the correspondent attenuation values that will be used in the calibration test
            att_test = (
                att_test - self.calibration_parameters[1]
            ) / self.calibration_parameters[0]
            att_test = 10**att_test

            # Test the calibration curve with the test attenuation factors
            self.db_spl_test, self.signals_test = self.sweep_db(
                att_test, self.settings.test_calibration.sound_duration, type="Test"
            )

    def pure_tone_calibration(self):
        # Perform the calibration
        if self.settings.calibration.calibrate:
            freq = np.linspace(
                self.settings.freq.min_freq,
                self.settings.freq.max_freq,
                self.settings.freq.num_freqs,
            )
            amp = np.linspace(
                0, 1, self.settings.calibration.att_steps
            )  # TODO: check whether it's better to use log spaced att_array
            freq, amp = np.meshgrid(freq, amp, indexing="ij")
            db = np.zeros(freq.shape)
            calib_array = np.stack((freq, amp, db), axis=2)

            calib_array, _ = self.sweep_2d_space(
                calib_array, self.settings.calibration.sound_duration, "Calibration"
            )

            calib = calib_array.reshape(calib_array.shape[0] * calib_array.shape[1], 3)

            np.savetxt(
                self.path / "calibration.csv",
                calib,
                delimiter=",",
                fmt="%f",
            )

        # Test the calibration
        if self.settings.test_calibration.test:
            # flattened_array = calib_array.reshape(
            #     calib_array.shape[0] * calib_array.shape[1], 3
            # )
            # interp = RBFInterpolator(flattened_array[:, 0:2], flattened_array[:, 2])

            test_freq = np.linspace(
                self.settings.freq.min_freq,
                self.settings.freq.max_freq,
                self.settings.freq.num_freqs,
            )  # TODO: add way to choose a different freq array for testing
            test_db = np.linspace(
                self.settings.test_calibration.db_min,
                self.settings.test_calibration.db_max,
                self.settings.test_calibration.db_steps,
            )

            x_calib = np.stack((freq, db), axis=2).reshape(
                freq.shape[0] * freq.shape[1], 2
            )
            x_test = np.stack((test_freq, test_db), axis=2).reshape(
                test_freq.shape[0] * test_freq.shape[1], 2
            )

            y = griddata(x_calib, amp.reshape(-1), x_test, method="linear")

            test_array = np.stack(
                (test_freq, y.reshape(freq.shape[0], freq.shape[1]), test_db), axis=2
            )

            test_array2, _ = self.sweep_2d_space(
                test_array, self.settings.test_calibration.sound_duration, "Test"
            )

            # if self.callback is not None:
            #     self.callback("Pre-calibration", log_att)

            test = np.stack(
                (
                    test_array[:, :, 0],
                    test_array[:, :, 1],
                    test_array[:, :, 2],
                    test_array2[:, :, 2],
                ),
                axis=2,
            )

            np.savetxt(
                self.path / "test_calibration.csv",
                test,
                delimiter=",",
                fmt="%f",
            )

    def calculate_inverse_filter(self):
        """
        Calculates the inverse filter used in the noise calibration protocol.
        """
        # Generate the white noise
        signal = white_noise(
            self.settings.inverse_filter.sound_duration,
            self.settings.soundcard.fs,
            self.settings.amplitude,
            self.settings.ramp_time,
            self.settings.filter.filter_input,
            self.settings.filter.min_value,
            self.settings.filter.max_value,
            noise_type="gaussian",  # FIXME
        )

        # Play the sound from the soundcard and record it with the microphone + DAQ system
        recorded_sound = self.record_sound(
            signal,
            str(self.path / "sounds" / "inverse_filter_sound.bin"),
            self.settings.inverse_filter.sound_duration,
        )

        # Calculate the inverse filter from the acquired signal
        freq, psd = welch(
            recorded_sound.signal[
                int(0.1 * recorded_sound.signal.size) : int(
                    0.9 * recorded_sound.signal.size
                )
            ],
            fs=self.settings.adc.fs,
            nperseg=self.settings.inverse_filter.time_constant * self.settings.adc.fs,
        )
        inverse_filter = 1 / np.sqrt(psd)
        inverse_filter = np.stack((freq, inverse_filter), axis=1)

        return inverse_filter, signal, recorded_sound

    def sweep_db(
        self,
        att_array: np.ndarray,
        duration: float,
        type: Literal["Calibration", "Test"] = "Calibration",
    ):
        """
        Plays sounds with different attenuations and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        att_array : np.ndarray
            the array containing the attenuation levels to be used in the different sounds.
        duration : float
            the duration of the sounds (s).
        """
        # Initialization of the output arrays
        sounds = np.zeros(att_array.size, dtype=Sound)
        db_spl = np.zeros(att_array.size)

        for i in range(att_array.size):
            # Generate the noise
            signal = white_noise(
                duration,
                self.settings.soundcard.fs,
                self.settings.amplitude * att_array[i],
                self.settings.ramp_time,
                self.settings.filter.filter_input,
                self.settings.filter.min_value,
                self.settings.filter.max_value,
                self.inverse_filter,
                noise_type="gaussian",  # FIXME
            )

            if type == "Calibration":
                filename = "calibration_sound_" + str(i) + ".bin"
            else:
                filename = "test_sound_" + str(i) + ".bin"

            # Play the sound from the soundcard and record it with the microphone + DAQ system
            sounds[i] = self.record_sound(
                signal,
                str(self.path / "sounds" / filename),
                duration,
                self.settings.filter.filter_acquisition,
            )

            # Calculate the intensity in dB SPL
            db_spl[i] = calculate_db_spl(sounds[i], self.settings.mic_factor)

            if self.callback is not None:
                self.callback(type, i, signal, sounds[i], db_spl[i])

        return db_spl, sounds

    def sweep_2d_space(
        self,
        calib_array: np.ndarray,
        duration: float,
        type: Literal["Calibration", "Test"] = "Calibration",
    ):
        """
        Plays sounds with different attenuations and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        att_array : np.ndarray
            the array containing the attenuation levels to be used in the different sounds.
        duration : float
            the duration of the sounds (s).
        """
        # Initialization of the output arrays
        sounds = np.zeros((calib_array.shape[0], calib_array.shape[1]), dtype=Sound)

        for i in range(calib_array.shape[0]):
            for j in range(calib_array.shape[1]):
                # Check if amplitude value is NaN
                if np.isnan(calib_array[i, j, 1]):
                    calib_array[i, j, 2] = np.nan
                    continue

                # Generate the noise
                signal = pure_tone(
                    duration,
                    self.settings.soundcard.fs,
                    calib_array[i, j, 0],
                    amplitude=calib_array[i, j, 1],
                    ramp_time=self.settings.ramp_time,
                )

                if type == "Calibration":
                    filename = "calibration_sound_" + str(i) + ".bin"
                else:
                    filename = "test_sound_" + str(i) + ".bin"

                # Play the sound from the soundcard and record it with the microphone + DAQ system
                sounds[i, j] = self.record_sound(
                    signal,
                    str(self.path / "sounds" / filename),
                    duration,
                    self.settings.filter.filter_acquisition,
                )

                # Calculate the intensity in dB SPL
                calib_array[i, j, 2] = calculate_db_spl(
                    sounds[i, j], self.settings.mic_factor
                )

                if self.callback is not None:
                    self.callback(type, i, signal, sounds[i, j], calib_array[i, j, 2])

        return calib_array, sounds

    def record_sound(
        self, signal: Sound, filename: str, duration: float, filter: bool = False
    ):
        """
        Records the sounds.

        Parameters
        ----------
        signal : Sound
            the signal to be played and recorded.
        filename : str
            the path to the file to which the sound will be saved to and from which the sound is upload from (in case a Harp SoundCard is used).
        duration : float
            the duration of the sound (s).
        filter : bool, optional
            indicates whether the acquired signal should be filtered or not.
        """
        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            create_sound_file(signal, filename)
            self.soundcard.load_sound(filename=filename)

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
                "filename": filename[:-4] + "_rec",
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
                3,
                [
                    self.settings.filter.min_value,
                    self.settings.filter.max_value,
                ],
                btype="bandpass",
                output="sos",
                fs=self.adc.fs,
            )
            result[0].signal = sosfilt(sos, result[0].signal)

        return result[0]
