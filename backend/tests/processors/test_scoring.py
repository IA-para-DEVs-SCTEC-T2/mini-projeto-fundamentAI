import pytest
from backend.processors.scoring import (
    _score_growth,
    _score_roe,
    _score_roic,
    _score_net_margin,
    _score_debt_ebitda,
    _score_valuation,
    _annual_growth_rates,
    _score_consistency,
    calculate_score,
    _get_label,
    _WEIGHTS_WITHOUT_HISTORY,
    _WEIGHTS_WITH_HISTORY,
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


# ---------------------------------------------------------------------------
# _annual_growth_rates
# ---------------------------------------------------------------------------

class TestAnnualGrowthRates:
    def test_series_com_crescimento_positivo(self):
        rates = _annual_growth_rates([100, 110, 121])
        assert rates == pytest.approx([0.10, 0.10])

    def test_serie_com_dois_valores(self):
        rates = _annual_growth_rates([100, 115])
        assert rates == pytest.approx([0.15])

    def test_serie_com_crescimento_negativo(self):
        rates = _annual_growth_rates([100, 90])
        assert rates == pytest.approx([-0.10])

    def test_ignora_base_zero(self):
        # Período com base zero não deve gerar taxa
        rates = _annual_growth_rates([0, 100, 110])
        assert len(rates) == 1
        assert rates[0] == pytest.approx(0.10)

    def test_ignora_base_negativa(self):
        rates = _annual_growth_rates([-10, 100, 110])
        assert len(rates) == 1
        assert rates[0] == pytest.approx(0.10)

    def test_ignora_valores_none(self):
        rates = _annual_growth_rates([100, None, 121])
        assert rates == []

    def test_serie_vazia(self):
        assert _annual_growth_rates([]) == []

    def test_serie_com_um_valor(self):
        assert _annual_growth_rates([100]) == []

    def test_cinco_anos_crescimento_uniforme(self):
        # Simula 5 anos com crescimento de 12% a.a.
        series = [100 * (1.12 ** i) for i in range(5)]
        rates = _annual_growth_rates(series)
        assert len(rates) == 4
        for r in rates:
            assert r == pytest.approx(0.12, rel=1e-4)


# ---------------------------------------------------------------------------
# _score_consistency
# ---------------------------------------------------------------------------

class TestScoreConsistency:
    def test_crescimento_excelente_todos_os_periodos(self):
        # Receita e lucro crescendo >10% em todos os 4 períodos
        history = {
            "revenue":    [100, 112, 126, 141, 158],
            "net_income": [10,  11.5, 13.2, 15.1, 17.2],
        }
        score, detail = _score_consistency(history)
        assert score == 100.0
        assert detail["periods_above_threshold"] == 8  # 4 períodos x 2 séries
        assert detail["periods_evaluated"] == 8

    def test_crescimento_zero_retorna_score_baixo(self):
        history = {
            "revenue":    [100, 100, 100, 100, 100],
            "net_income": [10,  10,  10,  10,  10],
        }
        score, detail = _score_consistency(history)
        assert score == 0.0
        assert detail["periods_above_threshold"] == 0

    def test_penalidade_por_anos_negativos(self):
        # Crescimento médio razoável mas com 2 anos negativos
        history_sem_negativo = {
            "revenue": [100, 110, 121, 133, 146],
        }
        history_com_negativo = {
            "revenue": [100, 90, 121, 133, 146],  # 1 ano negativo
        }
        score_sem, _ = _score_consistency(history_sem_negativo)
        score_com, _ = _score_consistency(history_com_negativo)
        assert score_com < score_sem

    def test_penalidade_multiplos_anos_negativos(self):
        history = {
            "revenue":    [100, 90, 85, 95, 100],   # 2 anos negativos
            "net_income": [10,  8,  7,  9,  10],    # 2 anos negativos
        }
        score, detail = _score_consistency(history)
        # 4 anos negativos no total → penalidade de 20 pontos
        assert score < 50.0

    def test_apenas_receita_disponivel(self):
        history = {"revenue": [100, 112, 126, 141, 158]}
        score, detail = _score_consistency(history)
        assert score == 100.0
        assert detail["net_income_rates"] == []
        assert len(detail["revenue_rates"]) == 4

    def test_apenas_lucro_disponivel(self):
        history = {"net_income": [10, 11.5, 13.2, 15.1, 17.2]}
        score, detail = _score_consistency(history)
        assert score == 100.0
        assert detail["revenue_rates"] == []
        assert len(detail["net_income_rates"]) == 4

    def test_sem_dados_retorna_neutro(self):
        score, detail = _score_consistency({})
        assert score == 50.0
        assert detail["periods_evaluated"] == 0
        assert detail["periods_above_threshold"] == 0

    def test_series_com_apenas_um_valor_retorna_neutro(self):
        # Menos de 2 valores não gera nenhuma taxa
        score, detail = _score_consistency({"revenue": [100], "net_income": [10]})
        assert score == 50.0

    def test_crescimento_parcial_entre_0_e_10(self):
        # Crescimento de 5% a.a. deve gerar score intermediário (não 0, não 100)
        history = {"revenue": [100, 105, 110.25, 115.76, 121.55]}
        score, detail = _score_consistency(history)
        assert 0 < score < 100
        assert detail["periods_above_threshold"] == 0

    def test_detail_arredonda_taxas(self):
        history = {"revenue": [100, 113]}
        _, detail = _score_consistency(history)
        assert detail["revenue_rates"] == [0.13]

    def test_peso_receita_maior_que_lucro(self):
        # Receita excelente (100pts), lucro péssimo (0pts)
        # Peso receita=60%, lucro=40% → score esperado = 60
        history = {
            "revenue":    [100, 115],   # +15% → 100pts
            "net_income": [10, 8],      # -20% → ~0pts
        }
        score, _ = _score_consistency(history)
        # Com penalidade de 1 ano negativo (-5): score ≈ 55
        assert 50 <= score <= 65


# ---------------------------------------------------------------------------
# calculate_score — comportamento com history
# ---------------------------------------------------------------------------

class TestCalculateScoreWithHistory:
    _base_indicators = {
        "roe": 0.20,
        "roic": 0.15,
        "net_margin": 0.18,
        "debt_ebitda": 1.2,
        "pe_ratio": 12.0,
        "pb_ratio": 2.0,
        "revenue_growth_yoy": 0.12,
        "net_income_growth_yoy": 0.15,
    }

    def test_sem_history_usa_pesos_sem_historico(self):
        result = calculate_score(self._base_indicators)
        assert result["weights"] == _WEIGHTS_WITHOUT_HISTORY
        assert "consistency" not in result["breakdown"]
        assert "consistency_detail" not in result

    def test_com_history_usa_pesos_com_historico(self):
        history = {
            "revenue":    [100, 112, 126, 141, 158],
            "net_income": [10,  11.5, 13.2, 15.1, 17.2],
        }
        result = calculate_score(self._base_indicators, history=history)
        assert result["weights"] == _WEIGHTS_WITH_HISTORY
        assert "consistency" in result["breakdown"]
        assert "consistency_detail" in result

    def test_consistency_detail_estrutura(self):
        history = {
            "revenue":    [100, 112, 126, 141, 158],
            "net_income": [10,  11.5, 13.2, 15.1, 17.2],
        }
        result = calculate_score(self._base_indicators, history=history)
        detail = result["consistency_detail"]
        assert "revenue_rates" in detail
        assert "net_income_rates" in detail
        assert "periods_evaluated" in detail
        assert "periods_above_threshold" in detail
        assert detail["periods_evaluated"] == 8
        assert detail["periods_above_threshold"] == 8

    def test_history_com_crescimento_excelente_aumenta_score(self):
        # Histórico excelente deve manter ou melhorar o score vs sem histórico
        history_excelente = {
            "revenue":    [100, 115, 132, 152, 175],  # ~15% a.a.
            "net_income": [10,  11.8, 13.9, 16.4, 19.3],
        }
        result_sem = calculate_score(self._base_indicators)
        result_com = calculate_score(self._base_indicators, history=history_excelente)
        # Ambos devem ser Excelente; score com histórico ≥ sem histórico
        assert result_com["score"] >= result_sem["score"] - 1.0  # tolerância de 1pt por redistribuição de pesos

    def test_history_com_crescimento_ruim_reduz_score(self):
        history_ruim = {
            "revenue":    [100, 95, 90, 88, 85],   # queda consistente
            "net_income": [10,  8,  6,  5,  4],
        }
        result_sem = calculate_score(self._base_indicators)
        result_com = calculate_score(self._base_indicators, history=history_ruim)
        assert result_com["score"] < result_sem["score"]

    def test_history_none_equivale_a_sem_history(self):
        result_none = calculate_score(self._base_indicators, history=None)
        result_sem = calculate_score(self._base_indicators)
        assert result_none["score"] == result_sem["score"]
        assert result_none["weights"] == result_sem["weights"]

    def test_history_vazio_equivale_a_sem_history(self):
        result_vazio = calculate_score(self._base_indicators, history={})
        result_sem = calculate_score(self._base_indicators)
        assert result_vazio["score"] == result_sem["score"]
        assert "consistency" not in result_vazio["breakdown"]

    def test_history_com_series_de_um_elemento_equivale_a_sem_history(self):
        # Série com 1 valor não gera taxas → não ativa consistency
        result = calculate_score(self._base_indicators, history={"revenue": [100]})
        assert result["weights"] == _WEIGHTS_WITHOUT_HISTORY
        assert "consistency" not in result["breakdown"]

    def test_score_permanece_entre_0_e_100_com_history(self):
        history = {
            "revenue":    [100, 50, 25, 10, 5],   # colapso total
            "net_income": [10,  2,  -5, -10, -20],
        }
        indicators_ruins = {
            "roe": -0.50, "roic": -0.30, "net_margin": -0.40,
            "debt_ebitda": 10.0, "pe_ratio": 50.0, "pb_ratio": 15.0,
            "revenue_growth_yoy": -0.50, "net_income_growth_yoy": -0.60,
        }
        result = calculate_score(indicators_ruins, history=history)
        assert 0.0 <= result["score"] <= 100.0

    def test_pesos_com_history_somam_1(self):
        assert sum(_WEIGHTS_WITH_HISTORY.values()) == pytest.approx(1.0)

    def test_pesos_sem_history_somam_1(self):
        assert sum(_WEIGHTS_WITHOUT_HISTORY.values()) == pytest.approx(1.0)
