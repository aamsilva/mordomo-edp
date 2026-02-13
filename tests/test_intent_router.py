"""
Unit tests for SemanticRouter (Intent Routing)
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic_router import SemanticRouter


class TestSemanticRouter:
    """Test SemanticRouter functionality"""
    
    @pytest.fixture
    def router(self):
        """Create semantic router fixture"""
        return SemanticRouter()
    
    def test_router_initialization(self, router):
        """Test router is properly initialized"""
        assert router.api_key is not None
        assert router.base_url is not None
        assert router.model is not None
        assert isinstance(router.agent_descriptions, dict)
        assert "billing_agent" in router.agent_descriptions
        assert "ev_agent" in router.agent_descriptions
        assert "solar_agent" in router.agent_descriptions
    
    def test_fallback_route_billing(self, router):
        """Test fallback routing for billing queries"""
        queries = [
            "Quanto tenho que pagar na fatura?",
            "Valor da conta",
            "Fatura deste mês",
        ]
        
        for query in queries:
            agent, confidence = router._fallback_route(query)
            assert agent == "billing_agent", f"Query '{query}' should route to billing_agent"
            assert confidence > 0
    
    def test_fallback_route_ev(self, router):
        """Test fallback routing for EV queries"""
        queries = [
            "Onde carregar carro elétrico?",
            "Carregar bateria",
            "Tesla modelo 3",
        ]
        
        for query in queries:
            agent, confidence = router._fallback_route(query)
            assert agent == "ev_agent", f"Query '{query}' should route to ev_agent"
            assert confidence > 0
    
    def test_fallback_route_solar(self, router):
        """Test fallback routing for solar queries"""
        queries = [
            "Painéis solares para casa",
            "Produção fotovoltaica",
            "Painel solar fotovoltaico",
        ]
        
        for query in queries:
            agent, confidence = router._fallback_route(query)
            assert agent == "solar_agent", f"Query '{query}' should route to solar_agent"
            assert confidence > 0
    
    def test_fallback_route_support(self, router):
        """Test fallback routing for support queries"""
        queries = [
            "Tenho uma avaria",
            "Problema técnico",
            "Suporte técnico",
        ]
        
        for query in queries:
            agent, confidence = router._fallback_route(query)
            assert agent == "support_agent", f"Query '{query}' should route to support_agent"
            assert confidence > 0
    
    def test_fallback_route_unknown(self, router):
        """Test fallback routing for unknown queries"""
        query = "xyz abc random text"
        agent, confidence = router._fallback_route(query)
        
        # Should return none or the best match with low confidence
        assert confidence == 0.0
    
    def test_confidence_scaling(self, router):
        """Test confidence is properly scaled"""
        # Query with single keyword
        agent1, conf1 = router._fallback_route("fatura")
        
        # Query with multiple keywords
        agent2, conf2 = router._fallback_route("fatura valor pagar conta")
        
        # Multiple keywords should have higher or equal confidence
        assert conf2 >= conf1
        # Max confidence should be 1.0
        assert conf2 <= 1.0
    
    def test_agent_descriptions_content(self, router):
        """Test agent descriptions are meaningful"""
        for agent_name, description in router.agent_descriptions.items():
            assert len(description) > 0
            assert "_agent" in agent_name


class TestIntentRouterIntegration:
    """Integration tests for intent routing"""
    
    @pytest.fixture
    def router(self):
        return SemanticRouter()
    
    def test_route_returns_tuple(self, router):
        """Test route method returns expected tuple format"""
        query = "Qual é o valor da fatura?"
        result = router.route(query)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        agent, confidence = result
        assert isinstance(agent, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_route_billing_queries(self, router):
        """Test routing billing queries"""
        billing_queries = [
            "Quanto tenho que pagar?",
            "Valor da fatura",
            "Conta de eletricidade",
            "Consumo em kWh",
        ]
        
        for query in billing_queries:
            agent, confidence = router.route(query)
            # With fallback, should get billing_agent
            assert agent in ["billing_agent", "none"], f"Query '{query}' routed to {agent}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
