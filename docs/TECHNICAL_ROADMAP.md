# Mordomo EDP 3.0 - Technical Roadmap

## Executive Summary

This document outlines the technical architecture, current state, and future roadmap for the Mordomo EDP 3.0 project - a Multi-Agent AI assistant for EDP (energy utility) customer service.

**Current Version:** 3.0  
**Last Updated:** 2024-02-13  
**Status:** Sprint 1 (Stabilization)

---

## 1. Architecture Overview

### 1.1 Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Web App    │  │  Mobile App  │  │   Chatbot    │           │
│  │  (Static)    │  │   (Future)   │  │   Widget     │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                    HTTP/WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    GATEWAY LAYER                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MCP Gateway (FastAPI)                       │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │    │
│  │  │  /chat     │  │   /mcp     │  │  /health   │        │    │
│  │  │  Endpoint  │  │  Endpoint  │  │  Endpoint  │        │    │
│  │  └─────┬──────┘  └─────┬──────┘  └────────────┘        │    │
│  └────────┼────────────────┼───────────────────────────────┘    │
└───────────┼────────────────┼─────────────────────────────────────┘
            │                │
            │    ┌───────────┘
            │    │
┌───────────▼────▼────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                Orchestrator                              │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │          Semantic Router (LLM-based)             │    │    │
│  │  │     DeepSeek-V3 for intent classification        │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
┌─────────────▼───┐  ┌────────▼──────┐  ┌─────▼──────────┐
│   AGENT LAYER    │  │   AGENT LAYER  │  │   AGENT LAYER │
│  ┌───────────┐   │  │  ┌──────────┐  │  │  ┌─────────┐  │
│  │  Billing  │   │  │  │    EV    │  │  │  │  Solar  │  │
│  │   Agent   │   │  │  │  Agent   │  │  │  │  Agent  │  │
│  └───────────┘   │  │  └──────────┘  │  │  └─────────┘  │
└──────────────────┘  └────────────────┘  └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LLM BRIDGE LAYER                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         DeepSeek-V3 via Synthetic.new API              │    │
│  │         - Response enhancement                         │    │
│  │         - Natural language generation                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Patterns

#### MCP Gateway Pattern
- **Model Context Protocol** compatibility for AI tool integration
- Unified interface for all agent interactions
- WebSocket support for real-time communication
- HTTP fallback for simple requests

#### Multi-Agent System (MAS)
- **Orchestrator** manages agent coordination
- **Semantic Router** uses LLM for intent classification
- **Message Bus** enables inter-agent communication
- **Shared Context** maintains conversation state

#### LLM Integration
- **DeepSeek-V3** (via Synthetic.new API) for:
  - Intent classification
  - Response enhancement
  - Natural language generation
- **Temperature 0.1** for consistent routing decisions

---

## 2. Component Matrix

| Component | Status | Version | Dependencies | Notes |
|-----------|--------|---------|--------------|-------|
| **Gateway** | ✅ Implemented | 3.0 | FastAPI, Uvicorn | MCP-compatible |
| **Orchestrator** | ✅ Implemented | 3.0 | Base Agent classes | MAS coordinator |
| **Semantic Router** | ✅ Implemented | 1.0 | DeepSeek-V3 API | LLM-based routing |
| **LLM Bridge** | ✅ Implemented | 2.0 | Synthetic.new API | Response enhancement |
| **Billing Agent** | ✅ Implemented | 1.0 | Mock data | Needs SAP integration |
| **EV Agent** | ✅ Implemented | 1.0 | Mock data | Needs MOBI.E integration |
| **Solar Agent** | ✅ Implemented | 1.0 | Mock data | Needs PV integration |
| **Support Agent** | 🔄 In Progress | 0.5 | - | Basic structure only |
| **Web Interface** | ✅ Implemented | 2.0 | Static files | Ready for enhancement |
| **Authentication** | ⏳ Planned | - | - | Not implemented |
| **Database** | ⏳ Planned | - | - | Currently in-memory |
| **Caching Layer** | ⏳ Planned | - | Redis | Performance optimization |

### Dependency Graph

```
gateway.py
├── Orchestrator
│   ├── Semantic Router
│   │   └── DeepSeek-V3 API
│   ├── Billing Agent
│   │   └── (future) SAP IS-U
│   ├── EV Agent
│   │   └── (future) MOBI.E API
│   └── Solar Agent
│       └── (future) PV Simulator
├── LLM Bridge
│   └── DeepSeek-V3 API
└── FastAPI/Uvicorn

web_server.py
└── gateway (HTTP proxy)
```

---

## 3. Technical Debt & Refactoring

### 3.1 Code Smells Identified

#### High Priority
1. **Hard-coded API Keys**
   - Location: `semantic_router.py`, `llm_bridge.py`
   - Issue: API keys stored in source code
   - Risk: Security vulnerability
   - **Action:** Move to environment variables

2. **Mock Data Everywhere**
   - Location: All agent implementations
   - Issue: No real data sources integrated
   - Risk: Demo-only system
   - **Action:** Implement real API connectors

3. **No Error Boundaries**
   - Location: Gateway exception handling
   - Issue: Generic try-catch blocks
   - Risk: Silent failures, poor UX
   - **Action:** Implement structured error handling

#### Medium Priority
4. **Synchronous LLM Calls**
   - Location: `semantic_router.py`
   - Issue: Blocking I/O on main thread
   - Risk: Gateway unresponsive under load
   - **Action:** Implement async LLM calls

5. **No Request Validation**
   - Location: Gateway endpoints
   - Issue: Minimal Pydantic validation
   - Risk: Invalid data crashes agents
   - **Action:** Add comprehensive validators

6. **Global State Management**
   - Location: `orchestrator.py`
   - Issue: Shared context is dict-based
   - Risk: Race conditions, data loss
   - **Action:** Implement proper state manager

#### Low Priority
7. **Missing Type Hints**
   - Location: Various files
   - Issue: Inconsistent typing
   - Risk: Runtime errors
   - **Action:** Add mypy and complete type hints

8. **No Rate Limiting**
   - Location: Gateway
   - Issue: Unlimited requests
   - Risk: API abuse, costs
   - **Action:** Add FastAPI rate limiter

### 3.2 Refactoring Roadmap

| Priority | Task | Effort | Sprint |
|----------|------|--------|--------|
| 🔴 High | Move API keys to environment | 2h | 1 |
| 🔴 High | Add structured logging | 4h | 1 |
| 🟡 Medium | Async LLM calls | 4h | 2 |
| 🟡 Medium | Enhanced error handling | 6h | 2 |
| 🟡 Medium | Request validation | 4h | 2 |
| 🟢 Low | Complete type hints | 4h | 3 |
| 🟢 Low | Rate limiting | 2h | 3 |
| 🟢 Low | State manager refactor | 6h | 3 |

---

## 4. Integration Roadmap

### 4.1 SAP IS-U Connector (Billing)

**Current State:** Mock data  
**Target:** Production SAP IS-U integration

**Integration Plan:**
```
Phase 1: API Gateway Setup (Sprint 3-4)
- Set up SAP API Management
- Configure OAuth 2.0 authentication
- Create test environment access

Phase 2: Data Mapping (Sprint 4-5)
- Map invoice structures
- Define consumption data formats
- Create customer profile mapping

Phase 3: Implementation (Sprint 5-6)
- Implement SAP connector class
- Add caching layer
- Error handling & retry logic

Phase 4: Testing (Sprint 6-7)
- Unit tests with mock SAP
- Integration tests
- Performance testing
```

**Technical Details:**
- **Protocol:** OData REST API
- **Authentication:** OAuth 2.0 with client credentials
- **Data:** IS-U Contract Accounts, Billing Documents, Interval Data
- **Caching:** Redis with 15-minute TTL
- **Fallback:** Mock data for SAP downtime

### 4.2 Salesforce CRM Integration

**Current State:** Not implemented  
**Target:** Customer 360° view

**Use Cases:**
- Customer profile enrichment
- Case management
- Interaction history
- Preference management

**Integration Approach:**
- **API:** Salesforce REST API v57.0
- **Authentication:** Connected App with JWT
- **Sync Strategy:** Real-time query, async updates
- **Data Privacy:** GDPR-compliant field filtering

### 4.3 Smart Meters Integration

**Current State:** Mock consumption data  
**Target:** Real-time smart meter data

**Architecture:**
```
Smart Meters → EDP AMI → API Gateway → Mordomo
```

**Features:**
- Real-time consumption tracking
- Anomaly detection
- Peak hour alerts
- Estimated readings

**Timeline:**
- Sprint 8-9: AMI API specification
- Sprint 9-10: Data pipeline setup
- Sprint 10-11: Agent integration
- Sprint 11-12: Testing & rollout

### 4.4 Integration Timeline

| Integration | Q1 2024 | Q2 2024 | Q3 2024 | Status |
|-------------|---------|---------|---------|--------|
| SAP IS-U | Research | Dev | Test | 🟡 Planned |
| Salesforce | Design | Dev | - | 🟡 Planned |
| Smart Meters | - | Design | Dev | 🔵 Future |
| MOBI.E | Research | Dev | - | 🟡 Planned |

---

## 5. Scalability Plan

### 5.1 Current Architecture
- **Deployment:** Single instance (localhost)
- **Process:** Python + FastAPI
- **State:** In-memory (dictionary)
- **Limitations:** Single point of failure, no horizontal scaling

### 5.2 Phase 2: Docker Containers (Sprint 4-6)

**Goal:** Containerization for consistent deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  gateway:
    build: .
    ports:
      - "8765:8765"
    environment:
      - API_KEY=${API_KEY}
      - REDIS_URL=redis://cache:6379
    depends_on:
      - cache
      - db
  
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mordomo
```

**Components:**
- Gateway service
- Redis for caching/sessions
- PostgreSQL for persistence
- Nginx reverse proxy

### 5.3 Phase 3: Kubernetes (Sprint 8-12)

**Goal:** Production-grade orchestration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mordomo-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mordomo-gateway
  template:
    spec:
      containers:
      - name: gateway
        image: mordomo/gateway:v3.0
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Architecture:**
- **Ingress:** Nginx Ingress Controller
- **Service Mesh:** Istio (optional)
- **Auto-scaling:** HPA based on CPU/memory
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack or Loki

### 5.4 Load Balancing Strategy

**Current:** None (single instance)  
**Phase 2:** Nginx round-robin  
**Phase 3:** Kubernetes service mesh

**Session Affinity:**
- Use Redis for session storage
- Enable sticky sessions for WebSocket
- Stateless gateway design

### 5.5 Performance Targets

| Metric | Current | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| Response Time (p95) | 2s | 500ms | 200ms |
| Throughput (req/s) | 10 | 100 | 1000+ |
| Availability | - | 99% | 99.9% |
| Concurrent Users | 1 | 50 | 1000+ |

---

## 6. Security Checklist

### 6.1 Current State
⚠️ **WARNING:** System currently has NO authentication

### 6.2 Authentication Roadmap

#### Sprint 1-2: API Key Management
- [ ] Implement API key generation
- [ ] Add API key middleware
- [ ] Create key rotation mechanism
- [ ] Document key management process

```python
# Example: API Key Middleware
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

#### Sprint 3-4: JWT Authentication
- [ ] JWT token generation
- [ ] Refresh token mechanism
- [ ] Role-based access control (RBAC)
- [ ] Token expiration handling

#### Sprint 5-6: OAuth 2.0 / SSO
- [ ] EDP corporate SSO integration
- [ ] OAuth 2.0 flow implementation
- [ ] Scope-based permissions
- [ ] Audit logging

### 6.3 Data Encryption

| Layer | Current | Target | Implementation |
|-------|---------|--------|----------------|
| Transit | ❌ HTTP | ✅ TLS 1.3 | Certbot/Let's Encrypt |
| At Rest | ❌ None | ✅ AES-256 | Database encryption |
| Secrets | ❌ Hardcoded | ✅ Vault | HashiCorp Vault |
| Logs | ❌ Plain | ✅ Masked | PII redaction |

### 6.4 GDPR Compliance

**Requirements:**
- [ ] Data minimization (only necessary data)
- [ ] Right to be forgotten
- [ ] Data portability
- [ ] Consent management
- [ ] Privacy by design
- [ ] Breach notification (72 hours)

**Implementation:**
- PII detection and classification
- Automated data retention policies
- Consent tracking database
- Data export functionality

### 6.5 Security Testing

| Test Type | Frequency | Tool | Status |
|-----------|-----------|------|--------|
| Dependency Scan | Weekly | Snyk | 🟡 Planned |
| Static Analysis | Per PR | Bandit | 🟡 Planned |
| Penetration Test | Quarterly | External | 🔵 Future |
| Vulnerability Scan | Daily | Trivy | 🟡 Planned |

---

## 7. Development Roadmap

### Sprint 1 (Current): Stabilization ✅
- [x] Consolidate web_server_v2
- [x] Create API documentation
- [x] Setup unit tests
- [x] Update GitHub issues

### Sprint 2: Hardening
- [ ] Environment-based configuration
- [ ] Structured logging (JSON)
- [ ] Error handling improvements
- [ ] Request validation

### Sprint 3: Data Layer
- [ ] PostgreSQL integration
- [ ] Redis caching
- [ ] Session management
- [ ] Migration scripts

### Sprint 4-5: SAP Integration
- [ ] SAP API connector
- [ ] Authentication setup
- [ ] Data mapping
- [ ] Fallback mechanisms

### Sprint 6-7: Enhanced Agents
- [ ] Support agent completion
- [ ] Agent collaboration
- [ ] Context persistence
- [ ] Follow-up improvements

### Sprint 8-10: Production Prep
- [ ] Docker containerization
- [ ] Kubernetes manifests
- [ ] Monitoring setup
- [ ] Load testing

### Sprint 11-12: Security & Launch
- [ ] Authentication implementation
- [ ] Security audit
- [ ] Performance optimization
- [ ] Production deployment

---

## 8. Monitoring & Observability

### 8.1 Metrics to Track

**Application Metrics:**
- Request latency (p50, p95, p99)
- Error rate (by endpoint, by agent)
- LLM API costs
- Agent routing distribution

**Business Metrics:**
- Query success rate
- User satisfaction (feedback)
- Agent