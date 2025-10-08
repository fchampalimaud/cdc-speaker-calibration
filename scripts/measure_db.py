import threading
import time
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from speaker_calibration.recording import NiDaq
from speaker_calibration.soundcards import HarpSoundCard

SERIAL_PORT = "COMx"


def measure_db(
    abl: float,
    ild: float,
    index: Literal[2, 4, 6, 8, 10],
    calibration_left: str,
    calibration_right: str,
    filename: str = "sound",
):
    soundcard = HarpSoundCard(SERIAL_PORT)
    adc = NiDaq(1)
    left_cal = np.load(calibration_left)
    right_cal = np.load(calibration_right)

    db_left = abl - ild / 2
    db_right = abl + ild / 2

    att_left = (-20 * (db_left - left_cal[1]) / left_cal[0]) * 10
    soundcard.device.write_attenuation_left(int(att_left))

    att_right = (-20 * (db_right - right_cal[1]) / right_cal[0]) * 10
    soundcard.device.write_attenuation_right(int(att_right))

    # Create the result list to pass to the recording thread
    result = []

    # Create the start event and the threads that will play and record the sound
    start_event = threading.Event()
    play_thread = threading.Thread(
        target=soundcard.play, kwargs={"index": index, "start_event": start_event}
    )
    record_thread = threading.Thread(
        target=adc.record_signal,
        args=[10],
        kwargs={
            "start_event": start_event,
            "result": result,
            "filename": str(filename)[:-4] + "_rec",
        },
    )

    # Start both threads
    record_thread.start()
    play_thread.start()

    # Activates the event in order to synchronize the sound being played with the acquisition
    time.sleep(0.1)
    start_event.set()
    record_thread.join()

    print(result[0].calculate_db_spl(mic_factor=0.41887))

    freq, fft = result[0].fft_welch(0.005)

    plt.plot(freq, fft)
    plt.show()


measure_db(
    abl=50,
    ild=0,
    index=2,
    calibration_left=r"C:/Users/RenartLab/Desktop/cdc-speaker-calibration/output/250819_142853/calibration_parameters.npy",
    calibration_right=r"C:/Users/RenartLab/Desktop/cdc-speaker-calibration/output/250819_142853/calibration_parameters.npy",
)
