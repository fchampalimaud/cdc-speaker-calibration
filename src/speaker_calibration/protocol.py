import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal, Optional, cast

import numpy as np
import yaml
from scipy.interpolate import RBFInterpolator, griddata
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, firwin2, freqz_sos, sosfilt

import speaker_calibration.settings as setts
from speaker_calibration.recording import Moku, NiDaq, RecordingDevice
from speaker_calibration.settings import Settings
from speaker_calibration.sound import Chirp, PureTone, RecordedSound, Sound, WhiteNoise
from speaker_calibration.soundcards import HarpSoundCard, SoundCard, create_sound_file
from speaker_calibration.utils import nextpow2


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
            Path() / self.settings.output_dir / datetime.now().strftime("%y%m%d_%H%M%S")
        )
        # Create the output directory structure for the current calibration
        os.makedirs(self.path / "sounds")

        # Initiate the soundcard to be used in the calibration
        # if self.settings.is_harp:
        if isinstance(self.settings.soundcard, setts.HarpSoundCard):
            self.soundcard = HarpSoundCard(
                self.settings.soundcard.com_port, self.settings.soundcard.fs
            )
        else:
            # TODO: implement interface with computer soundcard
            self.soundcard = None

        # Initiate the ADC to be used in the calibration
        if self.settings.adc_device == "NI-DAQ":
            self.adc = NiDaq(self.settings.adc.device_id, self.settings.adc.fs)
        else:
            self.adc = Moku(self.settings.adc.address, self.settings.adc.fs)

        # Perform the calibration according to the sound type (Noise or Pure Tone)
        if self.settings.sound_type == "Noise":
            self.noise_calibration()
        # else:
        #     self.pure_tone_calibration()

    # FIXME: the function doesn't currently allow to perform only some of the calibration steps isolated (e.g. calibration test), because there's no way to load a previously performed calibration
    def noise_calibration(self):
        """
        Performs the white noise speaker calibration.
        """
        # Calculate the EQ filter
        if self.settings.eq_filter.determine_filter:
            # self.eq_filter, eq_signal, eq_recorded = self.calculate_eq_filter()
            self.eq_filter, eq_signal, eq_recorded = self.noise_eq_filter()

            # Save EQ filter
            np.save(self.path / "eq_filter.npy", self.eq_filter)

            # FIXME
            # # Send EQ filter and signals to the interface
            # if self.callback is not None:
            #     self.callback(
            #         "EQ Filter", self.eq_filter, eq_signal, eq_recorded
            #     )

        # Perform the calibration
        if self.settings.calibration.calibrate:
            # Generate the amplitude values to be used in the calibration
            log_amp = np.linspace(
                cast(float, self.settings.calibration.amp_min),
                cast(float, self.settings.calibration.amp_max),
                cast(int, self.settings.calibration.amp_steps),
            )
            amp_factor = 10**log_amp

            # Send amplitudes to be used to the interface
            if self.callback is not None:
                self.callback("Pre-calibration", log_amp)

            # Generate and play the sounds for every amplitude value
            self.sounds = self.noise_sweep(
                amp_factor, cast(float, self.settings.calibration.sound_duration)
            )

            db_spl = [sound.db_spl for sound in self.sounds]

            # Calculate the calibration parameters
            self.calibration_parameters = np.polyfit(log_amp, db_spl, 1)

            # Save the calibration parameters
            np.save(
                self.path / "calibration_parameters.npy", self.calibration_parameters
            )

        # Test the calibration
        if self.settings.test_calibration.test:
            # Generate the dB values to be used in the calibration test
            db_test = np.linspace(
                cast(float, self.settings.test_calibration.db_min),
                cast(float, self.settings.test_calibration.db_max),
                cast(int, self.settings.test_calibration.db_steps),
            )

            # Send the desired dB values
            if self.callback is not None:
                self.callback("Pre-test", db_test)

            # Use the calibration parameters and the dB array to generate the correspondent amplitude values that will be used in the calibration test
            db_test = (
                db_test - self.calibration_parameters[1]
            ) / self.calibration_parameters[0]
            db_test = 10**db_test

            # Test the calibration curve with the test amplitude factors
            self.test_sounds = self.noise_sweep(
                db_test,
                cast(float, self.settings.test_calibration.sound_duration),
                type="Test",
            )

    # # FIXME: the function doesn't currently allow to perform only some of the calibration steps isolated (e.g. calibration test), because there's no way to load a previously performed calibration
    # def pure_tone_calibration(self):
    #     """
    #     Performs the pure tone speaker calibration.
    #     """
    #     # Perform the calibration
    #     if self.settings.calibration.calibrate:
    #         # Generate the array of frequencies to be used in the calibration
    #         freq = np.linspace(
    #             self.settings.calibration.freq.min_freq,
    #             self.settings.calibration.freq.max_freq,
    #             self.settings.calibration.freq.num_freqs,
    #         )

    #         # Generate the array of amplitudes to be used in the calibration
    #         amp = np.linspace(
    #             0, 1, self.settings.calibration.amp_steps
    #         )  # TODO: check whether it's better to use log spaced amp_array

    #         # Generate the input calibration array
    #         freq, amp = np.meshgrid(freq, amp, indexing="ij")
    #         db = np.zeros(freq.shape)
    #         calib_array = np.stack((freq, amp, db), axis=2)

    #         # Send the calibration frequency and amplitude information to the interface
    #         if self.callback is not None:
    #             self.callback("Pre-calibration", calib_array[:, :, 0:2])

    #         # Generate and play the sounds for every frequency and amplitude values
    #         calib_array, _ = self.pure_tone_sweep(
    #             calib_array, self.settings.calibration.sound_duration, "Calibration"
    #         )

    #         # Convert calibration array to 2D array and save it as a CSV file
    #         calib = calib_array.reshape(calib_array.shape[0] * calib_array.shape[1], 3)
    #         np.savetxt(
    #             self.path / "calibration.csv",
    #             calib,
    #             delimiter=",",
    #             fmt="%f",
    #         )

    #     # Test the calibration
    #     if self.settings.test_calibration.test:
    #         # Generate the array of frequencies to be used in the calibration test
    #         test_freq = np.linspace(
    #             self.settings.test_calibration.freq.min_freq,
    #             self.settings.test_calibration.freq.max_freq,
    #             self.settings.test_calibration.freq.num_freqs,
    #         )

    #         # Generate the array of dB values to be used in the calibration test
    #         test_db = np.linspace(
    #             self.settings.test_calibration.db_min,
    #             self.settings.test_calibration.db_max,
    #             self.settings.test_calibration.db_steps,
    #         )

    #         test_freq, test_db = np.meshgrid(test_freq, test_db, indexing="ij")

    #         # Generate the x arrays for the calibration and test to be used in the interpolation
    #         x_calib = np.stack((freq, db), axis=2).reshape(
    #             freq.shape[0] * freq.shape[1], 2
    #         )
    #         x_test = np.stack((test_freq, test_db), axis=2).reshape(
    #             test_freq.shape[0] * test_freq.shape[1], 2
    #         )

    #         # Perform the interpolation
    #         y = griddata(
    #             x_calib, amp.reshape(-1), x_test, method="linear"
    #         )  # TODO: check whether it's best to use RBFInterpolator

    #         # Send the test frequency and dB information to the interface
    #         if self.callback is not None:
    #             self.callback("Pre-test", x_test)

    #         # Generate the test array with the frequencies and amplitudes to be used
    #         test_array = np.stack(
    #             (test_freq, y.reshape(freq.shape[0], freq.shape[1]), test_db), axis=2
    #         )

    #         # Generate and play the sounds for every frequency and amplitude values
    #         test_array2, _ = self.pure_tone_sweep(
    #             test_array, self.settings.test_calibration.sound_duration, "Test"
    #         )

    #         # Create the final array with the results from the calibration test
    #         test = np.stack(
    #             (
    #                 test_array[:, :, 0],
    #                 test_array[:, :, 1],
    #                 test_array[:, :, 2],
    #                 test_array2[:, :, 2],
    #             ),
    #             axis=2,
    #         )

    #         # Save the calibration test results
    #         np.savetxt(
    #             self.path / "test_calibration.csv",
    #             test,
    #             delimiter=",",
    #             fmt="%f",
    #         )

    def calculate_eq_filter(
        self,
        smooth_window: int = 20,
        freq_min: float = 5000,
        freq_max: float = 20000,
        min_boost_db: float = -24,
        max_boost_db: float = 12,
    ):
        signal = Chirp(
            cast(float, self.settings.eq_filter.sound_duration),
            self.settings.soundcard.fs,
            cast(float, self.settings.eq_filter.freq_start),
            cast(float, self.settings.eq_filter.freq_end),
            amplitude=self.settings.amplitude,
            ramp_time=self.settings.ramp_time,
        )

        # Play the sound from the soundcard and record it with the microphone + DAQ system
        recorded_sound = self.record_sound(
            signal,
            self.path / "sounds" / "eq_filter_sound.bin",
            cast(float, self.settings.eq_filter.sound_duration),
            # use_mic_response=True,
        )

        resampled_sound = RecordedSound.resample(
            recorded_sound, self.settings.soundcard.fs
        )

        # Filter the acquired signal if desired
        # TODO: add possibility to filter or to not filter
        sos = butter(
            32,
            500,
            btype="highpass",
            output="sos",
            fs=self.settings.soundcard.fs,
        )
        resampled_sound.signal = cast(np.ndarray, sosfilt(sos, resampled_sound.signal))

        num_fft = resampled_sound.signal.size + signal.inverse_filter.size - 1
        num_fft_samples = int(2 ** nextpow2(num_fft))
        signal_fft = np.fft.fft(resampled_sound.signal, num_fft_samples)
        inv_fft = np.fft.fft(signal.inverse_filter, num_fft_samples)
        ir_fft = np.multiply(signal_fft, inv_fft)
        impulse_response = np.fft.ifft(ir_fft)[0:num_fft]

        peak_pos = max(0, int(np.argmax(np.abs(impulse_response)) - 150))
        hr_ir = impulse_response[peak_pos : peak_pos + 8192]
        new_num_fft = int(2 ** nextpow2(hr_ir.size))
        transfer_function = np.abs(np.fft.fft(hr_ir, new_num_fft))
        freq = np.fft.rfftfreq(new_num_fft, d=1 / self.settings.soundcard.fs)

        transfer_function = uniform_filter1d(
            transfer_function, smooth_window, mode="nearest"
        )

        inv_transfer_func = 1 / (transfer_function + 1e-10)
        inv_transfer_func = inv_transfer_func[0 : freq.size]

        mean_gain = np.mean(inv_transfer_func[(freq >= freq_min) & (freq <= freq_max)])

        inv_transfer_func /= mean_gain

        min_boost_linear = 10 ** (min_boost_db / 20)
        max_boost_linear = 10 ** (max_boost_db / 20)

        inv_transfer_func[inv_transfer_func < min_boost_linear] = min_boost_linear
        inv_transfer_func[inv_transfer_func > max_boost_linear] = max_boost_linear

        # if filter:
        # TODO: add possibility to filter or to not filter
        sos = butter(
            32,
            [5000, 20000],
            btype="bandpass",
            output="sos",
            fs=self.settings.soundcard.fs,
        )
        w, h = freqz_sos(sos, fs=self.settings.soundcard.fs)

        new_h = np.interp(freq, w, np.abs(h))

        response = np.multiply(inv_transfer_func, abs(new_h))
        response[-1] = 0

        final_filter = firwin2(4096, freq, response, fs=self.settings.soundcard.fs)

        return final_filter, signal, resampled_sound

    def noise_eq_filter(self):
        signal = WhiteNoise(
            cast(float, self.settings.eq_filter.sound_duration),
            self.settings.soundcard.fs,
            self.settings.amplitude,
            self.settings.ramp_time,
            filter=True,
            freq_min=self.settings.freq.min_freq,
            freq_max=self.settings.freq.max_freq,
        )

        # Play the sound from the soundcard and record it with the microphone + DAQ system
        recorded_sound = self.record_sound(
            signal,
            self.path / "sounds" / "eq_filter_sound.bin",
            cast(float, self.settings.eq_filter.sound_duration),
            # use_mic_response=True,
        )

        resampled_sound = RecordedSound.resample(
            recorded_sound, self.settings.soundcard.fs
        )

        freq, fft = resampled_sound.fft_welch(self.settings.eq_filter.time_constant)
        transfer_function = 1 / fft

        sos = butter(
            32,
            [self.settings.freq.min_freq, self.settings.freq.max_freq],
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

        for i in range(amp_array.size):
            # Generate the noise
            signal = WhiteNoise(
                duration,
                self.settings.soundcard.fs,
                self.settings.amplitude * amp_array[i],
                self.settings.ramp_time,
                self.settings.filter.filter_input,
                cast(float, self.settings.filter.min_value),
                cast(float, self.settings.filter.max_value),
                self.eq_filter,
                noise_type="gaussian",  # FIXME
            )

            # Save the generated noise
            if type == "Calibration":
                filename = "calibration_sound_" + str(i) + ".bin"
            else:
                filename = "test_sound_" + str(i) + ".bin"

            # Play the sound from the soundcard and record it with the microphone + DAQ system
            sounds[i] = self.record_sound(
                signal,
                self.path / "sounds" / filename,
                duration,
                self.settings.filter.filter_acquisition,
            )

            # Calculate the intensity in dB SPL
            sounds[i].calculate_db_spl(self.settings.mic_factor)

            # Send information regarding the current noise to the interface
            if self.callback is not None:
                self.callback(type, i, signal, sounds[i])

        return sounds

    # def pure_tone_sweep(
    #     self,
    #     calib_array: np.ndarray,
    #     duration: float,
    #     type: Literal["Calibration", "Test"] = "Calibration",
    # ):
    #     """
    #     Plays sounds with different amplitudes and calculates the correspondent intensities in dB SPL.

    #     Parameters
    #     ----------
    #     calib_array : np.ndarray
    #         The array containing the frequency and amplitude values to be used in the different sounds.
    #     duration : float
    #         The duration of the sounds (s).
    #     type : Literal["Calibration", "Test"], optional
    #         Indicates whether this function is being run in the calibration or in the test of a calibration

    #     Returns
    #     -------
    #     calib_array : numpy.ndarray
    #         The array containing the measured dB SPL values for each frequency and amplification values.
    #     sounds : numpy.ndarray
    #         The array containing both the original and acquired signals for each frequency and amplification values.
    #     """
    #     # Initialization of the output arrays
    #     sounds = np.zeros((calib_array.shape[0], calib_array.shape[1]), dtype=Sound)

    #     for i in range(calib_array.shape[0]):
    #         for j in range(calib_array.shape[1]):
    #             # If amplitude value is NaN skip this sound
    #             if np.isnan(calib_array[i, j, 1]):
    #                 calib_array[i, j, 2] = np.nan
    #                 continue

    #             # Generate the pure tone
    #             signal = pure_tone(
    #                 duration,
    #                 self.settings.soundcard.fs,
    #                 calib_array[i, j, 0],
    #                 amplitude=calib_array[i, j, 1],
    #                 ramp_time=self.settings.ramp_time,
    #             )

    #             # Save the generated pure tone
    #             if type == "Calibration":
    #                 filename = "calibration_sound_" + str(i) + ".bin"
    #             else:
    #                 filename = "test_sound_" + str(i) + ".bin"

    #             # Play the sound from the soundcard and record it with the microphone + DAQ system
    #             sounds[i, j] = self.record_sound(
    #                 signal,
    #                 self.path / "sounds" / filename,
    #                 duration,
    #                 self.settings.filter.filter_acquisition,
    #             )

    #             # Calculate the intensity in dB SPL
    #             calib_array[i, j, 2] = calculate_db_spl(
    #                 sounds[i, j], self.settings.mic_factor
    #             )

    #             # Send information regarding the current pure tone to the interface
    #             if self.callback is not None:
    #                 self.callback(
    #                     type, i, j, signal, sounds[i, j], calib_array[i, j, 2]
    #                 )

    #     return calib_array, sounds

    def record_sound(
        self,
        signal: Sound,
        filename: Path,
        duration: float,
        filter: bool = False,
    ) -> RecordedSound:
        """
        Records the sounds.

        Parameters
        ----------
        signal : Sound
            The signal to be played and recorded.
        filename : str
            The path to the file to which the sound will be saved to and from which the sound is upload from (in case a Harp SoundCard is used).
        duration : float
            The duration of the sound (s).
        filter : bool, optional
            Indicates whether the acquired signal should be filtered or not.
        use_mic_response : bool, optional
            Indicates whether the microphone frequency response should be used as a compensation method. It's useful when calculating the speaker EQ filter.

        Returns
        -------
        sound : Sound
            The recorded sound.
        """
        # Upload the sound to the Harp SoundCard in case one is used
        if isinstance(self.soundcard, HarpSoundCard):
            create_sound_file(signal, str(filename))
            self.soundcard.load_sound(filename=str(filename))

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
                "filename": str(filename)[:-4] + "_rec",
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


def main():
    with open("config/settings.yml", "r") as file:
        data = yaml.safe_load(file)

    settings = Settings(**data)
    Calibration(settings)
