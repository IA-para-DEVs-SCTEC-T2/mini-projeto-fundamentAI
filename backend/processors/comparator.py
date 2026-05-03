"""
Comparação setorial de indicadores fundamentalistas.

Compara os indicadores de um ativo com a média das empresas do mesmo setor,
fornecendo contexto relativo para a análise.

Uso:
    from backend.processors.comparator import compare_to_sector, get_sector_companies

    comparison = compare_to_sector("PETR4", indicators, sector="Petróleo")
    companies = get_sector_companies("Petróleo")
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Indicadores usados na comparação setorial
_COMPARISON_INDICATORS = ["roe", "roic", "net_margin", "debt_ebitda", "pe_ratio", "pb_ratio"]

# Mapeamento de setores do fundamentus para nomes padronizados
# Baseado na classificação setorial da B3/fundamentus
_SECTOR_ALIASES: dict[str, list[str]] = {
    "Petróleo, Gás e Biocombustíveis": ["Petróleo", "Petroleo", "Oil", "Gas"],
    "Financeiro e Outros": ["Financeiro", "Bancos", "Seguros", "Finance"],
    "Utilidade Pública": ["Energia", "Elétrico", "Saneamento", "Utility"],
    "Materiais Básicos": ["Mineração", "Siderurgia", "Química", "Materials"],
    "Consumo Cíclico": ["Varejo", "Automóveis", "Têxtil", "Consumer Cyclical"],
    "Consumo Não Cíclico": ["Alimentos", "Bebidas", "Saúde", "Consumer Staples"],
    "Saúde": ["Farmacêutico", "Hospitais", "Healthcare"],
    "Tecnologia da Informação": ["Tecnologia", "Software", "TI", "Technology"],
    "Telecomunicações": ["Telecom", "Comunicações"],
    "Imobiliário": ["FII", "Real Estate", "Imóveis"],
    "Bens Industriais": ["Indústria", "Construção", "Industrial"],
    "Transporte": ["Logística", "Aviação", "Transport"],
}


def get_sector_companies(sector: str, min_companies: int = 3) -> pd.DataFrame:
    """
    Retorna empresas do mesmo setor com seus indicadores via fundamentus.

    Args:
        sector: Nome do setor (ex: "Petróleo, Gás e Biocombustíveis").
        min_companies: Número mínimo de empresas para considerar o setor válido.

    Returns:
        DataFrame com empresas do setor e seus indicadores.
        Retorna DataFrame vazio se o setor tiver menos que min_companies.

    Exemplo:
        >>> companies = get_sector_companies("Financeiro e Outros")
        >>> print(f"Empresas no setor: {len(companies)}")
    """
    try:
        import fundamentus  # type: ignore

        all_data = fundamentus.get_resultado()

        if all_data is None or all_data.empty:
            logger.warning("Nenhum dado disponível no fundamentus para comparação setorial")
            return pd.DataFrame()

        # Filtra por setor — tenta correspondência exata e por aliases
        sector_filter = _build_sector_filter(all_data, sector)

        if sector_filter is None or sector_filter.sum() == 0:
            logger.warning("Setor '%s' não encontrado no fundamentus", sector)
            return pd.DataFrame()

        sector_companies = all_data[sector_filter].copy()

        if len(sector_companies) < min_companies:
            logger.warning(
                "Setor '%s' tem apenas %d empresa(s) — mínimo é %d",
                sector,
                len(sector_companies),
                min_companies,
            )
            return pd.DataFrame()

        logger.info("Empresas encontradas no setor '%s': %d", sector, len(sector_companies))
        return sector_companies

    except ImportError:
        logger.error("Biblioteca 'fundamentus' não instalada")
        return pd.DataFrame()
    except Exception as exc:
        logger.error("Erro ao buscar empresas do setor '%s': %s", sector, exc)
        return pd.DataFrame()


def calculate_sector_averages(sector_companies: pd.DataFrame) -> dict:
    """
    Calcula as médias dos indicadores fundamentalistas para um conjunto de empresas.

    Args:
        sector_companies: DataFrame retornado por get_sector_companies().

    Returns:
        Dicionário com médias e medianas dos indicadores:
        - {indicador}_mean: Média do setor
        - {indicador}_median: Mediana do setor
        - {indicador}_std: Desvio padrão
        - company_count: Número de empresas na amostra

    Exemplo:
        >>> averages = calculate_sector_averages(companies)
        >>> print(f"ROE médio do setor: {averages['roe_mean']:.1%}")
    """
    if sector_companies.empty:
        return {"company_count": 0}

    # Mapeamento de colunas do fundamentus para nomes do sistema
    col_map = {
        "ROE": "roe",
        "ROIC": "roic",
        "Mrg Liq": "net_margin",
        "P/L": "pe_ratio",
        "P/VP": "pb_ratio",
    }

    averages: dict = {"company_count": len(sector_companies)}

    for fundamentus_col, system_col in col_map.items():
        if fundamentus_col not in sector_companies.columns:
            continue

        series = pd.to_numeric(sector_companies[fundamentus_col], errors="coerce").dropna()

        # Remove outliers extremos (além de 3 desvios padrão)
        if len(series) > 5:
            mean = series.mean()
            std = series.std()
            series = series[abs(series - mean) <= 3 * std]

        if series.empty:
            continue

        averages[f"{system_col}_mean"] = round(float(series.mean()), 6)
        averages[f"{system_col}_median"] = round(float(series.median()), 6)
        averages[f"{system_col}_std"] = round(float(series.std()), 6)

    return averages


def compare_to_sector(
    ticker: str,
    indicators: dict,
    sector: Optional[str] = None,
    sector_averages: Optional[dict] = None,
) -> dict:
    """
    Compara os indicadores de um ativo com a média do seu setor.

    Args:
        ticker: Símbolo do ativo (ex: PETR4).
        indicators: Dicionário com indicadores do ativo (de calculate_all_indicators()).
        sector: Nome do setor. Se None, tenta obter via fundamentus.
        sector_averages: Médias setoriais pré-calculadas. Se None, calcula automaticamente.

    Returns:
        Dicionário com:
        - ticker: Símbolo do ativo
        - sector: Nome do setor
        - comparisons: Dict com posicionamento de cada indicador vs setor
          - {indicador}: {"value": float, "sector_mean": float, "sector_median": float,
                          "vs_mean_pct": float, "position": "above" | "below" | "inline"}
        - overall_position: "above_average" | "average" | "below_average"
        - company_count: Número de empresas na comparação

    Exemplo:
        >>> result = compare_to_sector("PETR4", indicators, sector="Petróleo")
        >>> print(result["overall_position"])
        "above_average"
    """
    result: dict = {
        "ticker": ticker.upper(),
        "sector": sector or "Desconhecido",
        "comparisons": {},
        "overall_position": "unknown",
        "company_count": 0,
    }

    # Obtém médias setoriais se não fornecidas
    if sector_averages is None and sector:
        companies = get_sector_companies(sector)
        if not companies.empty:
            sector_averages = calculate_sector_averages(companies)
            result["company_count"] = sector_averages.get("company_count", 0)

    if not sector_averages or sector_averages.get("company_count", 0) == 0:
        logger.warning("Sem dados setoriais para comparação de %s", ticker)
        result["overall_position"] = "no_sector_data"
        return result

    result["company_count"] = sector_averages.get("company_count", 0)

    # Compara cada indicador
    positions = []
    for indicator in _COMPARISON_INDICATORS:
        value = indicators.get(indicator)
        mean_key = f"{indicator}_mean"
        median_key = f"{indicator}_median"

        sector_mean = sector_averages.get(mean_key)
        sector_median = sector_averages.get(median_key)

        if value is None or sector_mean is None:
            continue

        vs_mean_pct = ((value - sector_mean) / abs(sector_mean) * 100) if sector_mean != 0 else None

        # Para dívida/EBITDA: menor é melhor (inverte a lógica)
        if indicator == "debt_ebitda":
            position = _classify_position(value, sector_mean, invert=True)
        else:
            position = _classify_position(value, sector_mean, invert=False)

        result["comparisons"][indicator] = {
            "value": value,
            "sector_mean": sector_mean,
            "sector_median": sector_median,
            "vs_mean_pct": round(vs_mean_pct, 2) if vs_mean_pct is not None else None,
            "position": position,
        }
        positions.append(position)

    # Posicionamento geral
    if positions:
        above = positions.count("above")
        below = positions.count("below")
        total = len(positions)

        if above / total >= 0.6:
            result["overall_position"] = "above_average"
        elif below / total >= 0.6:
            result["overall_position"] = "below_average"
        else:
            result["overall_position"] = "average"
    else:
        result["overall_position"] = "insufficient_data"

    logger.info(
        "Comparação setorial de %s: %s (%d indicadores comparados)",
        ticker,
        result["overall_position"],
        len(result["comparisons"]),
    )

    return result


def _classify_position(
    value: float, sector_mean: float, invert: bool = False, tolerance: float = 0.10
) -> str:
    """
    Classifica a posição de um indicador em relação à média setorial.

    Args:
        value: Valor do indicador do ativo.
        sector_mean: Média do setor.
        invert: Se True, menor valor é melhor (ex: dívida/EBITDA).
        tolerance: Margem de tolerância para considerar "inline" (10% por padrão).

    Returns:
        "above" | "below" | "inline"
    """
    if sector_mean == 0:
        return "inline"

    diff_pct = (value - sector_mean) / abs(sector_mean)

    if abs(diff_pct) <= tolerance:
        return "inline"

    if invert:
        return "above" if diff_pct < 0 else "below"
    else:
        return "above" if diff_pct > 0 else "below"


def _build_sector_filter(df: pd.DataFrame, sector: str):
    """
    Constrói um filtro booleano para selecionar empresas de um setor no DataFrame.

    Tenta correspondência exata primeiro, depois por aliases.

    Args:
        df: DataFrame com todos os tickers do fundamentus.
        sector: Nome do setor a filtrar.

    Returns:
        Série booleana ou None se nenhuma coluna de setor for encontrada.
    """
    sector_cols = [col for col in df.columns if "setor" in col.lower() or "sector" in col.lower()]

    if not sector_cols:
        logger.warning("Nenhuma coluna de setor encontrada no DataFrame do fundamentus")
        return None

    col = sector_cols[0]

    # Correspondência exata
    exact_filter = df[col].str.contains(sector, case=False, na=False)
    if exact_filter.sum() > 0:
        return exact_filter

    # Tenta aliases
    for canonical, aliases in _SECTOR_ALIASES.items():
        if sector.lower() in canonical.lower() or any(a.lower() in sector.lower() for a in aliases):
            for alias in [canonical] + aliases:
                alias_filter = df[col].str.contains(alias, case=False, na=False)
                if alias_filter.sum() > 0:
                    return alias_filter

    return exact_filter  # Retorna filtro vazio (sem matches)
