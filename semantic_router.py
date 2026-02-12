"""
Semantic Router - LLM-based intent classification
Uses DeepSeek-V3 to determine which agent should handle a query
"""
import requests
import json
from typing import Dict, List, Tuple

class SemanticRouter:
    """
    Routes queries to agents using LLM semantic understanding
    Instead of keyword matching, uses LLM to classify intent
    """
    
    def __init__(self):
        self.api_key = "syn_3005bb47081b13be8f207a31c56029fa"
        self.base_url = "https://api.synthetic.new/v1/chat/completions"
        self.model = "hf:deepseek-ai/DeepSeek-V3"
        
        # Agent descriptions for the LLM
        self.agent_descriptions = {
            "billing_agent": "Faturas, pagamentos, consumo de energia, valores em euros, histórico de faturação",
            "ev_agent": "Carros elétricos, carregamento, baterias, postos de carregamento, MOBI.E, custo de carregar",
            "solar_agent": "Painéis solares, fotovoltaicos, produção de energia, autoconsumo, venda à rede",
            "support_agent": "Avarias, problemas técnicos, suporte, intervenções, técnicos"
        }
    
    def route(self, query: str) -> Tuple[str, float]:
        """
        Use LLM to determine best agent for query
        Returns: (agent_name, confidence)
        """
        try:
            # Build prompt for LLM
            agents_list = "\n".join([f"- {name}: {desc}" for name, desc in self.agent_descriptions.items()])
            
            prompt = f"""Analisa a pergunta do cliente e determina qual é o agente mais adequado para responder.

AGENTES DISPONÍVEIS:
{agents_list}

PERGUNTA DO CLIENTE: "{query}"

INSTRUÇÕES:
- Escolhe APENAS UM agente da lista acima
- Responde em formato JSON exato: {{"agent": "nome_do_agente", "confidence": 0.95}}
- Confidence deve ser entre 0.0 e 1.0
- Se nenhum agente for adequado, usa: {{"agent": "none", "confidence": 0.0}}

Responde APENAS com o JSON:"""

            # Call LLM
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.1  # Low temperature for consistent results
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Parse JSON response
                    try:
                        # Extract JSON from response (might have markdown)
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        
                        routing = json.loads(content)
                        agent = routing.get("agent", "none")
                        confidence = float(routing.get("confidence", 0.0))
                        
                        # Validate agent name
                        if agent in self.agent_descriptions or agent == "none":
                            return agent, confidence
                            
                    except json.JSONDecodeError:
                        # Fallback: try to extract agent name directly
                        for agent_name in self.agent_descriptions.keys():
                            if agent_name in content:
                                return agent_name, 0.8
            
            # Fallback to keyword matching if LLM fails
            return self._fallback_route(query)
            
        except Exception as e:
            print(f"Semantic routing error: {e}")
            return self._fallback_route(query)
    
    def _fallback_route(self, query: str) -> Tuple[str, float]:
        """Fallback keyword matching if LLM fails"""
        query_lower = query.lower()
        
        # Simple keyword matching as fallback
        keywords = {
            "billing_agent": ["fatura", "conta", "pagar", "valor", "consumo", "kwh", "€"],
            "ev_agent": ["carro", "elétrico", "carregar", "bateria", "ev", "tesla", "mobie"],
            "solar_agent": ["painel", "solar", "fotovoltaico", "produção", "autoconsumo"],
            "support_agent": ["avaria", "problema", "técnico", "suporte", "não funciona"]
        }
        
        best_agent = "none"
        best_score = 0
        
        for agent, words in keywords.items():
            score = sum(1 for w in words if w in query_lower)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        confidence = min(best_score / 2, 1.0) if best_score > 0 else 0.0
        return best_agent, confidence

# Singleton
semantic_router = SemanticRouter()
