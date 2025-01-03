from pydantic import BaseModel, Field
from typing import Optional, Union


class Hardware:
    """
    A class used to represent the equipment being calibrated. This class mirrors the contents of the `config/hardware.yml` file.

    Attributes
    ----------
    fs_sc : int
        the sampling frequency of the soundcard (Hz).
    harp_soundcard : bool
        indicates whether the soundcard being calibrated is a Harp device or not.
    soundcard_com : str
        indicates the COM number the soundcard corresponds to in the computer used for the calibration. The string should be of the format "COM?", in which "?" is the COM number.
    soundcard_id : str
        the ID of the soundcard. If the soundcard is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    harp_audio_amp : bool
        indicates whether the audio amplifier used in the calibration is a Harp device or not.
    audio_amp_id : str
        the ID of the audio amplifier. If the audio amplifier is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.
    speaker_id : int
        the ID number of the speaker being calibrated (StC).
    setup_id : int
        the ID number of the setup.
    """

    fs_sc: int = Field(description="The sampling frequency of the soundcard (Hz).")
    harp_soundcard: bool
    soundcard_com: str
    soundcard_id: str
    harp_audio_amp: bool
    audio_amp_id: str
    speaker_id: int
    setup_id: int
