import threading
import time
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from pyharp.messages import HarpMessage
from speaker_calibration.recording import NiDaq
from speaker_calibration.soundcards import HarpSoundCard

SERIAL_PORT = "COMx"


def record_sound(
    desired_db: float,
    index: Literal[2, 4, 6, 8, 10],
    calibration_path: str,
    filename: str = "sound",
):
    soundcard = HarpSoundCard(SERIAL_PORT)
    adc = NiDaq(1)
    calibration = np.load(calibration_path)

    att = (-20 * (desired_db - calibration[1]) / calibration[0]) * 10
    soundcard.device.send(HarpMessage.WriteU16(34, int(att)).frame, False)
    soundcard.device.send(HarpMessage.WriteU16(35, int(att)).frame, False)

    # Create the result list to pass to the recording thread
    result = []

    # Create the start event and the threads that will play and record the sound
    start_event = threading.Event()
    play_thread = threading.Thread(
        target=soundcard.play, kwargs={"start_event": start_event}
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


record_sound(
    desired_db=50,
    index=2,
    calibration_path=r"C:/Users/RenartLab/Desktop/cdc-speaker-calibration/output/250819_142853",
)
