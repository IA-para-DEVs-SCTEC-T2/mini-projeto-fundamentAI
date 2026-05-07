import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.api.main import app

client = TestClient(app)

@patch("backend.api.routes.ticker.get_stock_quote")
@patch("backend.api.routes.ticker.get_financial_statements")
@patch("backend.api.routes.ticker.get_fundamentals")
@patch("backend.api.routes.ticker.get_sector")
@patch("backend.api.routes.ticker.get_price_history")
@patch("backend.api.routes.ticker._persist_ticker_data")
def test_get_ticker_valid(
    mock_persist, mock_price, mock_sector, mock_fund, mock_stmt, mock_quote
):
    # Setup mocks
    mock_quote.return_value = {"current_price": 40.0, "ticker": "PETR4"}
    mock_stmt.return_value = {}
    mock_fund.return_value = {"roe": 0.20}
    mock_sector.return_value = "Petróleo"
    mock_price.return_value = None
    
    response = client.get("/api/ticker/PETR4")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "PETR4"
    assert data["quote"]["current_price"] == 40.0
    assert data["sector"] == "Petróleo"

def test_get_ticker_invalid_format():
    response = client.get("/api/ticker/INVALIDO123")
    assert response.status_code == 400
    assert "Formato de ticker inv" in response.json()["detail"]

@patch("backend.api.routes.analysis._get_cached_analysis")
@patch("backend.api.routes.analysis._collect_data")
@patch("backend.api.routes.analysis._collect_macro")
@patch("backend.api.routes.analysis._call_anthropic")
@patch("backend.api.routes.analysis.parse_llm_response")
@patch("backend.api.routes.analysis._persist_analysis")
def test_analyze_ticker_mocked(
    mock_persist, mock_parse, mock_call, mock_macro, mock_data, mock_cache
):
    mock_cache.return_value = None
    mock_data.return_value = ({}, {"current_price": 40.0}, {}, "Petróleo")
    mock_macro.return_value = {"selic_rate": 10.5}
    mock_call.return_value = "{}"
    mock_parse.return_value = {
        "verdict": "Comprar",
        "score": 85.0,
        "confidence_level": "Alto",
        "positive_points": [],
        "negative_points": [],
        "conclusion": "Ok"
    }
    
    response = client.post("/api/analysis/PETR4")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "PETR4"
    assert data["score"] == 85.0
    assert data["verdict"] == "Comprar"

@pytest.mark.integration
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
