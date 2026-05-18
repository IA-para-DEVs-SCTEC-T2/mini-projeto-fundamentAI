"""
Testes unitários para backend/processors/scoring.py

Cobre:
- Funções de score individuais (ações e FIIs)
- calculate_stock_score / calculate_fii_score
- calculate_score (entry point unificado)
- _get_label
"""

import pytest
from backend.processors.scoring import (
    # Ações
    _score_pe_ratio,
    _score_roe,
    _score_debt_ebitda,
    _score_net_margin,
    _score_ev_ebitda,
    _score_dividend_yield_stock,
    _score_net_income_growth,
    calculate_stock_score,
    # FIIs
    _score_pvp_fii,
    _score_pe_fii,
    _score_dividend_yield_fii,
    _score_dividend_growth,
    calculate_fii_score,
    # Unificado
    calculate_score,
    _get_label,
    _STOCK_WEIGHTS,
    _FII_WEIGHTS,
)


# ===========================================================================
# _get_label
# ===========================================================================

class TestGetLabel:
    def test_excelente(self):
        assert _get_label(100.0) == "Excelente"
        assert _get_label(75.0) == "Excelente"

    def test_bom(self):
        assert _get_label(74.9) == "Bom"
        assert _get_label(50.0) == "Bom"

    def test_regular(self):
        assert _get_label(49.9) == "Regular"
        assert _get_label(25.0) == "Regular"

    def test_fraco(self):
        assert _get_label(24.9) == "Fraco"
        assert _get_label(0.0) == "Fraco"


# ===========================================================================
# Pesos somam 1.0
# ===========================================================================

class TestWeights:
    def test_stock_weights_somam_1(self):
        assert sum(_STOCK_WEIGHTS.values()) == pytest.approx(1.0)

    def test_fii_weights_somam_1(self):
        assert sum(_FII_WEIGHTS.values()) == pytest.approx(1.0)


# ===========================================================================
# Funções de score — AÇÕES
# ===========================================================================

class TestScorePeRatio:
    def test_excelente(self):
        assert _score_pe_ratio(8.0) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_pe_ratio(None) == 50.0

    def test_negativo_retorna_baixo(self):
        assert _score_pe_ratio(-5.0) == 10.0

    def test_zero_retorna_baixo(self):
        assert _score_pe_ratio(0.0) == 10.0

    def test_alto_retorna_baixo(self):
        score = _score_pe_ratio(50.0)
        assert score < 25.0

    def test_range_0_a_100(self):
        for pe in [-10, 0, 5, 10, 15, 25, 50, 100]:
            s = _score_pe_ratio(pe)
            assert 0.0 <= s <= 100.0, f"P/L={pe} gerou score={s} fora do range"


class TestScoreRoe:
    def test_excelente(self):
        assert _score_roe(0.25) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_roe(None) == 50.0

    def test_negativo_penaliza(self):
        assert _score_roe(-0.10) < 25.0

    def test_bom(self):
        score = _score_roe(0.16)
        assert 75.0 <= score < 100.0

    def test_range_0_a_100(self):
        for roe in [-0.5, -0.1, 0.0, 0.08, 0.15, 0.20, 0.30]:
            s = _score_roe(roe)
            assert 0.0 <= s <= 100.0, f"ROE={roe} gerou score={s} fora do range"


class TestScoreDebtEbitda:
    def test_excelente(self):
        assert _score_debt_ebitda(0.5) == 100.0

    def test_caixa_liquido(self):
        assert _score_debt_ebitda(-1.0) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_debt_ebitda(None) == 50.0

    def test_alto_retorna_baixo(self):
        assert _score_debt_ebitda(4.0) < 25.0

    def test_range_0_a_100(self):
        for d in [-5, 0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]:
            s = _score_debt_ebitda(d)
            assert 0.0 <= s <= 100.0, f"Debt/EBITDA={d} gerou score={s} fora do range"


class TestScoreNetMargin:
    def test_excelente(self):
        assert _score_net_margin(0.25) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_net_margin(None) == 50.0

    def test_baixo(self):
        score = _score_net_margin(0.02)
        assert score < 50.0

    def test_range_0_a_100(self):
        for m in [-0.5, 0.0, 0.02, 0.05, 0.10, 0.20, 0.40]:
            s = _score_net_margin(m)
            assert 0.0 <= s <= 100.0, f"Margem={m} gerou score={s} fora do range"


class TestScoreEvEbitda:
    def test_excelente(self):
        assert _score_ev_ebitda(4.0) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_ev_ebitda(None) == 50.0

    def test_zero_retorna_neutro(self):
        assert _score_ev_ebitda(0.0) == 50.0

    def test_alto_retorna_baixo(self):
        assert _score_ev_ebitda(30.0) < 25.0

    def test_range_0_a_100(self):
        for ev in [0, 3, 6, 10, 15, 20, 30]:
            s = _score_ev_ebitda(ev)
            assert 0.0 <= s <= 100.0, f"EV/EBITDA={ev} gerou score={s} fora do range"


class TestScoreDividendYieldStock:
    def test_excelente(self):
        assert _score_dividend_yield_stock(0.10) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_dividend_yield_stock(None) == 50.0

    def test_zero_retorna_baixo(self):
        assert _score_dividend_yield_stock(0.0) == 25.0

    def test_range_0_a_100(self):
        for dy in [0.0, 0.02, 0.04, 0.06, 0.08, 0.12]:
            s = _score_dividend_yield_stock(dy)
            assert 0.0 <= s <= 100.0, f"DY={dy} gerou score={s} fora do range"


class TestScoreNetIncomeGrowth:
    def test_excelente(self):
        assert _score_net_income_growth(0.15) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_net_income_growth(None) == 50.0

    def test_negativo_penaliza(self):
        assert _score_net_income_growth(-0.20) < 25.0

    def test_range_0_a_100(self):
        for g in [-0.3, -0.1, 0.0, 0.05, 0.10, 0.20]:
            s = _score_net_income_growth(g)
            assert 0.0 <= s <= 100.0, f"Growth={g} gerou score={s} fora do range"


# ===========================================================================
# Funções de score — FIIs
# ===========================================================================

class TestScorePvpFii:
    def test_excelente_desconto(self):
        assert _score_pvp_fii(0.80) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_pvp_fii(None) == 50.0

    def test_premio_alto_penaliza(self):
        assert _score_pvp_fii(2.0) < 25.0

    def test_range_0_a_100(self):
        for pvp in [0.5, 0.90, 1.0, 1.10, 1.5, 2.0]:
            s = _score_pvp_fii(pvp)
            assert 0.0 <= s <= 100.0, f"P/VP={pvp} gerou score={s} fora do range"


class TestScorePeFii:
    def test_excelente(self):
        assert _score_pe_fii(10.0) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_pe_fii(None) == 50.0

    def test_negativo_retorna_baixo(self):
        assert _score_pe_fii(-1.0) == 10.0

    def test_range_0_a_100(self):
        for pe in [0, 8, 12, 16, 22, 30]:
            s = _score_pe_fii(pe)
            assert 0.0 <= s <= 100.0, f"P/L FII={pe} gerou score={s} fora do range"


class TestScoreDividendYieldFii:
    def test_excelente(self):
        assert _score_dividend_yield_fii(0.12) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_dividend_yield_fii(None) == 50.0

    def test_zero_retorna_baixo(self):
        assert _score_dividend_yield_fii(0.0) == 25.0

    def test_range_0_a_100(self):
        for dy in [0.0, 0.04, 0.06, 0.08, 0.10, 0.15]:
            s = _score_dividend_yield_fii(dy)
            assert 0.0 <= s <= 100.0, f"DY FII={dy} gerou score={s} fora do range"


class TestScoreDividendGrowth:
    def test_excelente(self):
        assert _score_dividend_growth(0.10) == 100.0

    def test_none_retorna_neutro(self):
        assert _score_dividend_growth(None) == 50.0

    def test_negativo_penaliza(self):
        assert _score_dividend_growth(-0.10) < 25.0

    def test_range_0_a_100(self):
        for g in [-0.2, 0.0, 0.04, 0.08, 0.15]:
            s = _score_dividend_growth(g)
            assert 0.0 <= s <= 100.0, f"DivGrowth={g} gerou score={s} fora do range"


# ===========================================================================
# calculate_stock_score
# ===========================================================================

class TestCalculateStockScore:
    _excelente = {
        "pe_ratio": 8.0,
        "roe": 0.25,
        "debt_ebitda": 0.5,
        "net_margin": 0.25,
        "ev_ebitda": 4.0,
        "dividend_yield": 0.10,
        "net_income_growth_yoy": 0.15,
    }

    _fraco = {
        "pe_ratio": 50.0,
        "roe": -0.20,
        "debt_ebitda": 6.0,
        "net_margin": -0.15,
        "ev_ebitda": 30.0,
        "dividend_yield": 0.0,
        "net_income_growth_yoy": -0.30,
    }

    def test_score_excelente(self):
        result = calculate_stock_score(self._excelente)
        assert result["score"] == 100.0
        assert result["label"] == "Excelente"

    def test_score_fraco(self):
        result = calculate_stock_score(self._fraco)
        assert result["score"] < 25.0
        assert result["label"] == "Fraco"

    def test_output_tem_campos_obrigatorios(self):
        result = calculate_stock_score(self._excelente)
        assert "score" in result
        assert "label" in result
        assert "breakdown" in result
        assert "weights" in result
        assert "available_indicators" in result
        assert "asset_type" in result

    def test_asset_type_e_stock(self):
        result = calculate_stock_score(self._excelente)
        assert result["asset_type"] == "stock"

    def test_score_entre_0_e_100(self):
        result = calculate_stock_score(self._fraco)
        assert 0.0 <= result["score"] <= 100.0

    def test_indicadores_disponiveis(self):
        result = calculate_stock_score(self._excelente)
        assert len(result["available_indicators"]) == 7

    def test_indicadores_parciais_usa_neutro(self):
        # Apenas ROE disponível — demais usam 50.0 (neutro)
        result = calculate_stock_score({"roe": 0.25})
        assert result["score"] > 0.0
        assert result["score"] < 100.0

    def test_sem_indicadores_retorna_score_neutro(self):
        result = calculate_stock_score({})
        assert result["score"] == pytest.approx(50.0)

    def test_breakdown_tem_todos_os_componentes(self):
        result = calculate_stock_score(self._excelente)
        for key in _STOCK_WEIGHTS:
            assert key in result["breakdown"], f"Componente '{key}' ausente no breakdown"


# ===========================================================================
# calculate_fii_score
# ===========================================================================

class TestCalculateFiiScore:
    _excelente = {
        "pb_ratio": 0.80,
        "pe_ratio": 10.0,
        "dividend_yield": 0.12,
        "dividend_growth_yoy": 0.10,
    }

    _fraco = {
        "pb_ratio": 3.0,
        "pe_ratio": 40.0,
        "dividend_yield": 0.02,
        "dividend_growth_yoy": -0.15,
    }

    def test_score_excelente(self):
        result = calculate_fii_score(self._excelente)
        assert result["score"] == 100.0
        assert result["label"] == "Excelente"

    def test_score_fraco(self):
        result = calculate_fii_score(self._fraco)
        assert result["score"] < 25.0
        assert result["label"] == "Fraco"

    def test_output_tem_campos_obrigatorios(self):
        result = calculate_fii_score(self._excelente)
        assert "score" in result
        assert "label" in result
        assert "breakdown" in result
        assert "weights" in result
        assert "available_indicators" in result
        assert "asset_type" in result

    def test_asset_type_e_fii(self):
        result = calculate_fii_score(self._excelente)
        assert result["asset_type"] == "fii"

    def test_score_entre_0_e_100(self):
        result = calculate_fii_score(self._fraco)
        assert 0.0 <= result["score"] <= 100.0

    def test_breakdown_tem_todos_os_componentes(self):
        result = calculate_fii_score(self._excelente)
        for key in _FII_WEIGHTS:
            assert key in result["breakdown"], f"Componente '{key}' ausente no breakdown"

    def test_sem_indicadores_retorna_score_neutro(self):
        result = calculate_fii_score({})
        assert result["score"] == pytest.approx(50.0)


# ===========================================================================
# calculate_score — entry point unificado
# ===========================================================================

class TestCalculateScore:
    def test_despacha_para_stock_por_padrao(self):
        result = calculate_score({"roe": 0.20}, asset_type="stock")
        assert result["asset_type"] == "stock"

    def test_despacha_para_fii(self):
        result = calculate_score({"pb_ratio": 0.90}, asset_type="fii")
        assert result["asset_type"] == "fii"

    def test_asset_type_padrao_e_stock(self):
        result = calculate_score({"roe": 0.20})
        assert result["asset_type"] == "stock"

    def test_output_unificado_stock(self):
        result = calculate_score({"roe": 0.20, "pe_ratio": 12.0}, asset_type="stock")
        assert "score" in result
        assert "label" in result
        assert "breakdown" in result
        assert "weights" in result
        assert "available_indicators" in result
        assert "asset_type" in result

    def test_output_unificado_fii(self):
        result = calculate_score({"pb_ratio": 0.90, "dividend_yield": 0.10}, asset_type="fii")
        assert "score" in result
        assert "label" in result
        assert "breakdown" in result
        assert "weights" in result
        assert "available_indicators" in result
        assert "asset_type" in result

    def test_score_stock_excelente(self):
        indicators = {
            "pe_ratio": 8.0,
            "roe": 0.25,
            "debt_ebitda": 0.5,
            "net_margin": 0.25,
            "ev_ebitda": 4.0,
            "dividend_yield": 0.10,
            "net_income_growth_yoy": 0.15,
        }
        result = calculate_score(indicators, asset_type="stock")
        assert result["score"] == 100.0
        assert result["label"] == "Excelente"

    def test_score_fii_excelente(self):
        indicators = {
            "pb_ratio": 0.80,
            "pe_ratio": 10.0,
            "dividend_yield": 0.12,
            "dividend_growth_yoy": 0.10,
        }
        result = calculate_score(indicators, asset_type="fii")
        assert result["score"] == 100.0
        assert result["label"] == "Excelente"

    def test_score_stock_fraco(self):
        indicators = {
            "pe_ratio": 50.0,
            "roe": -0.20,
            "debt_ebitda": 6.0,
            "net_margin": -0.15,
            "ev_ebitda": 30.0,
            "dividend_yield": 0.0,
            "net_income_growth_yoy": -0.30,
        }
        result = calculate_score(indicators, asset_type="stock")
        assert result["score"] < 25.0
        assert result["label"] == "Fraco"

    def test_score_sempre_entre_0_e_100(self):
        """Score nunca sai do range 0-100, mesmo com valores extremos."""
        extremos = {
            "pe_ratio": 9999.0,
            "roe": -99.0,
            "debt_ebitda": 999.0,
            "net_margin": -99.0,
            "ev_ebitda": 999.0,
            "dividend_yield": 0.0,
            "net_income_growth_yoy": -99.0,
        }
        result = calculate_score(extremos, asset_type="stock")
        assert 0.0 <= result["score"] <= 100.0
