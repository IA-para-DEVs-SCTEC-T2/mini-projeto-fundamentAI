"""
Testes de endpoints da API FastAPI.

Cobre:
- GET /api/ticker/{ticker} — validação de formato, mock de dados, ticker inativo
- POST /api/analysis/{ticker} — mock de coleta e LLM
- GET /health — health check
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.api.main import app

client = TestClient(app)


# ===========================================================================
# Health check
# ===========================================================================

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


# ===========================================================================
# GET /api/ticker/{ticker}
# ===========================================================================

class TestGetTicker:
    def test_formato_invalido_retorna_400(self):
        response = client.get("/api/ticker/INVALIDO123")
        assert response.status_code == 400
        assert "Formato de ticker inv" in response.json()["detail"]

    def test_formato_invalido_numeros_no_inicio_retorna_400(self):
        # Formato inválido: começa com números
        response = client.get("/api/ticker/123ABC")
        assert response.status_code == 400

    def test_formato_invalido_apenas_letras_retorna_400(self):
        # Formato inválido: sem número no final
        response = client.get("/api/ticker/PETRO")
        assert response.status_code == 400

    @patch("backend.api.routes.ticker.get_inactive_symbols", return_value={"ABCD3"})
    def test_ticker_inativo_retorna_404(self, mock_inactive):
        response = client.get("/api/ticker/ABCD3")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["reason"] == "inactive"

    @patch("backend.api.routes.ticker.get_inactive_symbols", return_value=set())
    @patch("backend.api.routes.ticker.classify_asset_type", return_value="stock")
    @patch("backend.api.routes.ticker._get_stock_data")
    def test_ticker_valido_retorna_200(self, mock_stock, mock_classify, mock_inactive):
        from backend.api.routes.ticker import TickerResponse, QuoteResponse, IndicatorsResponse, ScoreResponse
        mock_stock.return_value = TickerResponse(
            ticker="PETR4",
            name="Petrobras",
            sector="Petróleo",
            asset_type="stock",
            quote=QuoteResponse(ticker="PETR4", current_price=40.0),
            indicators=IndicatorsResponse(),
            score=ScoreResponse(score=75.0, label="Excelente", asset_type="stock"),
            price_history=[],
            data_source="fundamentus + yfinance",
        )
        response = client.get("/api/ticker/PETR4")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "PETR4"
        assert data["asset_type"] == "stock"
        assert data["score"]["score"] == 75.0

    @patch("backend.api.routes.ticker.get_inactive_symbols", return_value=set())
    @patch("backend.api.routes.ticker.classify_asset_type", return_value="fii")
    @patch("backend.api.routes.ticker._get_fii_data")
    def test_fii_valido_retorna_200(self, mock_fii, mock_classify, mock_inactive):
        from backend.api.routes.ticker import TickerResponse, QuoteResponse, IndicatorsResponse, ScoreResponse
        mock_fii.return_value = TickerResponse(
            ticker="HGLG11",
            name=None,
            sector="Fundos Imobiliários",
            asset_type="fii",
            quote=QuoteResponse(ticker="HGLG11", current_price=160.0),
            indicators=IndicatorsResponse(pb_ratio=0.95, dividend_yield=0.10),
            score=ScoreResponse(score=85.0, label="Excelente", asset_type="fii"),
            price_history=[],
            data_source="yfinance",
        )
        response = client.get("/api/ticker/HGLG11")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "HGLG11"
        assert data["asset_type"] == "fii"


# ===========================================================================
# POST /api/analysis/{ticker}
# ===========================================================================

class TestAnalyzeTicker:
    @patch("backend.api.routes.analysis._get_cached_analysis", return_value=None)
    @patch("backend.api.routes.analysis._collect_data")
    @patch("backend.api.routes.analysis._collect_macro")
    @patch("backend.api.routes.analysis._call_anthropic")
    @patch("backend.api.routes.analysis.parse_llm_response")
    @patch("backend.api.routes.analysis._persist_analysis")
    def test_analise_retorna_200(
        self,
        mock_persist,
        mock_parse,
        mock_call,
        mock_macro,
        mock_data,
        mock_cache,
    ):
        mock_data.return_value = ({}, {"current_price": 40.0}, {}, "Petróleo")
        mock_macro.return_value = {"selic_rate": 10.5}
        mock_call.return_value = "{}"
        mock_parse.return_value = {
            "verdict": "Positivo",
            "score": 80.0,
            "confidence_level": "Alto",
            "positive_points": ["ROE elevado"],
            "negative_points": ["Endividamento moderado"],
            "indicators_explanation": {},
            "moment_suggestion": "Momento favorável",
            "conclusion": "Fundamentos sólidos",
            "risk_assessment": "Baixo",
            "disclaimer": "Esta análise é informativa.",
        }

        response = client.post("/api/analysis/PETR4")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "PETR4"
        assert data["score"] == 80.0
        assert data["verdict"] == "Positivo"
        assert "disclaimer" in data

    @patch("backend.api.routes.analysis._get_cached_analysis")
    def test_analise_retorna_cache(self, mock_cache):
        from backend.api.routes.analysis import AnalysisResponse, IndicatorsExplanation
        cached = AnalysisResponse(
            ticker="VALE3",
            verdict="Positivo",
            score=70.0,
            confidence_level="Médio",
            positive_points=[],
            negative_points=[],
            indicators_explanation=IndicatorsExplanation(),
            conclusion="Análise em cache",
            disclaimer="Esta análise é informativa.",
            model_used="claude-sonnet-4-5",
            prompt_version="1.0",
            cached=True,
        )
        mock_cache.return_value = cached

        response = client.post("/api/analysis/VALE3")
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["ticker"] == "VALE3"

    @patch("backend.api.routes.analysis._get_cached_analysis", return_value=None)
    @patch("backend.api.routes.analysis._collect_data")
    def test_ticker_nao_encontrado_retorna_404(self, mock_data, mock_cache):
        from fastapi import HTTPException
        mock_data.side_effect = HTTPException(status_code=404, detail="Ticker não encontrado")

        response = client.post("/api/analysis/XXXX9")
        assert response.status_code == 404


# ===========================================================================
# Testes de integração leve (sem mocks externos)
# ===========================================================================

@pytest.mark.integration
class TestIntegration:
    def test_health_check_integration(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_retorna_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_docs_disponiveis(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_ticker_formato_invalido_sem_db(self):
        """Validação de formato não depende de banco — deve funcionar sem mock."""
        response = client.get("/api/ticker/TOOLONG123")
        assert response.status_code == 400
