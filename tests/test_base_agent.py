"""
Unit tests for BaseAgent class
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentMessage


class MockAgent(BaseAgent):
    """Mock agent for testing"""
    def __init__(self):
        super().__init__(
            name="mock_agent",
            description="Mock agent for testing",
            capabilities=["test_capability"]
        )
    
    def can_handle(self, intent, context=None):
        return 0.8 if intent == "test_intent" else 0.0
    
    def process(self, query, context=None):
        return {
            "success": True,
            "data": {"query": query},
            "message": f"Processed: {query}",
            "follow_up": []
        }


class TestAgentMessage:
    """Test AgentMessage dataclass"""
    
    def test_message_creation(self):
        """Test creating an agent message"""
        msg = AgentMessage(
            from_agent="agent_a",
            to_agent="agent_b",
            message_type="request",
            payload={"test": "data"}
        )
        
        assert msg.from_agent == "agent_a"
        assert msg.to_agent == "agent_b"
        assert msg.message_type == "request"
        assert msg.payload == {"test": "data"}
        assert msg.timestamp is not None
    
    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        msg = AgentMessage(
            from_agent="agent_a",
            to_agent="agent_b",
            message_type="request",
            payload={"test": "data"}
        )
        
        msg_dict = msg.to_dict()
        assert isinstance(msg_dict, dict)
        assert msg_dict["from_agent"] == "agent_a"
        assert msg_dict["to_agent"] == "agent_b"
        assert "timestamp" in msg_dict


class TestBaseAgent:
    """Test BaseAgent functionality"""
    
    def test_agent_initialization(self):
        """Test agent is properly initialized"""
        agent = MockAgent()
        
        assert agent.name == "mock_agent"
        assert agent.description == "Mock agent for testing"
        assert "test_capability" in agent.capabilities
        assert agent.message_bus is None
        assert isinstance(agent.shared_context, dict)
    
    def test_get_info(self):
        """Test getting agent metadata"""
        agent = MockAgent()
        info = agent.get_info()
        
        assert info["name"] == "mock_agent"
        assert info["description"] == "Mock agent for testing"
        assert info["status"] == "active"
        assert "test_capability" in info["capabilities"]
    
    def test_can_handle(self):
        """Test intent handling confidence"""
        agent = MockAgent()
        
        # Should handle test_intent
        confidence = agent.can_handle("test_intent")
        assert confidence == 0.8
        
        # Should not handle other intents
        confidence = agent.can_handle("other_intent")
        assert confidence == 0.0
    
    def test_process(self):
        """Test query processing"""
        agent = MockAgent()
        result = agent.process("test query")
        
        assert result["success"] is True
        assert result["data"]["query"] == "test query"
        assert "Processed: test query" in result["message"]
        assert isinstance(result["follow_up"], list)
    
    def test_update_context(self):
        """Test context updates"""
        agent = MockAgent()
        
        agent._update_context({"key": "value"})
        assert agent.shared_context["key"] == "value"
        
        agent._update_context({"new_key": "new_value"})
        assert agent.shared_context["key"] == "value"
        assert agent.shared_context["new_key"] == "new_value"
    
    def test_receive_message_request(self):
        """Test receiving request messages"""
        agent = MockAgent()
        
        msg = AgentMessage(
            from_agent="other_agent",
            to_agent="mock_agent",
            message_type="request",
            payload={"request_type": "test"}
        )
        
        response = agent.receive_message(msg)
        # Default handler returns not_implemented
        assert response.message_type == "response"
        assert response.payload["status"] == "not_implemented"
    
    def test_receive_message_context(self):
        """Test receiving context messages"""
        agent = MockAgent()
        
        msg = AgentMessage(
            from_agent="other_agent",
            to_agent="mock_agent",
            message_type="context",
            payload={"shared_data": "test"}
        )
        
        agent.receive_message(msg)
        assert agent.shared_context["shared_data"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
