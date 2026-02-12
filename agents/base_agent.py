"""
Base Agent Class - All agents inherit from this
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AgentMessage:
    """Message format for inter-agent communication"""
    from_agent: str
    to_agent: str  # "*" for broadcast
    message_type: str  # "request", "response", "notification", "context"
    payload: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }

class BaseAgent:
    """
    Base class for all Mordomo agents
    """
    
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.message_bus = None  # Set by orchestrator
        self.shared_context = {}  # Shared state with other agents
        
    def can_handle(self, intent: str, context: Dict = None) -> float:
        """
        Returns confidence score (0.0-1.0) for handling this intent
        Override in subclasses
        """
        return 0.0
    
    def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by subclasses
        Returns: {
            "success": bool,
            "data": dict,
            "message": str,
            "follow_up": list  # suggested next actions
        }
        """
        raise NotImplementedError
    
    def receive_message(self, message: AgentMessage):
        """Handle messages from other agents"""
        if message.message_type == "request":
            return self._handle_request(message)
        elif message.message_type == "context":
            self._update_context(message.payload)
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Override to handle specific requests from other agents"""
        return AgentMessage(
            from_agent=self.name,
            to_agent=message.from_agent,
            message_type="response",
            payload={"status": "not_implemented"}
        )
    
    def _update_context(self, context_update: Dict):
        """Update shared context"""
        self.shared_context.update(context_update)
    
    def send_message(self, to_agent: str, message_type: str, payload: Dict):
        """Send message to another agent via message bus"""
        if self.message_bus:
            message = AgentMessage(
                from_agent=self.name,
                to_agent=to_agent,
                message_type=message_type,
                payload=payload
            )
            self.message_bus.route_message(message)
    
    def broadcast_context(self, context: Dict):
        """Share context with all agents"""
        self.send_message("*", "context", context)
    
    def get_info(self) -> Dict:
        """Get agent metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": "active"
        }
