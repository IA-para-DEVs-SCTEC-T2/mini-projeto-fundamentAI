import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout

from backend.collectors.bacen import (
    get_selic,
    get_ipca,
    get_macro_context,
    _calculate_accumulated,
    _fetch_bcb_series,
)

def test_calculate_accumulated():
    monthly_data = [
        {"valor": "1.0"}, # 1%
        {"valor": "2.0"}, # 2%
    ]
    # (1 + 0.01) * (1 + 0.02) - 1 = 1.01 * 1.02 - 1 = 1.0302 - 1 = 0.0302 -> 3.02%
    assert _calculate_accumulated(monthly_data) == 3.02

@patch("backend.collectors.bacen.requests.get")
def test_fetch_bcb_series_mocked(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"data": "01/01/2023", "valor": "10.5"}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    data = _fetch_bcb_series(11)
    assert len(data) == 1
    assert data[0]["valor"] == "10.5"

@patch("backend.collectors.bacen.requests.get")
def test_fetch_bcb_series_timeout(mock_get):
    mock_get.side_effect = Timeout("Timeout Error")
    
    with pytest.raises(RuntimeError, match="Timeout ao acessar API"):
        _fetch_bcb_series(11)

@patch("backend.collectors.bacen._fetch_bcb_series")
def test_get_selic_mocked(mock_fetch):
    mock_fetch.return_value = [{"data": "01/01/2023", "valor": "10.5"}]
    
    selic = get_selic()
    assert selic["current_rate"] == 10.5
    assert selic["reference_date"] == "01/01/2023"

@patch("backend.collectors.bacen._fetch_bcb_series")
def test_get_ipca_mocked(mock_fetch):
    # Mockando 12 meses com 1% cada
    mock_fetch.return_value = [{"data": f"01/{i:02d}/2023", "valor": "1.0"} for i in range(1, 13)]
    
    ipca = get_ipca(months=12)
    assert ipca["current_rate"] == 1.0
    # 1.01^12 - 1 = 0.1268 = 12.68%
    assert pytest.approx(ipca["accumulated_12m"], 0.01) == 12.68

@pytest.mark.integration
def test_get_selic_integration():
    selic = get_selic()
    assert "current_rate" in selic
    assert selic["current_rate"] > 0
    assert "reference_date" in selic

@pytest.mark.integration
def test_get_macro_context_integration():
    macro = get_macro_context()
    assert "selic_rate" in macro
    assert "ipca_12m" in macro
    assert macro["errors"] is None
