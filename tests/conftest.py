"""
Pytest fixtures for Mordomo EDP 3.0 tests
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def mock_invoice_data():
    """Mock invoice data for billing tests"""
    return {
        "number": "FT-2024-001",
        "amount": 127.50,
        "date": "2024-01-15",
        "consumption_kwh": 450,
        "status": "pending",
        "due_date": "2024-02-05"
    }

@pytest.fixture
def mock_consumption_data():
    """Mock consumption data for tests"""
    return {
        "current_month": 450,
        "previous_month": 380,
        "same_month_last_year": 420,
        "trend": "+18% vs mês anterior",
        "projection_next_month": 480
    }

@pytest.fixture
def mock_context():
    """Mock context for agent processing"""
    return {
        "session_id": "test-123",
        "customer_id": "CUST-001",
        "query": "test query"
    }

@pytest.fixture
def sample_queries():
    """Sample queries for routing tests"""
    return {
        "billing": [
            "Quanto tenho que pagar na fatura?",
            "Qual é o valor da minha conta?",
            "Quanto consumi este mês?",
            "Fatura de janeiro"
        ],
        "ev": [
            "Onde posso carregar o meu carro elétrico?",
            "Quanto custa carregar a bateria?",
            "Postos de carregamento MOBI.E"
        ],
        "solar": [
            "Painéis solares para minha casa",
            "Quanto posso produzir com fotovoltaicos?",
            "Autoconsumo energético"
        ]
    }
