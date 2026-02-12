# Mordomo 3.0 - Multi-Agent AI Assistant for Energy Utilities

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🤖 Assistente virtual multi-agente para utilities de energia, com integração LLM (DeepSeek-V3), interface web responsiva e memória de contexto persistente.

---

## 🎯 Visão Geral

O **Mordomo 3.0** é uma plataforma de assistência virtual inteligente para empresas de utilities (energia, água, telecomunicações), desenvolvida como demonstração de arquitetura multi-agente em tempo real.

### Funcionalidades Principais:
- 💰 **Consulta de Faturas** - Dados de faturação em tempo real
- ⚡ **Análise de Consumo** - Padrões de consumo energético
- 🔧 **Suporte Técnico** - Reporte e acompanhamento de avarias
- 🧠 **LLM Inteligente** - Respostas naturais com DeepSeek-V3
- 💬 **Memória de Contexto** - Conversas persistentes (localStorage)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Desktop    │  │    Mobile    │  │    localStorage      │  │
│  │   (Web)      │  │   (Web)      │  │   (Context Memory)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS (Cloudflare Tunnel)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GATEWAY MCP (Porta 8080)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Roteamento de Intenções                                 │ │
│  • Proxy para /mcp (dados) e /chat (LLM)                      │ │
│  • CORS habilitado para acesso web                            │ │
└────────────────────┬──────────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Billing │  │ Support  │  │   Grid   │
│  Agent   │  │  Agent   │  │  Agent   │
│  (Mock)  │  │  (Mock)  │  │  (Mock)  │
└──────────┘  └──────────┘  └──────────┘
       │             │             │
       └─────────────┴─────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LLM BRIDGE (Porta 8081)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Modelo: DeepSeek-V3 (hf:deepseek-ai/DeepSeek-V3)        │ │
│  • API: Synthetic.new (Anthropic format)                      │ │
│  • Contexto: Histórico de conversa (últimas 6 mensagens)      │ │
│  • Respostas: Naturais em português (PT-PT)                   │ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```
mordomo3-edp/
├── README.md                 # Este ficheiro
├── gateway.py               # MCP Gateway (FastAPI)
├── llm_bridge.py            # LLM Bridge (DeepSeek-V3)
├── web_server.py            # Servidor web estático + proxy
├── web_interface/
│   ├── index.html           # Interface universal (desktop + mobile)
│   └── mobile.html          # Versão mobile otimizada (legacy)
├── docs/
│   └── architecture_diagrams.md  # Diagramas de arquitetura
├── requirements.txt         # Dependências Python
├── start.sh                 # Script de inicialização
└── PUSH_TO_NEW_REPO.sh      # Script para push GitHub

```

---

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clonar repositório
git clone https://github.com/aamsilva/mordomo3-edp.git
cd mordomo3-edp

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Configurar API Key da Synthetic (opcional, já configurado)
export SYNTHETIC_API_KEY="syn_..."

# Ou editar diretamente em llm_bridge.py
```

### 3. Iniciar Serviços

```bash
# Método 1: Script automático
./start.sh

# Método 2: Manual (3 terminais)
# Terminal 1: Gateway MCP
python3 gateway.py

# Terminal 2: LLM Bridge
python3 llm_bridge.py

# Terminal 3: Web Server
python3 web_server.py
```

### 4. Aceder

- **Local:** http://localhost:8080
- **Público:** Usar Cloudflare Tunnel (ver abaixo)

---

## 🌐 Exposição Pública (Cloudflare Tunnel)

```bash
# Instalar cloudflared (se não instalado)
brew install cloudflared  # Mac
# ou: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation

# Iniciar túnel
cloudflared tunnel --url http://localhost:8080

# Copiar URL gerada (ex: https://xxx.trycloudflare.com)
```

---

## 🔌 API Endpoints

### Gateway MCP (`/mcp`)

**Consultar Fatura:**
```json
POST /mcp
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "get_invoice",
    "arguments": {"invoice_number": "latest"}
  }
}
```

**Consultar Consumo:**
```json
POST /mcp
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

### LLM Bridge (`/chat`)

**Gerar Resposta Natural:**
```json
POST /chat
{
  "message": "Qual é o valor da minha fatura?",
  "result": {"invoice": {...}},
  "tool": "get_invoice",
  "context": "Histórico da conversa..."
}
```

---

## 🧠 Modelo LLM

- **Modelo:** `hf:deepseek-ai/DeepSeek-V3`
- **Provider:** [Synthetic.new](https://synthetic.new)
- **Formato:** Anthropic Messages API
- **Temperatura:** 0.7
- **Max Tokens:** 200
- **Idioma:** Português (PT-PT)

### Características:
- ✅ Respostas naturais e diretas
- ✅ Sem "thinking" visível (diferente de Kimi/GLM)
- ✅ Contexto de conversa mantido
- ✅ Tom profissional e amigável

---

## 💾 Memória de Contexto

O sistema mantém o histórico de conversa usando **localStorage**:

- **Persistência:** Dados mantidos após fechar/reabrir browser
- **Limite:** Últimas 6 mensagens enviadas ao LLM
- **Privacidade:** Dados apenas no browser do utilizador
- **Clear:** Botão "🗑️ Limpar" para resetar conversa

---

## 🛠️ Tecnologias

| Componente | Tecnologia |
|------------|-----------|
| Gateway | FastAPI + Python 3.11+ |
| LLM Integration | Synthetic API (Anthropic format) |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Design | CSS Variables, Flexbox, Mobile-First |
| Tunnel | Cloudflare Quick Tunnels |
| Storage | localStorage (browser) |

---

## 📱 Interface Responsiva

A interface adapta-se automaticamente:

- **Mobile (< 640px):** Layout compacto, touch otimizado
- **Tablet (640-1024px):** Layout adaptativo
- **Desktop (> 1024px):** Layout expandido, max-width 800px

---

## 🤝 Contribuição

1. Fork o repositório
2. Cria uma branch (`git checkout -b feature/nova-feature`)
3. Commit alterações (`git commit -am 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abre um Pull Request

---

## 📄 Licença

MIT License - ver [LICENSE](LICENSE) para detalhes.

---

## 🙌 Créditos

Desenvolvido por [Augusto Silva](https://github.com/aamsilva) com apoio do OpenClaw Agent.

**Demo criada para:** EDP (Energias de Portugal) - Sistema Multi-Agente para Utilities.

---

*Última atualização: 2026-02-11*
