import numpy as np

REFERENCE_PRESSURE = 0.00002


def nextpow2(val: int):
    return np.ceil(np.log2(val))
