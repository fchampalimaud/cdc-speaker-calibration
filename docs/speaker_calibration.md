# Speaker Calibration Protocol

## Protocol
1. Connect the "+" terminal of the AI1 pin from the Ni-DAQ to the microphone's conditioner (amplifier) and the P1.0 pin (also from the Ni-DAQ) to the Harp SoundCard's IN0 pin (**WARNING**: don't forget the ground pins!).
2. Assemble some sort of structure which guarantees the desired distance between the speaker and the microphone that is going to be used for calibrating the speakers.
3. Use the following settings for the microphone's conditioner:
    - Transducer Supply > Voltage Polarization: 200 V
    - Transducer Set-up > Sensitivity: 4 mV/Pa
    - Amplifier: 10 V/Pa
4. Change the `hardware.yml` and `settings.yml` files that are located in the `config` directory if needed.
5. Run `speaker_calibration/main.py`.

## Known problems
At the moment, the results obtained with the speaker calibration setup are reliable and the code works (it can be improved, though). However, there are two issues that happen from time to time which remain unsolved:

- The soundcard disconnects in the middle of the calibration. It might be related to the call of the `toSoundCard.exe` or the Ni-DAQ or a mix of the two (not confirmed yet).
- When the soundcard is first connected to the computer, the first sound which should be triggered by the Ni-DAQ doesn't play. It is not certain if the soundcard doesn't receive the first harp messages before the Ni-DAQ trigger or if it doesn't receive the trigger itself.