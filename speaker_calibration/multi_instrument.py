# In Python, you specify the configuration by creating a MultiInstrument object
from moku.instruments import Datalogger, MultiInstrument, WaveformGenerator

# import os
# import time
# import subprocess
# import numpy as np

mim = MultiInstrument("[fe80:0000:0000:0000:7269:79ff:feb9:62a2%25]", force_connect=True, platform_id=2)

wg = mim.set_instrument(1, WaveformGenerator)
dl = mim.set_instrument(2, Datalogger)

mim.set_connections(
    [
        {"source": "Slot1OutA", "destination": "Slot2InB"},
        {"source": "Slot1OutA", "destination": "Output1"},
        {"source": "Input1", "destination": "Slot2InA"},
    ]
)

print(mim.get_connections())

mim.set_frontend(1, impedance="1MOhm", coupling="DC", attenuation="-14dB")
mim.set_output(1, "0dB")
mim.sync()

dl.set_samplerate(250000)
logFile = dl.start_logging(duration=3, trigger_source="Input2", trigger_level=2.5)
wg.generate_waveform(channel=1, type="DC", dc_level=5)
wg.generate_waveform(channel=1, type="Off")

# is_logging = True
# while is_logging:
#     # Wait for the logging session to progress by sleeping 0.5sec
#     time.sleep(1)
#     # Get current progress percentage and print it out
#     progress = dl.logging_progress()
#     remaining_time = int(progress["time_remaining"])
#     is_logging = not progress["complete"]
#     print(f"Remaining time {remaining_time} seconds")

# dl.download("persist", logFile["file_name"], os.path.join(os.getcwd(), "file.li"))
# subprocess.run("./liconvert-windows/liconvert --npy file.li")

# array = np.load("file.npy")

# t = np.array([x[0] for x in array])
# v = np.array([x[1] for x in array])
