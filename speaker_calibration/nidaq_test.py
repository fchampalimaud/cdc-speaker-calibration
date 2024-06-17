"""Example of analog input voltage acquisition.

This example demonstrates how to acquire a finite amount
of data using the DAQ device's internal clock.
"""

import matplotlib.pyplot as plt
import nidaqmx
import numpy as np
from nidaqmx.constants import READ_ALL_AVAILABLE, AcquisitionType

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.timing.cfg_samp_clk_timing(250000.0, sample_mode=AcquisitionType.FINITE, samps_per_chan=25000)

    a = task.read(READ_ALL_AVAILABLE)

plt.plot(a)
plt.show()

# print("Acquired data: [" + ", ".join(f"{value:f}" for value in data) + "]")
