#!/bin/bash
# Identity Agent Platform - Development Setup

set -e

echo "=== Identity Agent Platform - Init ==="

# Check required env vars
check_env() {
    local var=$1
    if [ -z "${!var}" ]; then
        echo "⚠ $var not set"
        return 1
    fi
    echo "✓ $var set"
    return 0
}

echo ""
echo "Checking environment..."
check_env "SOLANA_RPC_URL" || true
check_env "ANTHROPIC_API_KEY" || true
check_env "VOYAGE_API_KEY" || true

# Install frontend dependencies if needed
if [ -d "frontend" ] && [ ! -d "frontend/node_modules" ]; then
    echo ""
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Install gateway dependencies if needed
if [ -d "gateway" ] && [ ! -d "gateway/.venv" ]; then
    echo ""
    echo "Installing gateway dependencies..."
    cd gateway && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
fi

echo ""
echo "=== Init Complete ==="
echo ""
echo "Next steps:"
echo "  1. Set missing env vars in .env or shell"
echo "  2. Start Solana: solana-test-validator"
echo "  3. Start frontend: cd frontend && npm run dev"
echo "  4. Start gateway: cd gateway && uvicorn app.main:app --reload"
