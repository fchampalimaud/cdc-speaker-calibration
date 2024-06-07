import numpy as np
from classes import Hardware, InputParameters
from db_calibration import db_calibration
from psd_calibration import psd_calibration
from pyharp.device import Device
from test_calibration import test_calibration

if __name__ == "__main__":
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)

    # TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)

    calibration_factor, recorded_sound, fft_bef_cal = psd_calibration(device, input_parameters, hardware)

    db_spl_aft_cal, db_spl_bef_cal, filtered_signal, fft_aft_cal, rms_sound_aft_cal, signal, rms_fft, db_fft = db_calibration(
        input_parameters, hardware, calibration_factor, recorded_sound
    )

    fit_parameters = np.polyfit(input_parameters.log_att, db_spl_aft_cal, 1)

    print("Slope: " + str(fit_parameters[0]))
    print("Intercept: " + str(fit_parameters[1]))

    db_spl_test, db_fft_test = test_calibration(hardware, input_parameters, calibration_factor, fit_parameters[0], fit_parameters[1])

    device.disconnect()

    # Save output files

# TODO Understand what init_PsyTB.m does. If it just activates the SoundCard, use the pyharp package
