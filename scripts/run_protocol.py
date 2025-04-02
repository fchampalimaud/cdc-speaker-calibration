import yaml
from speaker_calibration.protocol import Calibration
from speaker_calibration.settings import Settings

with open("config/settings.yml", "r") as file:
    data = yaml.safe_load(file)

settings = Settings(**data)
calibration = Calibration(settings)

calibration.noise_calibration()
