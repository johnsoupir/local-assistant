#!/bin/bash
VENV_NAME="venv"

#Install python reqs
echo "-------------------- PYTHON PACKAGES --------------------"
echo ""
echo "Now installing python packages. Sit back and grab coffee."
echo ""

# Check if the virtual environment directory exists
if [ ! -d "$VENV_NAME" ]; then
    echo "Virtual environment not found. Creating one now..."
    python3 -m venv $VENV_NAME
fi
# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_NAME/bin/activate
# Install the packages...
pip install -r requirements.txt

#Install needed system packages
echo "-------------------- SYSTEM PACKAGES --------------------"
echo ""
echo "Python pydub requires ffmpeg to be installed."
echo "Please grant sudo for \"apt install ffmpeg\""
echo ""

packages=("python3" "python3-pip" "ffmpeg")

packages_to_install=0

# Do we need packages?
for package in "${packages[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        packages_to_install=1
        break
    fi
done

# For systems not using apt
if ! command -v apt &> /dev/null; then
    echo "Error: This system does not have apt package manager installed."
    if [ $packages_to_install -eq 1 ]; then
        echo "Please install the following packages manually:"
        for package in "${packages[@]}"; do
            echo "  - $package"
        done
    else
        echo "No package installations are needed. Continuing with other tasks..."
    fi
    exit 1
fi

# For systems with apt
if [ $packages_to_install -eq 1 ]; then
    echo "Installing required packages using apt..."
    sudo apt-get update
    sudo apt-get install -y "${packages[@]}"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install one or more packages. Please install them manually."
        exit 1
    else
        echo "All required packages are installed."
    fi
fi

# Download models
echo "-------------------- DOWNLOAD MODELS --------------------"
echo ""
echo "Now we are going to download the STT models. Hang tight."
echo ""
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip
echo "Decompress model..."
unzip vosk-model-en-us-0.42-gigaspeech.zip
rm vosk-model-en-us-0.42-gigaspeech.zip


# Completed installation!
echo "-------------------- INSTALLED!!! --------------------"
echo ""
echo "Now run ./start.sh and be amazed!"
echo ""