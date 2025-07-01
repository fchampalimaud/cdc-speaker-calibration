import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional

import nidaqmx
import numpy as np
from moku.instruments import Datalogger
from nidaqmx.constants import READ_ALL_AVAILABLE, AcquisitionType, TerminalConfiguration

from speaker_calibration.sound import Sound
from speaker_calibration.utils.decorators import greater_than, validate_range


class RecordingDevice(ABC):
    """
    The class representing an abstract recording device from which to implement specific ones.

    Attributes
    ----------
    fs : float | int
        The sampling frequency of the recording device.
    """

    fs: float | int

    def __init__(self, fs: float | int):
        self.fs = fs

    @abstractmethod
    def record_signal(self):
        """
        Records the desired signal. _This is the abstract method to be implemented for the specific recording devices that derive from this abstract class._
        """
        pass


class NiDaq(RecordingDevice):
    """
    This class is an implementation of the RecordingDevice class for the Ni-DAQ.

    Attributes
    ----------
    device_id : int
        The device ID of the Ni-DAQ being used.
    """

    device_id: int

    @greater_than("device_id", 1)
    @validate_range("fs", 0, 250000)
    def __init__(self, device_id: int, fs: int = 250000):
        super().__init__(fs)
        self.device_id = device_id

    @validate_range("ai_pin", 0, 7)
    def record_signal(
        self,
        duration: float,
        ai_pin: int = 1,
        start_event: Optional[threading.Event] = None,
        result: Optional[list] = None,
        filename: str = "file",
    ):
        """
        Records the signal with the NI-DAQ.

        Parameters
        ----------
        duration : float
            The duration of the acquisition (s).
        ai_pin : int, optional
            The analog input pin to acquire from.
        start_event : thread.Event, optional
            A thread event used to synchronize the start of the sound with the start of the recording. If `start_event` is not provided, the sound will play as soon as possible.
        result : list, optional
            A list to which the acquired signal will be appended.
        filename : str, optional
            The path to the file that will be saved with the acquired signal.
        """
        with nidaqmx.Task() as ai_task:
            # Configure the analog input responsible for the sound acquisition
            ai_task.ai_channels.add_ai_voltage_chan(
                "Dev" + str(self.device_id) + "/ai" + str(ai_pin),
                terminal_config=TerminalConfiguration.RSE,
            )

            ai_task.timing.cfg_samp_clk_timing(
                self.fs,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=int(self.fs * duration),
            )

            # Wait for the event if it exists
            if start_event is not None:
                start_event.wait()

            # Start the analog acquisition
            ai_task.start()
            time.sleep(duration)

            recorded_signal = ai_task.read(READ_ALL_AVAILABLE)
            ai_task.stop()

            acquired_signal = Sound(
                signal=np.array(recorded_signal),
                time=np.linspace(0, duration, int(self.fs * duration)),
            )

            # Append the acquired signal if a result list was passed to the function
            if result is not None:
                result.append(acquired_signal)

        # Save the acquired signal to a CSV file
        np.savetxt(
            filename + ".csv",
            np.stack((acquired_signal.time, acquired_signal.signal), axis=1),
            delimiter=",",
        )

        return acquired_signal


class Moku(RecordingDevice):
    """
    This class is an implementation of the RecordingDevice class for a Moku device.

    Attributes
    ----------
    address : int
        The address of the Moku device being used.
    """

    address: str

    @validate_range("fs", 0, 500000)
    def __init__(self, address: str, fs: int = 500000):
        super().__init__(fs)
        self.address = "[" + address + "]"

    @validate_range("channel", 0, 1)
    def record_signal(
        self,
        duration: float,
        channel: int = 1,
        start_event: Optional[threading.Event] = None,
        result: Optional[list] = None,
        filename: str = "file",
    ):
        """
        Records the signal with a Moku device.

        Parameters
        ----------
        duration : float
            The duration of the acquisition (s).
        channel : int, optional
            The channel to acquire from.
        start_event : thread.Event, optional
            A thread event used to synchronize the start of the sound with the start of the recording. If `start_event` is not provided, the sound will play as soon as possible.
        result : list, optional
            A list to which the acquired signal will be appended.
        filename : str, optional
            The path to the file that will be saved with the acquired signal.
        """
        # Connect to Moku:Go
        adc = Datalogger(self.address, force_connect=True)

        try:
            # Configure the frontend
            adc.set_frontend(
                channel=channel, impedance="1MOhm", coupling="AC", range="10Vpp"
            )
            # Set the sampling frequency of the Moku device
            adc.set_samplerate(self.fs)

            # Set the acquisition mode
            adc.set_acquisition_mode(mode="Precision")

            # Wait for the event if it exists
            if start_event is not None:
                start_event.wait()

            # Stop an existing log, if any, then start a new one. 10 seconds of both channels
            logFile = adc.start_logging(duration=duration, trigger_source="Input1")

            # Track progress percentage of the data logging session
            is_logging = True
            while is_logging:
                # Wait for the logging session to progress by sleeping 1 second
                time.sleep(1)
                # Get current progress percentage and print it out
                progress = adc.logging_progress()
                remaining_time = int(progress["time_remaining"])
                is_logging = not progress["complete"]
                print(f"Remaining time {remaining_time} seconds")

            # Download log from Moku
            adc.download("persist", logFile["file_name"], filename + ".li")

            # Use mokucli to convert this .li file to .csv
            os.system("mokucli convert " + filename + ".li --format=csv")
            signal_array = np.loadtxt(filename + ".csv", comments="%", delimiter=",")

            acquired_signal = Sound(
                signal=np.array([x[1] for x in signal_array]),
                time=np.array([x[0] for x in signal_array]),
            )

            # Append the acquired signal if a result list was passed to the function
            if result is not None:
                result.append(acquired_signal)

        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            # Close the connection to the Moku device
            # This ensures network resources and released correctly
            adc.relinquish_ownership()

        return acquired_signal
