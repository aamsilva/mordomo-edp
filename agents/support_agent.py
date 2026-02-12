"""
Support Agent - Technical support and troubleshooting
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentMessage

class SupportAgent(BaseAgent):
    """
    Agent especializado em suporte técnico e avarias
    """
    
    def __init__(self):
        super().__init__(
            name="support_agent",
            description="Suporte técnico, avarias e intervenções",
            capabilities=[
                "reportar_avaria",
                "estado_intervencao",
                "faq_tecnico",
                "agendar_tecnico"
            ]
        )
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """Check if this agent can handle the query"""
        support_keywords = [
            "avaria", "problema", "não funciona", "sem luz",
            "técnico", "intervenção", "suporte", "ajuda técnica",
            "falha", "disjuntor", "corte"
        ]
        
        query = context.get("query", "").lower() if context else ""
        matches = sum(1 for kw in support_keywords if kw in query)
        
        confidence = min(matches / 2, 1.0)
        
        if intent in ["report_fault", "technical_support"]:
            confidence = max(confidence, 0.9)
            
        return confidence
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Process support-related queries"""
        
        if any(kw in query.lower() for kw in ["avaria", "problema", "não funciona"]):
            return self._report_fault()
        
        elif any(kw in query.lower() for kw in ["técnico", "intervenção", "estado"]):
            return self._check_intervention_status()
        
        else:
            return {
                "success": True,
                "data": {"agent": "support"},
                "message": "Posso ajudar com avarias, agendar técnicos ou verificar estado de intervenções. O que precisa?",
                "follow_up": [
                    "Reportar avaria",
                    "Ver estado de intervenção",
                    "FAQ técnico"
                ]
            }
    
    def _report_fault(self) -> Dict[str, Any]:
        """Report a technical fault"""
        
        return {
            "success": True,
            "data": {
                "ticket_id": "AV-2024-001",
                "status": "registered",
                "priority": "medium",
                "estimated_response": "4 horas"
            },
            "message": "🎫 Avaria registada com ID AV-2024-001. Um técnico será enviado nas próximas 4 horas.",
            "follow_up": [
                "Verificar estado",
                "Cancelar pedido",
                "Contactar técnico"
            ]
        }
    
    def _check_intervention_status(self) -> Dict[str, Any]:
        """Check status of ongoing intervention"""
        
        return {
            "success": True,
            "data": {
                "ticket_id": "INT-2024-045",
                "status": "in_progress",
                "technician": "João Silva",
                "estimated_arrival": "14:30",
                "current_location": "A 2 km do destino"
            },
            "message": "🔧 Técnico João Silva em deslocação. Chegada estimada: 14:30 (2 km de distância).",
            "follow_up": [
                "Ver localização em tempo real",
                "Contactar técnico",
                "Reagendar"
            ]
        }
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Handle requests from other agents"""
        request_type = message.payload.get("request_type")
        
        if request_type == "get_technician_availability":
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "next_available_slot": "2024-02-12 10:00",
                    "technicians_on_duty": 3
                }
            )
        
        return super()._handle_request(message)
