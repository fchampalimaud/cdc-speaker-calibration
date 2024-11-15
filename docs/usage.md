# Usage

1. Connect the "+" terminal of the AI1 pin from the Ni-DAQ to the microphone's conditioner (amplifier) and the P1.0 pin (also from the Ni-DAQ) to the Harp SoundCard's IN0 pin (don't forget the ground pins!). **WARNING**: connect the Ni-DAQ and the Harp SoundCard to different hubs from the computer, because both devices compete for bandwidth when the computer is loading a sound to the SoundCard, which sometimes leads to SoundCard disconnects.
2. Assemble some sort of structure which guarantees the desired distance between the speaker and the microphone that is going to be used for calibrating the speakers.
3. Use the following settings for the microphone's conditioner:
    - Microphone factor: 418.87 mV/Pa
4. Run `main.py`. After configuring the desired protocol, click on the `Run` button.

The calibration results should be found in the `/output` directory after the calibration finishes.