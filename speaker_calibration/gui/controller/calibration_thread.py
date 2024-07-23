from threading import Thread
from speaker_calibration.main import noise_calibration


class AsyncCalibration(Thread):
    def __init__(
        self,
        fs,
        input_parameters,
        hardware,
        calibration_factor,
        fit_parameters,
        min_db: float = 40,
        max_db: float = 60,
        test_steps: int = 5,
        speaker_filter: bool = True,
        calibration_curve: bool = True,
        test_calibration: bool = True,
        callback=None,
    ):
        super().__init__()
        self.fs = fs
        self.input_parameters = input_parameters
        self.hardware = hardware
        self.calibration_factor = calibration_factor
        self.fit_parameters = fit_parameters
        self.min_db = min_db
        self.max_db = max_db
        self.test_steps = test_steps
        self.speaker_filter = speaker_filter
        self.calibration_curve = calibration_curve
        self.test_calibration = test_calibration
        self.callback = callback

    def run(self):
        self.inverse_filter, self.calibration_parameters = noise_calibration(
            self.fs,
            self.input_parameters,
            self.hardware,
            self.calibration_factor,
            self.fit_parameters,
            self.min_db,
            self.max_db,
            self.test_steps,
            self.speaker_filter,
            self.calibration_curve,
            self.test_calibration,
            self.callback,
        )
