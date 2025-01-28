# Checks if the output directory already exists
if (!(Test-Path ".\output")) { 
    New-Item -ItemType Directory -Path "output" 
}

# Checks if the assets directory already exists
if (!(Test-Path ".\assets")) { 
    New-Item -ItemType Directory -Path "assets" 
}

if (!(Test-Path ".\assets\toSoundCard.exe")) {
    Invoke-WebRequest "https://github.com/fchampalimaud/cdc-speaker-calibration/releases/download/v0.3.0-alpha/toSoundCard.exe" -OutFile ".\assets\toSoundCard.exe"
}

if (!(Test-Path ".\assets\LibUsbDotNet.dll")) {
    Invoke-WebRequest "https://github.com/fchampalimaud/cdc-speaker-calibration/releases/download/v0.3.0-alpha/LibUsbDotNet.dll" -OutFile ".\assets\LibUsbDotNet.dll"
}

# Check if uv is already installed
if (!(Get-Command -Name uv -ErrorAction SilentlyContinue)) {
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}
