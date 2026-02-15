@echo off
title Installing Autoclicker Dependencies
echo Checking Python...

python --version >nul 2>&1 || py --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Download from python.org.
    pause
    exit /b 1
)

echo Installing pyautogui and pynput...
pip install pyautogui pynput --user --upgrade
py -m pip install pyautogui pynput --user --upgrade

echo Verifying...
python -c "import pyautogui; print('pyautogui OK')" 2>nul || py -c "import pyautogui; print('pyautogui OK')" 2>nul
if errorlevel 1 (
    echo Install failed. Try as Administrator.
    pause
    exit /b 1
)

cls
echo Installation successful! Run runner.bat.
pause
