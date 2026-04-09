@echo off
echo ===================================================
echo     Library Management System - Startup Script
echo ===================================================
echo.

:: Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [!] First time setup detected!
    echo [1/4] Creating virtual environment...
    python -m venv venv
    
    echo [2/4] Installing requirements (this might take a minute)...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    
    echo [3/4] Initializing database and creating admin user...
    python seed.py
) else (
    echo [1/2] Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo [Final Step] Starting Flask server...
echo ---------------------------------------------------
echo The server is running! Opening your browser now...
echo Keep this black window open. Close it when you are done.
echo ---------------------------------------------------
echo.

:: Wait for a second then open the browser automatically
start http://127.0.0.1:5000

python app.py

pause
