import pytest
from backend.processors.scoring import (
    _score_growth,
    _score_roe,
    _score_roic,
    _score_net_margin,
    _score_debt_ebitda,
    _score_valuation,
    calculate_score,
    _get_label,
)

def test_score_growth():
    assert _score_growth(0.12, 0.15) == 100.0  # Ambos > 10%
    assert _score_growth(0.06, None) == pytest.approx(60.0)   # (50 + (0.06 - 0.05) / 0.05 * 50) = 50 + 10 = 60
    assert _score_growth(-0.10, -0.10) == 15.0 # Negativo penaliza
    assert _score_growth(None, None) == 50.0   # Sem dados

def test_score_roe():
    assert _score_roe(0.25) == 100.0
    assert _score_roe(0.16) == 80.0
    assert _score_roe(-0.10) == 15.0
    assert _score_roe(None) == 50.0

def test_score_roic():
    assert _score_roic(0.20) == 100.0
    assert _score_roic(0.12) == 85.0
    assert _score_roic(None) == 50.0

def test_score_net_margin():
    assert _score_net_margin(0.25) == 100.0
    assert _score_net_margin(0.02) == 20.0
    assert _score_net_margin(None) == 50.0

def test_score_debt_ebitda():
    assert _score_debt_ebitda(0.5) == 100.0
    assert _score_debt_ebitda(-1.0) == 100.0  # Caixa líquido
    assert _score_debt_ebitda(1.5) == 62.5    # (75 - (1.5 - 1.0)/1.0 * 25) = 75 - 12.5 = 62.5
    assert _score_debt_ebitda(4.0) == 15.0
    assert _score_debt_ebitda(None) == 50.0

def test_score_valuation():
    # P/L = 8, P/VP = 1.0 -> Excelente
    assert _score_valuation(8.0, 1.0) == 100.0
    
    # Sem dados
    assert _score_valuation(None, None) == 50.0
    
    # P/L = 12 (75 - (2/5)*25 = 65), P/VP = 2.0 (75 - (0.5/1.5)*25 = 66.66) -> avg = 65.83
    assert pytest.approx(_score_valuation(12.0, 2.0), 0.1) == 65.8

def test_calculate_score():
    indicators = {
        "roe": 0.25,                  # 100
        "roic": 0.20,                 # 100
        "net_margin": 0.25,           # 100
        "debt_ebitda": 0.5,           # 100
        "pe_ratio": 8.0,              # 100
        "pb_ratio": 1.0,              # 100
        "revenue_growth_yoy": 0.15,   # 100
        "net_income_growth_yoy": 0.12 # 100
    }
    
    result = calculate_score(indicators)
    assert result["score"] == 100.0
    assert result["label"] == "Excelente"
    assert len(result["available_indicators"]) == 8

def test_calculate_score_weak():
    indicators = {
        "roe": -0.20,
        "roic": -0.10,
        "net_margin": -0.15,
        "debt_ebitda": 5.0,
        "pe_ratio": 30.0,
        "pb_ratio": 8.0,
        "revenue_growth_yoy": -0.20,
        "net_income_growth_yoy": -0.30
    }
    
    result = calculate_score(indicators)
    assert result["score"] < 25.0
    assert result["label"] == "Fraco"

def test_get_label():
    assert _get_label(80.0) == "Excelente"
    assert _get_label(60.0) == "Bom"
    assert _get_label(30.0) == "Regular"
    assert _get_label(10.0) == "Fraco"
