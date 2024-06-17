import matplotlib.pyplot as plt
import numpy as np
from classes import Hardware, InputParameters
from get_db import get_db
from psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage

if __name__ == "__main__":
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)

    fig = plt.figure()
    ax = fig.subplots(3)

    calibration_factor, psd_signal = psd_calibration(hardware, input_parameters)
    ax[0].step(calibration_factor[:, 0], calibration_factor[:, 1])
    ax[0].fill_between(calibration_factor[:, 0], calibration_factor[:, 1], step="pre")
    ax[0].set_ylim(0, max(calibration_factor[:, 1]) * 1.1)

    db_spl, db_fft, signals = get_db(input_parameters.att_factor, input_parameters.sound_duration_db, hardware, input_parameters, calibration_factor)
    ax[1].plot(input_parameters.log_att, db_spl, "o-")
    ax[1].plot(input_parameters.log_att, db_fft, "o-")

    fit_parameters = np.polyfit(input_parameters.log_att, db_spl, 1)
    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    tdB = np.arange(70, 50, -10)
    att_test = (tdB - fit_parameters[1]) / fit_parameters[0]
    att_test = 10**att_test

    db_spl_test, db_fft_test, signals_test = get_db(att_test, input_parameters.sound_duration_test, hardware, input_parameters, calibration_factor)
    ax[2].plot(tdB, db_spl_test, "o-")
    ax[2].plot(tdB, db_fft_test, "o-")
    ax[2].plot(tdB, tdB, "o-")

    device.disconnect()

    plt.show()

    # Save output files

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
