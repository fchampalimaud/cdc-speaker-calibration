from pydantic import BaseModel, Field, model_validator
from typing import Optional, Union, Literal
from typing_extensions import Self
import json


# FIXME
class ComputerSoundCard(BaseModel):
    soundcard_name: str = Field(
        description="The name of the soundcard being used in the calibration."
    )
    fs: int = Field(description="The sampling frequency of the soundcard (Hz).", gt=0)


class HarpSoundCard(BaseModel):
    com_port: str = Field(
        description='The COM number the soundcard corresponds to in the computer used for the calibration. The string should be of the format "COM?", in which "?" is the COM number.'
    )
    fs: Literal[96000, 192000] = Field(
        description="The sampling frequency of the soundcard (Hz)."
    )
    soundcard_id: Optional[str] = Field(
        description='The ID of the soundcard. If the soundcard is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.',
        default=None,
    )
    audio_amp_id: Optional[str] = Field(
        description='The ID of the audio amplifier. If the audio amplifier is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.',
        default=None,
    )


class Hardware(BaseModel):
    is_harp: bool = Field(
        description="Indicates whether the soundcard being calibrated is a Harp device or not."
    )
    soundcard: Union[HarpSoundCard, ComputerSoundCard] = Field(
        description="The soundcard details."
    )
    speaker_id: int = Field(
        description="The ID number of the speaker being calibrated (StC)."
    )
    setup_id: int = Field(description="The ID number of the setup.")
    fs_adc: int = Field(
        description="The sampling frequency of the ADC (Hz).", gt=0, le=250000
    )
    mic_factor: float = Field(
        description="The conversion factor of the microphone (V/Pa).", gt=0
    )

    @model_validator(mode="after")
    def check_is_harp(self) -> Self:
        if self.is_harp and not isinstance(self.soundcard, HarpSoundCard):
            raise ValueError("soundcard must be of type HarpSoundCard")
        elif not self.is_harp and not isinstance(self.soundcard, ComputerSoundCard):
            raise ValueError("soundcard must be of type ComputerSoundCard")
        return self


if __name__ == "__main__":
    with open("config/schemas/hardware-schema.json", "w") as file:
        json.dump(Hardware.model_json_schema(), file, indent=2)
