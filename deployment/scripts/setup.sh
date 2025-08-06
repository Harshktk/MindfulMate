# ============================================================================
# FILE: deployment/scripts/setup.sh
# Project setup script
# ============================================================================

#!/bin/bash

echo "🧠 MindfulMate Setup Script"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $python_version == *"Python 3"* ]]; then
    print_status "Python 3 found: $python_version"
else
    print_error "Python 3 is required but not found"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
print_status "Pip upgraded"

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
print_status "Requirements installed"

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p data/{models,therapeutic,sample}
mkdir -p temp
mkdir -p user_data
print_status "Directories created"

# Copy environment file
echo "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Please edit .env file with your configuration"
else
    print_warning ".env file already exists"
fi

# Test Ollama connection
echo "Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_status "Ollama is running"
    
    # Check for Gemma models
    models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*gemma[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$models" ]; then
        print_status "Gemma models found: $models"
    else
        print_warning "No Gemma models found. Run: ollama pull gemma3n:e4b"
    fi
else
    print_error "Ollama is not running. Please start it with: ollama serve"
fi

# Make scripts executable
echo "Setting up scripts..."
chmod +x deployment/scripts/*.sh
print_status "Scripts made executable"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Make sure Ollama is running: ollama serve"
echo "3. Ensure you have a Gemma model: ollama pull gemma3n:e4b"
echo "4. Run tests: python -m pytest"
echo "5. Start the application: python run.py"
echo ""
