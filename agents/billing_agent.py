"""
Billing Agent - Handles invoices, payments, consumption history
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentMessage
from utils.logging_config import get_contextual_logger

class BillingAgent(BaseAgent):
    """
    Agent especializado em faturação e consumo
    """
    
    def __init__(self):
        super().__init__(
            name="billing_agent",
            description="Gestão de faturas, pagamentos e histórico de consumo",
            capabilities=[
                "consultar_fatura",
                "historico_consumo",
                "proxima_fatura",
                "metodos_pagamento",
                "comparativo_consumo"
            ]
        )
        self.logger = get_contextual_logger("billing_agent")
        
        # Mock data - substituir por API real EDP
        self.mock_invoices = {
            "latest": {
                "number": "FT-2024-001",
                "amount": 127.50,
                "date": "2024-01-15",
                "consumption_kwh": 450,
                "status": "pending",
                "due_date": "2024-02-05"
            },
            "FT-2024-001": {
                "number": "FT-2024-001",
                "amount": 127.50,
                "date": "2024-01-15",
                "consumption_kwh": 450,
                "status": "pending",
                "due_date": "2024-02-05"
            }
        }
        
        self.logger.info("BillingAgent initialized")
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """Confidence scoring for intent matching"""
        billing_keywords = [
            "fatura", "factura", "conta", "pagar", "valor", "consumo",
            "kwh", "eletricidade", "gás", "referência", "mb",
            "débito", "direto", "preço", "tarifa", "gastei", "gasto",
            "mês", "mes", "este mês", "último mês", "faturação",
            "montante", "total", "paguei", "custo", "despesa"
        ]
        
        query = context.get("query", "").lower() if context else ""
        matches = sum(1 for kw in billing_keywords if kw in query)
        
        # Normalizar para 0.0-1.0 (mais permissivo: 1 match = 50%)
        confidence = min(matches / 2, 1.0)
        
        # Se tem pelo menos 1 match, garantir mínimo de 0.4
        if matches > 0:
            confidence = max(confidence, 0.4)
        
        # Boost para intents explícitos
        if intent in ["get_invoice", "get_consumption"]:
            confidence = max(confidence, 0.9)
        
        self.logger.debug("can_handle checked", query=query[:50], confidence=confidence, matches=matches)
            
        return confidence
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Process billing-related queries"""
        context = context or {}
        query_lower = query.lower()
        
        self.logger.info("Processing billing query", query=query[:100])
        
        # Verificar se há parâmetros específicos
        invoice_number = context.get("invoice_number", "latest")
        period = context.get("period", "current")
        
        # Determinar ação específica
        if any(kw in query_lower for kw in ["fatura", "conta", "valor", "pagar"]):
            self.logger.debug("Routing to get_invoice", invoice_number=invoice_number)
            return self._get_invoice(invoice_number)
        
        elif any(kw in query_lower for kw in ["consumo", "kwh", "gastei", "gasto"]):
            self.logger.debug("Routing to get_consumption", period=period)
            return self._get_consumption(period)
        
        elif any(kw in query_lower for kw in ["próxima", "proxima", "previsão", "previsao", "vai custar", "estimativa"]):
            self.logger.debug("Routing to predict_next_bill")
            return self._predict_next_bill()
        
        elif any(kw in query_lower for kw in ["comparar", "comparação", "comparacao", "diferença", "difereca", "anterior", "mês passado", "mes passado"]):
            self.logger.debug("Routing to compare_consumption")
            return self._compare_consumption()
        
        elif any(kw in query_lower for kw in ["detalhes", "detalhe", "especificação", "especificacao", "itemizado"]):
            self.logger.debug("Routing to get_detailed_consumption")
            return self._get_detailed_consumption()
        
        elif any(kw in query_lower for kw in ["pagamento automático", "pagamento automatico", "débito direto", "debito direto", "automatizar"]):
            self.logger.debug("Routing to setup_automatic_payment")
            return self._setup_automatic_payment()
        
        else:
            self.logger.info("No specific action matched, returning default response")
            return {
                "success": True,
                "data": {"agent": "billing"},
                "message": "Posso ajudar com faturas, consumo ou previsões. O que precisa?",
                "follow_up": ["Ver última fatura", "Consumo deste mês", "Previsão próxima fatura"]
            }
    
    def _get_invoice(self, invoice_number: str) -> Dict[str, Any]:
        """Retrieve invoice details"""
        inv = self.mock_invoices.get(invoice_number, self.mock_invoices["latest"])
        
        self.logger.info(
            "Invoice retrieved",
            invoice_id=inv["number"],
            amount=inv["amount"],
            status=inv["status"]
        )
        
        # Broadcast context to other agents
        self.broadcast_context({
            "last_invoice_amount": inv["amount"],
            "last_consumption": inv["consumption_kwh"],
            "customer_segment": "residential" if inv["amount"] < 200 else "commercial"
        })
        
        return {
            "success": True,
            "data": {"invoice": inv},
            "message": f"Fatura {inv['number']}: €{inv['amount']}",
            "follow_up": [
                "Comparar com mês anterior",
                "Ver detalhes de consumo",
                "Configurar pagamento automático"
            ]
        }
    
    def _get_consumption(self, period: str) -> Dict[str, Any]:
        """Get consumption data"""
        # Mock consumption history
        consumption_data = {
            "current_month": 450,
            "previous_month": 380,
            "same_month_last_year": 420,
            "trend": "+18% vs mês anterior",
            "projection_next_month": 480
        }
        
        self.logger.info(
            "Consumption data retrieved",
            current_month=consumption_data["current_month"],
            trend=consumption_data["trend"]
        )
        
        return {
            "success": True,
            "data": {"consumption": consumption_data},
            "message": f"Consumo: {consumption_data['current_month']} kWh ({consumption_data['trend']})",
            "follow_up": [
                "Porque aumentou?",
                "Comparar com vizinhos",
                "Dicas para reduzir"
            ]
        }
    
    def _predict_next_bill(self) -> Dict[str, Any]:
        """Predict next bill based on consumption trends"""
        prediction = {
            "estimated_amount": 135.0,
            "confidence": 0.85,
            "factors": [
                "Inverno = maior consumo",
                "Tendência crescente (+5%)",
                "Previsão meteorológica: frio prolongado"
            ]
        }
        
        self.logger.info(
            "Next bill predicted",
            estimated_amount=prediction["estimated_amount"],
            confidence=prediction["confidence"]
        )
        
        return {
            "success": True,
            "data": {"prediction": prediction},
            "message": f"Próxima fatura estimada: €{prediction['estimated_amount']} (confiança: {prediction['confidence']*100:.0f}%)",
            "follow_up": [
                "Como reduzir?",
                "Simular mudança de tarifa",
                "Alertas de consumo"
            ]
        }
    
    def _compare_consumption(self) -> Dict[str, Any]:
        """Compare consumption with previous month"""
        comparison = {
            "current_month": 450,
            "previous_month": 380,
            "difference_kwh": 70,
            "difference_percent": "+18.4%",
            "current_amount": 127.50,
            "previous_amount": 108.20,
            "amount_difference": 19.30,
            "reasons": [
                "Maior utilização de aquecimento (inverno)",
                "Mais dias no período de faturação",
                "Possível uso de equipamentos novos"
            ]
        }
        
        self.logger.info(
            "Consumption comparison generated",
            difference_percent=comparison["difference_percent"],
            amount_difference=comparison["amount_difference"]
        )
        
        return {
            "success": True,
            "data": {"comparison": comparison},
            "message": f"Comparação: Consumo subiu {comparison['difference_percent']} ({comparison['difference_kwh']} kWh). Fatura aumentou €{comparison['amount_difference']}.",
            "follow_up": [
                "Ver detalhes de consumo",
                "Dicas para reduzir",
                "Previsão próxima fatura"
            ]
        }
    
    def _get_detailed_consumption(self) -> Dict[str, Any]:
        """Get detailed consumption breakdown"""
        details = {
            "total_kwh": 450,
            "breakdown": [
                {"category": "Aquecimento", "kwh": 180, "percent": 40, "cost": 51.00},
                {"category": "Águas quentes", "kwh": 90, "percent": 20, "cost": 25.50},
                {"category": "Eletrodomésticos", "kwh": 112, "percent": 25, "cost": 31.75},
                {"category": "Iluminação", "kwh": 45, "percent": 10, "cost": 12.75},
                {"category": "Outros", "kwh": 23, "percent": 5, "cost": 6.50}
            ]
        }
        
        self.logger.info(
            "Detailed consumption retrieved",
            total_kwh=details["total_kwh"],
            categories=len(details["breakdown"])
        )
        
        return {
            "success": True,
            "data": {"details": details},
            "message": f"Maior consumo: {details['breakdown'][0]['category']} ({details['breakdown'][0]['percent']}% = €{details['breakdown'][0]['cost']}).",
            "follow_up": [
                "Comparar com mês anterior",
                "Dicas para reduzir",
                "Simular mudança de tarifa"
            ]
        }
    
    def _setup_automatic_payment(self) -> Dict[str, Any]:
        """Setup automatic payment info"""
        self.logger.info("Automatic payment information requested")
        
        return {
            "success": True,
            "data": {
                "payment_methods": [
                    {"type": "Débito Direto", "description": "Pagamento automático na data de vencimento"}
                ]
            },
            "message": "Posso configurar débito direto para pagamento automático. Deseja ativar?",
            "follow_up": [
                "Ativar débito direto",
                "Ver outras opções"
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
        
        if request_type == "get_customer_value":
            # EV Agent quer saber se cliente é high-value
            last_invoice = self.mock_invoices["latest"]
            self.logger.debug("Returning customer value", annual_value=last_invoice["amount"] * 12)
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "annual_value": last_invoice["amount"] * 12,
                    "segment": "premium" if last_invoice["amount"] > 150 else "standard"
                }
            )
        
        elif request_type == "get_consumption_pattern":
            self.logger.debug("Returning consumption pattern")
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "peak_hours": ["19:00", "20:00", "21:00"],
                    "off_peak_usage": 0.35,
                    "monthly_trend": "increasing"
                }
            )
        
        return super()._handle_request(message)