from pydantic import BaseModel, Field
from typing import Optional, Union
from enum import Enum


class SoundType(Enum):
    NOISE = 1
    PURE_TONE = 2


class InputParameters(BaseModel):
    sound_type: SoundType
    fs_adc: int
    ramp_time: float
    amplification: float
    mic_factor: float
    reference_pressure: float
    freq_min: float
    freq_max: float
    noise: dict
    pure_tones: dict
