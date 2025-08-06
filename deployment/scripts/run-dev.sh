# ============================================================================
# FILE: deployment/scripts/run-dev.sh
# Development server script
# ============================================================================

#!/bin/bash

echo "🧠 Starting MindfulMate Development Server"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run setup.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if Ollama is running
echo "Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama is not running. Please start it with: ollama serve${NC}"
    exit 1
fi

# Check for Gemma model
echo "Checking for Gemma models..."
models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*gemma[^"]*"')
if [ ! -z "$models" ]; then
    echo -e "${GREEN}✅ Gemma models available${NC}"
else
    echo -e "${YELLOW}⚠️ No Gemma models found. Installing gemma3n:e4b...${NC}"
    ollama pull gemma3n:e4b
fi

# Create logs directory
mkdir -p logs

# Set development environment variables
export DEBUG=true
export LOG_LEVEL=INFO
export API_HOST=localhost
export API_PORT=8000

# Start the development server
echo ""
echo -e "${GREEN}🚀 Starting MindfulMate API server...${NC}"
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Interactive API: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with auto-reload for development
python run.py
