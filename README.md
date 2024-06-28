# cdc-speaker-calibration

This repository contains the Python code used during the speaker calibration protocol. 

For now, the setup was only tested in Windows and it still has some rough edges. The limitations for the remaining operating systems are unknown.

The code written for this project was inspired by a MATLAB version of a similar setup written by Juan Castiñeiras. The MATLAB code can be found in the `matlab` folder, in which the main file is `Calibrate.m`.

## Usage
### Prerequisites
- Install the firmware for the Harp SoundCard (follow the instructions in the [device's repository](https://github.com/harp-tech/device.soundcard)).
- Install the [NI-DAQ driver](https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710).
- Connect the AI1 pin from the Ni-DAQ to the microphone's conditioner and the P1.0 pin (also from the Ni-DAQ) to the Harp SoundCard's IN0 pin (**WARNING**: don't forget the ground pins!).

### Installation
1. Clone the repository (or download it for non-git users).
2. Change the execution policy to allow local PowerShell scripts to run without signing and click in "Apply". This option can be found in the "Developer Settings" of Windows 10/11.
3. Run `setup.ps1`.

## Future Work
- Documentation (in spite of the code being almost all commented)
- Moku:Go support

## Development
When using Visual Studio Code, it is recommended that you install the extensions from `.vscode/extensions.json`.

To add dependencies, run `poetry add` instead of `pip install`.

### Note
Throughout the code, it is possible to find comments/documentation strings containing the "StC" acronym, which stands for "Subject to Change".