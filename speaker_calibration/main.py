import matplotlib.pyplot as plt
import numpy as np
from classes import Hardware, InputParameters, Signal
from get_db import get_db
from psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage
import time
from scipy.signal import welch


def noise_calibration(hardware: Hardware, input_parameters: InputParameters):
    # Initializes the matplotlib figure
    fig = plt.figure()
    ax = fig.subplots(3)

    # Calibrates the hardware in power spectral density (PSD)
    calibration_factor, psd_signal, psd = psd_calibration(hardware, input_parameters)
    # Plots the PSD calibration factor
    ax[0].step(calibration_factor[:, 0], calibration_factor[:, 1])
    ax[0].fill_between(calibration_factor[:, 0], calibration_factor[:, 1], step="pre")
    ax[0].set_ylim(0, max(calibration_factor[:, 1]) * 1.1)

    freq, psd_og = welch(
        psd_signal.signal[int(0.1 * psd_signal.signal.size) : int(0.9 * psd_signal.signal.size)],
        fs=input_parameters.fs_adc,
        nperseg=input_parameters.time_constant * hardware.fs_sc,
    )

    # # Calculates the dB SPL values for different attenuation factors
    # db_spl, db_fft, signals = get_db(input_parameters.att_factor, input_parameters.sound_duration_db, hardware, input_parameters, calibration_factor)
    # # Plots dB SPL vs logarithmic attenuation factors
    # ax[1].plot(input_parameters.log_att, db_spl, "o-")
    # ax[1].plot(input_parameters.log_att, db_fft, "o-")

    # # Fits the dB SPL vs logarithmic attenuation to a straight line
    # fit_parameters = np.polyfit(input_parameters.log_att, db_spl, 1)
    # print("Slope: " + str(fit_parameters[0]))
    # print("Intercept: " + str(fit_parameters[1]))

    # # Defines new attenuation factors to test the fit performed
    # tdB = np.arange(70, 50, -10)
    # att_test = (tdB - fit_parameters[1]) / fit_parameters[0]
    # att_test = 10**att_test

    # # Tests the fit with the new attenuation factors
    # db_spl_test, db_fft_test, signals_test = get_db(att_test, input_parameters.sound_duration_test, hardware, input_parameters, calibration_factor)
    # # Plots dB SPL vs (new) test logarithmic attenuation factors
    # ax[2].plot(tdB, db_spl_test, "o-")
    # ax[2].plot(tdB, db_fft_test, "o-")
    # ax[2].plot(tdB, tdB, "o-")

    np.savetxt("output/calibration_factor.csv", calibration_factor, delimiter=",", fmt="%.2f")
    # np.savetxt("output/fit_parameters.csv", fit_parameters, delimiter=",", fmt="%.2f")
    np.savetxt("output/signal.csv", psd_signal.signal, delimiter=",")
    np.savetxt("output/recorded_sound.csv", psd_signal.recorded_sound, delimiter=",")

    plt.show()


def pure_tone_calibration(device: Device, hardware: Hardware, input_parameters: InputParameters):
    # Initializes the matplotlib figure
    fig = plt.figure()
    ax = fig.subplots(1)

    # Frequency response of the system
    freq_array = np.logspace(np.log10(1), np.log10(80000), 100)
    db_array = np.zeros(100)
    for i in range(100):
        print("Frequency (Hz): " + str(freq_array[i]))
        signal = Signal(1, hardware, input_parameters, freq=freq_array[i])
        # time.sleep(1)
        signal.load_sound()
        # time.sleep(1)
        signal.record_sound(input_parameters)
        signal.db_spl_calculation(input_parameters)
        db_array[i] = signal.db_spl
    ax.plot(freq_array, db_array, "o-")
    ax.set_xscale("log")

    np.savetxt("calibration.txt", db_array)
    # # Attenuation test
    # # 1000 Hz Pure Tone
    # signal = Signal(1, hardware, input_parameters, freq=1000)
    # signal.load_sound()
    # signal.record_sound(input_parameters)
    # signal.db_spl_calculation(input_parameters)
    # print("dB SPL original signal: " + str(signal.db_spl))

    # # 1000 Hz Pure Tone - Soundcard Attenuated
    # device.send(HarpMessage.WriteU16(34, 12).frame, False)
    # device.send(HarpMessage.WriteU16(35, 12).frame, False)
    # time.sleep(1)
    # signal.record_sound(input_parameters)
    # signal.db_spl_calculation(input_parameters)
    # print("dB SPL soundcard attenuated: " + str(signal.db_spl))

    # # 1000 Hz Pure Tone - Software Attenuated
    # device.send(HarpMessage.WriteU16(34, 0).frame, False)
    # device.send(HarpMessage.WriteU16(35, 0).frame, False)
    # signal = Signal(1, hardware, input_parameters, attenuation=0.5012, freq=1000)
    # signal.load_sound()
    # signal.record_sound(input_parameters)
    # signal.db_spl_calculation(input_parameters)
    # print("dB SPL software attenuated: " + str(signal.db_spl))

    plt.show()


# TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)
if __name__ == "__main__":
    # Reads the input parameters and hardware characteristics and initialize the Harp SoundCard
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # Choice of calibration type
    if input_parameters.sound_type == "noise":
        noise_calibration(hardware, input_parameters)
    elif input_parameters.sound_type == "pure tone":
        pure_tone_calibration(device, hardware, input_parameters)

    device.disconnect()
