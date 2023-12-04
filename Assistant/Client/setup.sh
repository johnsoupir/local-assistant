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

sudo apt install ffmpeg python-pip


# Download models
echo "-------------------- DOWNLOAD MODELS --------------------"
echo ""
echo "Now we are going to download the STT models. Hang tight."
echo ""
echo "REMINDER, ACTUALLY ADD THIS"

# Completed installation!
echo "-------------------- INSTALLED!!! --------------------"
echo ""
echo "Now run ./start.sh and be amazed!"
echo ""