import os
import time

import numpy as np
from classes import Hardware, InputParameters
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from pyharp.device import Device
from pyharp.messages import HarpMessage


def psd_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters):
    """
    Calculates the power spectral density calibration factor to be used with the setup being calibrated.

    Parameters
    ----------
    device : Device
        the initialized (Harp) Sound Card. This object allows to send and receive messages to and from the device.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.

    Returns
    -------
    calibration_factor : numpy.ndarray
        the power spectral density calibration factor.
    recorded_sound : numpy.ndarray
        the sound recorded with the microphone + DAQ system.
    fft_bef_cal : numpy.ndarray
        the fft of the recorded sound.
    """
    # Generates the noise and upload it to the soundcard
    signal = generate_noise(fs=hardware.fs_sc, duration=input_parameters.sound_duration_psd)
    create_sound_file(signal, "sound.bin")
    os.system("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(hardware.fs_sc))  # TODO: add toSoundCard.exe to the project

    # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
    device.send(HarpMessage.WriteU16(32, 2).frame, False)
    time.sleep(input_parameters.sound_duration_psd)
    recorded_sound = np.zeros(1000)  # TODO: Record sound

    # Calculates the fft of the recorded sound
    fft_bef_cal, freq_vector, n_intervals, samples_per_interval, rms = fft_intervals(
        recorded_sound, input_parameters.time_constant, input_parameters.fs_adc, input_parameters.smooth_window
    )

    # Calculates the power spectral density calibration factor to be used with the setup being calibrated
    calibration_factor = 1 / fft_bef_cal
    calibration_factor = np.stack((freq_vector, calibration_factor), axis=1)

    return calibration_factor, recorded_sound, fft_bef_cal  # StC
