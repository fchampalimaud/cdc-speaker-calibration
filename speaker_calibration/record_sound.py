import os
import subprocess
import time

import numpy as np
from moku.instruments import Datalogger


def record_sound(fs: float, duration: float):
    # Connect to your Moku by its ip address using Datalogger('192.168.###.###')
    # or by its serial number using Datalogger(serial=123)
    adc = Datalogger("[fe80:0000:0000:0000:7269:79ff:feb9:62a2%25]", force_connect=True)

    try:
        # Configure the frontend
        adc.set_frontend(channel=1, impedance="1MOhm", coupling="DC", range="50Vpp")
        adc.enable_input(2, False)
        adc.generate_waveform(channel=2, type="Off")
        # Log 100 samples per second
        adc.set_samplerate(fs)
        # adc.set_acquisition_mode(mode="Precision")

        # Stop an existing log, if any, then start a new one. 10 seconds of both
        # channels
        adc.generate_waveform(channel=1, type="DC", dc_level=5)
        # print("Play")
        logFile = adc.start_logging(duration=duration, trigger_source="Input1")
        # print("Acquisition Started")
        adc.generate_waveform(channel=1, type="Off")

        # Track progress percentage of the data logging session
        is_logging = True
        while is_logging:
            # Wait for the logging session to progress by sleeping 0.5sec
            time.sleep(1)
            # Get current progress percentage and print it out
            progress = adc.logging_progress()
            remaining_time = int(progress["time_remaining"])
            is_logging = not progress["complete"]
            print(f"Remaining time {remaining_time} seconds")

        # Download log from Moku, use liconverter to convert this .li file to .csv
        adc.download("persist", logFile["file_name"], os.path.join(os.getcwd(), "file.li"))
        subprocess.run("./liconvert-windows/liconvert --npy file.li")

        array = np.load("file.npy")

        t = np.array([x[0] for x in array])
        v = np.array([x[1] for x in array])

    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        # Close the connection to the Moku device
        # This ensures network resources and released correctly
        adc.relinquish_ownership()

    return v, t
