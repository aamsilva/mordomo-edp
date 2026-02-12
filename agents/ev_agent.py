"""
EV Charging Agent - Electric Vehicle optimization
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentMessage

class EVAgent(BaseAgent):
    """
    Agent especializado em carros elétricos e carregamento
    """
    
    def __init__(self):
        super().__init__(
            name="ev_agent",
            description="Otimização de carregamento de veículos elétricos",
            capabilities=[
                "melhor_horario_carregar",
                "custo_carregamento",
                "localizar_postos",
                "comparar_custo_eletrico_vs_combustao",
                "integracao_mobie"
            ]
        )
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """Check if this agent can handle the query"""
        ev_keywords = [
            "carro elétrico", "carro eletrico", "carregar", "bateria", "ev", "tesla",
            "kwh", "carregamento", "posto", "mobie", "wallbox",
            "carregador", "autonomia", "elétrico", "eletrico",
            "custo", "preço", "preco", "gasto", "quanto", "custa",
            "horário", "horario", "hora", "quando", "melhor",
            "veículo", "veiculo", "transporte", "automóvel", "automovel"
        ]
        
        query = context.get("query", "").lower() if context else ""
        matches = sum(1 for kw in ev_keywords if kw in query)
        
        confidence = min(matches / 2, 1.0)
        
        # Se tem pelo menos 1 match, garantir mínimo de 0.4
        if matches > 0:
            confidence = max(confidence, 0.4)
        
        if intent in ["ev_charging", "carregar_carro"]:
            confidence = max(confidence, 0.9)
            
        return confidence
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Process EV-related queries"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["horário", "horario", "hora", "quando", "melhor", "ótimo", "otimo"]):
            return self._optimal_charging_time()
        
        elif any(kw in query_lower for kw in ["custo", "custa", "custam", "preço", "preco", "gasto", "gastos", "pago", "paguei", "quanto", "valor", "eur", "€"]):
            return self._charging_cost_analysis()
        
        elif any(kw in query_lower for kw in ["posto", "postos", "carregador", "público", "publico", "mobie", "local", "próximo", "proximo", "perto"]):
            return self._find_charging_stations()
        
        else:
            return {
                "success": True,
                "data": {"agent": "ev"},
                "message": "Posso ajudar com otimização de carregamento, custos e localização de postos. O que precisa?",
                "follow_up": [
                    "Melhor horário para carregar",
                    "Quanto gasto por mês?",
                    "Postos mais próximos"
                ]
            }
    
    def _optimal_charging_time(self) -> Dict[str, Any]:
        """Calculate optimal charging time based on tariffs"""
        
        # Solicitar dados ao Billing Agent
        self.send_message("billing_agent", "request", {
            "request_type": "get_consumption_pattern"
        })
        
        analysis = {
            "best_start_time": "22:00",
            "best_end_time": "06:00",
            "savings_vs_peak": "€45/mês",
            "current_tariff": "Bi-horária",
            "recommendation": "Programar carregamento para iniciar às 22h",
            "autonomy_gained": "~350 km por carga completa"
        }
        
        return {
            "success": True,
            "data": {"optimization": analysis},
            "message": f"💡 Melhor horário: {analysis['best_start_time']}. Poupa {analysis['savings_vs_peak']}!",
            "follow_up": [
                "Como programar o carregador?",
                "Comparar com tarifa simples",
                "Ver consumo detalhado"
            ]
        }
    
    def _charging_cost_analysis(self) -> Dict[str, Any]:
        """Analyze EV charging costs"""
        
        costs = {
            "home_charging_monthly": 85.50,
            "public_charging_monthly": 45.00,
            "total_monthly": 130.50,
            "vs_gasoline": "-€120/mês (poupança)",
            "cost_per_100km": "€4.20",
            "annual_projection": "€1,566"
        }
        
        return {
            "success": True,
            "data": {"costs": costs},
            "message": f"🔌 Gasta €{costs['total_monthly']}/mês (€{costs['vs_gasoline']} vs gasolina)",
            "follow_up": [
                "Como reduzir mais?",
                "Comparar tarifas",
                "Simular upgrade para trifásico"
            ]
        }
    
    def _find_charging_stations(self) -> Dict[str, Any]:
        """Find nearby charging stations"""
        
        stations = [
            {"name": "MOBI.E - Continente Benfica", "distance": "1.2 km", "available": True, "price": "€0.35/kWh"},
            {"name": "Tesla Supercharger - Colombo", "distance": "2.5 km", "available": True, "price": "€0.42/kWh"},
            {"name": "Ionity - A1", "distance": "5.8 km", "available": False, "price": "€0.65/kWh"}
        ]
        
        return {
            "success": True,
            "data": {"stations": stations},
            "message": f"📍 {len(stations)} postos encontrados. Mais próximo: {stations[0]['name']} ({stations[0]['distance']})",
            "follow_up": [
                "Navegar para lá",
                "Ver disponibilidade em tempo real",
                "Comparar preços"
            ]
        }
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Handle requests from other agents"""
        request_type = message.payload.get("request_type")
        
        if request_type == "get_ev_impact_on_bill":
            # Billing Agent quer saber impacto do EV
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "monthly_consumption_kwh": 280,
                    "monthly_cost": 85.50,
                    "peak_hour_usage": 0.15  # 15% em horário caro (bom!)
                }
            )
        
        return super()._handle_request(message)
