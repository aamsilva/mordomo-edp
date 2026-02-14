"""
Support Agent - Technical support, ticketing, and technician scheduling
Suporte técnico, avarias e agendamento de intervenções
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import re
from .base_agent import BaseAgent, AgentMessage
from utils.logging_config import get_contextual_logger

class SupportAgent(BaseAgent):
    """
    Agent especializado em suporte técnico, avarias e agendamento
    """
    
    def __init__(self):
        super().__init__(
            name="support_agent",
            description="Suporte técnico, avarias e agendamento de intervenções",
            capabilities=[
                "reportar_avaria",
                "estado_ticket",
                "agendar_tecnico",
                "faq_tecnico",
                "verificar_corte",
                "diagnostico_basico"
            ]
        )
        self.logger = get_contextual_logger("support_agent")
        
        # Mock data for tickets
        self.mock_tickets = {
            "AV-2024-001": {
                "id": "AV-2024-001",
                "type": "contador",
                "description": "Contador não regista consumo",
                "status": "in_progress",
                "priority": "high",
                "created_at": "2024-02-10T09:00:00",
                "technician": "João Silva",
                "estimated_arrival": "14:30",
                "current_location": "A 2 km do destino",
                "location": "Rua das Flores, 45, Lisboa"
            },
            "AV-2024-002": {
                "id": "AV-2024-002",
                "type": "quadro_eletrico",
                "description": "Disjuntor salta frequentemente",
                "status": "open",
                "priority": "medium",
                "created_at": "2024-02-14T16:30:00",
                "technician": None,
                "estimated_arrival": None,
                "current_location": None,
                "location": "Av. da Liberdade, 120, Lisboa"
            },
            "AV-2024-003": {
                "id": "AV-2024-003",
                "type": "falta_luz",
                "description": "Sem energia em toda a casa",
                "status": "resolved",
                "priority": "high",
                "created_at": "2024-02-08T20:00:00",
                "technician": "Mário Santos",
                "resolution": "Reposição de fusível no quadro",
                "location": "Rua Augusta, 15, Lisboa"
            },
            "AV-2024-004": {
                "id": "AV-2024-004",
                "type": "tomada",
                "description": "Tomada da cozinha não funciona",
                "status": "closed",
                "priority": "low",
                "created_at": "2024-02-01T10:00:00",
                "technician": "Ana Costa",
                "resolution": "Substituição da tomada",
                "location": "Praça do Comércio, 5, Lisboa"
            }
        }
        
        # Mock technician availability
        self.technician_availability = {
            "today": {
                "slots": ["15:00", "16:00", "17:00"],
                "technicians_on_duty": 3
            },
            "tomorrow": {
                "slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                "technicians_on_duty": 5
            },
            "next_week": {
                "slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"],
                "technicians_on_duty": 5
            }
        }
        
        # FAQ Database
        self.faq_database = {
            "sem_luz": {
                "question": "O que faço se não tenho luz?",
                "answer": """Verifique estes passos:
1. Confirme se há corte na sua zona (consulte app EDP ou ligue 800 10 10 10)
2. Verifique o disjuntor geral no quadro elétrico
3. Confirme se há luz na rua
4. Se o problema persistir, reporte uma avaria""",
                "keywords": ["sem luz", "falta luz", "corte", "escuro"]
            },
            "disjuntor": {
                "question": "Porque é que o disjuntor salta?",
                "answer": """O disjuntor pode saltar por:
• Sobrecarga: muitos equipamentos ligados ao mesmo tempo
• Curto-circuito: contacto entre fios
• Avaria num eletrodoméstico
• Disjuntor deteriorado

Dica: Desligue alguns equipamentos e tente religar. Se continuar a saltar, contacte um eletricista.""",
                "keywords": ["disjuntor", "salta", "desarma", "quadro"]
            },
            "contador": {
                "question": "O contador está avariado, o que fazer?",
                "answer": """Se o contador não funciona:
1. Verifique se há luz no display
2. Confirme se o código de erro (se houver)
3. Reporte a avaria para substituição gratuita

⚠️ Não tente abrir o contador - é perigoso e ilegal""",
                "keywords": ["contador", "medidor", "display", "avariado"]
            },
            "potencia": {
                "question": "Como saber se preciso de mais potência?",
                "answer": """Sinais de que precisa de mais potência:
• Disjuntor salta frequentemente
• Não pode usar vários equipamentos simultaneamente
• As luzes piscam quando liga eletrodomésticos

Contacte-nos para aumentar a potência contratada.""",
                "keywords": ["potência", "potencia", "aumentar", "mais potência"]
            },
            "fatura_alta": {
                "question": "Porque está a minha fatura tão alta?",
                "answer": """Possíveis causas de fatura alta:
• Alteração de tarifa ou preço da energia
• Mudança de hábitos de consumo
• Equipamentos novos ou defeituosos
• Fuga de corrente
• Estimativa incorreta do consumo

Consulte o agente de Faturação para análise detalhada.""",
                "keywords": ["fatura alta", "conta alta", "caro", "aumentou"]
            },
            "tomada": {
                "question": "Tomada não funciona, o que fazer?",
                "answer": """Verificações rápidas:
1. Teste outro equipamento na mesma tomada
2. Verifique o disjuntor específico
3. Confirme se há luz noutras tomadas
4. Se só essa tomada não funciona, pode ser avaria na instalação interna

⚠️ Para avarias internas, necessita de eletricista particular.""",
                "keywords": ["tomada", "socket", "não funciona", "sem corrente"]
            },
            "horas": {
                "question": "Quais são as horas de vazio?",
                "answer": """Horário bi-horário (vazio):
• Diário: 00h00-08h00
• Fim de semana e feriados: 24h

Horário tri-horário:
• Fora de ponta: 00h00-07h30, 09h30-11h30, 13h00-19h30, 22h00-24h00
• Cheias: 09h30-12h30, 19h30-21h00
• Ponta: 11h30-13h00, 21h00-22h00""",
                "keywords": ["vazio", "horas", "bi-horário", "tri-horário"]
            }
        }
        
        # Ticket counter for new IDs
        self.ticket_counter = 5
        
        self.logger.info("SupportAgent initialized", tickets=len(self.mock_tickets))
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """Check if this agent can handle the query"""
        support_keywords = [
            "avaria", "problema", "não funciona", "sem luz", "falta luz",
            "técnico", "intervenção", "suporte", "ajuda técnica",
            "falha", "disjuntor", "corte", "contador", "quadro",
            "ticket", "estado", "agendar", "visita", "arranjar",
            "avariado", "queimado", "sem energia"
        ]
        
        query = context.get("query", "").lower() if context else ""
        matches = sum(1 for kw in support_keywords if kw in query)
        
        confidence = min(matches / 2, 1.0)
        
        if matches > 0:
            confidence = max(confidence, 0.4)
        
        if intent in ["report_fault", "technical_support", "check_ticket", "schedule_visit"]:
            confidence = max(confidence, 0.9)
            
        self.logger.debug("can_handle checked", query=query[:50], confidence=confidence)
        return confidence
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Process support-related queries"""
        context = context or {}
        query_lower = query.lower()
        
        self.logger.info("Processing support query", query=query[:100])
        
        # Report issue / avaria
        if any(kw in query_lower for kw in ["avaria", "problema", "não funciona", "avariado", "queimado", "reportar"]):
            issue_type = self._detect_issue_type(query_lower)
            return self._report_issue(issue_type, query, context.get("location"))
        
        # Check ticket status
        elif any(kw in query_lower for kw in ["estado", "ticket", "intervenção", "andamento", "situação"]):
            ticket_id = self._extract_ticket_id(query)
            return self._check_ticket_status(ticket_id)
        
        # Schedule technician visit
        elif any(kw in query_lower for kw in ["agendar", "marcar", "técnico", "visita", "tecnico", "quando", "disponível"]):
            preferred_date = self._extract_date(query_lower)
            issue_type = self._detect_issue_type(query_lower)
            return self._schedule_visit(preferred_date, issue_type)
        
        # FAQ / common questions
        elif any(kw in query_lower for kw in ["faq", "pergunta", "dúvida", "duvida", "como", "o que faço", "porque"]):
            return self._get_faq(query_lower)
        
        # No light / corte
        elif any(kw in query_lower for kw in ["sem luz", "falta luz", "corte", "escuro"]):
            return self._handle_no_power(query_lower)
        
        # Default help response
        else:
            return {
                "success": True,
                "data": {"agent": "support"},
                "message": "Sou o agente de Suporte Técnico. Posso ajudar com:\n• Reportar avarias (contador, quadro, falta de luz)\n• Ver estado de tickets\n• Agendar visitas de técnicos\n• Responder a dúvidas técnicas comuns\n\nO que precisa?",
                "follow_up": [
                    "Reportar avaria",
                    "Ver estado do meu ticket",
                    "Agendar técnico",
                    "Não tenho luz - ajuda!"
                ]
            }
    
    def _detect_issue_type(self, query: str) -> str:
        """Detect the type of issue from query"""
        if any(kw in query for kw in ["contador", "medidor", "contadores"]):
            return "contador"
        elif any(kw in query for kw in ["quadro", "disjuntor", "fusível", "fusiveis"]):
            return "quadro_eletrico"
        elif any(kw in query for kw in ["sem luz", "falta luz", "corte", "escuro"]):
            return "falta_luz"
        elif any(kw in query for kw in ["tomada", "socket", "plug"]):
            return "tomada"
        elif any(kw in query for kw in ["potência", "potencia"]):
            return "potencia"
        else:
            return "outro"
    
    def _extract_ticket_id(self, query: str) -> Optional[str]:
        """Extract ticket ID from query"""
        # Look for pattern AV-2024-XXX or similar
        patterns = [
            r'AV-\d{4}-\d{3}',
            r'INT-\d{4}-\d{3}',
            r'ticket\s+([A-Z]+-\d{4}-\d{3})',
            r'([A-Z]+-\d{4}-\d{3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                ticket = match.group(1) if match.groups() else match.group(0)
                return ticket.upper()
        
        return None
    
    def _extract_date(self, query: str) -> str:
        """Extract preferred date from query"""
        if any(kw in query for kw in ["hoje"]):
            return "today"
        elif any(kw in query for kw in ["amanhã", "amanha"]):
            return "tomorrow"
        elif any(kw in query for kw in ["segunda", "segunda-feira"]):
            return "monday"
        elif any(kw in query for kw in ["terça", "terca", "terça-feira"]):
            return "tuesday"
        elif any(kw in query for kw in ["quarta", "quarta-feira"]):
            return "wednesday"
        elif any(kw in query for kw in ["quinta", "quinta-feira"]):
            return "thursday"
        elif any(kw in query for kw in ["sexta", "sexta-feira"]):
            return "friday"
        else:
            return "next_available"
    
    def _report_issue(self, issue_type: str, description: str, location: str = None) -> Dict[str, Any]:
        """Report a technical fault and create ticket"""
        
        # Generate new ticket ID
        ticket_id = f"AV-2024-{self.ticket_counter:03d}"
        self.ticket_counter += 1
        
        # Determine priority based on issue type
        priority = "high" if issue_type in ["falta_luz", "contador"] else "medium"
        
        # Create ticket
        ticket = {
            "id": ticket_id,
            "type": issue_type,
            "description": description[:100],
            "status": "open",
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "technician": None,
            "estimated_arrival": None,
            "current_location": None,
            "location": location or "Morada do cliente"
        }
        
        self.mock_tickets[ticket_id] = ticket
        
        self.logger.info(
            "Issue reported",
            ticket_id=ticket_id,
            issue_type=issue_type,
            priority=priority
        )
        
        # Determine response time based on priority
        if priority == "high":
            estimated_response = "4 horas"
            emoji = "🔴"
        else:
            estimated_response = "24 horas"
            emoji = "🟡"
        
        # Check with billing agent if there are pending issues
        self._request_billing_check()
        
        return {
            "success": True,
            "data": {
                "ticket_id": ticket_id,
                "status": "open",
                "priority": priority,
                "issue_type": issue_type,
                "estimated_response": estimated_response
            },
            "message": f"{emoji} Avaria registada com ID {ticket_id}.\n\nTipo: {issue_type.replace('_', ' ').title()}\nPrioridade: {priority.upper()}\nTempo estimado de resposta: {estimated_response}\n\nUm técnico será contactado em breve.",
            "follow_up": [
                "Verificar estado do ticket",
                "Agendar visita para amanhã",
                "Cancelar pedido",
                "Outras dúvidas técnicas"
            ]
        }
    
    def _check_ticket_status(self, ticket_id: str = None) -> Dict[str, Any]:
        """Check status of an existing ticket"""
        
        if ticket_id and ticket_id in self.mock_tickets:
            ticket = self.mock_tickets[ticket_id]
        else:
            # Return most recent open ticket
            open_tickets = [t for t in self.mock_tickets.values() if t["status"] in ["open", "in_progress"]]
            if open_tickets:
                ticket = sorted(open_tickets, key=lambda x: x["created_at"], reverse=True)[0]
                ticket_id = ticket["id"]
            else:
                # Return most recent closed ticket
                all_tickets = sorted(self.mock_tickets.values(), key=lambda x: x["created_at"], reverse=True)
                ticket = all_tickets[0]
                ticket_id = ticket["id"]
        
        self.logger.info("Ticket status checked", ticket_id=ticket_id, status=ticket["status"])
        
        # Format status
        status_map = {
            "open": ("Aberto", "🟡"),
            "in_progress": ("Em andamento", "🔵"),
            "resolved": ("Resolvido", "✅"),
            "closed": ("Fechado", "📋")
        }
        
        status_text, emoji = status_map.get(ticket["status"], ("Desconhecido", "❓"))
        
        message = f"{emoji} Ticket {ticket_id}\n\n"
        message += f"Estado: {status_text}\n"
        message += f"Tipo: {ticket['type'].replace('_', ' ').title()}\n"
        message += f"Descrição: {ticket['description']}\n"
        message += f"Prioridade: {ticket['priority'].upper()}\n"
        
        if ticket.get("technician"):
            message += f"\n👨‍🔧 Técnico: {ticket['technician']}\n"
        
        if ticket.get("estimated_arrival"):
            message += f"⏰ Chegada estimada: {ticket['estimated_arrival']}\n"
        
        if ticket.get("current_location"):
            message += f"📍 Localização: {ticket['current_location']}\n"
        
        if ticket.get("resolution"):
            message += f"\n✓ Resolução: {ticket['resolution']}\n"
        
        follow_up = []
        if ticket["status"] in ["open", "in_progress"]:
            follow_up = ["Ver localização em tempo real", "Contactar técnico", "Reagendar", "Cancelar ticket"]
        else:
            follow_up = ["Reportar nova avaria", "Ver histórico completo", "Avaliar serviço"]
        
        return {
            "success": True,
            "data": {"ticket": ticket},
            "message": message,
            "follow_up": follow_up
        }
    
    def _schedule_visit(self, preferred_date: str, issue_type: str) -> Dict[str, Any]:
        """Schedule a technician visit"""
        
        self.logger.info("Scheduling visit", preferred_date=preferred_date, issue_type=issue_type)
        
        # Get availability
        if preferred_date in ["today", "hoje"]:
            slots = self.technician_availability["today"]["slots"]
            day_text = "hoje"
        elif preferred_date in ["tomorrow", "amanha", "amanhã"]:
            slots = self.technician_availability["tomorrow"]["slots"]
            day_text = "amanhã"
        else:
            slots = self.technician_availability["next_week"]["slots"]
            day_text = "próxima semana"
        
        if not slots:
            return {
                "success": False,
                "data": {},
                "message": "❌ Não há slots disponíveis para essa data. Posso agendar para outro dia?",
                "follow_up": ["Agendar para amanhã", "Agendar para próxima semana", "Ver disponibilidade"]
            }
        
        # Create a scheduled ticket
        ticket_id = f"AV-2024-{self.ticket_counter:03d}"
        self.ticket_counter += 1
        
        scheduled_slot = slots[0]  # First available slot
        technician = random.choice(["João Silva", "Mário Santos", "Ana Costa", "Pedro Ferreira"])
        
        ticket = {
            "id": ticket_id,
            "type": issue_type or "visita_tecnica",
            "description": f"Visita técnica agendada para {day_text}",
            "status": "open",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "technician": technician,
            "scheduled_date": day_text,
            "scheduled_time": scheduled_slot,
            "location": "Morada do cliente"
        }
        
        self.mock_tickets[ticket_id] = ticket
        
        return {
            "success": True,
            "data": {
                "ticket_id": ticket_id,
                "scheduled_date": day_text,
                "scheduled_time": scheduled_slot,
                "technician": technician
            },
            "message": f"✅ Visita técnica agendada!\n\n📅 Data: {day_text.title()}\n⏰ Hora: {scheduled_slot}\n👨‍🔧 Técnico: {technician}\n🎫 Ticket: {ticket_id}\n\nO técnico entrará em contacto 30 minutos antes da chegada.",
            "follow_up": [
                "Reagendar visita",
                "Cancelar visita",
                "Adicionar instruções",
                "Confirmar endereço"
            ]
        }
    
    def _get_faq(self, query: str) -> Dict[str, Any]:
        """Answer common technical questions"""
        
        self.logger.info("FAQ requested", query=query[:50])
        
        # Match query to FAQ
        best_match = None
        best_score = 0
        
        for faq_id, faq in self.faq_database.items():
            score = sum(1 for kw in faq["keywords"] if kw in query)
            if score > best_score:
                best_score = score
                best_match = faq
        
        if best_match and best_score > 0:
            return {
                "success": True,
                "data": {"faq_id": faq_id, "matched": True},
                "message": f"❓ {best_match['question']}\n\n{best_match['answer']}",
                "follow_up": [
                    "Ainda tenho dúvidas",
                    "Reportar avaria relacionada",
                    "Falar com técnico",
                    "Outra pergunta"
                ]
            }
        
        # Return list of common FAQs
        faq_list = "\n".join([f"• {faq['question']}" for faq in self.faq_database.values()])
        
        return {
            "success": True,
            "data": {"matched": False},
            "message": f"Posso ajudar com estas questões comuns:\n\n{faq_list}\n\nQual a sua dúvida?",
            "follow_up": list(self.faq_database.keys())[:5]
        }
    
    def _handle_no_power(self, query: str) -> Dict[str, Any]:
        """Handle no power situations with diagnostic"""
        
        self.logger.info("No power situation reported")
        
        # Check if there's a known outage in the area (simulated)
        has_known_outage = random.random() < 0.3  # 30% chance
        
        if has_known_outage:
            return {
                "success": True,
                "data": {"outage_detected": True},
                "message": """⚠️ Detetámos um corte de energia na sua zona!

Estamos já a trabalhar na resolução.
Tempo estimado de reposição: 2-3 horas

Agradecemos a compreensão.

📞 Para emergências: 800 10 10 10""",
                "follow_up": [
                    "Receber notificação quando voltar",
                    "Reportar problema diferente",
                    "Ver estado de outros cortes"
                ]
            }
        
        # Provide diagnostic steps
        return {
            "success": True,
            "data": {"outage_detected": False},
            "message": """💡 Verifique estes passos para diagnosticar o problema:

1️⃣ Verifique se há luz na rua (vizinhos, postes)
2️⃣ Confirme o disjuntor geral no seu quadro elétrico
3️⃣ Verifique se há algum código de erro no contador
4️⃣ Contacte-nos se o problema persistir

Se for apenas na sua casa, pode precisar de um técnico.""",
            "follow_up": [
                "Já verifiquei tudo - preciso de técnico",
                "Como verificar o disjuntor?",
                "Qual o número de emergência?",
                "Há corte na minha zona?"
            ]
        }
    
    def _request_billing_check(self):
        """Request billing agent to check for pending issues"""
        self.logger.debug("Requesting billing check")
        self.send_message(
            "billing_agent",
            "request",
            {"request_type": "check_pending_issues"}
        )
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Handle requests from other agents"""
        request_type = message.payload.get("request_type")
        
        self.logger.info(
            "Handling inter-agent request",
            from_agent=message.from_agent,
            request_type=request_type
        )
        
        if request_type == "get_technician_availability":
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "next_available_slot": "2024-02-15 10:00",
                    "technicians_on_duty": 5,
                    "slots_today": self.technician_availability["today"]["slots"],
                    "slots_tomorrow": self.technician_availability["tomorrow"]["slots"]
                }
            )
        
        elif request_type == "check_pending_tickets":
            open_tickets = [t for t in self.mock_tickets.values() if t["status"] in ["open", "in_progress"]]
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "has_pending_tickets": len(open_tickets) > 0,
                    "ticket_count": len(open_tickets),
                    "tickets": [{"id": t["id"], "status": t["status"]} for t in open_tickets]
                }
            )
        
        elif request_type == "get_customer_issues_history":
            return AgentMessage(
                from_agent=self.name,
                to_agent=message.from_agent,
                message_type="response",
                payload={
                    "total_tickets_30d": 2,
                    "recurring_issues": ["disjuntor"],
                    "avg_resolution_time": "6 horas"
                }
            )
        
        return super()._handle_request(message)
