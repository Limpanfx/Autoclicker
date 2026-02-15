@echo off
title Autoclicker
echo Starting autoclicker.py...

py autoclicker.py
if errorlevel 1 (
    echo Failed to run. Run install_deps.bat first.
    pause
)
pause