"""
Unit tests for BillingAgent
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.billing_agent import BillingAgent


class TestBillingAgent:
    """Test BillingAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create billing agent fixture"""
        return BillingAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized"""
        assert agent.name == "billing_agent"
        assert "consultar_fatura" in agent.capabilities
        assert "historico_consumo" in agent.capabilities
        assert isinstance(agent.mock_invoices, dict)
    
    def test_can_handle_billing_keywords(self, agent):
        """Test agent recognizes billing keywords"""
        test_cases = [
            ("Quanto tenho que pagar na fatura?", 0.4),
            ("Qual é o valor da minha conta?", 0.4),
            ("Quanto consumi em kWh?", 0.4),
        ]
        
        for query, expected_min in test_cases:
            context = {"query": query}
            confidence = agent.can_handle("unknown", context)
            assert confidence >= expected_min, f"Query '{query}' should have confidence >= {expected_min}"
    
    def test_can_handle_explicit_intent(self, agent):
        """Test agent handles explicit billing intents"""
        confidence = agent.can_handle("get_invoice", {"query": "test"})
        assert confidence == 0.9
        
        confidence = agent.can_handle("get_consumption", {"query": "test"})
        assert confidence == 0.9
    
    def test_get_invoice(self, agent):
        """Test getting invoice details"""
        result = agent._get_invoice("latest")
        
        assert result["success"] is True
        assert "invoice" in result["data"]
        assert "message" in result
        assert isinstance(result["follow_up"], list)
        
        invoice = result["data"]["invoice"]
        assert "number" in invoice
        assert "amount" in invoice
        assert "consumption_kwh" in invoice
    
    def test_get_consumption(self, agent):
        """Test getting consumption data"""
        result = agent._get_consumption("current")
        
        assert result["success"] is True
        assert "consumption" in result["data"]
        
        consumption = result["data"]["consumption"]
        assert "current_month" in consumption
        assert "previous_month" in consumption
        assert "trend" in consumption
    
    def test_predict_next_bill(self, agent):
        """Test predicting next bill"""
        result = agent._predict_next_bill()
        
        assert result["success"] is True
        assert "prediction" in result["data"]
        
        prediction = result["data"]["prediction"]
        assert "estimated_amount" in prediction
        assert "confidence" in prediction
        assert isinstance(prediction["factors"], list)
    
    def test_compare_consumption(self, agent):
        """Test comparing consumption"""
        result = agent._compare_consumption()
        
        assert result["success"] is True
        assert "comparison" in result["data"]
        
        comparison = result["data"]["comparison"]
        assert "current_month" in comparison
        assert "previous_month" in comparison
        assert "difference_percent" in comparison
    
    def test_process_invoice_query(self, agent):
        """Test processing invoice-related query"""
        result = agent.process("Quanto tenho que pagar na fatura?")
        
        assert result["success"] is True
        assert "invoice" in result["data"] or "agent" in result["data"]
    
    def test_process_consumption_query(self, agent):
        """Test processing consumption-related query"""
        result = agent.process("Qual foi o meu consumo?")
        
        assert result["success"] is True
    
    def test_get_info(self, agent):
        """Test getting agent info"""
        info = agent.get_info()
        
        assert info["name"] == "billing_agent"
        assert info["status"] == "active"
        assert isinstance(info["capabilities"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
