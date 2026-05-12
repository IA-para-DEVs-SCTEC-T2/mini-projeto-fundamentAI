"""
Cálculo de indicadores fundamentalistas.

Recebe dados financeiros brutos (coletados pelos collectors) e calcula
os indicadores usados na análise e no scoring.

Todos os cálculos são funções puras — sem dependência de banco ou API.
Isso facilita testes unitários e reutilização.

Uso:
    from backend.processors.indicators import calculate_all_indicators

    indicators = calculate_all_indicators(financial_data, quote_data)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Indicadores individuais
# ---------------------------------------------------------------------------


def calculate_roe(net_income: Optional[float], total_equity: Optional[float]) -> Optional[float]:
    """
    Calcula o ROE (Return on Equity / Retorno sobre Patrimônio Líquido).

    Fórmula: ROE = Lucro Líquido / Patrimônio Líquido

    Args:
        net_income: Lucro líquido do período.
        total_equity: Patrimônio líquido.

    Returns:
        ROE como decimal (ex: 0.18 = 18%) ou None se dados insuficientes.

    Exemplo:
        >>> calculate_roe(1_000_000, 5_000_000)
        0.2
    """
    if net_income is None or total_equity is None:
        return None
    if total_equity == 0:
        logger.warning("ROE: patrimônio líquido é zero — divisão por zero evitada")
        return None
    return net_income / total_equity


def calculate_roic(
    net_income: Optional[float],
    total_debt: Optional[float],
    total_equity: Optional[float],
    cash: Optional[float] = None,
) -> Optional[float]:
    """
    Calcula o ROIC (Return on Invested Capital / Retorno sobre Capital Investido).

    Fórmula: ROIC = NOPAT / Capital Investido
    Aproximação: ROIC = Lucro Líquido / (Dívida Total + Patrimônio Líquido - Caixa)

    Args:
        net_income: Lucro líquido do período.
        total_debt: Dívida total (curto + longo prazo).
        total_equity: Patrimônio líquido.
        cash: Caixa e equivalentes (opcional, para calcular dívida líquida).

    Returns:
        ROIC como decimal ou None se dados insuficientes.

    Exemplo:
        >>> calculate_roic(1_000_000, 3_000_000, 5_000_000)
        0.125
    """
    if net_income is None or total_debt is None or total_equity is None:
        return None

    cash_value = cash or 0.0
    invested_capital = total_debt + total_equity - cash_value

    if invested_capital <= 0:
        logger.warning("ROIC: capital investido <= 0 — divisão por zero evitada")
        return None

    return net_income / invested_capital


def calculate_net_margin(
    net_income: Optional[float], revenue: Optional[float]
) -> Optional[float]:
    """
    Calcula a Margem Líquida.

    Fórmula: Margem Líquida = Lucro Líquido / Receita Líquida

    Args:
        net_income: Lucro líquido do período.
        revenue: Receita líquida do período.

    Returns:
        Margem líquida como decimal (ex: 0.12 = 12%) ou None.

    Exemplo:
        >>> calculate_net_margin(1_200_000, 10_000_000)
        0.12
    """
    if net_income is None or revenue is None:
        return None
    if revenue == 0:
        logger.warning("Margem líquida: receita é zero — divisão por zero evitada")
        return None
    return net_income / revenue


def calculate_debt_ebitda(
    net_debt: Optional[float], ebitda: Optional[float]
) -> Optional[float]:
    """
    Calcula o índice Dívida Líquida / EBITDA.

    Mede o nível de alavancagem financeira. Valores abaixo de 2x são
    geralmente considerados saudáveis; acima de 3x indicam alto endividamento.

    Fórmula: Dívida Líquida / EBITDA

    Args:
        net_debt: Dívida líquida (Dívida Total - Caixa).
        ebitda: EBITDA do período.

    Returns:
        Índice de alavancagem ou None se dados insuficientes.
        Retorna None se EBITDA for negativo (empresa com prejuízo operacional).

    Exemplo:
        >>> calculate_debt_ebitda(6_000_000, 3_000_000)
        2.0
    """
    if net_debt is None or ebitda is None:
        return None
    if ebitda <= 0:
        logger.warning("Dívida/EBITDA: EBITDA <= 0 — índice não calculável")
        return None
    return net_debt / ebitda


def calculate_pe_ratio(
    current_price: Optional[float], earnings_per_share: Optional[float] = None,
    net_income: Optional[float] = None, shares_outstanding: Optional[float] = None,
) -> Optional[float]:
    """
    Calcula o P/L (Preço / Lucro).

    Pode ser calculado de duas formas:
    1. P/L = Preço atual / LPA (Lucro por Ação)
    2. P/L = Market Cap / Lucro Líquido

    Args:
        current_price: Preço atual da ação.
        earnings_per_share: LPA (Lucro por Ação). Prioritário se fornecido.
        net_income: Lucro líquido total (alternativa ao LPA).
        shares_outstanding: Número de ações em circulação (necessário com net_income).

    Returns:
        P/L ou None se dados insuficientes.

    Exemplo:
        >>> calculate_pe_ratio(current_price=38.50, earnings_per_share=3.85)
        10.0
    """
    if current_price is None:
        return None

    if earnings_per_share is not None:
        if earnings_per_share <= 0:
            logger.warning("P/L: LPA <= 0 (empresa com prejuízo) — P/L não calculável")
            return None
        return current_price / earnings_per_share

    if net_income is not None and shares_outstanding is not None:
        if shares_outstanding <= 0 or net_income <= 0:
            return None
        lpa = net_income / shares_outstanding
        return current_price / lpa

    return None


def calculate_pb_ratio(
    current_price: Optional[float],
    book_value_per_share: Optional[float] = None,
    total_equity: Optional[float] = None,
    shares_outstanding: Optional[float] = None,
) -> Optional[float]:
    """
    Calcula o P/VP (Preço / Valor Patrimonial por Ação).

    Pode ser calculado de duas formas:
    1. P/VP = Preço atual / VPA (Valor Patrimonial por Ação)
    2. P/VP = Market Cap / Patrimônio Líquido

    Args:
        current_price: Preço atual da ação.
        book_value_per_share: VPA (Valor Patrimonial por Ação). Prioritário.
        total_equity: Patrimônio líquido total (alternativa ao VPA).
        shares_outstanding: Número de ações em circulação.

    Returns:
        P/VP ou None se dados insuficientes.

    Exemplo:
        >>> calculate_pb_ratio(current_price=38.50, book_value_per_share=25.0)
        1.54
    """
    if current_price is None:
        return None

    if book_value_per_share is not None:
        if book_value_per_share <= 0:
            logger.warning("P/VP: VPA <= 0 — P/VP não calculável")
            return None
        return current_price / book_value_per_share

    if total_equity is not None and shares_outstanding is not None:
        if shares_outstanding <= 0 or total_equity <= 0:
            return None
        vpa = total_equity / shares_outstanding
        return current_price / vpa

    return None


def calculate_revenue_growth(revenue_history: list[float]) -> Optional[float]:
    """
    Calcula o crescimento médio anual de receita (CAGR) com base no histórico.

    Args:
        revenue_history: Lista de receitas anuais, do mais recente para o mais antigo.
                         Ex: [120, 110, 100, 90, 80] (últimos 5 anos)

    Returns:
        CAGR como decimal (ex: 0.10 = 10% a.a.) ou None se histórico insuficiente.

    Exemplo:
        >>> calculate_revenue_growth([161.05, 146.41, 133.1, 121.0, 110.0])
        0.1  # ~10% a.a.
    """
    return _calculate_cagr(revenue_history)


def calculate_net_income_growth(net_income_history: list[float]) -> Optional[float]:
    """
    Calcula o crescimento médio anual de lucro líquido (CAGR).

    Args:
        net_income_history: Lista de lucros anuais, do mais recente para o mais antigo.

    Returns:
        CAGR como decimal ou None se histórico insuficiente.
    """
    return _calculate_cagr(net_income_history)


def _calculate_cagr(values: list[float]) -> Optional[float]:
    """
    Calcula o CAGR (Compound Annual Growth Rate) a partir de uma lista de valores.

    Fórmula: CAGR = (Valor_Final / Valor_Inicial) ^ (1 / n_anos) - 1

    Args:
        values: Lista de valores anuais, do mais recente para o mais antigo.

    Returns:
        CAGR como decimal ou None se dados insuficientes ou inválidos.
    """
    if not values or len(values) < 2:
        return None

    # Remove None e zeros
    clean = [v for v in values if v is not None and v != 0]
    if len(clean) < 2:
        return None

    # Mais recente é o primeiro elemento
    final_value = clean[0]
    initial_value = clean[-1]
    n_years = len(clean) - 1

    if initial_value <= 0 or final_value <= 0:
        # Empresa com histórico de prejuízo — CAGR não é representativo
        return None

    try:
        cagr = (final_value / initial_value) ** (1 / n_years) - 1
        return round(cagr, 6)
    except (ZeroDivisionError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Função agregadora
# ---------------------------------------------------------------------------


def calculate_all_indicators(
    financial_data: dict,
    quote_data: Optional[dict] = None,
    fundamentus_data: Optional[dict] = None,
) -> dict:
    """
    Calcula todos os indicadores fundamentalistas a partir dos dados coletados.

    Prioridade dos dados:
    1. fundamentus_data (indicadores já calculados pela fonte)
    2. Cálculo próprio a partir de financial_data + quote_data

    Args:
        financial_data: Dicionário retornado por extract_key_financials() do yfinance.
        quote_data: Dicionário retornado por get_stock_quote() do yfinance.
        fundamentus_data: Dicionário retornado por get_fundamentals() do fundamentus.

    Returns:
        Dicionário com todos os indicadores calculados:
        - roe, roic, net_margin, debt_ebitda, pe_ratio, pb_ratio
        - revenue_growth_yoy, net_income_growth_yoy
        - Cada valor é float ou None se não calculável.

    Exemplo:
        >>> indicators = calculate_all_indicators(financial_data, quote_data)
        >>> print(f"ROE: {indicators['roe']:.1%}")
    """
    current_price = quote_data.get("current_price") if quote_data else None

    # Dados do yfinance
    net_income = financial_data.get("net_income")
    revenue = financial_data.get("revenue")
    ebitda = financial_data.get("ebitda")
    total_equity = financial_data.get("total_equity")
    total_debt = financial_data.get("total_debt")
    net_debt = financial_data.get("net_debt")
    revenue_history = financial_data.get("revenue_history", [])
    net_income_history = financial_data.get("net_income_history", [])

    # Calcula indicadores — usa fundamentus se disponível, senão calcula
    def _prefer_fundamentus(key: str, calculated: Optional[float]) -> Optional[float]:
        """Prefere o valor do fundamentus se disponível e válido."""
        if fundamentus_data and fundamentus_data.get(key) is not None:
            return fundamentus_data[key]
        return calculated

    roe = _prefer_fundamentus(
        "roe",
        calculate_roe(net_income, total_equity),
    )
    roic = _prefer_fundamentus(
        "roic",
        calculate_roic(net_income, total_debt, total_equity),
    )
    net_margin = _prefer_fundamentus(
        "net_margin",
        calculate_net_margin(net_income, revenue),
    )
    debt_ebitda = _prefer_fundamentus(
        "debt_ebitda",
        calculate_debt_ebitda(net_debt, ebitda),
    )
    pe_ratio = _prefer_fundamentus(
        "pe_ratio",
        calculate_pe_ratio(current_price, net_income=net_income,
                           shares_outstanding=quote_data.get("shares_outstanding") if quote_data else None),
    )
    pb_ratio = _prefer_fundamentus(
        "pb_ratio",
        calculate_pb_ratio(current_price, total_equity=total_equity,
                           shares_outstanding=quote_data.get("shares_outstanding") if quote_data else None),
    )

    revenue_growth = calculate_revenue_growth(revenue_history)
    net_income_growth = calculate_net_income_growth(net_income_history)

    indicators = {
        "roe": roe,
        "roic": roic,
        "net_margin": net_margin,
        "debt_ebitda": debt_ebitda,
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "revenue_growth_yoy": revenue_growth,
        "net_income_growth_yoy": net_income_growth,
    }

    # Log de indicadores calculados
    available = [k for k, v in indicators.items() if v is not None]
    missing = [k for k, v in indicators.items() if v is None]
    logger.info("Indicadores calculados: %s | Indisponíveis: %s", available, missing)

    return indicators
