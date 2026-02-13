# Mordomo EDP 3.0 - API Documentation

## Overview

The Mordomo EDP 3.0 API provides endpoints for interacting with the Multi-Agent System (MAS) that handles customer queries for EDP (energy utility) services.

**Base URL:** `http://localhost:8765`

## Endpoints

### 1. GET /

**Description:** Web interface and API info

**Response:**
- If `web_interface/index.html` exists: Returns the HTML interface
- Otherwise: Returns JSON with service information

**Example Response (JSON mode):**
```json
{
  "service": "Mordomo MAS Gateway",
  "version": "3.0",
  "agents": [
    {
      "name": "billing_agent",
      "description": "Gestão de faturas, pagamentos e histórico de consumo",
      "capabilities": ["consultar_fatura", "historico_consumo", "proxima_fatura"],
      "status": "active"
    }
  ],
  "status": "running"
}
```

### 2. GET /health

**Description:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "agents": 3
}
```

**Status Codes:**
- `200 OK` - Service is healthy

### 3. POST /chat

**Description:** Main chat endpoint - processes natural language queries using the Multi-Agent System with LLM enhancement

**Request Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "message": "Quanto tenho que pagar na fatura?",
  "session_id": "optional-session-id",
  "context": {
    "customer_id": "CUST-001",
    "previous_intent": "check_balance"
  }
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User query in natural language |
| session_id | string | No | Session identifier for context tracking |
| context | object | No | Additional context data |

**Response:**
```json
{
  "response": "Sua fatura FT-2024-001 é de €127.50 e vence em 05/02/2024.",
  "agent": "billing_agent",
  "data": {
    "invoice": {
      "number": "FT-2024-001",
      "amount": 127.50,
      "date": "2024-01-15",
      "consumption_kwh": 450,
      "status": "pending",
      "due_date": "2024-02-05"
    }
  },
  "follow_up": [
    "Comparar com mês anterior",
    "Ver detalhes de consumo",
    "Configurar pagamento automático"
  ]
}
```

**Status Codes:**
- `200 OK` - Query processed successfully
- `500 Internal Server Error` - Processing error

### 4. POST /mcp

**Description:** MCP (Model Context Protocol) compatible endpoint for tool calls. Maintains backward compatibility with MCP protocol.

**Request Headers:**
- `Content-Type: application/json`

**Request Body - List Tools:**
```json
{
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "tools": [
    {
      "name": "billing_agent",
      "description": "Gestão de faturas, pagamentos e histórico de consumo",
      "parameters": {
        "query": {"type": "string"},
        "context": {"type": "object"}
      }
    },
    {
      "name": "ev_agent",
      "description": "Gestão de carros elétricos e carregamento",
      "parameters": {
        "query": {"type": "string"},
        "context": {"type": "object"}
      }
    }
  ]
}
```

**Request Body - Call Tool:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "billing_agent",
    "arguments": {
      "query": "Qual é o valor da minha fatura?",
      "context": {
        "customer_id": "CUST-001"
      }
    }
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"data\": {...}, \"message\": \"...\"}"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Request processed
- `400 Bad Request` - Invalid request format

### 5. GET /agents

**Description:** List all registered agents and their capabilities

**Response:**
```json
{
  "agents": [
    {
      "name": "billing_agent",
      "description": "Gestão de faturas, pagamentos e histórico de consumo",
      "capabilities": ["consultar_fatura", "historico_consumo", "proxima_fatura"],
      "status": "active"
    },
    {
      "name": "ev_agent",
      "description": "Gestão de carros elétricos e carregamento",
      "capabilities": ["find_charging_stations", "calculate_charging_cost", "vehicle_status"],
      "status": "active"
    },
    {
      "name": "solar_agent",
      "description": "Gestão de painéis solares e autoconsumo",
      "capabilities": ["estimate_production", "calculate_savings", "installation_info"],
      "status": "active"
    }
  ],
  "total": 3
}
```

### 6. POST /agents/{agent_name}/query

**Description:** Query a specific agent directly (for testing/debugging)

**Path Parameters:**
| Parameter | Description |
|-----------|-------------|
| agent_name | Name of the agent to query |

**Request Body:**
```json
{
  "message": "Quanto consumi este mês?",
  "session_id": "test-session",
  "context": {}
}
```

**Response:**
```json
{
  "agent": "billing_agent",
  "response": {
    "success": true,
    "data": {"consumption": {...}},
    "message": "Consumo: 450 kWh (+18% vs mês anterior)",
    "follow_up": [...]
  }
}
```

**Status Codes:**
- `200 OK` - Query processed
- `404 Not Found` - Agent not found

### 7. POST /context/clear

**Description:** Clear conversation context (start new session)

**Response:**
```json
{
  "status": "context cleared"
}
```

### 8. GET /context

**Description:** Get current shared context

**Response:**
```json
{
  "last_invoice_amount": 127.50,
  "last_consumption": 450,
  "customer_segment": "residential"
}
```

## Error Responses

All endpoints return consistent error formats:

```json
{
  "detail": "Error description message"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## CORS

All endpoints support CORS with the following configuration:
- **Allow-Origin:** `*`
- **Allow-Methods:** `GET, POST, OPTIONS`
- **Allow-Headers:** `Content-Type`

## Example Usage

### Python Example
```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8765/chat",
    json={"message": "Qual é o valor da minha fatura?"}
)
data = response.json()
print(data["response"])

# List agents
response = requests.get("http://localhost:8765/agents")
agents = response.json()["agents"]
for agent in agents:
    print(f"{agent['name']}: {agent['description']}")
```

### cURL Example
```bash
# Chat
curl -X POST http://localhost:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quanto consumi este mês?"}'

# Health check
curl http://localhost:8765/health

# List agents
curl http://localhost:8765/agents
```

## Agent Capabilities

### billing_agent
- `consultar_fatura` - Check invoice details
- `historico_consumo` - Get consumption history
- `proxima_fatura` - Predict next bill
- `metodos_pagamento` - Payment methods
- `comparativo_consumo` - Compare consumption

### ev_agent
- `find_charging_stations` - Find EV charging stations
- `calculate_charging_cost` - Calculate charging costs
- `vehicle_status` - Check vehicle status

### solar_agent
- `estimate_production` - Estimate solar production
- `calculate_savings` - Calculate potential savings
- `installation_info` - Installation information

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2024-02-13 | Initial API documentation for MAS Gateway |

## Support

For support and questions:
