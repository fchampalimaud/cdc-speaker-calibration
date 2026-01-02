import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import yaml

import speaker_calibration.config as settings
from speaker_calibration.config import Config
from speaker_calibration.protocol import NoiseProtocol, PureToneProtocol
from speaker_calibration.recording import Moku, NiDaq
from speaker_calibration.soundcards import HarpSoundCard


def run_calibration(config: Config, callback: Optional[Callable] = None):
    # Define the path for the output directory for the current calibration
    path = Path() / config.paths.output / datetime.now().strftime("%y%m%d_%H%M%S")
    # Create the output directory structure for the current calibration
    os.makedirs(path / "sounds")

    config_dict = config.model_dump(by_alias=True, exclude_unset=True)
    with open(path / "config.yml", "w") as file:
        yaml.dump(config_dict, file, default_flow_style=False)

    # Initiate the soundcard to be used in the calibration
    match config.soundcard:
        case settings.HarpSoundCard():
            soundcard = HarpSoundCard(
                config.soundcard.serial_port,
                config.soundcard.fs,
                config.soundcard.speaker,
            )
        case settings.ComputerSoundCard():
            # TODO: implement interface with computer soundcard
            soundcard = None

    # Initiate the ADC to be used in the calibration
    match config.adc:
        case settings.NiDaq():
            adc = NiDaq(config.adc.device_id, config.adc.fs)
        case settings.Moku():
            adc = Moku(config.adc.address, config.adc.fs)

    match config.protocol:
        case settings.NoiseProtocolSettings():
            NoiseProtocol(config.protocol, soundcard, adc, path, config.paths, callback)
        case settings.PureToneProtocolSettings():
            PureToneProtocol(
                config.protocol, soundcard, adc, path, config.paths, callback
            )
