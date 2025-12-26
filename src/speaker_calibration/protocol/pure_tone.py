from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy.interpolate import RBFInterpolator, griddata

from speaker_calibration.config import Paths, PureToneProtocolSettings
from speaker_calibration.protocol.utils import Protocol
from speaker_calibration.recording import RecordingDevice
from speaker_calibration.sound import PureTone, Sound
from speaker_calibration.soundcards import HarpSoundCard, SoundCard, create_sound_file
from speaker_calibration.utils import SweepType


class PureToneProtocol(Protocol):
    def __init__(
        self,
        settings: PureToneProtocolSettings,
        soundcard: SoundCard,
        adc: RecordingDevice,
        output_path: Path,
        paths: Paths,
        callback: Optional[Callable] = None,
    ):
        super().__init__(settings, soundcard, adc, output_path, paths, callback)

        """
        Performs the pure tone speaker calibration.
        """
        # Perform the calibration
        if self.paths.calibration is None:
            # Generate the array of frequencies to be used in the calibration
            freq = np.linspace(
                self.settings.calibration.min_freq,
                self.settings.calibration.max_freq,
                self.settings.calibration.num_freqs,
            )

            # Generate the array of amplitudes to be used in the calibration
            # TODO: check whether it's better to use log spaced amp_array
            amp = np.linspace(0, 1, self.settings.calibration.amp_steps)

            # Generate the input calibration array
            freq, amp = np.meshgrid(freq, amp, indexing="ij")
            db = np.zeros(freq.shape)
            calib_array = np.stack((freq, amp, db), axis=2)

            # Send the calibration frequency and amplitude information to the interface
            if self.callback is not None:
                self.callback("Pre-calibration", calib_array[:, :, 0:2])

            # Generate and play the sounds for every frequency and amplitude values
            calib_array, _ = self.sound_sweep(
                calib_array,
                self.settings.calibration.sound_duration,
            )

            # Convert calibration array to 2D array and save it as a CSV file
            calib = calib_array.reshape(calib_array.shape[0] * calib_array.shape[1], 3)
            np.save(self.path / "calibration.npy", calib)

            amp = amp.reshape(-1)
        else:
            calib = np.load(self.paths.calibration)
            amp = calib[:, 1]

        # Test the calibration
        if self.settings.test is not None:
            # Generate the array of frequencies to be used in the calibration test
            test_freq = np.linspace(
                self.settings.test.min_freq,
                self.settings.test.max_freq,
                self.settings.test.num_freqs,
            )

            # Generate the array of dB values to be used in the calibration test
            test_db = np.linspace(
                self.settings.test.min_db,
                self.settings.test.max_db,
                self.settings.test.db_steps,
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
            test_array2, _ = self.sound_sweep(
                test_array,
                self.settings.test.sound_duration,
                SweepType.TEST,
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
            np.save(self.path / "test.npy", test)

    def sound_sweep(
        self,
        calib_array: np.ndarray,
        duration: float,
        type: SweepType = SweepType.CALIBRATION,
    ):
        """
        Plays sounds with different amplitudes and calculates the correspondent intensities in dB SPL.

        Parameters
        ----------
        calib_array : np.ndarray
            The array containing the frequency and amplitude values to be used in the different sounds.
        duration : float
            The duration of the sounds (s).
        type : SweepType, optional
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
                self.soundcard.fs,
                calib_array[i, 0, 0],
                amplitude=calib_array[i, -1, 1],
                ramp_time=self.settings.ramp_time,
            )

            # Save the generated pure tone
            match type:
                case SweepType.CALIBRATION:
                    filename = (
                        self.path
                        / "sounds"
                        / ("calibration_" + str(round(calib_array[i, 0, 0])) + "hz.bin")
                    )
                case SweepType.TEST:
                    filename = (
                        self.path
                        / "sounds"
                        / ("test_" + str(round(calib_array[i, 0, 0])) + "hz.bin")
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
                    calib_array[i, j, 1],
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
