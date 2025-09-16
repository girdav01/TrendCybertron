#!/bin/bash

echo "============================================================"
echo "🛡️  Trend Cybertron App Launcher (Unix)"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version is installed"
echo

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found"
    echo "Please run this script from the TrendCybertronApp directory"
    exit 1
fi

echo "✅ Found app.py"
echo

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "Please install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama is installed"
echo

# Start Ollama service
echo "🚀 Starting Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 5
fi

echo "✅ Ollama service is running"
echo

# Check if model is available
if ! ollama list | grep -q "llama-trendcybertron-primus-merged"; then
    echo "⚠️  Trend Cybertron model not found. Pulling..."
    ollama pull llama-trendcybertron-primus-merged
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull model"
        exit 1
    fi
fi

echo "✅ Model is available"
echo

echo "✅ All prerequisites are ready!"
echo
echo "🌐 Starting the application..."
echo "📱 The app will open in your default browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo

# Run the Streamlit app
python3 -m streamlit run app.py
