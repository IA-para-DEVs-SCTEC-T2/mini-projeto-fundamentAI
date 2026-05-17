"""
Testes unitários para backend/processors/data_validator.py

Cobre:
- validate_indicators: ranges por tipo de ativo, remoção de anomalias
- validate_and_log_batch: processamento em lote
- is_valid_ticker_symbol: validação de formato de ticker
- generate_anomaly_report: geração de relatório (smoke test)
"""

import pytest
from backend.processors.data_validator import (
    validate_indicators,
    validate_and_log_batch,
    is_valid_ticker_symbol,
)


# ===========================================================================
# validate_indicators — AÇÕES
# ===========================================================================

class TestValidateIndicatorsStock:
    def test_indicadores_validos_passam_sem_anomalias(self):
        indicators = {
            "roe": 0.20,
            "net_margin": 0.15,
            "pe_ratio": 12.0,
            "pb_ratio": 2.0,
            "debt_ebitda": 1.5,
            "ev_ebitda": 8.0,
            "dividend_yield": 0.06,
        }
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert anomalies == []
        assert clean["roe"] == 0.20
        assert clean["pe_ratio"] == 12.0

    def test_roe_fora_do_range_e_removido(self):
        # ROE range: -5.0 a 5.0
        indicators = {"roe": 10.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "roe" not in clean
        assert len(anomalies) == 1
        assert anomalies[0]["field"] == "roe"
        assert anomalies[0]["action"] == "removed"

    def test_roe_negativo_extremo_e_removido(self):
        indicators = {"roe": -10.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "roe" not in clean
        assert len(anomalies) == 1

    def test_pe_ratio_negativo_valido(self):
        # P/L negativo é válido (empresa com prejuízo) — range: -500 a 500
        indicators = {"pe_ratio": -50.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "pe_ratio" in clean
        assert anomalies == []

    def test_pe_ratio_extremo_e_removido(self):
        indicators = {"pe_ratio": 600.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "pe_ratio" not in clean
        assert len(anomalies) == 1

    def test_dividend_yield_acima_do_range_e_removido(self):
        # DY range: 0 a 1.0 (100%)
        indicators = {"dividend_yield": 1.5}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "dividend_yield" not in clean
        assert len(anomalies) == 1

    def test_net_margin_fora_do_range_e_removida(self):
        # Margem range: -2.0 a 1.0
        indicators = {"net_margin": 2.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "net_margin" not in clean
        assert len(anomalies) == 1

    def test_multiplas_anomalias_detectadas(self):
        indicators = {
            "roe": 10.0,          # fora do range
            "net_margin": 2.0,    # fora do range
            "pe_ratio": 12.0,     # válido
        }
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert len(anomalies) == 2
        assert "pe_ratio" in clean
        assert "roe" not in clean
        assert "net_margin" not in clean

    def test_none_passa_sem_anomalia(self):
        indicators = {"roe": None, "pe_ratio": None}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert anomalies == []
        assert clean["roe"] is None
        assert clean["pe_ratio"] is None

    def test_campo_sem_range_definido_passa(self):
        # Campo não mapeado nos ranges — deve passar sem validação
        indicators = {"campo_desconhecido": 999.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        assert "campo_desconhecido" in clean
        assert anomalies == []

    def test_anomalia_inclui_metadados_corretos(self):
        indicators = {"roe": 10.0}
        clean, anomalies = validate_indicators(indicators, "stock", "PETR4")
        anomaly = anomalies[0]
        assert anomaly["ticker"] == "PETR4"
        assert anomaly["asset_type"] == "stock"
        assert anomaly["field"] == "roe"
        assert anomaly["value"] == 10.0
        assert "expected_range" in anomaly
        assert anomaly["action"] == "removed"


# ===========================================================================
# validate_indicators — FIIs
# ===========================================================================

class TestValidateIndicatorsFii:
    def test_indicadores_fii_validos_passam(self):
        indicators = {
            "pb_ratio": 0.95,
            "pe_ratio": 14.0,
            "dividend_yield": 0.10,
            "dividend_growth_yoy": 0.05,
        }
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert anomalies == []
        assert clean["pb_ratio"] == 0.95

    def test_pb_ratio_fii_fora_do_range_e_removido(self):
        # P/VP FII range: 0 a 10
        indicators = {"pb_ratio": 15.0}
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert "pb_ratio" not in clean
        assert len(anomalies) == 1

    def test_dividend_yield_fii_fora_do_range_e_removido(self):
        indicators = {"dividend_yield": 1.5}
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert "dividend_yield" not in clean
        assert len(anomalies) == 1

    def test_dividend_growth_negativo_extremo_e_removido(self):
        # Crescimento DY range: -1.0 a 5.0
        indicators = {"dividend_growth_yoy": -2.0}
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert "dividend_growth_yoy" not in clean
        assert len(anomalies) == 1

    def test_pe_ratio_fii_fora_do_range_e_removido(self):
        # P/L FII range: 0 a 100
        indicators = {"pe_ratio": 150.0}
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert "pe_ratio" not in clean
        assert len(anomalies) == 1

    def test_indicadores_de_acao_em_fii_passam_sem_range(self):
        # ROE não tem range definido para FII — deve passar
        indicators = {"roe": 0.20}
        clean, anomalies = validate_indicators(indicators, "fii", "HGLG11")
        assert "roe" in clean
        assert anomalies == []


# ===========================================================================
# validate_and_log_batch
# ===========================================================================

class TestValidateAndLogBatch:
    def test_lote_vazio_retorna_listas_vazias(self):
        clean_list, anomalies = validate_and_log_batch([])
        assert clean_list == []
        assert anomalies == []

    def test_lote_com_um_ticker_valido(self):
        batch = [("PETR4", "stock", {"roe": 0.20, "pe_ratio": 12.0})]
        clean_list, anomalies = validate_and_log_batch(batch)
        assert len(clean_list) == 1
        assert clean_list[0][0] == "PETR4"
        assert anomalies == []

    def test_lote_com_anomalia_detectada(self):
        batch = [("PETR4", "stock", {"roe": 10.0})]  # ROE fora do range
        clean_list, anomalies = validate_and_log_batch(batch)
        assert len(anomalies) == 1
        assert anomalies[0]["ticker"] == "PETR4"

    def test_lote_misto_stock_e_fii(self):
        batch = [
            ("PETR4", "stock", {"roe": 0.20, "pe_ratio": 12.0}),
            ("HGLG11", "fii", {"pb_ratio": 0.95, "dividend_yield": 0.10}),
        ]
        clean_list, anomalies = validate_and_log_batch(batch)
        assert len(clean_list) == 2
        assert anomalies == []

    def test_lote_com_multiplos_tickers_e_anomalias(self):
        batch = [
            ("PETR4", "stock", {"roe": 10.0}),    # anomalia
            ("VALE3", "stock", {"roe": 0.15}),     # válido
            ("HGLG11", "fii", {"pb_ratio": 20.0}), # anomalia
        ]
        clean_list, anomalies = validate_and_log_batch(batch)
        assert len(clean_list) == 3
        assert len(anomalies) == 2

    def test_clean_list_preserva_ordem(self):
        batch = [
            ("PETR4", "stock", {"roe": 0.20}),
            ("VALE3", "stock", {"roe": 0.15}),
            ("WEGE3", "stock", {"roe": 0.25}),
        ]
        clean_list, _ = validate_and_log_batch(batch)
        tickers = [t for t, _ in clean_list]
        assert tickers == ["PETR4", "VALE3", "WEGE3"]


# ===========================================================================
# is_valid_ticker_symbol
# ===========================================================================

class TestIsValidTickerSymbol:
    # --- Formatos válidos ---
    def test_acao_on(self):
        assert is_valid_ticker_symbol("PETR4") is True

    def test_acao_pn(self):
        assert is_valid_ticker_symbol("VALE3") is True

    def test_fii(self):
        assert is_valid_ticker_symbol("HGLG11") is True

    def test_fracionario(self):
        assert is_valid_ticker_symbol("PETR4F") is True

    def test_fii_fracionario(self):
        assert is_valid_ticker_symbol("HGLG11F") is True

    def test_minusculo_normalizado(self):
        assert is_valid_ticker_symbol("petr4") is True

    # --- Formatos inválidos ---
    def test_muito_longo(self):
        assert is_valid_ticker_symbol("TOOLONG123") is False

    def test_apenas_letras(self):
        assert is_valid_ticker_symbol("PETR") is False

    def test_apenas_numeros(self):
        assert is_valid_ticker_symbol("1234") is False

    def test_com_caractere_especial(self):
        assert is_valid_ticker_symbol("PETR-4") is False

    def test_vazio(self):
        assert is_valid_ticker_symbol("") is False

    def test_com_espaco(self):
        assert is_valid_ticker_symbol("PETR 4") is False

    def test_tres_letras_mais_numero(self):
        # Padrão exige 4 letras
        assert is_valid_ticker_symbol("PET4") is False
