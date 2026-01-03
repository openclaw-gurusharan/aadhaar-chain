#!/bin/bash
# Restart frontend (3000) and gateway (8000) servers
# Usage: restart-servers.sh [--no-logs]
# Exit: 0 = both healthy, 1 = startup failed, 2 = timeout
# Logs: /tmp/server-logs/frontend.log, /tmp/server-logs/gateway.log

# ─────────────────────────────────────────────────────────────────
# Config helper
# ─────────────────────────────────────────────────────────────────
CONFIG="$PWD/.claude/config/project.json"
get_config() { jq -r ".$1 // empty" "$CONFIG" 2>/dev/null || echo "$2"; }

FRONTEND_PORT=$(get_config "dev_server_port" "3000")
GATEWAY_PORT="8000"
TIMEOUT=30
LOGS_DIR="/tmp/server-logs"

mkdir -p "$LOGS_DIR"

# ─────────────────────────────────────────────────────────────────
# Kill existing servers
# ─────────────────────────────────────────────────────────────────
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

echo "=== Stopping existing servers ==="
kill_port $FRONTEND_PORT
kill_port $GATEWAY_PORT

# ─────────────────────────────────────────────────────────────────
# Start servers
# ─────────────────────────────────────────────────────────────────
echo "=== Starting servers ==="

# Start frontend
cd frontend
if [ "$1" != "--no-logs" ]; then
    npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
else
    npm run dev >/dev/null 2>&1 &
fi
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID, port: $FRONTEND_PORT)"
cd ..

# Start gateway
cd gateway
if [ "$1" != "--no-logs" ]; then
    uvicorn main:app --reload --port $GATEWAY_PORT > "$LOGS_DIR/gateway.log" 2>&1 &
else
    uvicorn main:app --reload --port $GATEWAY_PORT >/dev/null 2>&1 &
fi
GATEWAY_PID=$!
echo "Gateway started (PID: $GATEWAY_PID, port: $GATEWAY_PORT)"
cd ..

# ─────────────────────────────────────────────────────────────────
# Health checks
# ─────────────────────────────────────────────────────────────────
echo "=== Waiting for servers to be healthy ==="

wait_for_health() {
    local url=$1
    local name=$2
    local elapsed=0

    while [ $elapsed -lt $TIMEOUT ]; do
        if curl -s "$url" | grep -q "healthy\|status"; then
            echo "✓ $name is healthy"
            return 0
        fi
        sleep 1
        ((elapsed++))
        echo "  Waiting for $name... (${elapsed}s)"
    done

    echo "✗ $name failed to start within ${TIMEOUT}s"
    return 1
}

# Check frontend
if ! wait_for_health "http://localhost:$FRONTEND_PORT" "Frontend"; then
    echo "=== Frontend startup failed ==="
    if [ "$1" != "--no-logs" ]; then
        echo "Frontend log:"
        tail -20 "$LOGS_DIR/frontend.log"
    fi
    exit 1
fi

# Check gateway
if ! wait_for_health "http://localhost:$GATEWAY_PORT/api/health" "Gateway"; then
    echo "=== Gateway startup failed ==="
    if [ "$1" != "--no-logs" ]; then
        echo "Gateway log:"
        tail -20 "$LOGS_DIR/gateway.log"
    fi
    exit 1
fi

echo ""
echo "=== Both servers healthy ==="
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Gateway:  http://localhost:$GATEWAY_PORT"
echo "Logs:     $LOGS_DIR/"

# Save server info for later use
cat > "$LOGS_DIR/server-info.json" << EOF
{
  "frontend_port": $FRONTEND_PORT,
  "gateway_port": $GATEWAY_PORT,
  "frontend_pid": $FRONTEND_PID,
  "gateway_pid": $GATEWAY_PID,
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

exit 0
