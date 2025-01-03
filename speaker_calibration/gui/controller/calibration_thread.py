from threading import Thread
from speaker_calibration.protocol.calibration_protocols import noise_calibration


class AsyncCalibration(Thread):
    def __init__(
        self,
        hardware,
        input_parameters,
        inverse_filter,
        calibration_parameters,
        callback=None,
    ):
        super().__init__()
        self.hardware = hardware
        self.input_parameters = input_parameters
        self.inverse_filter = inverse_filter
        self.calibration_parameters = calibration_parameters
        self.callback = callback

    def run(self):
        self.inverse_filter, self.calibration_parameters = noise_calibration(
            self.hardware,
            self.input_parameters,
            self.inverse_filter,
            self.calibration_parameters,
            self.callback,
        )
