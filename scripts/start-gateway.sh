#!/bin/bash
cd "$(dirname "$0")/../gateway"
source venv/bin/activate
# Kill existing gateway on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null
# Start gateway in background
nohup python main.py > /tmp/gateway.log 2>&1 &
echo $! > /tmp/gateway.pid
# Wait for health check
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "Gateway started: http://127.0.0.1:8000"
        exit 0
    fi
    sleep 1
done
echo "Failed to start gateway"
exit 1
