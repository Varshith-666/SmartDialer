@echo off
title SmartDialer Live Engine
cd /d "%~dp0"
echo =========================================================
echo    SmartDialer - Progressive ^& Predictive Outbound Engine
echo =========================================================
echo.
echo Verifying Python environment...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH! Please ensure Python is installed.
    pause
    exit /b %errorlevel%
)
echo.
echo Installing requirements (if missing)...
pip install -r requirements.txt
echo.
echo Launching SmartDialer live server...
python run_server.py
pause
