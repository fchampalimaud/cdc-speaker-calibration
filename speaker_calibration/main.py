import numpy as np
from classes import Hardware, InputParameters
from psd_calibration import psd_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage
from get_db import get_db

if __name__ == "__main__":
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)

    calibration_factor, psd_signal = psd_calibration(device, hardware, input_parameters)

    db_spl, db_fft, signals = get_db(input_parameters.att_factor, input_parameters.sound_duration_db, device, hardware, input_parameters, calibration_factor)

    fit_parameters = np.polyfit(input_parameters.log_att, db_spl, 1)
    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    tdB = np.arange(70, 50, -10)
    att_test = (tdB - fit_parameters[1]) / fit_parameters[0]
    att_test = 10**att_test

    db_spl_test, db_fft_test, signals_test = get_db(att_test, input_parameters.sound_duration_test, device, hardware, input_parameters, calibration_factor)

    device.disconnect()

    # Save output files

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
