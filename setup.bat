@echo off
REM Sahanak Backend Setup Script for Windows

echo.
echo ============================================
echo  Sahanak Backend Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully

REM Check for .env file
echo.
echo [5/5] Checking environment configuration...
if not exist .env (
    echo WARNING: .env file not found
    echo Creating .env from template...
    (
        echo ANTHROPIC_API_KEY=your_api_key_here
        echo GEMINI_API_KEY=
        echo SERVER_HOST=0.0.0.0
        echo SERVER_PORT=8001
        echo BACKEND_HOST=0.0.0.0
        echo BACKEND_PORT=8001
        echo DATABASE_URL=sqlite:///sahanak.db
        echo FRONTEND_URL=http://localhost:8000
    ) > .env
    echo .env file created - please add your ANTHROPIC_API_KEY
) else (
    echo .env file found
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env and add your ANTHROPIC_API_KEY
echo 2. Run: python -m uvicorn main:app --reload
echo 3. Access API at: http://localhost:8001
echo 4. API Docs at: http://localhost:8001/docs
echo.
echo To activate the environment in future sessions:
echo   venv\Scripts\activate.bat
echo.
echo Press any key to exit...
pause >nul
