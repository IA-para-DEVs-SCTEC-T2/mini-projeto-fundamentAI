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

Formato esperado do parâmetro `history`:
    {
        "revenue": [100.0, 112.0, 125.0, 138.0, 155.0],   # últimos 5 anos, ordem cronológica
        "net_income": [10.0, 11.5, 13.0, 14.8, 16.5],     # últimos 5 anos, ordem cronológica
        "roe": [0.18, 0.19, 0.20, 0.21, 0.22],             # opcional
        "roic": [0.12, 0.13, 0.14, 0.14, 0.15],            # opcional
        "net_margin": [0.10, 0.10, 0.10, 0.11, 0.11],      # opcional
    }
    Cada lista deve conter ao menos 2 valores para calcular crescimento.
    Com 5 valores é possível avaliar os 4 períodos de crescimento anual.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds e pesos
# ---------------------------------------------------------------------------

# Pesos de cada componente no score final (soma = 1.0)
# Quando histórico está disponível, consistency substitui parte do peso de growth.
_WEIGHTS_WITHOUT_HISTORY = {
    "growth": 0.25,       # Crescimento de receita e lucro (YoY)
    "roe": 0.15,          # Retorno sobre Patrimônio
    "roic": 0.15,         # Retorno sobre Capital Investido
    "net_margin": 0.15,   # Margem Líquida
    "debt_ebitda": 0.15,  # Endividamento
    "valuation": 0.15,    # P/L e P/VP combinados
}

_WEIGHTS_WITH_HISTORY = {
    "growth": 0.15,       # Crescimento YoY (reduzido — consistency complementa)
    "consistency": 0.10,  # Consistência histórica de 5 anos
    "roe": 0.15,          # Retorno sobre Patrimônio
    "roic": 0.15,         # Retorno sobre Capital Investido
    "net_margin": 0.15,   # Margem Líquida
    "debt_ebitda": 0.15,  # Endividamento
    "valuation": 0.15,    # P/L e P/VP combinados
}

# Mantido para compatibilidade — aponta para o conjunto sem histórico por padrão
_WEIGHTS = _WEIGHTS_WITHOUT_HISTORY

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


def _annual_growth_rates(series: list) -> list:
    """
    Calcula as taxas de crescimento anuais a partir de uma série de valores.

    Args:
        series: Lista de valores em ordem cronológica (mais antigo → mais recente).

    Returns:
        Lista de taxas de crescimento anual (ex: 0.10 = 10%).
        Períodos com valor base zero ou negativo são ignorados.
    """
    rates = []
    for i in range(1, len(series)):
        base = series[i - 1]
        current = series[i]
        if base is None or current is None:
            continue
        if base <= 0:
            # Base zero ou negativa: crescimento não é calculável de forma confiável
            continue
        rates.append((current - base) / base)
    return rates


def _score_consistency(history: dict) -> tuple:
    """
    Avalia a consistência do crescimento de receita e lucro nos últimos 5 anos (0-100).

    Critério do product.md:
    - Crescimento anual ≥ 10% em cada período
    - Consistência ao longo dos últimos 5 anos

    Lógica de pontuação:
    - Cada período anual com crescimento ≥ 10% contribui com pontuação máxima
    - Crescimento positivo mas abaixo de 10% contribui parcialmente
    - Crescimento negativo penaliza
    - A pontuação final é a média ponderada de receita e lucro (60/40)

    Args:
        history: Dicionário com séries históricas. Chaves esperadas:
                 "revenue" e/ou "net_income" — listas com valores anuais
                 em ordem cronológica (mais antigo → mais recente).

    Returns:
        Tupla (score: float, detail: dict) onde detail contém:
        - revenue_rates: taxas de crescimento anuais de receita
        - net_income_rates: taxas de crescimento anuais de lucro
        - periods_evaluated: número de períodos avaliados
        - periods_above_threshold: períodos com crescimento ≥ 10%
    """
    revenue_series = history.get("revenue") or []
    net_income_series = history.get("net_income") or []

    revenue_rates = _annual_growth_rates(revenue_series)
    net_income_rates = _annual_growth_rates(net_income_series)

    # Sem dados históricos suficientes
    if not revenue_rates and not net_income_rates:
        return 50.0, {
            "revenue_rates": [],
            "net_income_rates": [],
            "periods_evaluated": 0,
            "periods_above_threshold": 0,
        }

    def _rate_score(rate: float) -> float:
        """Pontua uma única taxa de crescimento anual (0-100)."""
        threshold = _THRESHOLDS["growth_excellent"]  # 10%
        if rate >= threshold:
            return 100.0
        if rate >= _THRESHOLDS["growth_good"]:  # 5%
            return 50.0 + (rate - 0.05) / 0.05 * 50.0
        if rate >= _THRESHOLDS["growth_regular"]:  # 0%
            return rate / 0.05 * 50.0
        # Negativo: penaliza
        return max(0.0, 25.0 + rate * 100)

    component_scores = []
    all_rates = []

    if revenue_rates:
        rev_score = sum(_rate_score(r) for r in revenue_rates) / len(revenue_rates)
        # Receita tem peso 60% na consistência
        component_scores.append((rev_score, 0.60))
        all_rates.extend(revenue_rates)

    if net_income_rates:
        ni_score = sum(_rate_score(r) for r in net_income_rates) / len(net_income_rates)
        # Lucro tem peso 40% na consistência
        component_scores.append((ni_score, 0.40))
        all_rates.extend(net_income_rates)

    # Normaliza pesos caso apenas uma série esteja disponível
    total_weight = sum(w for _, w in component_scores)
    consistency_score = sum(s * (w / total_weight) for s, w in component_scores)

    # Bônus de consistência: penaliza se houver anos com crescimento negativo
    # mesmo que a média seja boa (volatilidade é indesejável)
    negative_periods = sum(1 for r in all_rates if r < 0)
    if negative_periods > 0:
        penalty = negative_periods * 5.0  # -5 pontos por ano negativo
        consistency_score = max(0.0, consistency_score - penalty)

    periods_above = sum(
        1 for r in (revenue_rates + net_income_rates)
        if r >= _THRESHOLDS["growth_excellent"]
    )
    total_periods = len(revenue_rates) + len(net_income_rates)

    detail = {
        "revenue_rates": [round(r, 4) for r in revenue_rates],
        "net_income_rates": [round(r, 4) for r in net_income_rates],
        "periods_evaluated": total_periods,
        "periods_above_threshold": periods_above,
    }

    return round(consistency_score, 2), detail


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
        history: Dicionário opcional com séries históricas para análise de consistência
                 nos últimos 5 anos. Formato esperado:
                 {
                     "revenue": [100.0, 112.0, 125.0, 138.0, 155.0],
                     "net_income": [10.0, 11.5, 13.0, 14.8, 16.5],
                 }
                 Quando fornecido, ativa o componente "consistency" no score e
                 redistribui os pesos (growth: 15%, consistency: 10%).

    Returns:
        Dicionário com:
        - score: Float de 0 a 100
        - label: "Excelente" | "Bom" | "Regular" | "Fraco"
        - breakdown: Pontuação detalhada por componente
        - weights: Pesos utilizados
        - available_indicators: Lista de indicadores disponíveis para o cálculo
        - consistency_detail: Detalhes da análise de consistência (quando history fornecido)

    Exemplo sem histórico:
        >>> result = calculate_score({"roe": 0.20, "roic": 0.15, ...})
        >>> print(f"Score: {result['score']:.1f} — {result['label']}")
        Score: 78.3 — Excelente

    Exemplo com histórico:
        >>> history = {
        ...     "revenue": [100, 112, 125, 140, 158],
        ...     "net_income": [10, 11.5, 13.2, 15.0, 17.1],
        ... }
        >>> result = calculate_score(indicators, history)
        >>> print(result["consistency_detail"])
        {'revenue_rates': [0.12, 0.116, 0.12, 0.129], 'periods_above_threshold': 8, ...}
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

    consistency_detail = None

    # Avalia consistência histórica quando dados estão disponíveis
    has_history = (
        history is not None
        and isinstance(history, dict)
        and (
            len(history.get("revenue") or []) >= 2
            or len(history.get("net_income") or []) >= 2
        )
    )

    if has_history:
        consistency_score, consistency_detail = _score_consistency(history)
        breakdown["consistency"] = consistency_score
        weights = _WEIGHTS_WITH_HISTORY
    else:
        weights = _WEIGHTS_WITHOUT_HISTORY

    # Score ponderado
    total_score = sum(
        breakdown[component] * weight
        for component, weight in weights.items()
    )
    total_score = round(min(100.0, max(0.0, total_score)), 2)

    # Classificação qualitativa
    label = _get_label(total_score)

    # Indicadores disponíveis (não None)
    available = [k for k, v in indicators.items() if v is not None]

    logger.info(
        "Score calculado: %.1f (%s) | Indicadores disponíveis: %d/%d | Histórico: %s",
        total_score,
        label,
        len(available),
        len(indicators),
        "sim" if has_history else "não",
    )

    result = {
        "score": total_score,
        "label": label,
        "breakdown": breakdown,
        "weights": weights,
        "available_indicators": available,
    }

    if consistency_detail is not None:
        result["consistency_detail"] = consistency_detail

    return result


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
