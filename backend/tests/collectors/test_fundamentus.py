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
    """
    Testa as conversões do _safe_get com os formatos reais do fundamentus.

    Formatos reais do fundamentus:
    - Percentuais: "15.2%" (ponto decimal real) → remove "%" e "." → "152" → /1000 = 0.152
    - Percentuais com vírgula: "15,3%" → remove "%" → "15,3" → replace(",",".") → "15.3" → /1000 = 0.0153
      NOTA: fundamentus real usa ponto como decimal em percentuais, não vírgula.
    - Valores monetários: "1.234,56" → remove "." → "1234,56" → replace(",",".") → 1234.56
    - Inteiros ×100 (valuation): "1050" → /100 = 10.5
    - Float direto: 10.5 com divide_100=True → 10.5/100 = 0.105
    """
    mock_series = pd.Series({
        # Percentual com ponto decimal (formato real do fundamentus: "15.2%")
        "percent_ponto":    "15.2%",
        # Valor monetário com separador de milhar
        "valor_com_ponto":  "1.234,56",
        # Inteiro ×100 como string (formato real de valuation: "1050" = P/L 10.5)
        "valuation_str":    "1050",
        # Float direto (quando fundamentus retorna float)
        "float_direto":     10.5,
        # Nulo
        "nulo_str":         "-",
    })

    # "15.2%" → remove "%" e "." → "152" → 152.0 / 1000 = 0.152
    assert _safe_get(mock_series, "percent_ponto") == pytest.approx(0.152)

    # "1.234,56" → remove "." → "1234,56" → replace "," → 1234.56 (sem divide_100)
    assert _safe_get(mock_series, "valor_com_ponto") == pytest.approx(1234.56)

    # "1050" com divide_100=True → 1050.0 / 100 = 10.5
    assert _safe_get(mock_series, "valuation_str", divide_100=True) == pytest.approx(10.5)

    # float 10.5 com divide_100=True → 10.5 / 100 = 0.105 (comportamento correto para floats)
    assert _safe_get(mock_series, "float_direto", divide_100=True) == pytest.approx(0.105)

    # float 10.5 sem divide_100 → 10.5
    assert _safe_get(mock_series, "float_direto") == pytest.approx(10.5)

    # Nulo
    assert _safe_get(mock_series, "nulo_str") is None
    assert _safe_get(mock_series, "nao_existe") is None

@patch("fundamentus.get_papel")
def test_get_fundamentals_mocked(mock_get_papel):
    """
    Testa get_fundamentals com mock no formato real do fundamentus.

    Formatos reais:
    - PL: string inteira ×100 → "1050" = P/L 10.5
    - ROE: string percentual com ponto decimal → "15.5%" = ROE 15.5% = 0.155
    """
    mock_df = pd.DataFrame({
        "PL":    ["1050"],   # string ×100: "1050" → 1050/100 = 10.5
        "ROE":   ["15.5%"],  # percentual: "15.5%" → remove "%" e "." → "155" → 155/1000 = 0.155
        "Setor": ["Petróleo"]
    }, index=["PETR4"])

    mock_get_papel.return_value = mock_df

    result = get_fundamentals("PETR4")

    assert result["ticker"] == "PETR4"
    assert result["pe_ratio"] == pytest.approx(10.5)
    assert result["roe"] == pytest.approx(0.155)

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
