@echo off
echo ============================================================
echo 🛡️  Trend Cybertron App Launcher (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found
    echo Please run this script from the TrendCybertronApp directory
    pause
    exit /b 1
)

echo ✅ Found app.py
echo.

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

REM Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not installed
    echo Please install Ollama from https://ollama.ai/
    pause
    exit /b 1
)

echo ✅ Ollama is installed
echo.

REM Start Ollama service
echo 🚀 Starting Ollama service...
start /B ollama serve
timeout /t 5 /nobreak >nul

REM Check if model is available
ollama list | findstr "llama-trendcybertron-primus-merged" >nul
if %errorlevel% neq 0 (
    echo ⚠️  Trend Cybertron model not found. Pulling...
    ollama pull llama-trendcybertron-primus-merged
    if %errorlevel% neq 0 (
        echo ❌ Failed to pull model
        pause
        exit /b 1
    )
)

echo ✅ Model is available
echo.

echo ✅ All prerequisites are ready!
echo.
echo 🌐 Starting the application...
echo 📱 The app will open in your default browser at http://localhost:8501
echo 🛑 Press Ctrl+C to stop the application
echo.

REM Run the Streamlit app
python -m streamlit run app.py

pause
