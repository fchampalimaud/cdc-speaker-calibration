import os
from datetime import datetime
from typing import Optional

import numpy as np
from speaker_calibration.sound import WhiteNoise
from speaker_calibration.soundcards import create_sound_file


def upload_sound(
    duration: float,
    calib_left: np.ndarray,
    eq_left: np.ndarray,
    calib_right: np.ndarray,
    eq_right: np.ndarray,
    abl: Optional[float] = None,
    ild: float = 0,
    fs: int = 192000,
    ramp_time: float = 0.005,
    filename: str = "sound.bin",
    soundcard_index: Optional[int] = None,
):
    if soundcard_index is not None and soundcard_index < 2 and soundcard_index > 31:
        raise (ValueError("soundcard_index must be between 2 and 31"))

    if abl is None:
        attenuation_left = 1
        attenuation_right = 1
    else:
        db_left = abl - ild / 2
        attenuation_left = 10 ** ((db_left - calib_left[1]) / calib_left[0])
        db_right = abl + ild / 2
        attenuation_right = 10 ** ((db_right - calib_right[1]) / calib_right[0])

    signal_left = WhiteNoise(
        duration,
        fs,
        amplitude=attenuation_left,
        ramp_time=ramp_time,
        freq_min=5000,
        freq_max=20000,
        eq_filter=eq_left,
    )
    signal_right = WhiteNoise(
        duration,
        fs,
        amplitude=attenuation_right,
        ramp_time=ramp_time,
        freq_min=5000,
        freq_max=20000,
        eq_filter=eq_right,
    )

    create_sound_file(signal_left, signal_right, filename)
    if soundcard_index is not None:
        os.system(
            "cmd /c .\\assets\\toSoundCard.exe "
            + filename
            + " "
            + str(soundcard_index)
            + " 0 "
            + str(fs)
        )


def main():
    calib_left = np.load(
        "C:/Users/HSP/Desktop/output/left_speaker_setup1/calibration_parameters_speaker0_setup0.csv"
    )
    eq_left = np.load(
        "C:/Users/HSP/Desktop/output/left_speaker_setup1/inverse_filter_speaker0_setup0.csv"
    )
    calib_right = np.load(
        "C:/Users/HSP/Desktop/output/right_speaker_setup/calibration_parameters_speaker0_setup0.csv"
    )
    eq_right = np.load(
        "C:/Users/HSP/Desktop/output/right_speaker_setup/inverse_filter_speaker0_setup0.csv"
    )

    date = datetime.now().strftime("%y%m%d_%H%M%S")

    for i in range(5):
        upload_sound(
            10,
            calib_left,
            eq_left,
            calib_right,
            eq_right,
            fs=192000,
            filename="output/sounds/" + date + "/noise" + str(i) + ".bin",
            soundcard_index=(2 * i + 2),
        )

    upload_sound(
        0.001,
        calib_left,
        eq_left,
        calib_right,
        eq_right,
        abl=0,
        fs=96000,
        ramp_time=0,
        filename="output/sounds/" + date + "/silence.bin",
        soundcard_index=31,
    )

    if __name__ == "__main__":
        main()
