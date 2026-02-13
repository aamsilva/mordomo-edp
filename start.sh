#!/bin/bash
# Mordomo 3.0 MCP Gateway - Start Script
# Single command to start the gateway

echo "=============================================="
echo "  Mordomo 3.0 MCP Gateway for EDP"
echo "=============================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start the gateway
echo ""
echo "🚀 Starting MCP Gateway..."
echo ""
echo "  📡 Gateway URL: http://localhost:8765"
echo "  🔌 WebSocket:   ws://localhost:8765/mcp/ws"
echo "  📋 HTTP MCP:    http://localhost:8765/mcp"
echo ""
echo "  Agents available:"
echo "    • edp-billing-agent"
echo ""
echo "  Endpoints:"
echo "    • GET  /           - Gateway info"
echo "    • GET  /health     - Health check"
echo "    • GET  /agents     - List agents"
echo "    • POST /mcp        - MCP HTTP endpoint"
echo "    • WS   /mcp/ws     - MCP WebSocket endpoint"
echo ""
echo "Press Ctrl+C to stop"
echo "=============================================="
echo ""

python3 gateway.py &
GATEWAY_PID=$!

# Wait for gateway to start
sleep 2

# Start web server
echo ""
echo "🌐 Starting Web Server..."
echo "  📡 Web URL: http://localhost:8080"
echo ""
python3 web_server.py