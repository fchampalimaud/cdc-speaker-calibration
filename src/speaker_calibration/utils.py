from enum import Enum

REFERENCE_PRESSURE = 0.00002


class Speaker(Enum):
    LEFT = 1
    RIGHT = 2
    BOTH = 3


class SweepType(Enum):
    CALIBRATION = 1
    TEST = 2
