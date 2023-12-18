@echo off
set VENV_NAME=venv

REM Check if the virtual environment directory exists
if not exist "%VENV_NAME%" (
    echo Virtual environment not found. Did you run the setup script?
    exit /b
)

REM Activate the virtual environment
echo Activating the virtual environment...
call %VENV_NAME%\Scripts\activate

REM Run the assistant!
python local-assistant.py
