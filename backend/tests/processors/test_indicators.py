import pytest
from backend.processors.indicators import (
    calculate_roe,
    calculate_roic,
    calculate_net_margin,
    calculate_debt_ebitda,
    calculate_pe_ratio,
    calculate_pb_ratio,
    calculate_revenue_growth,
    calculate_net_income_growth,
    calculate_all_indicators,
)

def test_calculate_roe():
    # Sucesso
    assert calculate_roe(200_000, 1_000_000) == 0.2
    
    # Valores nulos
    assert calculate_roe(None, 1_000_000) is None
    assert calculate_roe(200_000, None) is None
    
    # Divisão por zero
    assert calculate_roe(200_000, 0) is None


def test_calculate_roic():
    # Sucesso: 100k / (300k + 200k - 0) = 0.2
    assert calculate_roic(100_000, 300_000, 200_000) == 0.2
    
    # Com caixa: 100k / (300k + 200k - 100k) = 0.25
    assert calculate_roic(100_000, 300_000, 200_000, 100_000) == 0.25
    
    # Valores nulos
    assert calculate_roic(None, 300_000, 200_000) is None
    
    # Capital investido nulo ou zero
    assert calculate_roic(100_000, 0, 0) is None


def test_calculate_net_margin():
    # Sucesso
    assert calculate_net_margin(120_000, 1_000_000) == 0.12
    
    # Valores nulos
    assert calculate_net_margin(None, 1_000_000) is None
    
    # Divisão por zero
    assert calculate_net_margin(120_000, 0) is None


def test_calculate_debt_ebitda():
    # Sucesso
    assert calculate_debt_ebitda(600_000, 300_000) == 2.0
    
    # Valores nulos
    assert calculate_debt_ebitda(None, 300_000) is None
    
    # EBITDA zero ou negativo
    assert calculate_debt_ebitda(600_000, 0) is None
    assert calculate_debt_ebitda(600_000, -100_000) is None


def test_calculate_pe_ratio():
    # Por LPA
    assert calculate_pe_ratio(38.5, earnings_per_share=3.85) == 10.0
    
    # Por Lucro Líquido e Ações
    assert calculate_pe_ratio(38.5, net_income=3_850_000, shares_outstanding=1_000_000) == 10.0
    
    # Prejuízo
    assert calculate_pe_ratio(38.5, earnings_per_share=-1.0) is None
    
    # Faltam dados
    assert calculate_pe_ratio(38.5) is None


def test_calculate_pb_ratio():
    # Por VPA
    assert calculate_pb_ratio(38.5, book_value_per_share=25.0) == 1.54
    
    # Por Patrimônio e Ações
    assert calculate_pb_ratio(38.5, total_equity=25_000_000, shares_outstanding=1_000_000) == 1.54
    
    # Patrimônio negativo
    assert calculate_pb_ratio(38.5, book_value_per_share=-5.0) is None


def test_calculate_revenue_growth():
    # Crescimento
    history = [133.1, 121.0, 110.0, 100.0]
    assert pytest.approx(calculate_revenue_growth(history), 0.01) == 0.1
    
    # Histórico insuficiente
    assert calculate_revenue_growth([]) is None
    assert calculate_revenue_growth([100]) is None


def test_calculate_all_indicators():
    financial_data = {
        "net_income": 200_000,
        "revenue": 1_000_000,
        "ebitda": 300_000,
        "total_equity": 1_000_000,
        "total_debt": 400_000,
        "net_debt": 300_000,
        "revenue_history": [121, 110, 100],
        "net_income_history": [24, 22, 20]
    }
    quote_data = {
        "current_price": 10.0,
        "shares_outstanding": 100_000
    }
    
    indicators = calculate_all_indicators(financial_data, quote_data)
    
    assert indicators["roe"] == 0.2
    assert indicators["net_margin"] == 0.2
    assert indicators["debt_ebitda"] == 1.0
    assert indicators["pe_ratio"] == 5.0
    assert indicators["pb_ratio"] == 1.0
    assert indicators["revenue_growth_yoy"] is not None

def test_calculate_all_indicators_with_fundamentus():
    financial_data = {
        "net_income": 200_000,
        "total_equity": 1_000_000,
    }
    fundamentus_data = {
        "roe": 0.25 # Override
    }
    
    indicators = calculate_all_indicators(financial_data, fundamentus_data=fundamentus_data)
    
    # Deve preferir o do fundamentus
    assert indicators["roe"] == 0.25
    # Os outros que não foram calculados ficam None
    assert indicators["pe_ratio"] is None
