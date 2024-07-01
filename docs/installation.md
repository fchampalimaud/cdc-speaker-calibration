# Installation
For now, the setup was only tested in Windows and it still has some rough edges. The limitations for the remaining operating systems are unknown.

## Prerequisites
- Install the firmware for the Harp SoundCard (follow the instructions in the [device's repository](https://github.com/harp-tech/device.soundcard)). It is recommended that the Harp SoundCard GUI is installed (although it is not absolutely necessary).
- Install the [NI-DAQ driver](https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710).

## Installation
1. Clone the repository (or download it for non-git users).
2. Change the execution policy to allow local PowerShell scripts to run without signing and click in "Apply". This option can be found in the "Developer Settings" of Windows 10/11.
3. Run `setup.ps1`.
4. Copy `toSoundCard.exe` and `LibUsbDotNet.dll` from `C:\Users\<username>\Documents\HarpSoundCard\Interface` to the `assets` directory of the project directory. The Harp Sound Card GUI must be installed.