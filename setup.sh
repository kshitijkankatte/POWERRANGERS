#!/bin/bash

# Sahanak Backend Setup Script for Mac/Linux

echo ""
echo "============================================"
echo "  Sahanak Backend Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-venv"
    exit 1
fi

echo "[1/5] Python found"
python3 --version

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"

# Check for .env file
echo ""
echo "[5/5] Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating .env from template..."
    cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
DATABASE_URL=sqlite:///sahanak.db
FRONTEND_URL=http://localhost:8000
EOF
    echo ".env file created - please add your ANTHROPIC_API_KEY"
else
    echo ".env file found"
fi

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run: python -m uvicorn main:app --reload"
echo "3. Access API at: http://localhost:8001"
echo "4. API Docs at: http://localhost:8001/docs"
echo ""
echo "To activate the environment in future sessions:"
echo "   source venv/bin/activate"
echo ""
