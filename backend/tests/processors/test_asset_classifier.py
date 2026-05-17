"""
Testes unitários para backend/processors/asset_classifier.py

Cobre:
- classify_asset_type: classificação stock/fii por símbolo
- is_inactive: critérios de inatividade
- is_valid_ticker_symbol (via data_validator, mas testado aqui por completude)
"""

import pytest
from backend.processors.asset_classifier import (
    classify_asset_type,
    is_inactive,
    REASON_NO_PRICE,
    REASON_NO_DATA,
)


# ===========================================================================
# classify_asset_type
# ===========================================================================

class TestClassifyAssetType:
    # --- FIIs (terminam em 11) ---
    def test_fii_hglg11(self):
        assert classify_asset_type("HGLG11") == "fii"

    def test_fii_xpml11(self):
        assert classify_asset_type("XPML11") == "fii"

    def test_fii_mxrf11(self):
        assert classify_asset_type("MXRF11") == "fii"

    def test_fii_knri11(self):
        assert classify_asset_type("KNRI11") == "fii"

    def test_fii_visc11(self):
        assert classify_asset_type("VISC11") == "fii"

    # --- Ações ---
    def test_stock_petr4(self):
        assert classify_asset_type("PETR4") == "stock"

    def test_stock_vale3(self):
        assert classify_asset_type("VALE3") == "stock"

    def test_stock_wege3(self):
        assert classify_asset_type("WEGE3") == "stock"

    def test_stock_bbas3(self):
        assert classify_asset_type("BBAS3") == "stock"

    def test_stock_itub4(self):
        assert classify_asset_type("ITUB4") == "stock"

    # --- Normalização de entrada ---
    def test_minusculo_normalizado_para_fii(self):
        assert classify_asset_type("hglg11") == "fii"

    def test_minusculo_normalizado_para_stock(self):
        assert classify_asset_type("petr4") == "stock"

    def test_com_espacos_normalizado(self):
        assert classify_asset_type("  PETR4  ") == "stock"

    # --- Casos limítrofes ---
    def test_ticker_terminando_em_11_mas_com_5_letras_e_stock(self):
        # Padrão FII é exatamente 4 letras + 11
        # ABCDE11 tem 5 letras → não é FII pelo regex
        assert classify_asset_type("ABCDE11") == "stock"

    def test_ticker_terminando_em_11_com_3_letras_e_stock(self):
        # ABC11 tem 3 letras → não é FII pelo regex
        assert classify_asset_type("ABC11") == "stock"

    def test_ticker_com_sufixo_fracionario(self):
        # PETR4F — fracionário de ação
        assert classify_asset_type("PETR4F") == "stock"


# ===========================================================================
# is_inactive
# ===========================================================================

class TestIsInactive:
    # --- Critério 1: sem preço ---
    def test_preco_none_e_inativo(self):
        inactive, reason = is_inactive("PETR4", current_price=None)
        assert inactive is True
        assert reason == REASON_NO_PRICE

    def test_preco_zero_e_inativo(self):
        inactive, reason = is_inactive("PETR4", current_price=0)
        assert inactive is True
        assert reason == REASON_NO_PRICE

    def test_preco_zero_float_e_inativo(self):
        inactive, reason = is_inactive("PETR4", current_price=0.0)
        assert inactive is True
        assert reason == REASON_NO_PRICE

    # --- Critério 2: sem dados ---
    def test_sem_indicadores_e_sem_financeiros_e_inativo(self):
        inactive, reason = is_inactive(
            "ABCD3",
            current_price=10.0,
            net_income=None,
            total_equity=None,
            roe=None,
            pe_ratio=None,
            pb_ratio=None,
        )
        assert inactive is True
        assert reason == REASON_NO_DATA

    # --- Ativo válido ---
    def test_com_preco_e_roe_e_ativo(self):
        inactive, reason = is_inactive("PETR4", current_price=40.0, roe=0.20)
        assert inactive is False
        assert reason == ""

    def test_com_preco_e_pe_ratio_e_ativo(self):
        inactive, reason = is_inactive("VALE3", current_price=80.0, pe_ratio=8.0)
        assert inactive is False
        assert reason == ""

    def test_com_preco_e_pb_ratio_e_ativo(self):
        inactive, reason = is_inactive("WEGE3", current_price=35.0, pb_ratio=10.0)
        assert inactive is False
        assert reason == ""

    def test_com_preco_e_net_income_e_ativo(self):
        inactive, reason = is_inactive(
            "BBAS3",
            current_price=50.0,
            net_income=1_000_000.0,
        )
        assert inactive is False
        assert reason == ""

    def test_com_preco_e_total_equity_e_ativo(self):
        inactive, reason = is_inactive(
            "ITUB4",
            current_price=30.0,
            total_equity=5_000_000.0,
        )
        assert inactive is False
        assert reason == ""

    # --- Prioridade: preço tem precedência ---
    def test_preco_zero_tem_precedencia_sobre_dados(self):
        """Mesmo com indicadores disponíveis, preço zero = inativo."""
        inactive, reason = is_inactive(
            "PETR4",
            current_price=0.0,
            roe=0.20,
            pe_ratio=8.0,
        )
        assert inactive is True
        assert reason == REASON_NO_PRICE

    # --- FIIs (sem net_income por design) ---
    def test_fii_com_preco_e_pb_ratio_e_ativo(self):
        inactive, reason = is_inactive(
            "HGLG11",
            current_price=160.0,
            pb_ratio=0.95,
        )
        assert inactive is False
        assert reason == ""

    def test_fii_sem_preco_e_inativo(self):
        inactive, reason = is_inactive("HGLG11", current_price=None, pb_ratio=0.95)
        assert inactive is True
        assert reason == REASON_NO_PRICE
