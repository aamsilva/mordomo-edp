# Configurar Gemini CLI API Key

## Opção 1: Usar Gemini API (Grátis)

1. Vai a https://aistudio.google.com/app/apikey
2. Cria uma API key
3. Configura no terminal:

```bash
# Adicionar ao ~/.zshrc ou ~/.bash_profile
export GEMINI_API_KEY="sua-api-key-aqui"

# Recarregar
source ~/.zshrc
```

## Opção 2: Configurar via ficheiro

```bash
cat > ~/.gemini/settings.json << 'EOF'
{
  "key": "sua-api-key-aqui"
}
EOF
```

## Testar

```bash
gemini -p "Olá, como estás?"
```

---

## ⚡ Alternativa Rápida (Sem API Key)

Se não quiseres configurar API key agora, posso:

1. **Criar respostas mock inteligentes** — parecem naturais mas são templates
2. **Usar Synthetic API** — já tens acesso, posso integrar
3. **Demo com fallback** — mostra o conceito, depois configuramos LLM

Qual preferes?
