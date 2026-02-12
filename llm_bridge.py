"""
LLM Bridge - Natural Language Enhancement with DeepSeek-V3
Polishes agent responses into conversational Portuguese
"""
import requests
import json
from typing import Dict, Any

class LLMBridge:
    """
    Bridge to DeepSeek-V3 for natural language generation
    """
    
    def __init__(self):
        self.api_key = "syn_3005bb47081b13be8f207a31c56029fa"  # Synthetic API
        self.base_url = "https://api.synthetic.new/v1/chat/completions"  # OpenAI-compatible endpoint
        self.model = "hf:deepseek-ai/DeepSeek-V3"
        
    def enhance_response(self, user_query: str, agent_response: Dict, agent_name: str) -> str:
        """
        Take structured agent response and generate natural language
        """
        try:
            # Build context from agent data
            context = self._build_context(agent_response, agent_name)
            
            # Create prompt for LLM
            prompt = f"""Responde como assistente de atendimento de uma empresa de energia em Portugal.

PERGUNTA DO CLIENTE: "{user_query}"

DADOS DO AGENTE ({agent_name}):
{context}

INSTRUÇÕES:
- Responde de forma natural e amigável em português (PT-PT)
- Usa os dados acima mas reformula de forma conversacional
- Máximo 2-3 frases curtas
- Tom profissional mas próximo
- Não uses linguagem técnica excessiva
- Se houver valores em euros, formata como €XX.XX

Responde APENAS com a mensagem ao cliente:"""

            # Call DeepSeek-V3 via Synthetic API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # OpenAI format: choices[0].message.content
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"].strip()
            else:
                print(f"LLM API Error: {response.status_code} - {response.text[:200]}")
            
            # Fallback to original agent message if LLM fails
            return agent_response.get("message", "Desculpe, não consegui processar o pedido.")
            
        except Exception as e:
            print(f"LLM Error: {e}")
            # Return original agent message on error
            return agent_response.get("message", "Desculpe, não consegui processar o pedido.")
    
    def _build_context(self, agent_response: Dict, agent_name: str) -> str:
        """Build context string from agent response data"""
        context_parts = []
        
        data = agent_response.get("data", {})
        
        if agent_name == "billing_agent":
            if "invoice" in data:
                inv = data["invoice"]
                context_parts.append(f"- Fatura: {inv.get('number')}")
                context_parts.append(f"- Valor: €{inv.get('amount')}")
                context_parts.append(f"- Data: {inv.get('date')}")
                context_parts.append(f"- Consumo: {inv.get('consumption_kwh')} kWh")
                context_parts.append(f"- Estado: {inv.get('status')}")
        
        elif agent_name == "ev_agent":
            if "costs" in data:
                costs = data["costs"]
                context_parts.append(f"- Custo mensal: €{costs.get('monthly_consumption_kwh', 'N/A')}")
                context_parts.append(f"- Custo por 100km: {costs.get('cost_per_100km', 'N/A')}")
            if "optimization" in data:
                opt = data["optimization"]
                context_parts.append(f"- Melhor horário: {opt.get('best_start_time')}")
                context_parts.append(f"- Poupança vs horário caro: {opt.get('savings_vs_peak')}")
            if "stations" in data:
                stations = data["stations"]
                context_parts.append(f"- {len(stations)} postos de carregamento encontrados")
        
        elif agent_name == "solar_agent":
            if "production" in data:
                prod = data["production"]
                context_parts.append(f"- Produção hoje: {prod.get('today_kwh')} kWh")
                context_parts.append(f"- Autoconsumo: {prod.get('autoconsumed')} kWh")
                context_parts.append(f"- Vendido à rede: {prod.get('sold_to_grid')} kWh")
            if "sales" in data:
                sales = data["sales"]
                context_parts.append(f"- Vendas este mês: €{sales.get('month_earnings')}")
            if "savings" in data:
                savings = data["savings"]
                context_parts.append(f"- Poupança mensal: €{savings.get('monthly_savings')}")
        
        return "\n".join(context_parts) if context_parts else "- Dados não disponíveis"

# Singleton instance
llm_bridge = LLMBridge()
