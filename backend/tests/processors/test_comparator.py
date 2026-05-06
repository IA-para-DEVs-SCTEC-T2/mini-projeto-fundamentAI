import pandas as pd
from backend.processors.comparator import (
    calculate_sector_averages,
    _classify_position,
    compare_to_sector,
)

def test_calculate_sector_averages():
    # Setup dataframe mock do fundamentus
    data = {
        "Papel": ["PETR3", "PETR4", "PRIO3", "ENAT3"],
        "ROE": ["0.35", "0.35", "0.20", "0.15"], # strings, assim como vem do fundamentus
        "ROIC": ["0.25", "0.25", "0.15", "0.10"],
        "Mrg Liq": ["0.25", "0.25", "0.20", "0.15"],
        "P/L": ["3.5", "3.0", "8.0", "12.0"],
        "P/VP": ["1.2", "1.1", "2.5", "1.5"]
    }
    df = pd.DataFrame(data)
    
    averages = calculate_sector_averages(df)
    
    assert averages["company_count"] == 4
    # PETR3, PETR4, PRIO3, ENAT3 => médias:
    # ROE = (0.35 + 0.35 + 0.20 + 0.15) / 4 = 1.05 / 4 = 0.2625
    assert averages["roe_mean"] == 0.2625
    assert averages["pe_ratio_mean"] == 6.625

def test_calculate_sector_averages_empty():
    averages = calculate_sector_averages(pd.DataFrame())
    assert averages["company_count"] == 0

def test_classify_position():
    # invert = False (maior é melhor)
    assert _classify_position(0.25, 0.20, invert=False, tolerance=0.10) == "above" # 25% > 20% + 10%
    assert _classify_position(0.205, 0.20, invert=False, tolerance=0.10) == "inline" # 2.5% > 0, mas dentro da tolerância de 10%
    assert _classify_position(0.15, 0.20, invert=False, tolerance=0.10) == "below"
    
    # invert = True (menor é melhor)
    assert _classify_position(1.0, 2.0, invert=True, tolerance=0.10) == "above" # 1 é "acima" da média porque é melhor (menor)
    assert _classify_position(3.0, 2.0, invert=True, tolerance=0.10) == "below"
    
    # media zero
    assert _classify_position(1.0, 0.0) == "inline"

def test_compare_to_sector():
    indicators = {
        "roe": 0.30,
        "roic": 0.20,
        "pe_ratio": 5.0,
        "debt_ebitda": 1.0
    }
    
    sector_averages = {
        "company_count": 5,
        "roe_mean": 0.15,
        "roe_median": 0.14,
        "roic_mean": 0.10,
        "roic_median": 0.10,
        "pe_ratio_mean": 10.0,
        "pe_ratio_median": 10.0,
        "debt_ebitda_mean": 2.5,
        "debt_ebitda_median": 2.5
    }
    
    result = compare_to_sector("MOCK3", indicators, sector="Mock", sector_averages=sector_averages)
    
    assert result["ticker"] == "MOCK3"
    assert result["overall_position"] == "above_average"
    assert result["company_count"] == 5
    
    comp = result["comparisons"]
    assert comp["roe"]["position"] == "above"
    assert comp["pe_ratio"]["position"] == "below" # P/L = 5 vs media 10, position "below" no sentido de numérico, mas aqui a logica do P/L invert=False, então resultará em below? Wait, o P/L devia ser invertido? 
    # Ah, no codigo atual: if indicator == "debt_ebitda": invert=True, else: invert=False
    # Logo PE = "below", porque 5 < 10. E isso no código atual significa "below average" numericamente.
    assert comp["debt_ebitda"]["position"] == "above" # invert=True, 1.0 < 2.5 => "above"
