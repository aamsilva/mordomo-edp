"""
Orchestrator - Coordinates all agents in the Multi-Agent System
"""
from typing import Dict, Any, List, Optional, Tuple
from .base_agent import BaseAgent, AgentMessage
import sys
sys.path.insert(0, '..')
from semantic_router import semantic_router

class Orchestrator:
    """
    Central coordinator for the Multi-Agent System
    Responsibilities:
    1. Register and manage all agents
    2. Route user queries to appropriate agent(s)
    3. Handle multi-agent collaboration
    4. Aggregate responses from multiple agents
    5. Manage shared context/state
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_context: Dict[str, Any] = {
            "conversation_history": [],
            "user_profile": {},
            "session_data": {}
        }
        self.message_queue: List[AgentMessage] = []
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        agent.message_bus = self  # Give agent access to message routing
        print(f"✅ Agent registered: {agent.name}")
        
    def get_all_agents(self) -> List[Dict]:
        """Get info about all registered agents"""
        return [agent.get_info() for agent in self.agents.values()]
    
    def route_query(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """
        Main entry point: Route user query to appropriate agent(s)
        
        Returns:
        {
            "primary_agent": str,
            "collaborating_agents": list,
            "response": dict,
            "context_updates": dict
        }
        """
        user_context = user_context or {}
        user_context["query"] = query
        
        # Store in conversation history
        self.shared_context["conversation_history"].append({
            "role": "user",
            "content": query,
            "timestamp": user_context.get("timestamp")
        })
        
        # Step 1: Find best agent(s) for this query
        candidates = self._select_agents(query, user_context)
        
        if not candidates:
            # No agent confident enough - use fallback
            return self._fallback_response(query)
        
        # Step 2: Process with primary agent
        primary_agent = candidates[0]
        primary_response = primary_agent.process(query, user_context)
        
        # Step 3: Check if we need collaboration
        collaborating_agents = []
        if len(candidates) > 1:
            # Secondary agents provide additional context
            for agent in candidates[1:]:
                collab_response = agent.process(query, user_context)
                collaborating_agents.append({
                    "agent": agent.name,
                    "data": collab_response.get("data", {})
                })
        
        # Step 4: Check if primary agent requested collaboration
        if self._needs_collaboration(primary_response):
            collab_data = self._request_collaboration(primary_agent, primary_response)
            primary_response = self._merge_responses(primary_response, collab_data)
        
        # Step 5: Update shared context
        self._update_context_from_response(primary_response)
        
        # Step 6: Store assistant response in history
        self.shared_context["conversation_history"].append({
            "role": "assistant",
            "content": primary_response.get("message", ""),
            "agent": primary_agent.name,
            "timestamp": user_context.get("timestamp")
        })
        
        return {
            "primary_agent": primary_agent.name,
            "collaborating_agents": collaborating_agents,
            "response": primary_response,
            "context": self.shared_context
        }
    
    def _select_agents(self, query: str, context: Dict) -> List[BaseAgent]:
        """
        Select best agent(s) using semantic routing (LLM-based)
        Falls back to keyword matching if LLM fails
        """
        # 🧠 SEMANTIC ROUTING: Use LLM to classify intent
        agent_name, confidence = semantic_router.route(query)
        
        if agent_name != "none" and agent_name in self.agents and confidence > 0.3:
            selected_agent = self.agents[agent_name]
            print(f"🧠 Semantic routing: {agent_name} (confidence: {confidence:.2f})")
            return [selected_agent]
        
        # Fallback to keyword-based routing
        print(f"⚠️ Semantic routing failed, using keyword fallback")
        scored_agents = []
        
        for name, agent in self.agents.items():
            conf = agent.can_handle("", context)
            if conf > 0.3:
                scored_agents.append((conf, agent))
        
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        selected = [agent for _, agent in scored_agents]
        
        if len(scored_agents) >= 2:
            if scored_agents[0][0] - scored_agents[1][0] < 0.2:
                return selected[:2]
        
        return selected[:1] if selected else []
    
    def _needs_collaboration(self, response: Dict) -> bool:
        """Check if response indicates need for data from other agents"""
        # Agent can signal it needs help via specific flags
        return response.get("data", {}).get("needs_collaboration", False)
    
    def _request_collaboration(self, requesting_agent: BaseAgent, response: Dict) -> Dict:
        """Request data from other agents to complete the response"""
        collab_requests = response.get("data", {}).get("collaboration_requests", [])
        collab_data = {}
        
        for request in collab_requests:
            target_agent = request.get("agent")
            request_type = request.get("request_type")
            
            if target_agent in self.agents:
                message = AgentMessage(
                    from_agent=requesting_agent.name,
                    to_agent=target_agent,
                    message_type="request",
                    payload={"request_type": request_type}
                )
                
                target = self.agents[target_agent]
                response_msg = target.receive_message(message)
                
                if response_msg:
                    collab_data[target_agent] = response_msg.payload
        
        return collab_data
    
    def _merge_responses(self, primary: Dict, collab_data: Dict) -> Dict:
        """Merge primary response with collaboration data"""
        merged = primary.copy()
        
        if "data" not in merged:
            merged["data"] = {}
        
        merged["data"]["collaboration"] = collab_data
        
        # Enhance message with collaboration insights
        if collab_data:
            enhancement = self._generate_collaboration_message(collab_data)
            merged["message"] = f"{merged['message']}\n\n{enhancement}"
        
        return merged
    
    def _generate_collaboration_message(self, collab_data: Dict) -> str:
        """Generate natural language from collaboration data"""
        parts = []
        
        if "billing_agent" in collab_data:
            bill = collab_data["billing_agent"]
            if "annual_value" in bill:
                parts.append(f"💡 Com base no seu histórico (valor anual: €{bill['annual_value']}), tem acesso a tarifas especiais.")
        
        if "ev_agent" in collab_data:
            ev = collab_data["ev_agent"]
            if "monthly_consumption_kwh" in ev:
                parts.append(f"🔋 O seu carro elétrico representa {ev['monthly_consumption_kwh']} kWh/mês da fatura.")
        
        if "solar_agent" in collab_data:
            solar = collab_data["solar_agent"]
            if "bill_reduction_percent" in solar:
                parts.append(f"☀️ Os seus painéis solares estão a reduzir a fatura em {solar['bill_reduction_percent']}%.")
        
        return " ".join(parts) if parts else ""
    
    def _update_context_from_response(self, response: Dict):
        """Extract and store relevant context from agent response"""
        data = response.get("data", {})
        
        # Update user profile with relevant data
        if "invoice" in data:
            inv = data["invoice"]
            self.shared_context["user_profile"]["last_invoice"] = inv.get("amount")
            self.shared_context["user_profile"]["monthly_consumption"] = inv.get("consumption_kwh")
        
        if "consumption" in data:
            cons = data["consumption"]
            self.shared_context["user_profile"]["consumption_trend"] = cons.get("trend")
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Generate fallback when no agent can handle the query"""
        return {
            "primary_agent": "orchestrator",
            "collaborating_agents": [],
            "response": {
                "success": True,
                "data": {},
                "message": "Não tenho a certeza de como ajudar com isso. Posso ajudar com:\n• Faturas e consumo de energia\n• Carregamento de veículos elétricos\n• Painéis solares e autoconsumo\n\nO que gostaria de saber?",
                "follow_up": ["Ver minha fatura", "Otimizar carregamento EV", "Produção solar"]
            },
            "context": self.shared_context
        }
    
    # Message Bus Implementation
    def route_message(self, message: AgentMessage):
        """Route messages between agents (Message Bus)"""
        if message.to_agent == "*":
            # Broadcast to all agents except sender
            for name, agent in self.agents.items():
                if name != message.from_agent:
                    agent.receive_message(message)
        elif message.to_agent in self.agents:
            # Direct message
            self.agents[message.to_agent].receive_message(message)
        else:
            print(f"⚠️ Message to unknown agent: {message.to_agent}")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.shared_context["conversation_history"]
    
    def clear_context(self):
        """Reset shared context (e.g., new conversation)"""
        self.shared_context = {
            "conversation_history": [],
            "user_profile": {},
            "session_data": {}
        }
        # Also clear all agent contexts
        for agent in self.agents.values():
            agent.shared_context = {}
