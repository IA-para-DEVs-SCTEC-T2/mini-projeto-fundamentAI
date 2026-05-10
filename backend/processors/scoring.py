"""
Lógica de scoring fundamentalista — ações e FIIs.

Cada tipo de ativo usa indicadores específicos para o cálculo do score,
mas o OUTPUT é idêntico para ambos:
- score: float 0-100
- label: "Excelente" | "Bom" | "Regular" | "Fraco"
- breakdown: pontuação detalhada por componente
- weights: pesos utilizados

Isso garante que o frontend não precise ser alterado.

=== AÇÕES ===
Indicadores e pesos:
  - P/L (Valuation)          : 15%
  - ROE                      : 20%
  - Dívida Líquida / EBITDA  : 15%
  - Margem Líquida           : 15%
  - EV/EBITDA                : 10%
  - Dividend Yield           : 10%
  - Crescimento Lucro YoY    : 15%

=== FIIs ===
Indicadores e pesos:
  - P/VP                     : 30%
  - P/L                      : 15%
  - Dividend Yield           : 35%
  - Crescimento Dividendos   : 20%

Uso:
    from backend.processors.scoring import calculate_score

    # Ação
    result = calculate_score(indicators, asset_type="stock")

    # FII
    result = calculate_score(indicators, asset_type="fii")
"""

import logging
from typing import Optional

from backend.db.models import ASSET_TYPE_FII, ASSET_TYPE_STOCK

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Classificações qualitativas (iguais para ações e FIIs)
# ---------------------------------------------------------------------------

_LABELS = {
    "excellent": "Excelente",
    "good": "Bom",
    "regular": "Regular",
    "weak": "Fraco",
}


def _get_label(score: float) -> str:
    if score >= 75:
        return _LABELS["excellent"]
    if score >= 50:
        return _LABELS["good"]
    if score >= 25:
        return _LABELS["regular"]
    return _LABELS["weak"]


# ===========================================================================
# SCORING DE AÇÕES
# ===========================================================================

_STOCK_WEIGHTS = {
    "pe_ratio":             0.15,
    "roe":                  0.20,
    "debt_ebitda":          0.15,
    "net_margin":           0.15,
    "ev_ebitda":            0.10,
    "dividend_yield":       0.10,
    "net_income_growth":    0.15,
}

_STOCK_THRESHOLDS = {
    # P/L: quanto menor, mais barato (contexto B3)
    "pe_excellent": 10.0,
    "pe_good":      15.0,
    "pe_regular":   25.0,
    # ROE: ≥15% é referência para ações brasileiras
    "roe_excellent": 0.20,
    "roe_good":      0.15,
    "roe_regular":   0.08,
    # Dívida/EBITDA: quanto menor, melhor
    "debt_excellent": 1.0,
    "debt_good":      2.0,
    "debt_regular":   3.0,
    # Margem Líquida
    "margin_excellent": 0.20,
    "margin_good":      0.10,
    "margin_regular":   0.05,
    # EV/EBITDA: quanto menor, mais barato
    "ev_excellent": 6.0,
    "ev_good":      10.0,
    "ev_regular":   15.0,
    # Dividend Yield (decimal): ≥6% é atrativo no Brasil
    "dy_excellent": 0.08,
    "dy_good":      0.06,
    "dy_regular":   0.03,
    # Crescimento de lucro YoY: ≥10% a.a.
    "growth_excellent": 0.10,
    "growth_good":      0.05,
    "growth_regular":   0.0,
}


def _score_pe_ratio(pe: Optional[float]) -> float:
    """P/L: quanto menor, melhor. Negativo = empresa com prejuízo."""
    if pe is None:
        return 50.0
    if pe <= 0:
        return 10.0  # Prejuízo
    t = _STOCK_THRESHOLDS
    if pe <= t["pe_excellent"]:
        return 100.0
    if pe <= t["pe_good"]:
        return 75.0 - (pe - t["pe_excellent"]) / (t["pe_good"] - t["pe_excellent"]) * 25.0
    if pe <= t["pe_regular"]:
        return 50.0 - (pe - t["pe_good"]) / (t["pe_regular"] - t["pe_good"]) * 25.0
    return max(0.0, 25.0 - (pe - t["pe_regular"]) * 1.0)


def _score_roe(roe: Optional[float]) -> float:
    """ROE: quanto maior, melhor."""
    if roe is None:
        return 50.0
    t = _STOCK_THRESHOLDS
    if roe >= t["roe_excellent"]:
        return 100.0
    if roe >= t["roe_good"]:
        return 75.0 + (roe - t["roe_good"]) / (t["roe_excellent"] - t["roe_good"]) * 25.0
    if roe >= t["roe_regular"]:
        return 50.0 + (roe - t["roe_regular"]) / (t["roe_good"] - t["roe_regular"]) * 25.0
    if roe > 0:
        return roe / t["roe_regular"] * 50.0
    return max(0.0, 25.0 + roe * 100)


def _score_debt_ebitda(debt: Optional[float]) -> float:
    """Dívida/EBITDA: quanto menor, melhor. Negativo = caixa líquido (ótimo)."""
    if debt is None:
        return 50.0
    if debt < 0:
        return 100.0
    t = _STOCK_THRESHOLDS
    if debt <= t["debt_excellent"]:
        return 100.0
    if debt <= t["debt_good"]:
        return 75.0 - (debt - t["debt_excellent"]) / (t["debt_good"] - t["debt_excellent"]) * 25.0
    if debt <= t["debt_regular"]:
        return 50.0 - (debt - t["debt_good"]) / (t["debt_regular"] - t["debt_good"]) * 25.0
    return max(0.0, 25.0 - (debt - t["debt_regular"]) * 10.0)


def _score_net_margin(margin: Optional[float]) -> float:
    """Margem líquida: quanto maior, melhor."""
    if margin is None:
        return 50.0
    t = _STOCK_THRESHOLDS
    if margin >= t["margin_excellent"]:
        return 100.0
    if margin >= t["margin_good"]:
        return 75.0 + (margin - t["margin_good"]) / (t["margin_excellent"] - t["margin_good"]) * 25.0
    if margin >= t["margin_regular"]:
        return 50.0 + (margin - t["margin_regular"]) / (t["margin_good"] - t["margin_regular"]) * 25.0
    if margin > 0:
        return margin / t["margin_regular"] * 50.0
    return max(0.0, 25.0 + margin * 100)


def _score_ev_ebitda(ev: Optional[float]) -> float:
    """EV/EBITDA: quanto menor, mais barato."""
    if ev is None:
        return 50.0
    if ev <= 0:
        return 50.0
    t = _STOCK_THRESHOLDS
    if ev <= t["ev_excellent"]:
        return 100.0
    if ev <= t["ev_good"]:
        return 75.0 - (ev - t["ev_excellent"]) / (t["ev_good"] - t["ev_excellent"]) * 25.0
    if ev <= t["ev_regular"]:
        return 50.0 - (ev - t["ev_good"]) / (t["ev_regular"] - t["ev_good"]) * 25.0
    return max(0.0, 25.0 - (ev - t["ev_regular"]) * 2.0)


def _score_dividend_yield_stock(dy: Optional[float]) -> float:
    """Dividend Yield para ações: quanto maior, melhor."""
    if dy is None:
        return 50.0
    t = _STOCK_THRESHOLDS
    if dy >= t["dy_excellent"]:
        return 100.0
    if dy >= t["dy_good"]:
        return 75.0 + (dy - t["dy_good"]) / (t["dy_excellent"] - t["dy_good"]) * 25.0
    if dy >= t["dy_regular"]:
        return 50.0 + (dy - t["dy_regular"]) / (t["dy_good"] - t["dy_regular"]) * 25.0
    if dy > 0:
        return dy / t["dy_regular"] * 50.0
    return 25.0


def _score_net_income_growth(growth: Optional[float]) -> float:
    """Crescimento de lucro YoY: ≥10% a.a. = máximo."""
    if growth is None:
        return 50.0
    t = _STOCK_THRESHOLDS
    if growth >= t["growth_excellent"]:
        return 100.0
    if growth >= t["growth_good"]:
        return 50.0 + (growth - t["growth_good"]) / (t["growth_excellent"] - t["growth_good"]) * 50.0
    if growth >= t["growth_regular"]:
        return growth / t["growth_good"] * 50.0
    return max(0.0, 25.0 + growth * 100)


def calculate_stock_score(indicators: dict) -> dict:
    """
    Calcula o score fundamentalista para uma AÇÃO.

    Args:
        indicators: Dicionário com indicadores da ação.
            Chaves: pe_ratio, roe, debt_ebitda, net_margin, ev_ebitda,
                    dividend_yield, net_income_growth_yoy

    Returns:
        Dicionário com score, label, breakdown e weights.
    """
    breakdown = {
        "pe_ratio":          _score_pe_ratio(indicators.get("pe_ratio")),
        "roe":               _score_roe(indicators.get("roe")),
        "debt_ebitda":       _score_debt_ebitda(indicators.get("debt_ebitda")),
        "net_margin":        _score_net_margin(indicators.get("net_margin")),
        "ev_ebitda":         _score_ev_ebitda(indicators.get("ev_ebitda")),
        "dividend_yield":    _score_dividend_yield_stock(indicators.get("dividend_yield")),
        "net_income_growth": _score_net_income_growth(indicators.get("net_income_growth_yoy")),
    }

    total = sum(breakdown[k] * _STOCK_WEIGHTS[k] for k in _STOCK_WEIGHTS)
    total = round(min(100.0, max(0.0, total)), 2)

    available = [k for k, v in indicators.items() if v is not None]
    logger.info("Score AÇÃO: %.1f (%s) | Indicadores: %d/%d",
                total, _get_label(total), len(available), len(indicators))

    return {
        "score": total,
        "label": _get_label(total),
        "breakdown": breakdown,
        "weights": _STOCK_WEIGHTS,
        "available_indicators": available,
        "asset_type": ASSET_TYPE_STOCK,
    }


# ===========================================================================
# SCORING DE FIIs
# ===========================================================================

_FII_WEIGHTS = {
    "pb_ratio":           0.30,
    "pe_ratio":           0.15,
    "dividend_yield":     0.35,
    "dividend_growth":    0.20,
}

_FII_THRESHOLDS = {
    # P/VP: < 1 = desconto sobre o patrimônio (atrativo)
    "pvp_excellent": 0.90,   # ≤ 0.90 = desconto significativo
    "pvp_good":      1.00,   # ≤ 1.00 = no valor patrimonial
    "pvp_regular":   1.10,   # ≤ 1.10 = leve prêmio
    # P/L para FIIs (baseado em rendimentos)
    "pe_excellent": 12.0,
    "pe_good":      16.0,
    "pe_regular":   22.0,
    # Dividend Yield: FIIs geralmente pagam mais que ações
    "dy_excellent": 0.10,    # ≥ 10% a.a.
    "dy_good":      0.08,    # ≥ 8% a.a.
    "dy_regular":   0.06,    # ≥ 6% a.a.
    # Crescimento de dividendos YoY
    "dg_excellent": 0.08,    # ≥ 8% a.a.
    "dg_good":      0.04,    # ≥ 4% a.a.
    "dg_regular":   0.0,     # Positivo
}


def _score_pvp_fii(pvp: Optional[float]) -> float:
    """P/VP para FIIs: abaixo de 1 é atrativo (desconto sobre patrimônio)."""
    if pvp is None:
        return 50.0
    t = _FII_THRESHOLDS
    if pvp <= t["pvp_excellent"]:
        return 100.0
    if pvp <= t["pvp_good"]:
        return 75.0 + (t["pvp_good"] - pvp) / (t["pvp_good"] - t["pvp_excellent"]) * 25.0
    if pvp <= t["pvp_regular"]:
        return 50.0 + (t["pvp_regular"] - pvp) / (t["pvp_regular"] - t["pvp_good"]) * 25.0
    # Acima de 1.10: penaliza progressivamente
    return max(0.0, 50.0 - (pvp - t["pvp_regular"]) * 100.0)


def _score_pe_fii(pe: Optional[float]) -> float:
    """P/L para FIIs."""
    if pe is None:
        return 50.0
    if pe <= 0:
        return 10.0
    t = _FII_THRESHOLDS
    if pe <= t["pe_excellent"]:
        return 100.0
    if pe <= t["pe_good"]:
        return 75.0 - (pe - t["pe_excellent"]) / (t["pe_good"] - t["pe_excellent"]) * 25.0
    if pe <= t["pe_regular"]:
        return 50.0 - (pe - t["pe_good"]) / (t["pe_regular"] - t["pe_good"]) * 25.0
    return max(0.0, 25.0 - (pe - t["pe_regular"]) * 1.0)


def _score_dividend_yield_fii(dy: Optional[float]) -> float:
    """Dividend Yield para FIIs: quanto maior, melhor. Referência mais alta que ações."""
    if dy is None:
        return 50.0
    t = _FII_THRESHOLDS
    if dy >= t["dy_excellent"]:
        return 100.0
    if dy >= t["dy_good"]:
        return 75.0 + (dy - t["dy_good"]) / (t["dy_excellent"] - t["dy_good"]) * 25.0
    if dy >= t["dy_regular"]:
        return 50.0 + (dy - t["dy_regular"]) / (t["dy_good"] - t["dy_regular"]) * 25.0
    if dy > 0:
        return dy / t["dy_regular"] * 50.0
    return 25.0


def _score_dividend_growth(growth: Optional[float]) -> float:
    """Crescimento de dividendos YoY para FIIs."""
    if growth is None:
        return 50.0
    t = _FII_THRESHOLDS
    if growth >= t["dg_excellent"]:
        return 100.0
    if growth >= t["dg_good"]:
        return 75.0 + (growth - t["dg_good"]) / (t["dg_excellent"] - t["dg_good"]) * 25.0
    if growth >= t["dg_regular"]:
        return 50.0 + growth / t["dg_good"] * 25.0
    return max(0.0, 25.0 + growth * 100)


def calculate_fii_score(indicators: dict) -> dict:
    """
    Calcula o score fundamentalista para um FII.

    Args:
        indicators: Dicionário com indicadores do FII.
            Chaves: pb_ratio, pe_ratio, dividend_yield, dividend_growth_yoy

    Returns:
        Dicionário com score, label, breakdown e weights (mesmo formato que ações).
    """
    breakdown = {
        "pb_ratio":        _score_pvp_fii(indicators.get("pb_ratio")),
        "pe_ratio":        _score_pe_fii(indicators.get("pe_ratio")),
        "dividend_yield":  _score_dividend_yield_fii(indicators.get("dividend_yield")),
        "dividend_growth": _score_dividend_growth(indicators.get("dividend_growth_yoy")),
    }

    total = sum(breakdown[k] * _FII_WEIGHTS[k] for k in _FII_WEIGHTS)
    total = round(min(100.0, max(0.0, total)), 2)

    available = [k for k, v in indicators.items() if v is not None]
    logger.info("Score FII: %.1f (%s) | Indicadores: %d/%d",
                total, _get_label(total), len(available), len(indicators))

    return {
        "score": total,
        "label": _get_label(total),
        "breakdown": breakdown,
        "weights": _FII_WEIGHTS,
        "available_indicators": available,
        "asset_type": ASSET_TYPE_FII,
    }


# ===========================================================================
# Função unificada (entry point)
# ===========================================================================


def calculate_score(indicators: dict, asset_type: str = ASSET_TYPE_STOCK) -> dict:
    """
    Calcula o score fundamentalista para qualquer tipo de ativo.

    Despacha para calculate_stock_score() ou calculate_fii_score()
    conforme o asset_type. O output é idêntico para ambos.

    Args:
        indicators: Dicionário com indicadores do ativo.
        asset_type: "stock" (padrão) ou "fii".

    Returns:
        Dicionário com:
        - score: float 0-100
        - label: "Excelente" | "Bom" | "Regular" | "Fraco"
        - breakdown: pontuação por componente
        - weights: pesos utilizados
        - available_indicators: indicadores com dados
        - asset_type: tipo do ativo

    Exemplo:
        >>> # Ação
        >>> result = calculate_score({"roe": 0.20, "pe_ratio": 12.0, ...}, "stock")
        >>> # FII
        >>> result = calculate_score({"pb_ratio": 0.95, "dividend_yield": 0.09, ...}, "fii")
        >>> print(result["score"], result["label"])
    """
    if asset_type == ASSET_TYPE_FII:
        return calculate_fii_score(indicators)
    return calculate_stock_score(indicators)
