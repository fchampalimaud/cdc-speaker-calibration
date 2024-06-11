import os
import time

import numpy as np
from classes import Hardware, InputParameters
from fft_intervals import fft_intervals
from generate_noise import create_sound_file, generate_noise
from scipy.signal import butter, sosfilt
from pyharp.device import Device
from pyharp.messages import HarpMessage


def test_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters, calibration_factor: np.ndarray, slope: float, intercept: float):
    """
    Tests the calibration curve given by `slope` and `intercept`.

    Parameters
    ----------
    device : Device
        the initialized (Harp) Sound Card. This object allows to send and receive messages to and from the device.
    input_parameters : InputParameters
        the object containing the input parameters used for the calibration.
    hardware : Hardware
        the object containing information regarding the equipment being calibrated.
    calibration_factor : numpy.array
        the power spectral density calibration factor.
    slope : float
        the slope of the dB calibration curve.
    intercept : float
        the intercept of the dB calibration curve.

    Returns
    -------
    db_spl_test : numpy.ndarray
        the dB values calculated for each attenuation factor (dB).
    db_fft_test : numpy.ndarray
        # TODO
    """
    tdB = np.arange(70, 50, -10)
    db_spl_test = np.zeros(tdB.size, dtype=np.ndarray)
    db_fft_test = np.zeros(tdB.size, dtype=np.ndarray)

    for i in range(tdB.size):
        att = (tdB[i] - intercept) / slope
        att = 10**att
        print("Target dB: " + str(att))

        # Generates the noise and upload it to the soundcard
        signal = generate_noise(
            fs=hardware.fs_sc,
            duration=input_parameters.sound_duration_test,
            head_phone_amp=input_parameters.amplification * att,
            filter=True,
            freq_min=input_parameters.freq_min,
            freq_max=input_parameters.freq_max,
            calibrate=True,
            calibration_factor=calibration_factor,
        )  # TODO: see noise MATLAB function
        create_sound_file(signal, "sound.bin")
        os.system("cmd /c .\\assets\\toSoundCard.exe sound.bin 2 0 " + str(hardware.fs_sc))  # TODO: add toSoundCard.exe to the project

        # Plays the sound throught the soundcard and recorded it with the microphone + DAQ system
        device.send(HarpMessage.WriteU16(32, 2).frame, False)
        time.sleep(input_parameters.sound_duration_psd)
        recorded_signal = np.zeros(1000)  # TODO: Record sound

        # Calculates the fft of the recorded sound
        fft, freq_vector, n_intervals, samples_per_interval, rms = fft_intervals(
            recorded_signal, input_parameters.time_constant, input_parameters.fs_adc, input_parameters.smooth_window
        )

        # Applies a 3th-order butterworth band-pass filter to the recorded signal
        sos = butter(3, [input_parameters.freq_high, input_parameters.freq_low], btype="bandpass", output="sos", fs=input_parameters.fs_adc)
        filtered_signal = sosfilt(sos, recorded_signal)

        rms_fft = rms / input_parameters.mic_factor
        db_fft = 20 * np.log10(rms_fft / input_parameters.reference_pressure)

        signal_pascal = filtered_signal[int(0.1 * filtered_signal.size) : int(0.9 * filtered_signal.size)] / input_parameters.mic_factor
        rms_sound = np.sqrt(np.mean(signal_pascal**2))
        db_spl = 20 * np.log10(rms_sound / input_parameters.reference_pressure)

        db_spl_test[i] = db_spl
        db_fft_test[i] = db_fft

    return db_spl_test, db_fft_test  # StC
