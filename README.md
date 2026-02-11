# Mordomo 3.0 MCP Gateway for EDP

Real-time MCP (Model Context Protocol) Gateway for EDP with WebSocket streaming support.

## 🚀 Quick Start

```bash
# Navigate to project
cd ~/clawd/projects/mordomo3-edp

# Start the gateway
./start.sh
```

The gateway will be available at:
- **HTTP Gateway**: http://localhost:8765
- **WebSocket**: ws://localhost:8765/mcp/ws
- **HTTP MCP**: http://localhost:8765/mcp

## 📁 Project Structure

```
mordomo3-edp/
├── gateway.py          # Main MCP Gateway (FastAPI + WebSocket)
├── demo_chatgpt.py     # ChatGPT integration demo
├── start.sh            # Single-command startup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔌 MCP Protocol Endpoints

### HTTP Endpoint
```bash
POST http://localhost:8765/mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/list",
  "params": {"agent_id": "edp-billing-agent"}
}
```

### WebSocket Endpoint
```javascript
const ws = new WebSocket('ws://localhost:8765/mcp/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: "1",
    method: "tools/call",
    params: {
      name: "get_invoice",
      arguments: {invoice_number: "INV-2026-001"}
    }
  }));
};
```

## 🤖 EDP Billing Agent

The billing agent provides these tools:

### Available Tools

| Tool | Description |
|------|-------------|
| `get_invoice` | Retrieve invoice by number or date |
| `get_consumption` | Get electricity/gas consumption data |
| `list_payments` | List payment history |
| `get_contract_info` | Get contract details |

### Example Tool Calls

**Get Invoice:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "get_invoice",
    "arguments": {"invoice_number": "INV-2026-001"}
  }
}
```

**Get Consumption:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "get_consumption",
    "arguments": {"period": "month"}
  }
}
```

## 🧪 Testing with ChatGPT

### Method 1: Custom GPT Actions

1. Go to ChatGPT → Explore → Create a GPT
2. Add an Action with this schema:

```yaml
openapi: 3.1.0
info:
  title: EDP Billing MCP
  version: 1.0.0
servers:
  - url: http://localhost:8765
paths:
  /mcp:
    post:
      operationId: mcpCall
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                jsonrpc: {type: string}
                id: {type: string}
                method: {type: string}
                params: {type: object}
      responses:
        "200":
          description: MCP Response
```

3. Use ngrok or Cloudflare tunnel to expose localhost

### Method 2: Direct API Integration

Use the demo script to test:

```bash
# Run the demo
python3 demo_chatgpt.py
```

This demonstrates:
- HTTP endpoint communication
- WebSocket streaming
- Performance testing

### Method 3: Python Client

```python
import httpx

response = httpx.post("http://localhost:8765/mcp", json={
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
        "name": "get_invoice",
        "arguments": {"invoice_number": "INV-2026-001"}
    }
})
print(response.json())
```

## 🧪 Testing with Claude

Claude can connect via:

1. **MCP Inspector**: Use the MCP Inspector tool to test
2. **Direct Integration**: Use the WebSocket endpoint

Example:
```bash
# Using wscat for testing
npm install -g wscat
wscat -c ws://localhost:8765/mcp/ws

> {"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}
```

## 🔍 API Reference

### Gateway Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Gateway info |
| `/health` | GET | Health check |
| `/agents` | GET | List registered agents |
| `/mcp` | POST | MCP HTTP endpoint |
| `/mcp/ws` | WS | MCP WebSocket endpoint |

### MCP Methods

| Method | Description |
|--------|-------------|
| `tools/list` | List available tools |
| `tools/call` | Execute a tool |
| `agent/info` | Get agent information |

## 📊 Performance

The gateway is optimized for real-time responses:

- **Target latency**: < 100ms for simple queries
- **WebSocket**: Persistent connection for streaming
- **HTTP**: Stateless request/response

## 🛠️ Development

### Add a New Agent

1. Create agent class in `gateway.py`:
```python
class MyNewAgent:
    def __init__(self):
        self.info = MCPAgentInfo(
            id="my-agent",
            name="My Agent",
            description="...",
            tools=[...]
        )
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        # Handle MCP requests
        pass
```

2. Register in gateway:
```python
my_agent = MyNewAgent()
registry.register_agent(my_agent.info, my_agent.handle_request)
```

### Testing Changes

```bash
# Restart gateway
./start.sh

# Run demo tests
python3 demo_chatgpt.py
```

## 🌐 External Access

To test with ChatGPT/Claude externally, use a tunnel:

### Option 1: Cloudflare Quick Tunnel
```bash
cloudflared tunnel --url http://localhost:8765
```

### Option 2: ngrok
```bash
ngrok http 8765
```

Then use the provided public URL in your MCP client configuration.

## 📝 Requirements

- Python 3.8+
- FastAPI
- WebSockets
- Uvicorn

## 🎯 Demo Checklist

- [ ] Gateway starts successfully
- [ ] HTTP endpoint responds
- [ ] WebSocket connects
- [ ] Tool calls work
- [ ] Response time < 2 seconds
- [ ] Demo script runs successfully

## 📄 License

Internal EDP Project - Mordomo 3.0