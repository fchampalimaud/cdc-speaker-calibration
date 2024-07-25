from pyharp.device import Device
from pyharp.messages import HarpMessage
from speaker_calibration.calibration_protocols import noise_calibration, pure_tone_calibration
from speaker_calibration.classes import Hardware, InputParameters


# TODO Init DAQ (Ni-DAQ or Moku:Go or add the possibility to choose between them)
if __name__ == "__main__":
    # Reads the input parameters and hardware characteristics and initialize the Harp SoundCard
    input_parameters = InputParameters()
    hardware = Hardware()
    device = Device(hardware.soundcard_com)
    device.send(HarpMessage.WriteU8(41, 0).frame, False)
    device.send(HarpMessage.WriteU8(44, 2).frame, False)

    # Choice of calibration type
    if input_parameters.sound_type == "Noise":
        noise_calibration(hardware, input_parameters)
    elif input_parameters.sound_type == "Pure Tone":
        pure_tone_calibration(hardware, input_parameters)

    # TODO: save content

    device.disconnect()
