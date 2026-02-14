"""
Solar Agent - Photovoltaic systems and energy trading
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentMessage
from utils.logging_config import get_contextual_logger

class SolarAgent(BaseAgent):
    """
    Agent especializado em painéis fotovoltaicos e autoconsumo
    """
    
    def __init__(self):
        super().__init__(
            name="solar_agent",
            description="Monitorização solar, produção PV e venda à rede",
            capabilities=[
                "producao_diaria",
                "autoconsumo_vs_venda",
                "previsao_producao",
                "roi_solar",
                "alertas_performance"
            ]
        )
        self.logger = get_contextual_logger("solar_agent")
        self.logger.info("SolarAgent initialized")
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """Check if this agent can handle the query"""
        solar_keywords = [
            "painel", "solar", "fotovoltaico", "pv", "produção",
            "autoconsumo", "vender", "rede", "inversor", "kwh produzidos",
            "sun", "irradiância", "auto-consumo"
        ]
        
        query = context.get("query", "").lower() if context else ""
        matches = sum(1 for kw in solar_keywords if kw in query)
        
        confidence = min(matches / 2, 1.0)
        
        if intent in ["solar_production", "autoconsumo"]:
            confidence = max(confidence, 0.9)
        
        self.logger.debug("can_handle checked", query=query[:50], confidence=confidence, matches=matches)
            
        return confidence
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Process solar-related queries"""
        
        self.logger.info("Processing solar query", query=query[:100])
        
        if any(kw in query.lower() for kw in ["produzi", "produção", "hoje", "gerado"]):
            self.logger.debug("Routing to get_production")
            return self._get_production()
        
        elif any(kw in query.lower() for kw in ["vendi", "venda", "rede", "compensação"]):
            self.logger.debug("Routing to get_grid_sales")
            return self._get_grid_sales()
        
        elif any(kw in query.lower() for kw in ["poupança", "economia", "roi", "rentabilidade"]):
            self.logger.debug("Routing to calculate_savings")
            return self._calculate_savings()
        
        elif any(kw in query.lower() for kw in ["previsão", "amanhã", "sol", "tempo"]):
            self.logger.debug("Routing to forecast_production")
            return self._forecast_production()
        
        else:
            self.logger.info("No specific action matched, returning default response")
            return {
                "success": True,
                "data": {"agent": "solar"},
                "message": "Posso ajudar com monitorização solar, autoconsumo e vendas à rede. O que precisa?",
                "follow_up": [
                    "Produção de hoje",
                    "Quanto vendi à rede?",
                    "Poupança total"
                ]
            }
    
    def _get_production(self) -> Dict[str, Any]:
        """Get today's solar production"""
        
        self.logger.info("Getting solar production data")
        
        # Pedir dados de consumo ao Billing Agent para calcular cobertura
        self.send_message("billing_agent", "request", {
            "request_type": "get_consumption_pattern"
        })
        
        production = {
            "today_kwh": 18.5,
            "today_vs_expected": "+12%",
            "month_total": 420,
            "month_vs_last_year": "+8%",
            "peak_power_reached": "4.2 kW",
            "system_efficiency": "94%",
            "autoconsumed": 12.3,
            "sold_to_grid": 6.2
        }
        
        self.logger.info(
            "Solar production retrieved",
            today_kwh=production["today_kwh"],
            efficiency=production["system_efficiency"],
            autoconsumed=production["autoconsumed"]
        )
        
        return {
            "success": True,
            "data": {"production": production},
            "message": f"☀️ Hoje: {production['today_kwh']} kWh ({production['today_vs_expected']} vs esperado). Autoconsumo: {production['autoconsumed']} kWh",
            "follow_up": [
                "Ver gráfico detalhado",
                "Performance vs vizinhos",
                "Alerta se underperforming"
            ]
        }
    
    def _get_grid_sales(self) -> Dict[str, Any]:
        """Get energy sold to grid"""
        
        self.logger.info("Getting grid sales data")
        
        sales = {
            "month_sold_kwh": 185,
            "month_earnings": 23.50,
            "year_sold_kwh": 2100,
            "year_earnings": 266,
            "current_price_per_kwh": 0.127,
            "market_trend": "stable"
        }
        
        self.logger.info(
            "Grid sales retrieved",
            month_earnings=sales["month_earnings"],
            year_earnings=sales["year_earnings"]
        )
        
        return {
            "success": True,
            "data": {"sales": sales},
            "message": f"💰 Este mês vendeu {sales['month_sold_kwh']} kWh = €{sales['month_earnings']}. Este ano: €{sales['year_earnings']}",
            "follow_up": [
                "Previsão anual",
                "Histórico de preços",
                "Otimizar autoconsumo vs venda"
            ]
        }
    
    def _calculate_savings(self) -> Dict[str, Any]:
        """Calculate total savings from solar"""
        
        self.logger.info("Calculating solar savings")
        
        savings = {
            "monthly_savings": 89.50,
            "annual_savings": 1074,
            "lifetime_savings_25y": 26850,
            "payback_remaining_years": 4.5,
            "roi_percent": 12.5,
            "co2_avoided_kg": 1800
        }
        
        self.logger.info(
            "Solar savings calculated",
            monthly_savings=savings["monthly_savings"],
            roi=savings["roi_percent"],
            payback_years=savings["payback_remaining_years"]
        )
        
        return {
            "success": True,
            "data": {"savings": savings},
            "message": f"💚 Poupa €{savings['monthly_savings']}/mês. Retorno do investimento: {savings['payback_remaining_years']} anos restantes",
            "follow_up": [
                "Comparar com investimento alternativo",
                "Impacto ambiental detalhado",
                "Otimizar para máximo ROI"
            ]
        }
    
    def _forecast_production(self) -> Dict[str, Any]:
        """Forecast tomorrow's production based on weather"""
        
        self.logger.info("Forecasting solar production")
        
        forecast = {
            "tomorrow_kwh": 16.2,
            "confidence": 0.82,
            "weather": "Parcialmente nublado",
            "irradiance": "5.8 kWh/m²",
            "recommendation": "Bom dia para lavar painéis à tarde"
        }
        
        self.logger.info(
            "Solar forecast generated",
            tomorrow_kwh=forecast["tomorrow_kwh"],
            confidence=forecast["confidence"],
            weather=forecast["weather"]
        )
        
        return {
            "success": True,
            "data": {"forecast": forecast},
            "message": f"🔮 Amanhã: {forecast['tomorrow_kwh']} kWh previstos ({forecast['weather']})",
            "follow_up": [
                "Previsão 7 dias",
                "Melhores dias do mês",
                "Alerta de nuvem/poeira"
            ]
        }
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Handle requests from other agents"""
        request_type = message.payload.get("request_type")
        
        self.logger.info(
            "Handling inter-agent request",
            from_agent=message.from_agent,
            request_type=request_type
        )
        
        if request_type == "get_solar_contribution":
            # Billing Agent quer saber contribuição solar
            self.logger.debug("Returning solar contribution")
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "monthly_production": 420,
                    "autoconsume_rate": 0.65,
                    "grid_injection": 185,
                    "bill_reduction_percent": 45
                }
            )
        
        return super()._handle_request(message)