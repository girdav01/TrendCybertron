#!/usr/bin/env python3
"""
Trend Cybertron App Launcher
Simple launcher script for the Streamlit application
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_model_available():
    """Check if the Trend Cybertron model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return 'llama-trendcybertron-primus-merged' in models
        return False
    except:
        return False

def start_ollama():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Wait for service to start
        return True
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def pull_model():
    """Pull the Trend Cybertron model"""
    print("📥 Pulling Trend Cybertron Primus 8B model...")
    print("This may take several minutes depending on your internet connection...")
    try:
        subprocess.run(["ollama", "pull", "llama-trendcybertron-primus-merged"], check=True)
        print("✅ Model pulled successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to pull model: {e}")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    print("🌐 Starting Trend Cybertron Streamlit App...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🛡️  Trend Cybertron App Launcher")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the TrendCybertronApp directory.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama_running():
        print("⚠️  Ollama is not running. Attempting to start...")
        if not start_ollama():
            print("❌ Failed to start Ollama. Please start manually:")
            print("   ollama serve")
            sys.exit(1)
    
    # Check model
    if not check_model_available():
        print("⚠️  Trend Cybertron model not found. Attempting to pull...")
        if not pull_model():
            print("❌ Failed to pull model. Please pull manually:")
            print("   ollama pull llama-trendcybertron-primus-merged")
            sys.exit(1)
    
    print("✅ All prerequisites are ready!")
    print()
    print("🌐 Starting the application...")
    print("📱 The app will open in your default browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print()
    
    # Run the Streamlit app
    run_streamlit()

if __name__ == "__main__":
    main()
