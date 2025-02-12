from speaker_calibration.protocol.generate_sound import generate_noise
import numpy as np


def create_sound_file(
    signal_left: np.ndarray,
    signal_right: np.ndarray,
    filename: str,
    speaker_side: str = "both",
):
    """
    Creates the .bin sound file to be loaded to the Harp Sound Card.

    Parameters
    ----------
    signal_left : numpy.ndarray
        the signal to be written to the .bin file that is going to be played by the left speaker.
    signal_right : numpy.ndarray
        the signal to be written to the .bin file that is going to be played by the right speaker.
    filename : str
        the name of the .bin file.
    speaker_side : str
        whether the sound plays in both speakers or in a single one. Possible values: "both", "left" or "right.
    """
    # Transforms the signal from values between -1 to 1 into 24-bit integers
    amplitude24bits = np.power(2, 31) - 1

    if speaker_side == "both":
        wave_left = amplitude24bits * signal_left
        wave_right = amplitude24bits * signal_right
    elif speaker_side == "left":
        wave_left = amplitude24bits * signal_left
        wave_right = 0 * signal_right
    elif speaker_side == "right":
        wave_left = 0 * signal_left
        wave_right = amplitude24bits * signal_right
    else:
        raise ValueError(
            'speaker_side value should be "both", "left" or "right" instead of "%s"'
            % speaker_side
        )

    # Groups the signals to be played in the left and right channels/speakers in a single array
    stereo = np.stack((wave_left, wave_right), axis=1)
    wave_int = stereo.astype(np.int32)

    # Writes the sound to the .bin file
    with open(filename, "wb") as f:
        wave_int.tofile(f)


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
    soundcard_index: int = 2,
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

    signal_left = generate_noise(
        fs, duration, amplification=attenuation_left, calibration_factor=cf_left
    )
    signal_right = generate_noise(
        fs, duration, amplification=attenuation_right, calibration_factor=cf_right
    )

    create_sound_file(signal_left, signal_right, filename)


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
    )
