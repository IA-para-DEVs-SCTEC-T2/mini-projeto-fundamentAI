"""
Coletor de dados macroeconômicos via API do Banco Central do Brasil (BCB).

Coleta SELIC e IPCA usando a API pública do BCB (SGS - Sistema Gerenciador
de Séries Temporais): https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados

Códigos das séries:
- SELIC diária: 11
- IPCA mensal: 433

Uso:
    from backend.collectors.bacen import get_selic, get_ipca

    selic = get_selic()
    ipca = get_ipca()
    selic_history = get_selic(months=12)
"""

import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Endpoint base da API do BCB (SGS)
_BCB_API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# Códigos das séries temporais
_SELIC_CODE = 11    # Taxa SELIC diária (% a.a.)
_IPCA_CODE = 433    # IPCA mensal (%)

# Timeout para requisições (segundos)
_REQUEST_TIMEOUT = 10

# Cache TTL em segundos (dados macro mudam com baixa frequência)
# SELIC: reuniões do COPOM a cada ~45 dias
# IPCA: divulgado mensalmente
_CACHE_TTL_SECONDS = 3600  # 1 hora


def get_selic(months: Optional[int] = None) -> dict:
    """
    Retorna a taxa SELIC atual e, opcionalmente, o histórico.

    Args:
        months: Se informado, retorna histórico dos últimos N meses.
                Se None, retorna apenas o valor mais recente.

    Returns:
        Dicionário com:
        - current_rate: Taxa SELIC atual (% a.a., ex: 10.5)
        - reference_date: Data de referência do valor atual
        - history: Lista de {"date": str, "value": float} (se months informado)
        - source: "BCB/SGS"

    Raises:
        RuntimeError: Se houver erro na comunicação com a API do BCB.

    Exemplo:
        >>> selic = get_selic()
        >>> print(f"SELIC: {selic['current_rate']}% a.a.")
        SELIC: 10.50% a.a.

        >>> selic_history = get_selic(months=12)
        >>> print(len(selic_history['history']))
        252  # dias úteis em ~12 meses
    """
    try:
        data = _fetch_bcb_series(_SELIC_CODE, months=months)

        if not data:
            raise RuntimeError("API do BCB retornou dados vazios para SELIC.")

        latest = data[-1]
        current_rate = float(latest["valor"])
        reference_date = latest["data"]

        result: dict = {
            "current_rate": current_rate,
            "reference_date": reference_date,
            "source": "BCB/SGS",
        }

        if months is not None:
            result["history"] = [
                {"date": item["data"], "value": float(item["valor"])}
                for item in data
            ]

        logger.info("SELIC coletada: %.2f%% (ref: %s)", current_rate, reference_date)
        return result

    except RuntimeError:
        raise
    except Exception as exc:
        logger.error("Erro ao coletar SELIC: %s", exc)
        raise RuntimeError(f"Falha ao coletar SELIC do BCB: {exc}") from exc


def get_ipca(months: Optional[int] = None) -> dict:
    """
    Retorna o IPCA atual (acumulado 12 meses) e, opcionalmente, o histórico mensal.

    Args:
        months: Se informado, retorna histórico dos últimos N meses.
                Se None, retorna apenas o valor mais recente.

    Returns:
        Dicionário com:
        - current_rate: IPCA do mês mais recente (%, ex: 0.44)
        - accumulated_12m: IPCA acumulado nos últimos 12 meses (%)
        - reference_date: Data de referência (mês/ano)
        - history: Lista de {"date": str, "value": float} (se months informado)
        - source: "BCB/SGS"

    Raises:
        RuntimeError: Se houver erro na comunicação com a API do BCB.

    Exemplo:
        >>> ipca = get_ipca()
        >>> print(f"IPCA mensal: {ipca['current_rate']}%")
        IPCA mensal: 0.44%

        >>> ipca_history = get_ipca(months=12)
        >>> print(f"IPCA 12m: {ipca_history['accumulated_12m']:.2f}%")
        IPCA 12m: 4.83%
    """
    try:
        # Busca sempre os últimos 13 meses para calcular acumulado 12m
        fetch_months = max(months or 1, 13)
        data = _fetch_bcb_series(_IPCA_CODE, months=fetch_months)

        if not data:
            raise RuntimeError("API do BCB retornou dados vazios para IPCA.")

        latest = data[-1]
        current_rate = float(latest["valor"])
        reference_date = latest["data"]

        # Acumulado 12 meses: produto dos últimos 12 valores mensais
        last_12 = data[-12:] if len(data) >= 12 else data
        accumulated_12m = _calculate_accumulated(last_12)

        result: dict = {
            "current_rate": current_rate,
            "accumulated_12m": accumulated_12m,
            "reference_date": reference_date,
            "source": "BCB/SGS",
        }

        if months is not None:
            result["history"] = [
                {"date": item["data"], "value": float(item["valor"])}
                for item in data[-months:]
            ]

        logger.info(
            "IPCA coletado: %.2f%% (mês), %.2f%% (12m), ref: %s",
            current_rate,
            accumulated_12m,
            reference_date,
        )
        return result

    except RuntimeError:
        raise
    except Exception as exc:
        logger.error("Erro ao coletar IPCA: %s", exc)
        raise RuntimeError(f"Falha ao coletar IPCA do BCB: {exc}") from exc


def get_macro_context() -> dict:
    """
    Retorna o contexto macroeconômico completo (SELIC + IPCA) em uma única chamada.

    Conveniente para uso no builder de prompts.

    Returns:
        Dicionário com:
        - selic_rate: Taxa SELIC atual (% a.a.)
        - ipca_monthly: IPCA do mês mais recente (%)
        - ipca_12m: IPCA acumulado 12 meses (%)
        - selic_reference_date: Data de referência da SELIC
        - ipca_reference_date: Data de referência do IPCA

    Exemplo:
        >>> macro = get_macro_context()
        >>> print(f"SELIC: {macro['selic_rate']}% | IPCA 12m: {macro['ipca_12m']}%")
    """
    errors = []

    selic_data: dict = {}
    ipca_data: dict = {}

    try:
        selic_data = get_selic()
    except RuntimeError as exc:
        logger.warning("Falha ao coletar SELIC: %s", exc)
        errors.append(str(exc))

    try:
        ipca_data = get_ipca()
    except RuntimeError as exc:
        logger.warning("Falha ao coletar IPCA: %s", exc)
        errors.append(str(exc))

    return {
        "selic_rate": selic_data.get("current_rate"),
        "selic_reference_date": selic_data.get("reference_date"),
        "ipca_monthly": ipca_data.get("current_rate"),
        "ipca_12m": ipca_data.get("accumulated_12m"),
        "ipca_reference_date": ipca_data.get("reference_date"),
        "errors": errors if errors else None,
    }


# ---------------------------------------------------------------------------
# Funções internas
# ---------------------------------------------------------------------------


def _fetch_bcb_series(codigo: int, months: Optional[int] = None) -> list[dict]:
    """
    Faz a requisição à API do BCB e retorna os dados da série temporal.

    Args:
        codigo: Código da série no SGS do BCB.
        months: Número de meses de histórico. Se None, busca os últimos 30 dias.

    Returns:
        Lista de dicionários com {"data": str, "valor": str}.

    Raises:
        RuntimeError: Se a requisição falhar ou retornar status != 200.
    """
    url = _BCB_API_URL.format(codigo=codigo)

    # Define período de busca
    end_date = datetime.utcnow()
    if months:
        # Adiciona margem de 10% para garantir cobertura de dias úteis
        start_date = end_date - timedelta(days=int(months * 31 * 1.1))
    else:
        # Sem histórico: busca últimos 30 dias para garantir o valor mais recente
        start_date = end_date - timedelta(days=30)

    params = {
        "formato": "json",
        "dataInicial": start_date.strftime("%d/%m/%Y"),
        "dataFinal": end_date.strftime("%d/%m/%Y"),
    }

    try:
        response = requests.get(url, params=params, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise RuntimeError(f"Formato inesperado da API do BCB: {type(data)}")

        return data

    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout ao acessar API do BCB (série {codigo})")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Erro de conexão com API do BCB (série {codigo})")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Erro HTTP {exc.response.status_code} na API do BCB") from exc
    except Exception as exc:
        raise RuntimeError(f"Erro inesperado ao acessar API do BCB: {exc}") from exc


def _calculate_accumulated(monthly_data: list[dict]) -> float:
    """
    Calcula o IPCA acumulado a partir de uma lista de valores mensais.

    Usa a fórmula de capitalização composta:
    acumulado = (∏(1 + taxa_i/100) - 1) * 100

    Args:
        monthly_data: Lista de {"data": str, "valor": str} com valores mensais.

    Returns:
        IPCA acumulado em percentual (ex: 4.83 para 4.83%).
    """
    if not monthly_data:
        return 0.0

    accumulated = 1.0
    for item in monthly_data:
        try:
            rate = float(item["valor"]) / 100
            accumulated *= (1 + rate)
        except (ValueError, KeyError):
            continue

    return round((accumulated - 1) * 100, 4)
