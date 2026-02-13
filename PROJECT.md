# Mordomo EDP 3.0 — Project Package

**Gestor de Projeto:** AAMS (OpenClaw Agent)  
**Cliente:** EDP (via Hexa Labs)  
**Início:** 13 Fev 2026  
**Status:** Em curso (PoC funcional)  

---

## 1. Scope & Objectivos

### 1.1 Visão
Assistente virtual multi-agente para utilities de energia (EDP), com respostas naturais em PT-PT via LLM e arquitetura MCP (Model Context Protocol) escalável.

### 1.2 Objectivos Técnicos
| Fase | Objetivo | Status |
|------|----------|--------|
| PoC (Sem 1-2) | Gateway MCP + Billing Agent + Demo web | ✅ Funcional |
| Piloto (Mês 1) | Support Agent + Grid Agent + Integração real | 🔄 A iniciar |
| Produção (Mês 2-3) | EV Agent + Solar Agent + Deployment cloud | ⏳ Planeado |

### 1.3 Funcionalidades Atuais (PoC)
- ✅ Consulta de faturas (mock)
- ✅ Análise de consumo (mock)
- ✅ Interface web responsiva (desktop + mobile)
- ✅ Integração LLM DeepSeek-V3
- ✅ Memória de contexto (localStorage)
- ✅ Cloudflare Tunnel para demo pública

### 1.4 Funcionalidades Planeadas
- [ ] Suporte técnico com ticketing
- [ ] Agendamento de técnicos (Grid Agent)
- [ ] Mobilidade elétrica (EV Agent)
- [ ] Autoconsumo solar (Solar Agent)
- [ ] Integração SAP IS-U (dados reais)
- [ ] Integração Salesforce CRM
- [ ] Autenticação de clientes

---

## 2. Equipa & Organização

### 2.1 Estrutura
```
PM (AAMS)
├── Sub-Agente: Architecture Lead
├── Sub-Agente: Backend Lead (FastAPI/MCP)
├── Sub-Agente: Frontend Lead (UI/UX)
├── Sub-Agente: DevOps Lead (Deploy/Cloud)
└── Sub-Agente: QA Lead (Testing/Validação)
```

### 2.2 Responsabilidades
| Função | Responsável | Tarefas Principais |
|--------|-------------|-------------------|
| **PM** | AAMS | Roadmap, coordenação, relatórios, decisões técnicas |
| Architecture | Sub-agente | Design de sistema, padrões, integrações |
| Backend | Sub-agente | Gateway MCP, agents, APIs, LLM bridge |
| Frontend | Sub-agente | Interface web, mobile, UX improvements |
| DevOps | Sub-agente | Deploy, Docker, K8s, cloud, CI/CD |
| QA | Sub-agente | Testes, validação, edge cases, benchmarks |

### 2.3 Comunicação
- **Daily check-in:** Auto-gerido (logs em `logs/`)
- **Relatórios:** Telegram (grupo Mordomo EDP)
- **Bloqueios:** Alerta imediato via Telegram

---

## 3. Recursos

### 3.1 Infraestrutura Existente
| Recurso | Detalhe | Status |
|---------|---------|--------|
| Repo GitHub | https://github.com/aamsilva/mordomo-edp | ✅ Ativo |
| Ambiente Dev | Mac Mini (localhost) | ✅ Funcional |
| Tunnel Público | Cloudflare Quick Tunnels | ✅ Rotativo |
| LLM API | Synthetic.new (DeepSeek-V3) | ✅ Créditos disponíveis |

### 3.2 Tecnologias
- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Protocolo:** MCP (Model Context Protocol)
- **LLM:** DeepSeek-V3 via Synthetic.new API
- **Frontend:** HTML5, CSS3, Vanilla JS
- **Deploy:** Docker (planeado), K8s (futuro)

### 3.3 APIs & Integrações (a desenvolver)
| Sistema | Tipo | Prioridade |
|---------|------|------------|
| SAP IS-U | SOAP/REST | Alta |
| Salesforce CRM | REST | Alta |
| Smart Meters | MQTT/REST | Média |
| SCADA Grid | Protocolo específico | Média |

### 3.4 Limitações Atuais
- Dados mock (não integrados com sistemas reais EDP)
- Tunnel Cloudflare é temporário (URL muda)
- Sem autenticação de utilizadores
- Sem persistência server-side

---

## 4. Entregáveis & Ritmo

### 4.1 Relatórios
| Tipo | Frequência | Conteúdo | Canal |
|------|------------|----------|-------|
| **Daily** | 9h (dias úteis) | O que foi feito, bloqueios, plano para hoje | Telegram |
| **Weekly** | 2ª 10h | Resumo semana, métricas, riscos, próxima sprint | Telegram + GitHub |
| **Alerta** | Imediato | Bloqueios, bugs críticos, decisões urgentes | Telegram |

### 4.2 GitHub Workflow
- **Issues:** Tarefas, bugs, features (labels: `bug`, `feature`, `tech-debt`)
- **Projects:** Kanban board (To Do → In Progress → Review → Done)
- **PRs:** Code review obrigatório antes de merge
- **Commits:** Mensagens descritivas em inglês

### 4.3 Checkpoints com Stakeholder
| Checkpoint | Quando | Objectivo |
|------------|--------|-----------|
| Kickoff | Início de cada fase | Alinhar expectativas, confirmar recursos |
| Review | Final de cada sprint | Demo, feedback, ajustes |
| Go/No-Go | Antes de produção | Aprovação final, handover |

---

## 5. O que Preciso do Augusto

### 5.1 Decisões (requerem aprovação)
| Tema | Minha recomendação | Decisão |
|------|-------------------|---------|
| **Integração SAP IS-U** | Mock → API real em piloto | ⏳ Pendente |
| **Cloud deployment** | Docker → K8s em Azure/AWS | ⏳ Pendente |
| **Autenticação** | JWT simples → OAuth2 EDP | ⏳ Pendente |
| **Novo agente prioritário** | Support Agent vs EV Agent | ⏳ Pendente |

### 5.2 Acesso & Credenciais
- [ ] API SAP IS-U (test environment)
- [ ] Salesforce CRM sandbox
- [ ] Azure/AWS subscription (para deploy)
- [ ] Cloudflare account (tunnel permanente)

### 5.3 Checkpoints Regulares
- **Semanal:** 15 min de sync (quarta ou quinta, flexível)
- **Bloqueios:** Alerta imediato via Telegram
- **Decisões estratégicas:** Antes de mudanças de arquitetura

---

## 6. Roadmap Detalhado

### Sprint 1 (13-20 Fev) — Estabilização PoC
- [ ] Consolidar web_server_v2 como principal
- [ ] Documentar API endpoints
- [ ] Criar testes básicos (unitários)
- [ ] Setup GitHub Projects board
- [ ] Primeiro relatório semanal

### Sprint 2 (21-27 Fev) — Support Agent
- [ ] Implementar Support Agent (esqueleto)
- [ ] Mock de ticketing system
- [ ] Integração Support → Billing (cross-agent)
- [ ] Melhorias na interface web
- [ ] Testes E2E básicos

### Sprint 3 (28 Fev - 6 Mar) — Grid Agent & Infra
- [ ] Implementar Grid Agent
- [ ] Dockerização (Dockerfile + docker-compose)
- [ ] CI/CD pipeline básica (GitHub Actions)
- [ ] Preparação para cloud deploy

### Sprint 4 (7-13 Mar) — EV/Solar Agents
- [ ] Implementar EV Agent
- [ ] Implementar Solar Agent
- [ ] Integrações cross-agent avançadas
- [ ] Stress tests

---

## 7. Riscos & Mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Acesso APIs EDP negado | Média | Alto | Mock avançado, mostrar valor primeiro |
| Créditos Synthetic.new esgotam | Baixa | Médio | Monitorar, fallback para outro provider |
| LLM lento (>5s) | Média | Médio | Caching, otimização de prompts |
| Concorrência mostra similar | Baixa | Alto | Focar em integração EDP específica |

---

## 8. Métricas de Sucesso

### Técnicas
- Tempo resposta LLM < 3s
- Uptime demo > 95%
- Cobertura testes > 70%

### Negócio
- Nº de agentes funcionais: 5 (target)
- Integrações reais: 2+ (target)
- Demo funcional 24/7: ✅

---

## 9. Documentação & Recursos

- **Repo:** https://github.com/aamsilva/mordomo-edp
- **Docs:** `~/clawd/projects/mordomo3-edp/docs/`
- **Logs:** `~/clawd/projects/mordomo3-edp/*.log`
- **Proposta EDP:** `docs/EDP_PROPOSAL.md`
- **Arquitetura:** `docs/architecture_diagrams.md`

---

**Última atualização:** 13 Fev 2026  
**Próximo checkpoint:** 20 Fev 2026 (Review Sprint 1)
