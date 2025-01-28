from speaker_calibration.protocol.generate_sound import (
    generate_noise,
    create_sound_file,
)
import os
import numpy as np


def upload_sound(
    duration: float,
    abl: float,
    inverse_filter_left_path: str,
    inverse_filter_right_path: str,
    fit_left_path: str,
    fit_right_path: str,
    ild: float = 0,
    fs: int = 192000,
    filename: str = "sound.bin",
    soundcard_index: int = 2,
):
    if soundcard_index < 2 and soundcard_index > 31:
        raise (ValueError("soundcard_index must be between 2 and 31"))

    cf_left = np.loadtxt(inverse_filter_left_path, delimiter=",")
    cf_right = np.loadtxt(inverse_filter_right_path, delimiter=",")
    fit_left = np.loadtxt(fit_left_path, delimiter=",")
    fit_right = np.loadtxt(fit_right_path, delimiter=",")

    db_left = abl - ild / 2
    attenuation_left = 10 ** ((db_left - fit_left[1]) / fit_left[0])
    db_right = abl + ild / 2
    attenuation_right = 10 ** ((db_right - fit_right[1]) / fit_right[0])

    signal_left = generate_noise(
        fs, duration, head_phone_amp=attenuation_left, calibration_factor=cf_left
    )
    signal_right = generate_noise(
        fs, duration, head_phone_amp=attenuation_right, calibration_factor=cf_right
    )

    create_sound_file(signal_left, signal_right, filename)
    # os.system(
    #     "cmd /c .\\assets\\toSoundCard.exe "
    #     + filename
    #     + " "
    #     + str(soundcard_index)
    #     + " 0 "
    #     + str(fs)
    # )


i = 10
for ABL in [30, 40, 50]:
    for ILD in [-12, -8, 8, 12]:
        i = i + 1
        upload_sound(
            10,
            58.5,
            "output/calibration_factor_speaker1_setup1.csv",
            "output/calibration_factor_speaker1_setup1.csv",
            "output/fit_parameters_speaker1_setup1.csv",
            "output/fit_parameters_speaker1_setup1.csv",
            ild=ILD,
            fs=192000,
            filename="sound.bin",
        )
