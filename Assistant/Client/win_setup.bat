@echo off
set VENV_NAME=venv

echo -------------------- PYTHON PACKAGES --------------------
echo.
echo Now installing python packages. Sit back and grab coffee.
echo.

REM Check if the virtual environment directory exists
if not exist "%VENV_NAME%" (
    echo Virtual environment not found. Creating one now...
    python -m venv %VENV_NAME%
)

REM Activate the virtual environment
echo Activating the virtual environment...
call %VENV_NAME%\Scripts\activate

REM Install the packages...
pip install -r requirements.txt

echo -------------------- SYSTEM PACKAGES --------------------
echo.
echo Python pydub requires ffmpeg to be installed.
echo Please manually install ffmpeg if not already installed.
echo.

REM System package installation is platform specific and cannot be done directly in a batch script

echo -------------------- DOWNLOAD MODELS --------------------
echo.
echo Now we are going to download the STT models. Hang tight.
echo.
echo REMINDER, ACTUALLY ADD THIS

REM Completed installation!
echo -------------------- INSTALLED!!! --------------------
echo.
echo Now run start.bat and be amazed!
echo.
