# cdc-speaker-calibration

This repository contains the Python code used during the speaker calibration protocol.

## Usage
<!-- _To be added in the future._ -->
1. Install the firmware for the Harp SoundCard (follow the instructions in the [device's repository](https://github.com/harp-tech/device.soundcard)).
2. Connect the AI1 pin from the Ni-DAQ to the microphone's conditioner and the P1.0 pin (also from the Ni-DAQ) to the Harp SoundCard's IN0 pin (**WARNING**: don't forget the ground pins!).
3. Change the calibration settings according to the needs by changing the `.yml` files that are inside the `config` folder. The `hardware.yml` files contains settings related to the hardware being calibrated while the `settings.yml` are the protocol-specific settings.
4. Run the `main.py` script. The output files are located at the `output` folder.

## Future Work
- Documentation (in spite of the code being almost all commented)
- Add pure tones calibration
- Moku:Go support
- Use Welch's Method to calculate the fft

## Development
To start contributing to the project, follow the steps:

1. Install Python 3.12.3.
2. Install `poetry`:

    ```
    pip install pipx
    pipx install poetry
    ```

3. Clone the repository.
4. Run `poetry init` inside the project's folder.
5. Create a virtual environment and install the dependencies:

    ```
    poetry shell
    poetry install
    ```

When using Visual Studio Code, it is recommended that you install the extensions from `.vscode/extensions.json`.

To add dependencies, run `poetry add` instead of `pip install`.

### Note
Throughout the code, it is possible to find comments/documentation strings containing the "StC" acronym, which stands for "Subject to Change".