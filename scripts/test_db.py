from typing import Literal

import numpy as np
from speaker_calibration.soundcards import HarpSoundCard

SERIAL_PORT = "COMx"


def test_db(
    abl: float,
    ild: float,
    index: Literal[2, 4, 6, 8, 10],
    calibration_left: str,
    calibration_right: str,
    filename: str = "sound",
):
    soundcard = HarpSoundCard(SERIAL_PORT)
    left_cal = np.load(calibration_left)
    right_cal = np.load(calibration_right)

    db_left = abl - ild / 2
    db_right = abl + ild / 2

    att_left = (-20 * (db_left - left_cal[1]) / left_cal[0]) * 10
    soundcard.device.write_attenuation_left(int(att_left))

    att_right = (-20 * (db_right - right_cal[1]) / right_cal[0]) * 10
    soundcard.device.write_attenuation_right(int(att_right))

    soundcard.play(index)


test_db(
    abl=50,
    ild=0,
    index=2,
    calibration_left=r"C:/Users/RenartLab/Desktop/cdc-speaker-calibration/output/250819_142853/calibration_parameters.npy",
    calibration_right=r"C:/Users/RenartLab/Desktop/cdc-speaker-calibration/output/250819_142853/calibration_parameters.npy",
)
