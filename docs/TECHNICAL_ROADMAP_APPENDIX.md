# Appendix - Continued from TECHNICAL_ROADMAP.md

## 8. Monitoring & Observability (Continued)

### 8.2 Logging Strategy

```json
{
  "timestamp": "2024-02-13T10:30:00Z",
  "level": "INFO",
  "service": "mordomo-gateway",
  "trace_id": "abc-123",
  "span_id": "def-456",
  "message": "Query processed",
  "agent": "billing_agent",
  "latency_ms": 245,
  "query_hash": "sha256:..."
}
```

### 8.3 Alerting Rules

- Error rate > 5% for 5 minutes
- Latency p95 > 1s for 10 minutes
- LLM API errors > 10 in 5 minutes
- Disk usage > 80%

---

## 9. Decision Records

### ADR-001: LLM Provider
**Status:** Accepted  
**Decision:** Use DeepSeek-V3 via Synthetic.new API  
**Rationale:** 
- Good Portuguese language support
- Cost-effective
- Sufficient context window

### ADR-002: Agent Communication
**Status:** Accepted  
**Decision:** Message bus pattern with shared context  
**Rationale:**
- Decoupled agents
- Easy to add new agents
- Flexible routing

### ADR-003: Data Storage
**Status:** Proposed  
**Decision:** PostgreSQL + Redis  
**Rationale:**
- ACID compliance for transactions
- Redis for session/cache performance

---

## 10. Appendix

### A. Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | 0.109.0 |
| Server | Uvicorn | 0.27.0 |
| LLM | DeepSeek-V3 | - |
| Testing | pytest | 8.0.0 |
| Deployment | Docker/K8s | - |

### B. Glossary

- **MAS**: Multi-Agent System
- **MCP**: Model Context Protocol
- **LLM**: Large Language Model
- **IS-U**: Industry Solution Utilities (SAP)
- **AMI**: Advanced Metering Infrastructure

### C. References

- FastAPI Documentation: https://fastapi.tiangolo.com
- MCP Specification: https://modelcontextprotocol.io
- EDP Technical Standards (internal)

---

**Document Owner:** Development Team  
**Review Cycle:** Monthly  
**Next Review:** 2024-03-13
