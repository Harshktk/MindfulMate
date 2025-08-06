# ============================================================================
# FILE: deployment/scripts/test.sh
# Testing script
# ============================================================================

#!/bin/bash

echo "🧪 Running MindfulMate Tests"
echo "============================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    exit 1
fi

# Check if Ollama is running
echo "Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama not running - some tests may fail${NC}"
fi

# Run quick connection test
echo ""
echo "🔌 Testing Ollama integration..."
python -c "
import sys
sys.path.append('.')
try:
    from src.core.gemma_client import GemmaClient
    client = GemmaClient()
    print('✅ Gemma client initialization successful')
except Exception as e:
    print(f'❌ Gemma client failed: {e}')
"

# Run unit tests
echo ""
echo "🧪 Running unit tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short
    test_result=$?
else
    echo -e "${YELLOW}⚠️ pytest not found, running basic tests${NC}"
    python -m pytest tests/ -v
    test_result=$?
fi

# Run integration tests
echo ""
echo "🔗 Running integration tests..."
python tests/test_integration/test_end_to_end.py

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
if [ $test_result -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi
