# MAS Implementation Guide - Mordomo 3.0

## Overview

Transformação do Mordomo 3.0 de sistema single-agent para Multi-Agent System (MAS) enterprise.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Web/Mobile)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              GATEWAY MAS (FastAPI)                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  • /chat (unified interface)                          │ │
│  │  • /mcp (MCP protocol compatibility)                  │ │
│  │  • /agents (management)                               │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              ORCHESTRATOR (MAS Core)                        │
│  • Agent Registry                                         │
│  • Intent Routing (confidence scoring)                    │
│  • Collaboration Management                               │
│  • Shared Context                                         │
└────────┬────────┬────────┬────────┬─────────────────────────┘
         │        │        │        │
   ┌─────▼────┐ ┌─▼─────┐ ┌─▼─────┐ ┌─▼─────┐
   │ Billing  │ │  EV   │ │ Solar │ │Support│
   │  Agent   │ │ Agent │ │ Agent │ │ Agent │
   └──────────┘ └───────┘ └───────┘ └───────┘
```

## Agents

### 1. Billing Agent
**Capabilities:**
- Consultar faturas
- Histórico de consumo
- Previsão de próxima fatura
- Comparativos

**Keywords:** fatura, conta, pagar, valor, consumo, kwh, eletricidade

### 2. EV Agent
**Capabilities:**
- Otimização horário carregamento
- Análise de custos
- Localização postos MOBI.E
- Comparativo vs combustão

**Keywords:** carro elétrico, carregar, bateria, ev, tesla, mobie

### 3. Solar Agent
**Capabilities:**
- Monitorização produção
- Autoconsumo vs venda à rede
- Previsão meteorológica
- ROI e poupanças

**Keywords:** painel, solar, fotovoltaico, produção, autoconsumo, vender

## API Endpoints

### Chat (Main)
```http
POST /chat
Content-Type: application/json

{
  "message": "Quanto paguei na última fatura?",
  "session_id": "user_123",
  "context": {}
}
```

Response:
```json
{
  "response": "Sua fatura FT-2024-001: €127.50",
  "agent": "billing_agent",
  "data": {...},
  "follow_up": ["Ver consumo", "Pagar fatura"]
}
```

### MCP Protocol
```http
POST /mcp
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "billing_agent",
    "arguments": {"query": "última fatura"}
  }
}
```

### Agent Management
```http
GET /agents                    # List all agents
GET /context                   # Get shared context
POST /context/clear            # Reset conversation
POST /agents/{name}/query      # Direct agent query
```

## Migration Steps

### 1. Backup
```bash
cd ~/clawd/projects/mordomo3-edp
cp gateway.py gateway_old.py
```

### 2. Activate MAS
```bash
# Option A: Replace gateway
mv gateway.py gateway_single.py
mv gateway_mas.py gateway.py

# Option B: Run in parallel (recommended for testing)
# Keep both, use different ports
```

### 3. Update Dependencies
```bash
pip install fastapi uvicorn
```

### 4. Test
```bash
python3 gateway.py
# Verify: curl http://localhost:8765/health
```

## Configuration

### Environment Variables
```bash
export MAS_PORT=8765
export MAS_DEBUG=true
```

### Agent Registration
Edit `gateway.py`:
```python
from agents import EVAgent, SolarAgent, BillingAgent

orchestrator.register_agent(BillingAgent())
orchestrator.register_agent(EVAgent())
orchestrator.register_agent(SolarAgent())
# Add more agents here
```

## Testing

### Unit Tests
```bash
# Test specific agent
python3 -c "
from agents import BillingAgent
agent = BillingAgent()
result = agent.process('Qual a minha fatura?')
print(result)
"
```

### Integration Tests
```bash
# Test full flow
curl -X POST http://localhost:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Monitoring

### Logs
```bash
tail -f logs/mas.log
```

### Metrics
```bash
GET /health
# Returns: {"status": "healthy", "agents": 3}
```

## Troubleshooting

### Issue: Agent not responding
**Check:** Agent registered correctly
```python
print(orchestrator.agents.keys())
```

### Issue: Wrong agent selected
**Check:** Confidence scores in logs
**Fix:** Adjust keyword matching in `can_handle()`

### Issue: Collaboration not working
**Check:** Message bus connectivity
**Fix:** Verify `agent.message_bus = orchestrator`

## Future Enhancements

### Phase 2
- [ ] Smart Home Agent (IoT integration)
- [ ] Predictive Maintenance Agent
- [ ] Green Energy Agent (sustainability)

### Phase 3
- [ ] Grid Balancing Agent (B2B)
- [ ] ML-based intent classification
- [ ] Real EDP API integration

## References

- Google Cloud MAS: https://cloud.google.com/discover/what-is-a-multi-agent-system
- FastAPI: https://fastapi.tiangolo.com
- MCP Protocol: https://modelcontextprotocol.io

---

**Version:** 3.0-MAS  
**Last Updated:** 2026-02-11  
**Author:** OpenClaw Agent
