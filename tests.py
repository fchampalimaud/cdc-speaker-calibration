import numpy as np

# import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from speaker_calibration.classes import Signal

import time


def test_calibration():
    db_array = np.loadtxt("output/pure_tones.csv", delimiter=",")
    db_array = db_array.flatten()
    attenuations = np.linspace(0.1, 1, 5)
    freq_array = np.logspace(
        np.log10(5000),
        np.log10(20000),
        5,
    )

    freq_array, attenuations = np.meshgrid(freq_array, attenuations, indexing="ij")
    freq_array = freq_array.flatten()
    attenuations = attenuations.flatten()

    test_freq = [5000, 10000, 15000]
    test_db = [50, 55]
    freq, db = np.meshgrid(test_freq, test_db, indexing="ij")
    freq = freq.flatten()
    db = db.flatten()

    atti = griddata((freq_array, db_array), attenuations, (freq, db), method="linear")

    print(atti)

    measured_db = np.zeros(freq.size)
    for i in range(measured_db.size):
        signal = Signal(
            0.15,
            192000,
            sound_type="Pure Tone",
            amplification=0.2 * atti[i],
            ramp_time=0.005,
            freq=freq[i],
            mic_factor=10,
            reference_pressure=0.00002,
        )
        time.sleep(1)
        signal.load_sound()
        signal.record_sound(250000)
        signal.db_spl_calculation()
        print("desired dB SPL: " + str(db[i]))
        print("dB SPL: " + str(signal.db_spl))
        measured_db[i] = signal.db_spl

    print(measured_db)


test_calibration()
