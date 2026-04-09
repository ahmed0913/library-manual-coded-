@echo off
echo ===================================================
echo     Library Management System - Startup Script
echo ===================================================
echo.

:: Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found!
    echo Please make sure you ran 'python -m venv venv' and installed the requirements.
    pause
    exit /b
)

:: Activate the virtual environment and run the app
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/2] Starting Flask server...
echo.
echo ---------------------------------------------------
echo The server is running! Opening your browser now...
echo Keep this black window open. Close it when you are done.
echo ---------------------------------------------------
echo.

:: Wait for a second then open the browser automatically
start http://127.0.0.1:5000

python app.py

pause
