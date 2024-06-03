import numpy as np
from pyharp.device import Device
from classes import Hardware, InputParameters
from psd_calibration import psd_calibration
from db_calibration import db_calibration

if __name__ == "__main__":
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)

    # TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)

    cal_factor, f_vec, sig_bef_cal, fft_bef_cal = psd_calibration(device, input_parameters, hardware)

    db_spl_aft_cal = db_calibration()  # unfinished

    fit_parameters = np.polyfit(input_parameters.log_att, db_spl_aft_cal, 1)

    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    device.disconnect()

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
