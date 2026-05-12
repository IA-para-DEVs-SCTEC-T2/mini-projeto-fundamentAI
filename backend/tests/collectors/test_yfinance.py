import pytest
from backend.collectors.yfinance import (
    _normalize_ticker,
    get_stock_quote,
    get_price_history,
)

def test_normalize_ticker():
    assert _normalize_ticker("PETR4") == "PETR4.SA"
    assert _normalize_ticker("vale3.sa") == "VALE3.SA"
    assert _normalize_ticker("  itub4  ") == "ITUB4.SA"

@pytest.mark.integration
def test_get_stock_quote():
    # Testa a integração real com yfinance
    quote = get_stock_quote("PETR4")
    
    assert "ticker" in quote
    assert quote["ticker"] == "PETR4"
    assert "current_price" in quote
    assert quote["current_price"] > 0
    assert "currency" in quote

@pytest.mark.integration
def test_get_stock_quote_invalid_ticker():
    # Testa falha
    with pytest.raises((ValueError, RuntimeError)):
        get_stock_quote("TICKERINVALIDO123")

@pytest.mark.integration
def test_get_price_history():
    history = get_price_history("PETR4", years=1)
    
    assert not history.empty
    assert "Close" in history.columns
    assert "Volume" in history.columns
    assert len(history) > 100 # Em 1 ano deve ter mais de 100 pregões
