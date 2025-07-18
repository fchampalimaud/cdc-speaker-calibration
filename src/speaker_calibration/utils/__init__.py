import numpy as np


def nextpow2(val: int):
    return np.ceil(np.log2(val))
