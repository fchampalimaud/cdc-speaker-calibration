# cdc-speaker-calibration

This repository contains the Python code used during the speaker calibration protocol. 

For now, the setup was only tested in Windows and it still has some rough edges. The limitations for the remaining operating systems are unknown.

## Usage

Run the `Run.cmd` file to open the GUI app. Then modify the settings on the right panel according to your calibration needs and hit the `Run` button.

> [!NOTE]
> If it's your first time running this project, check the [prerequisites](#prerequisites) and the [installation](#installation) sections.

### Prerequisites
- Install the firmware for the Harp SoundCard (follow the instructions in the [device's repository](https://github.com/harp-tech/device.soundcard)).
- Install the [NI-DAQ driver](https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710).
- Connect the AI1 pin from the Ni-DAQ to the microphone's conditioner (it's possible to use a different analog input pin, but that's the one used by default).

### Installation
1. Clone the repository (or download it for non-git users).
2. Run `Setup.cmd`.

## Development
When using Visual Studio Code, it is recommended that you install the extensions from `.vscode/extensions.json`.

To add dependencies, run `uv add` instead of `pip install`.

### Documentation
To develop the documentation of the project, run `uv sync` in the command line. Then activate the virtual environment by running the `.venv/Scripts/activate.ps1` file.

After installing the development dependencies and activating the virtual environment, run `mkdocs serve` to see the documentation locally at address [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
