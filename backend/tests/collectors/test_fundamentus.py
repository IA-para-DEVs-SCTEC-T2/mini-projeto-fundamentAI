import pytest
import pandas as pd
from unittest.mock import patch

from backend.collectors.fundamentus import (
    get_fundamentals,
    get_sector,
    get_all_tickers,
    _safe_get,
)

def test_safe_get():
    # Testa conversões
    mock_series = pd.Series({
        "percent_com_virgula": "15,3%",
        "valor_com_ponto": "1.234,56",
        "inteiro": 10,
        "nulo_str": "-",
    })
    
    # 15,3% deveria virar 0.153, mas no fundamentus já vem divido dependendo, a função lida com isso.
    # No _safe_get, se tem % e > 1, divide por 100
    assert _safe_get(mock_series, "percent_com_virgula") == 0.153
    assert _safe_get(mock_series, "valor_com_ponto") == 1234.56
    assert _safe_get(mock_series, "inteiro") == 10.0
    assert _safe_get(mock_series, "nulo_str") is None
    assert _safe_get(mock_series, "nao_existe") is None

@patch("fundamentus.get_papel")
def test_get_fundamentals_mocked(mock_get_papel):
    # Mock do retorno do fundamentus
    mock_df = pd.DataFrame({
        "P/L": [10.5],
        "ROE": ["15,5%"],
        "Setor": ["Petróleo"]
    }, index=["PETR4"])
    
    mock_get_papel.return_value = mock_df
    
    result = get_fundamentals("PETR4")
    
    assert result["ticker"] == "PETR4"
    assert result["pe_ratio"] == 10.5
    assert result["roe"] == 0.155

@patch("fundamentus.get_papel")
def test_get_sector_mocked(mock_get_papel):
    mock_df = pd.DataFrame({
        "Setor": ["Financeiro"]
    }, index=["ITUB4"])
    
    mock_get_papel.return_value = mock_df
    
    assert get_sector("ITUB4") == "Financeiro"

@patch("fundamentus.get_resultado")
def test_get_all_tickers_mocked(mock_get_resultado):
    mock_df = pd.DataFrame({
        "Papel": ["PETR4", "VALE3"],
        "P/L": [10.5, 8.0]
    })
    
    mock_get_resultado.return_value = mock_df
    
    result = get_all_tickers()
    assert len(result) == 2

@pytest.mark.integration
def test_get_fundamentals_integration():
    result = get_fundamentals("PETR4")
    assert result["ticker"] == "PETR4"
    assert "pe_ratio" in result
    assert "roe" in result
