"""Example of analog input voltage acquisition.

This example demonstrates how to acquire a finite amount
of data using the DAQ device's internal clock.
"""

import nidaqmx
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE, TimestampEvent
import numpy as np
import time
import matplotlib.pyplot as plt

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.timing.cfg_samp_clk_timing(250000.0, sample_mode=AcquisitionType.FINITE, samps_per_chan=25000)

    # b = task.wait_for_valid_timestamp(TimestampEvent.START_TRIGGER)
    a = task.read(READ_ALL_AVAILABLE)

# print(b)
plt.plot(a)
plt.show()

# print("Acquired data: [" + ", ".join(f"{value:f}" for value in data) + "]")
