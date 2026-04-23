@echo off
chcp 65001 >nul
title System Health Monitor

echo.
echo  +====================================================+
echo  ^|       System Health Monitor - Launcher            ^|
echo  +====================================================+
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.12:
    echo          https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

if not exist ".env" (
    if exist ".env.example" (
        echo  [WARN] .env not found. Copying from .env.example...
        copy ".env.example" ".env" >nul
        echo  [!] Please set your DISCORD_WEBHOOK_URL in .env before continuing.
        echo.
        notepad .env
        echo.
        echo  Press any key once you have saved .env...
        pause >nul
    ) else (
        echo  [WARN] No .env file found. Default config will be used.
        echo.
    )
)

echo  [*] Checking dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  [ERROR] Failed to install dependencies. Check requirements.txt.
    pause
    exit /b 1
)
echo  [OK] All dependencies are ready.
echo.

echo  [*] Starting monitor...
echo  [*] Press CTRL+C to stop.
echo  ====================================================
echo.

python monitor.py

echo.
echo  [!] Monitor stopped.
pause