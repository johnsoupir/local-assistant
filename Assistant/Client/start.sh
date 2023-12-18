#!/bin/bash

VENV_NAME="venv"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_NAME" ]; then
    echo "Virtual environment not found. Did you run the setup script?"
    exit
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_NAME/bin/activate

# Run the assistant!
./local-assistant.py