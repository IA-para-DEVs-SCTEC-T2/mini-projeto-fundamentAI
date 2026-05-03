"""
Lógica de scoring fundamentalista.

Avalia a qualidade de um ativo com base nos indicadores calculados e nos
critérios definidos em product.md:
- Crescimento sustentável (receita e lucro ≥ 10% a.a.)
- Consistência nos últimos 5 anos
- Ponderação de indicadores (ROE, ROIC, margem, dívida, P/L, P/VP)

O score final é um número de 0 a 100, acompanhado de uma classificação
qualitativa: Excelente (≥75), Bom (≥50), Regular (≥25), Fraco (<25).

Uso:
    from backend.processors.scoring import calculate_score

    result = calculate_score(indicators, history)
    print(result["score"], result["label"])
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds e pesos
# ---------------------------------------------------------------------------

# Pesos de cada componente no score final (soma = 1.0)
_WEIGHTS = {
    "growth": 0.25,       # Crescimento de receita e lucro
    "roe": 0.15,          # Retorno sobre Patrimônio
    "roic": 0.15,         # Retorno sobre Capital Investido
    "net_margin": 0.15,   # Margem Líquida
    "debt_ebitda": 0.15,  # Endividamento
    "valuation": 0.15,    # P/L e P/VP combinados
}

# Thresholds para pontuação máxima de cada indicador
_THRESHOLDS = {
    # Crescimento: ≥10% a.a. = máximo (conforme product.md)
    "growth_excellent": 0.10,   # 10% a.a.
    "growth_good": 0.05,        # 5% a.a.
    "growth_regular": 0.0,      # Positivo mas abaixo de 5%

    # ROE: referência setorial, mas ≥15% é considerado bom
    "roe_excellent": 0.20,      # ≥20%
    "roe_good": 0.15,           # ≥15%
    "roe_regular": 0.08,        # ≥8%

    # ROIC: similar ao ROE
    "roic_excellent": 0.15,     # ≥15%
    "roic_good": 0.10,          # ≥10%
    "roic_regular": 0.05,       # ≥5%

    # Margem Líquida
    "margin_excellent": 0.20,   # ≥20%
    "margin_good": 0.10,        # ≥10%
    "margin_regular": 0.05,     # ≥5%

    # Dívida/EBITDA: quanto menor, melhor
    "debt_excellent": 1.0,      # ≤1x
    "debt_good": 2.0,           # ≤2x
    "debt_regular": 3.0,        # ≤3x

    # P/L: avaliação de valuation (contexto brasileiro)
    "pe_excellent": 10.0,       # ≤10x (barato)
    "pe_good": 15.0,            # ≤15x
    "pe_regular": 25.0,         # ≤25x

    # P/VP
    "pb_excellent": 1.5,        # ≤1.5x
    "pb_good": 3.0,             # ≤3x
    "pb_regular": 5.0,          # ≤5x
}

# Classificações qualitativas
_LABELS = {
    "excellent": "Excelente",
    "good": "Bom",
    "regular": "Regular",
    "weak": "Fraco",
}


# ---------------------------------------------------------------------------
# Funções de pontuação por indicador
# ---------------------------------------------------------------------------


def _score_growth(revenue_growth: Optional[float], net_income_growth: Optional[float]) -> float:
    """
    Pontua o crescimento de receita e lucro (0-100).

    Usa a média dos dois crescimentos. Se apenas um estiver disponível, usa ele.
    Crescimento ≥10% a.a. = 100 pontos (critério do product.md).
    """
    scores = []

    for growth in [revenue_growth, net_income_growth]:
        if growth is None:
            continue
        if growth >= _THRESHOLDS["growth_excellent"]:
            scores.append(100.0)
        elif growth >= _THRESHOLDS["growth_good"]:
            # Interpolação linear entre 5% e 10%
            scores.append(50.0 + (growth - 0.05) / 0.05 * 50.0)
        elif growth >= _THRESHOLDS["growth_regular"]:
            # Interpolação linear entre 0% e 5%
            scores.append(growth / 0.05 * 50.0)
        else:
            # Crescimento negativo: penaliza proporcionalmente
            scores.append(max(0.0, 25.0 + growth * 100))

    if not scores:
        return 50.0  # Neutro quando sem dados

    return sum(scores) / len(scores)


def _score_roe(roe: Optional[float]) -> float:
    """Pontua o ROE (0-100)."""
    if roe is None:
        return 50.0
    if roe >= _THRESHOLDS["roe_excellent"]:
        return 100.0
    if roe >= _THRESHOLDS["roe_good"]:
        return 75.0 + (roe - 0.15) / 0.05 * 25.0
    if roe >= _THRESHOLDS["roe_regular"]:
        return 50.0 + (roe - 0.08) / 0.07 * 25.0
    if roe > 0:
        return roe / 0.08 * 50.0
    return max(0.0, 25.0 + roe * 100)


def _score_roic(roic: Optional[float]) -> float:
    """Pontua o ROIC (0-100)."""
    if roic is None:
        return 50.0
    if roic >= _THRESHOLDS["roic_excellent"]:
        return 100.0
    if roic >= _THRESHOLDS["roic_good"]:
        return 75.0 + (roic - 0.10) / 0.05 * 25.0
    if roic >= _THRESHOLDS["roic_regular"]:
        return 50.0 + (roic - 0.05) / 0.05 * 25.0
    if roic > 0:
        return roic / 0.05 * 50.0
    return max(0.0, 25.0 + roic * 100)


def _score_net_margin(net_margin: Optional[float]) -> float:
    """Pontua a Margem Líquida (0-100)."""
    if net_margin is None:
        return 50.0
    if net_margin >= _THRESHOLDS["margin_excellent"]:
        return 100.0
    if net_margin >= _THRESHOLDS["margin_good"]:
        return 75.0 + (net_margin - 0.10) / 0.10 * 25.0
    if net_margin >= _THRESHOLDS["margin_regular"]:
        return 50.0 + (net_margin - 0.05) / 0.05 * 25.0
    if net_margin > 0:
        return net_margin / 0.05 * 50.0
    return max(0.0, 25.0 + net_margin * 100)


def _score_debt_ebitda(debt_ebitda: Optional[float]) -> float:
    """
    Pontua o índice Dívida/EBITDA (0-100).
    Quanto menor o endividamento, maior a pontuação.
    """
    if debt_ebitda is None:
        return 50.0
    if debt_ebitda < 0:
        # Dívida líquida negativa = empresa com mais caixa que dívida (ótimo)
        return 100.0
    if debt_ebitda <= _THRESHOLDS["debt_excellent"]:
        return 100.0
    if debt_ebitda <= _THRESHOLDS["debt_good"]:
        return 75.0 - (debt_ebitda - 1.0) / 1.0 * 25.0
    if debt_ebitda <= _THRESHOLDS["debt_regular"]:
        return 50.0 - (debt_ebitda - 2.0) / 1.0 * 25.0
    # Acima de 3x: penaliza progressivamente
    return max(0.0, 25.0 - (debt_ebitda - 3.0) * 10.0)


def _score_valuation(pe_ratio: Optional[float], pb_ratio: Optional[float]) -> float:
    """
    Pontua o valuation combinando P/L e P/VP (0-100).

    Contexto brasileiro: P/L abaixo de 10x é considerado barato.
    P/VP abaixo de 1.5x indica ativo negociado próximo ao valor patrimonial.
    """
    scores = []

    if pe_ratio is not None and pe_ratio > 0:
        if pe_ratio <= _THRESHOLDS["pe_excellent"]:
            scores.append(100.0)
        elif pe_ratio <= _THRESHOLDS["pe_good"]:
            scores.append(75.0 - (pe_ratio - 10.0) / 5.0 * 25.0)
        elif pe_ratio <= _THRESHOLDS["pe_regular"]:
            scores.append(50.0 - (pe_ratio - 15.0) / 10.0 * 25.0)
        else:
            scores.append(max(0.0, 25.0 - (pe_ratio - 25.0) * 1.0))

    if pb_ratio is not None and pb_ratio > 0:
        if pb_ratio <= _THRESHOLDS["pb_excellent"]:
            scores.append(100.0)
        elif pb_ratio <= _THRESHOLDS["pb_good"]:
            scores.append(75.0 - (pb_ratio - 1.5) / 1.5 * 25.0)
        elif pb_ratio <= _THRESHOLDS["pb_regular"]:
            scores.append(50.0 - (pb_ratio - 3.0) / 2.0 * 25.0)
        else:
            scores.append(max(0.0, 25.0 - (pb_ratio - 5.0) * 5.0))

    if not scores:
        return 50.0

    return sum(scores) / len(scores)


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------


def calculate_score(indicators: dict, history: Optional[dict] = None) -> dict:
    """
    Calcula o score fundamentalista de um ativo (0-100).

    Args:
        indicators: Dicionário com indicadores calculados por calculate_all_indicators().
                    Chaves esperadas: roe, roic, net_margin, debt_ebitda, pe_ratio,
                    pb_ratio, revenue_growth_yoy, net_income_growth_yoy.
        history: Dicionário opcional com histórico de indicadores para análise
                 de consistência. Não utilizado na versão atual (reservado para v2).

    Returns:
        Dicionário com:
        - score: Float de 0 a 100
        - label: "Excelente" | "Bom" | "Regular" | "Fraco"
        - breakdown: Pontuação detalhada por componente
        - weights: Pesos utilizados
        - available_indicators: Lista de indicadores disponíveis para o cálculo

    Exemplo:
        >>> result = calculate_score({"roe": 0.20, "roic": 0.15, ...})
        >>> print(f"Score: {result['score']:.1f} — {result['label']}")
        Score: 78.3 — Excelente
    """
    # Extrai indicadores
    roe = indicators.get("roe")
    roic = indicators.get("roic")
    net_margin = indicators.get("net_margin")
    debt_ebitda = indicators.get("debt_ebitda")
    pe_ratio = indicators.get("pe_ratio")
    pb_ratio = indicators.get("pb_ratio")
    revenue_growth = indicators.get("revenue_growth_yoy")
    net_income_growth = indicators.get("net_income_growth_yoy")

    # Calcula pontuação por componente
    breakdown = {
        "growth": _score_growth(revenue_growth, net_income_growth),
        "roe": _score_roe(roe),
        "roic": _score_roic(roic),
        "net_margin": _score_net_margin(net_margin),
        "debt_ebitda": _score_debt_ebitda(debt_ebitda),
        "valuation": _score_valuation(pe_ratio, pb_ratio),
    }

    # Score ponderado
    total_score = sum(
        breakdown[component] * weight
        for component, weight in _WEIGHTS.items()
    )
    total_score = round(min(100.0, max(0.0, total_score)), 2)

    # Classificação qualitativa
    label = _get_label(total_score)

    # Indicadores disponíveis (não None)
    available = [k for k, v in indicators.items() if v is not None]

    logger.info(
        "Score calculado: %.1f (%s) | Indicadores disponíveis: %d/%d",
        total_score,
        label,
        len(available),
        len(indicators),
    )

    return {
        "score": total_score,
        "label": label,
        "breakdown": breakdown,
        "weights": _WEIGHTS,
        "available_indicators": available,
    }


def _get_label(score: float) -> str:
    """
    Retorna a classificação qualitativa baseada no score.

    Args:
        score: Score de 0 a 100.

    Returns:
        "Excelente" (≥75), "Bom" (≥50), "Regular" (≥25), "Fraco" (<25).
    """
    if score >= 75:
        return _LABELS["excellent"]
    if score >= 50:
        return _LABELS["good"]
    if score >= 25:
        return _LABELS["regular"]
    return _LABELS["weak"]
