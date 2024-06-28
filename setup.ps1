Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Check if Python is already installed
if (!(Get-Package -Name Python -ErrorAction SilentlyContinue)) {
    choco install python312 -y
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# Check if pipx is already installed
if (!(Get-Command pipx -ErrorAction SilentlyContinue)) {
    python -m pip install pipx
    pipx ensurepath
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# Check if Poetry is already installed
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Poetry using pipx..."
    pipx install poetry
}

# Create a new Poetry environment if it doesn't exist
if (!(Get-ChildItem -Path poetry.lock -ErrorAction SilentlyContinue)) {
    Write-Host "Creating a new Poetry environment..."
    poetry env use 3.12
}

# Install packages from pyproject.toml
Write-Host "Installing packages from pyproject.toml..."
poetry install
