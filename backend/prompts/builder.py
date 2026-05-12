"""
Builder de prompts estruturados para análise via Anthropic API.

Monta o prompt completo com dados financeiros, indicadores calculados e
contexto macroeconômico, definindo o formato de saída JSON esperado.

Templates são versionados e separados da lógica de injeção de dados.

Uso:
    from backend.prompts.builder import build_analysis_prompt

    prompt = build_analysis_prompt(
        ticker="PETR4",
        financial_data=financial_data,
        indicators=indicators,
        macro=macro_context,
        score_result=score_result,
        sector_comparison=sector_comparison,
    )
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Versão atual do template de prompt
PROMPT_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Template do prompt (versionado)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Você é um analista fundamentalista especializado em ações da B3 (Bolsa de Valores do Brasil).

Sua função é analisar dados financeiros objetivos e gerar uma análise estruturada, clara e educativa para investidores.

REGRAS IMPORTANTES:
1. Baseie-se EXCLUSIVAMENTE nos dados fornecidos — não invente informações
2. NÃO faça recomendações de compra ou venda — apenas análise informativa
3. Use linguagem acessível para investidores iniciantes
4. Seja objetivo e equilibrado — aponte pontos positivos E negativos
5. Responda SEMPRE em JSON válido, seguindo exatamente o formato especificado
6. Contextualize os indicadores com benchmarks do mercado brasileiro"""

_ANALYSIS_PROMPT_TEMPLATE = """Analise o ativo {ticker} com base nos dados abaixo e retorne uma análise estruturada em JSON.

## DADOS DO ATIVO

### Informações Gerais
- Ticker: {ticker}
- Setor: {sector}
- Preço atual: {current_price}

### Indicadores Fundamentalistas
{indicators_section}

### Score Fundamentalista
- Score: {score}/100
- Classificação: {score_label}
- Detalhamento do score:
{score_breakdown}

### Contexto Macroeconômico
- Taxa SELIC: {selic_rate}% a.a.
- IPCA (12 meses): {ipca_12m}%

### Comparação Setorial
{sector_comparison_section}

## FORMATO DE SAÍDA OBRIGATÓRIO

Retorne APENAS o JSON abaixo, sem texto adicional antes ou depois:

```json
{{
  "verdict": "string — um dos valores: Positivo | Neutro | Negativo",
  "score": number — entre 0 e 100,
  "confidence_level": "string — um dos valores: Alto | Médio | Baixo",
  "positive_points": [
    "string — ponto positivo 1",
    "string — ponto positivo 2"
  ],
  "negative_points": [
    "string — ponto negativo 1",
    "string — ponto negativo 2"
  ],
  "indicators_explanation": {{
    "roe": "string — explicação do ROE deste ativo em linguagem simples",
    "roic": "string — explicação do ROIC",
    "net_margin": "string — explicação da margem líquida",
    "debt_ebitda": "string — explicação do endividamento",
    "pe_ratio": "string — explicação do P/L",
    "pb_ratio": "string — explicação do P/VP",
    "growth": "string — explicação do crescimento de receita/lucro"
  }},
  "moment_suggestion": "string — sugestão de momento para análise (NÃO é recomendação de compra/venda)",
  "conclusion": "string — conclusão geral da análise em 2-3 frases",
  "risk_assessment": "string — avaliação de risco: Baixo | Moderado | Alto | Muito Alto",
  "disclaimer": "Esta análise é informativa e baseada em dados históricos. Não constitui recomendação de investimento."
}}
```

IMPORTANTE: Retorne apenas o JSON, sem markdown, sem texto explicativo."""


# ---------------------------------------------------------------------------
# Funções de formatação de seções
# ---------------------------------------------------------------------------


def _format_indicators_section(indicators: dict) -> str:
    """Formata os indicadores para inserção no prompt."""
    lines = []

    indicator_labels = {
        "roe": ("ROE (Retorno sobre Patrimônio)", "decimal_percent"),
        "roic": ("ROIC (Retorno sobre Capital Investido)", "decimal_percent"),
        "net_margin": ("Margem Líquida", "decimal_percent"),
        "debt_ebitda": ("Dívida Líquida / EBITDA", "ratio"),
        "pe_ratio": ("P/L (Preço / Lucro)", "ratio"),
        "pb_ratio": ("P/VP (Preço / Valor Patrimonial)", "ratio"),
        "revenue_growth_yoy": ("Crescimento de Receita (CAGR)", "decimal_percent"),
        "net_income_growth_yoy": ("Crescimento de Lucro (CAGR)", "decimal_percent"),
    }

    for key, (label, fmt) in indicator_labels.items():
        value = indicators.get(key)
        if value is None:
            lines.append(f"- {label}: Dados não disponíveis")
        elif fmt == "decimal_percent":
            lines.append(f"- {label}: {value:.1%}")
        else:
            lines.append(f"- {label}: {value:.2f}x")

    return "\n".join(lines) if lines else "Dados de indicadores não disponíveis"


def _format_score_breakdown(score_result: dict) -> str:
    """Formata o detalhamento do score para inserção no prompt."""
    breakdown = score_result.get("breakdown", {})
    weights = score_result.get("weights", {})

    labels = {
        "growth": "Crescimento",
        "roe": "ROE",
        "roic": "ROIC",
        "net_margin": "Margem Líquida",
        "debt_ebitda": "Endividamento",
        "valuation": "Valuation (P/L + P/VP)",
    }

    lines = []
    for key, label in labels.items():
        score = breakdown.get(key, 0)
        weight = weights.get(key, 0)
        lines.append(f"  - {label}: {score:.1f}/100 (peso: {weight:.0%})")

    return "\n".join(lines)


def _format_sector_comparison(sector_comparison: Optional[dict]) -> str:
    """Formata a comparação setorial para inserção no prompt."""
    if not sector_comparison or sector_comparison.get("overall_position") in (
        "unknown", "no_sector_data", "insufficient_data"
    ):
        return "Comparação setorial não disponível."

    lines = [
        f"- Posicionamento geral: {sector_comparison.get('overall_position', 'N/A')}",
        f"- Empresas comparadas: {sector_comparison.get('company_count', 0)}",
    ]

    comparisons = sector_comparison.get("comparisons", {})
    position_labels = {
        "above": "acima da média",
        "below": "abaixo da média",
        "inline": "na média",
    }

    indicator_names = {
        "roe": "ROE",
        "roic": "ROIC",
        "net_margin": "Margem Líquida",
        "debt_ebitda": "Dívida/EBITDA",
        "pe_ratio": "P/L",
        "pb_ratio": "P/VP",
    }

    for key, data in comparisons.items():
        name = indicator_names.get(key, key)
        position = position_labels.get(data.get("position", ""), "N/A")
        vs_pct = data.get("vs_mean_pct")
        vs_str = f" ({vs_pct:+.1f}% vs média)" if vs_pct is not None else ""
        lines.append(f"  - {name}: {position}{vs_str}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------


def build_analysis_prompt(
    ticker: str,
    financial_data: dict,
    indicators: dict,
    macro: dict,
    score_result: dict,
    sector_comparison: Optional[dict] = None,
    sector: Optional[str] = None,
) -> dict:
    """
    Monta o prompt completo para análise de um ativo via Anthropic API.

    Args:
        ticker: Símbolo do ativo (ex: PETR4).
        financial_data: Dados financeiros brutos (de extract_key_financials()).
        indicators: Indicadores calculados (de calculate_all_indicators()).
        macro: Contexto macroeconômico (de get_macro_context()).
        score_result: Resultado do scoring (de calculate_score()).
        sector_comparison: Comparação setorial opcional (de compare_to_sector()).
        sector: Nome do setor do ativo.

    Returns:
        Dicionário com:
        - system_prompt: Prompt de sistema para a API
        - user_prompt: Prompt do usuário com os dados injetados
        - prompt_version: Versão do template utilizado
        - ticker: Símbolo do ativo

    Exemplo:
        >>> prompt = build_analysis_prompt("PETR4", financial_data, indicators, macro, score)
        >>> print(prompt["prompt_version"])
        "1.0.0"
    """
    current_price = financial_data.get("current_price") or "N/A"
    if isinstance(current_price, float):
        current_price = f"R$ {current_price:.2f}"

    selic_rate = macro.get("selic_rate")
    ipca_12m = macro.get("ipca_12m")

    user_prompt = _ANALYSIS_PROMPT_TEMPLATE.format(
        ticker=ticker.upper(),
        sector=sector or "Não identificado",
        current_price=current_price,
        indicators_section=_format_indicators_section(indicators),
        score=score_result.get("score", 0),
        score_label=score_result.get("label", "N/A"),
        score_breakdown=_format_score_breakdown(score_result),
        selic_rate=f"{selic_rate:.2f}" if selic_rate is not None else "N/A",
        ipca_12m=f"{ipca_12m:.2f}" if ipca_12m is not None else "N/A",
        sector_comparison_section=_format_sector_comparison(sector_comparison),
    )

    logger.info(
        "Prompt montado para %s | versão: %s | tamanho: %d chars",
        ticker.upper(),
        PROMPT_VERSION,
        len(user_prompt),
    )

    return {
        "system_prompt": _SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "prompt_version": PROMPT_VERSION,
        "ticker": ticker.upper(),
    }


def parse_llm_response(raw_response: str) -> dict:
    """
    Faz o parsing da resposta JSON da LLM com tratamento de erros.

    Remove possíveis marcadores de código markdown antes de parsear.

    Args:
        raw_response: Resposta bruta da API da Anthropic.

    Returns:
        Dicionário com os campos da análise ou dicionário de erro.

    Raises:
        ValueError: Se a resposta não puder ser parseada como JSON válido.
    """
    # Remove blocos de código markdown se presentes
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove primeira linha (```json ou ```) e última linha (```)
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed = json.loads(cleaned)
        _validate_response_structure(parsed)
        return parsed
    except json.JSONDecodeError as exc:
        logger.error("Falha ao parsear resposta da LLM: %s", exc)
        raise ValueError(f"Resposta da LLM não é JSON válido: {exc}") from exc


def _validate_response_structure(response: dict) -> None:
    """
    Valida que a resposta da LLM contém os campos obrigatórios.

    Args:
        response: Dicionário parseado da resposta.

    Raises:
        ValueError: Se campos obrigatórios estiverem ausentes.
    """
    required_fields = [
        "verdict", "score", "confidence_level",
        "positive_points", "negative_points",
        "indicators_explanation", "conclusion",
    ]

    missing = [field for field in required_fields if field not in response]
    if missing:
        logger.warning("Campos ausentes na resposta da LLM: %s", missing)
        # Não levanta exceção — campos opcionais podem estar ausentes
        # Apenas loga o aviso para monitoramento
