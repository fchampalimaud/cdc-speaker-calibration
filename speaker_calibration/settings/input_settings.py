from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from typing_extensions import Self
import json


class Freq(BaseModel):
    num_freqs: Optional[int] = Field(
        description="The number of frequencies to use in the pure tone calibration.",
        default=None,
        gt=0,
    )
    min_freq: float = Field(
        description="The minimum frequency value (Hz).", ge=0, le=80000
    )
    max_freq: float = Field(
        description="The maximum frequency value (Hz).", gt=0, le=80000
    )


class TestCalibration(BaseModel):
    test: bool = Field(description="Indicates whether the calibration is tested.")
    sound_duration: Optional[float] = Field(
        description="The duration of the test sounds.", default=None, gt=0
    )
    db_min: Optional[float] = Field(
        description="The minimum nominal dB SPL value to be tested.", default=None
    )
    db_max: Optional[float] = Field(
        description="The maximum nominal dB SPL value to be tested.", default=None
    )
    db_steps: Optional[int] = Field(
        description="The number of dB SPL values to be tested.", default=None, gt=0
    )

    @model_validator(mode="after")
    def use_test(self) -> Self:
        if self.test and not (
            isinstance(self.sound_duration, float)
            and isinstance(self.db_min, float)
            and isinstance(self.db_max, float)
            and isinstance(self.db_steps, int)
        ):
            raise ValueError(
                "All of the following parameters must be correctly filled: sound_duration, db_min, db_max, db_steps."
            )
        return self


class Calibration(BaseModel):
    calibrate: bool = Field(
        description="Indicates whether the calibration is performed."
    )
    sound_duration: Optional[float] = Field(
        description="The duration of the calibration sounds.", default=None
    )
    att_min: Optional[float] = Field(
        description="The minimum attenuation value.", default=None, le=0
    )
    att_max: Optional[float] = Field(
        description="The maximum attenuation value.", default=None, le=0
    )
    att_steps: Optional[int] = Field(
        description="The number of attenuation values to use in the calibration.",
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def use_calibration(self) -> Self:
        if self.calibrate and not (
            isinstance(self.sound_duration, float)
            and isinstance(self.att_min, float)
            and isinstance(self.att_max, float)
            and isinstance(self.att_steps, int)
        ):
            raise ValueError(
                "All of the following parameters must be correctly filled: sound_duration, att_min, att_max, att_steps."
            )
        return self


class InverseFilter(BaseModel):
    determine_filter: bool = Field(
        description="Indicates whether the inverse filter is determined. Noise calibration only!"
    )
    sound_duration: Optional[float] = Field(
        description="The duration of the sound used to determine the inverse filter.",
        default=None,
        gt=0,
    )
    time_constant: Optional[float] = Field(
        description="The duration of each division of the original signal that is used to compute the inverse filter (s).",
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def calculate_filter(self) -> Self:
        if self.determine_filter and not (
            isinstance(self.sound_duration, float)
            and isinstance(self.time_constant, float)
        ):
            raise ValueError(
                "All of the following parameters must be correctly filled: sound_duration, time_constant."
            )
        return self


class Filter(BaseModel):
    filter_input: bool = Field(
        description="Indicates whether the band-pass filter is applied to the input sound."
    )
    filter_acquisition: bool = Field(
        description="Indicates whether the band-pass filter is applied to the acquired sound."
    )
    min_value: Optional[float] = Field(
        description="The low cuttoff frequency of the filter (Hz).",
        default=None,
        ge=0,
        le=80000,
    )
    max_value: Optional[float] = Field(
        description="The high cuttoff frequency of the filter (Hz).",
        default=None,
        gt=0,
        le=80000,
    )

    @model_validator(mode="after")
    def use_filter(self) -> Self:
        if (self.filter_input or self.filter_acquisition) and not (
            isinstance(self.min_value, float) and isinstance(self.max_value, float)
        ):
            raise ValueError(
                "All of the following parameters must be correctly filled: min_value, max_value."
            )
        return self


class Sound(BaseModel):
    ramp_time: float = Field(
        description="The ramp time of the sounds used during the calibration process (s).",
        ge=0,
    )
    amplification: float = Field(
        description="The amplification of the speakers.", ge=0, le=1
    )
    freq: Freq = Field(
        description="The frequency-related parameters to be used in the calibration."
    )
    filter: Filter = Field(
        description="The configuration parameters of the band-pass filter used."
    )
    inverse_filter: Optional[InverseFilter] = Field(
        description="The settings related to the inverse filter calculation. Noise calibration only!",
        default=None,
    )
    calibration: Calibration = Field(
        description="The settings used for the actual speaker calibration."
    )
    test_calibration: TestCalibration = Field(
        description="The settings used for the calibration test."
    )


class Settings(BaseModel):
    sound_type: Literal["noise", "pure_tone"] = Field(
        description="Indicates whether the calibration will be made with noise or pure tones."
    )
    reference_pressure: float = Field(description="The reference pressure (Pa).", gt=0)
    sound: Sound = Field(description="The sound-related configurations.")

    @model_validator(mode="after")
    def is_noise(self) -> Self:
        if self.sound_type == "noise" and not isinstance(
            self.sound.inverse_filter, InverseFilter
        ):
            raise ValueError("The sound.inverse_filter parameter must be filled.")
        return self


if __name__ == "__main__":
    with open("config/schemas/settings-schema.json", "w") as file:
        json.dump(Settings.model_json_schema(), file, indent=2)
