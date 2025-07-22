import os

import numpy as np
from speaker_calibration.sound import create_sound_file, white_noise


def upload_sound(
    duration: float,
    inverse_filter_left_path: str,
    inverse_filter_right_path: str,
    fit_left_path: str,
    fit_right_path: str,
    abl: float = None,
    ild: float = 0,
    fs: int = 192000,
    filename: str = "sound.bin",
    soundcard_index: int = None,
):
    if soundcard_index < 2 and soundcard_index > 31:
        raise (ValueError("soundcard_index must be between 2 and 31"))

    cf_left = np.loadtxt(inverse_filter_left_path, delimiter=",")
    cf_right = np.loadtxt(inverse_filter_right_path, delimiter=",")
    fit_left = np.loadtxt(fit_left_path, delimiter=",")
    fit_right = np.loadtxt(fit_right_path, delimiter=",")

    if abl is None:
        attenuation_left = 1
        attenuation_right = 1
    else:
        db_left = abl - ild / 2
        attenuation_left = 10 ** ((db_left - fit_left[1]) / fit_left[0])
        db_right = abl + ild / 2
        attenuation_right = 10 ** ((db_right - fit_right[1]) / fit_right[0])

    signal_left = white_noise(
        duration,
        fs,
        amplitude=attenuation_left,
        freq_min=5000,
        freq_max=20000,
        inverse_filter=cf_left,
    )
    signal_right = white_noise(
        duration,
        fs,
        amplitude=attenuation_right,
        freq_min=5000,
        freq_max=20000,
        inverse_filter=cf_right,
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


for i in range(5):
    upload_sound(
        10,
        "C:/Users/HSP/Desktop/output/left_speaker_setup1/inverse_filter_speaker0_setup0.csv",
        "C:/Users/HSP/Desktop/output/right_speaker_setup/inverse_filter_speaker0_setup0.csv",
        "C:/Users/HSP/Desktop/output/left_speaker_setup1/calibration_parameters_speaker0_setup0.csv",
        "C:/Users/HSP/Desktop/output/right_speaker_setup/calibration_parameters_speaker0_setup0.csv",
        abl=None,
        ild=0,
        fs=192000,
        filename="sound" + str(i) + ".bin",
        soundcard_index=(2 * i + 2),
    )
