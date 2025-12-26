import json
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from speaker_calibration.utils import Speaker


class Test(BaseModel):
    sound_duration: float = Field(description="The duration of the test sounds.", gt=0)
    min_db: float = Field(description="The minimum nominal dB SPL value to be tested.")
    max_db: float = Field(description="The maximum nominal dB SPL value to be tested.")
    db_steps: int = Field(description="The number of dB SPL values to be tested.", gt=0)


class Calibration(BaseModel):
    sound_duration: float = Field(description="The duration of the calibration sounds.")
    min_amp: float = Field(description="The minimum amplitude value.", le=0)
    max_amp: float = Field(description="The maximum amplitude value.", le=0)
    amp_steps: int = Field(
        description="The number of amplitude values to use in the calibration.",
        gt=0,
    )


class EQFilter(BaseModel):
    sound_duration: float = Field(
        description="The duration of the sound used to determine the EQ filter.",
        gt=0,
    )
    time_constant: float = Field(
        description="The duration of each division of the original signal that is used to compute the EQ filter (s).",
        gt=0,
        default=0.005,
    )
    amplitude: float = Field(
        description="The amplitude of the speakers.", ge=0, le=1, default=1
    )
    min_boost_db: float = Field(description="TODO", default=-24)
    max_boost_db: float = Field(description="TODO", default=12)


class Filter(BaseModel):
    filter_input: bool = Field(
        description="Indicates whether the band-pass filter is applied to the input sound.",
        default=True,
    )
    filter_acquisition: bool = Field(
        description="Indicates whether the band-pass filter is applied to the acquired sound.",
        default=True,
    )
    min_freq: float = Field(
        description="The low cuttoff frequency of the filter (Hz).",
        ge=0,
        le=80000,
    )
    max_freq: float = Field(
        description="The high cuttoff frequency of the filter (Hz).",
        gt=0,
        le=80000,
    )


class ComputerSoundCard(BaseModel):
    soundcard_name: str = Field(
        description="The name of the soundcard being used in the calibration."
    )
    fs: int = Field(description="The sampling frequency of the soundcard (Hz).", gt=0)
    speaker: Speaker = Field(description="Indicates which speaker will be calibrated.")


class HarpSoundCard(BaseModel):
    serial_port: Annotated[
        str, StringConstraints(pattern=r"^((COM\d+)|(/dev/ttyUSB\d+))$")
    ] = Field(
        description='The serial port of the soundcard used for the calibration. The string should be of the format "COM?" in Windows and "/dev/ttyUSB?" in Linux, in which "?" is the serial port number.'
    )
    fs: Literal[96000, 192000] = Field(
        description="The sampling frequency of the soundcard (Hz)."
    )
    speaker: Speaker = Field(description="Indicates which speaker will be calibrated.")
    soundcard_id: Optional[
        Annotated[str, StringConstraints(pattern=r"^V\d.\d X\d{4}$")]
    ] = Field(
        description='The ID of the soundcard. If the soundcard is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.',
        default=None,
    )
    audio_amp_id: Optional[
        Annotated[str, StringConstraints(pattern=r"^V\d.\d X\d{4}$")]
    ] = Field(
        description='The ID of the audio amplifier. If the audio amplifier is a Harp device, the ID should be of the format "V?.? X????", in which "?" are numbers.',
        default=None,
    )


class NiDaq(BaseModel):
    fs: int = Field(
        description="The sampling frequency of the ADC (Hz).", gt=0, le=250000
    )
    device_id: int = Field(description="The NI-DAQ ID number.", ge=1)
    channel: int = Field(
        description="The analog input pin of the NI-DAQ being used.", gt=0, le=7
    )


class Moku(BaseModel):
    fs: int = Field(
        description="The sampling frequency of the ADC (Hz).", gt=0, le=500000
    )
    address: Annotated[
        str,
        StringConstraints(
            pattern=r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$|^[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$|^[0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,4}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){0,2}[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,3}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){0,3}[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,2}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){0,4}[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:)?[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}::[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}::$"
        ),
    ]
    channel: int = Field(
        description="The Moku channel used in the recordings.", ge=1, le=2
    )


class NoiseProtocolSettings(BaseModel):
    min_freq: float = Field(
        description="The minimum frequency of the noise spectrum (Hz).", gt=0, le=80000
    )
    max_freq: float = Field(
        description="The maximum frequency of the noise spectrum (Hz).", gt=0, le=80000
    )
    mic_factor: float = Field(
        description="The conversion factor of the microphone (V/Pa).", gt=0
    )
    reference_pressure: float = Field(description="The reference pressure (Pa).", gt=0)
    ramp_time: float = Field(
        description="The ramp time of the sounds used during the calibration process (s).",
        ge=0,
        default=0.005,
    )
    eq_filter: EQFilter = Field(
        description="The settings related to the EQ filter calculation. Noise calibration only!",
    )
    calibration: Calibration = Field(
        description="The settings used for the actual speaker calibration."
    )
    test: Optional[Test] = Field(
        description="The settings used for the calibration test.", default=None
    )
    filter: Filter = Field(
        description="The configuration parameters of the band-pass filter used.",
        default=Filter(
            filter_input=True, filter_acquisition=True, min_freq=5000, max_freq=20000
        ),
    )


class PureToneCalibration(Calibration):
    min_freq: float = Field(
        description="The minimum frequency to use in the pure tone calibration protocol (Hz).",
        gt=0,
        le=80000,
    )
    max_freq: float = Field(
        description="The maximum frequency to use in the pure tone calibration protocol (Hz).",
        gt=0,
        le=80000,
    )
    freq_steps: int = Field(
        description="The number of pure tones to use in the calibration.", gt=0
    )


class PureToneTest(Test):
    min_freq: float = Field(
        description="The minimum frequency to use in the pure tone calibration protocol (Hz).",
        gt=0,
        le=80000,
    )
    max_freq: float = Field(
        description="The maximum frequency to use in the pure tone calibration protocol (Hz).",
        gt=0,
        le=80000,
    )
    freq_steps: int = Field(
        description="The number of pure tones to use in the calibration.", gt=0
    )


class PureToneProtocolSettings(BaseModel):
    mic_factor: float = Field(
        description="The conversion factor of the microphone (V/Pa).", gt=0
    )
    reference_pressure: float = Field(description="The reference pressure (Pa).", gt=0)
    ramp_time: float = Field(
        description="The ramp time of the sounds used during the calibration process (s).",
        ge=0,
        default=0.005,
    )
    calibration: PureToneCalibration = Field(
        description="The settings used for the actual speaker calibration."
    )
    test: Optional[PureToneTest] = Field(
        description="The settings used for the calibration test.", default=None
    )
    filter: Filter = Field(
        description="The configuration parameters of the band-pass filter used.",
        default=Filter(
            filter_input=True, filter_acquisition=True, min_freq=5000, max_freq=20000
        ),
    )


class Paths(BaseModel):
    output: str = Field(
        description="The path to the output directory, where the output date will be saved."
    )
    eq_filter: Optional[Annotated[str, StringConstraints(pattern=r"\.npy$")]] = Field(
        description="The path to the EQ filter to be used in the calibration.",
        default=None,
    )
    calibration: Optional[Annotated[str, StringConstraints(pattern=r"\.npy$")]] = Field(
        description="The calibration parameters to be used to test the calibration.",
        default=None,
    )


class Config(BaseModel):
    soundcard: Union[HarpSoundCard, ComputerSoundCard] = Field(
        description="The soundcard details."
    )
    adc: Union[NiDaq, Moku] = Field(description="The ADC details.")
    protocol: Union[NoiseProtocolSettings, PureToneProtocolSettings]
    paths: Paths = Field(
        description="Contains paths to files that will be used in the calibration protocol."
    )


if __name__ == "__main__":
    with open("config/schemas/config-schema.json", "w") as file:
        json.dump(Config.model_json_schema(), file, indent=2)
