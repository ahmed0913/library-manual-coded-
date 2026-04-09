@echo off
title Library Management System
color 0A

echo ===================================================
echo     Library Management System - Startup Script
echo ===================================================
echo.

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    pause
    exit /b
)

:: Check if the virtual environment exists
if exist "venv\Scripts\activate.bat" goto START_SERVER

echo [!] First time setup detected!
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing requirements ... This might take a minute ...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to install requirements!
    pause
    exit /b
)

echo [4/4] Initializing database and creating admin user...
python seed.py

:START_SERVER
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ===================================================
echo [SUCCESS] Starting Flask server...
echo ---------------------------------------------------
echo The website will open in your browser automatically.
echo Keep this black window open. Close it when you are done.
echo ---------------------------------------------------
echo.

:: Wait for a second then open the browser automatically
start http://127.0.0.1:5000

:: Run the app
python app.py

:: If app.py crashes, keep the window open so we can see the error
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] The server stopped unexpectedly!
    pause
)
