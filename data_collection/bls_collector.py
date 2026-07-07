"""Pulls BLS OES retail wage data and BLS Consumer Expenditure Survey
home-furnishings spend by Census region for the 5 candidate metros.

Hourly wages come live from the public BLS Timeseries API v2 (rate-limited,
hence the delay between calls). CEX region-level furnishings spend isn't
cleanly queryable through that API, so those 4 values are transcribed from
the published table directly -- see SOURCE note below.
"""

import time
from pathlib import Path

import pandas as pd
import requests

BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# BLS OES area codes for these 5 metros match their Census CBSA codes.
METRO_AREA_CODES = {
    "Nashville, TN": "34980",
    "Austin, TX": "12420",
    "Denver, CO": "19740",
    "Charlotte, NC": "16740",
    "Indianapolis, IN": "26900",
}

# Occupation: Retail Salespersons (SOC 41-2031). Datatype 03 = hourly mean wage.
OCCUPATION_CODE = "412031"
DATATYPE_HOURLY_MEAN_WAGE = "03"

# SOURCE: BLS Consumer Expenditure Survey, Table 1800 "Region of residence:
# Annual expenditure means...", 2023-2024, line item "Household furnishings
# and equipment" (mean annual expenditure per consumer unit, in dollars).
# https://www.bls.gov/cex/tables/geographic/mean/cu-region-2-year-average-2023-2024.xlsx
CEX_FURNISHINGS_SPEND_BY_REGION = {
    "Northeast": 2523,
    "Midwest": 2440,
    "South": 2153,
    "West": 2978,
}

METRO_TO_REGION = {
    "Nashville, TN": "South",
    "Austin, TX": "South",
    "Denver, CO": "West",
    "Charlotte, NC": "South",
    "Indianapolis, IN": "Midwest",
}


def _oes_series_id(area_code: str) -> str:
    return f"OEUM00{area_code}000000{OCCUPATION_CODE}{DATATYPE_HOURLY_MEAN_WAGE}"


def collect_bls_wages() -> pd.DataFrame:
    """Pulls mean hourly wage for Retail Salespersons (SOC 41-2031) by metro."""
    rows = []
    for metro_name, area_code in METRO_AREA_CODES.items():
        series_id = _oes_series_id(area_code)
        resp = requests.get(BLS_BASE_URL + series_id, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        series_data = payload["Results"]["series"][0]["data"]
        if not series_data:
            raise ValueError(f"No BLS OES data returned for {metro_name} ({series_id})")
        latest = series_data[0]  # BLS returns most recent first
        wage = float(latest["value"])
        rows.append(
            {
                "metro_name": metro_name,
                "mean_hourly_wage_retail": wage,
                "annual_wage_retail": wage * 2080,
                "wage_year": latest["year"],
            }
        )
        print(f"  BLS OES: {metro_name} -> ${wage}/hr ({latest['year']})")
        time.sleep(2)  # be polite to the unauthenticated public API
    return pd.DataFrame(rows)


def collect_consumer_expenditure() -> pd.DataFrame:
    """Returns home-furnishings annual spend per household by Census region."""
    rows = [
        {"region": region, "annual_hh_spend_furnishings": spend}
        for region, spend in CEX_FURNISHINGS_SPEND_BY_REGION.items()
    ]
    return pd.DataFrame(rows)


def collect_all_bls_data() -> pd.DataFrame:
    print("Pulling BLS OES hourly wages (retail salespersons)...")
    wages = collect_bls_wages()
    print("Loading BLS CEX home-furnishings spend by region (sourced table, see docstring)...")
    cex = collect_consumer_expenditure()

    wages["region"] = wages["metro_name"].map(METRO_TO_REGION)
    merged = wages.merge(cex, on="region")

    out_path = Path(__file__).parent / "raw" / "bls_data.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    return merged


if __name__ == "__main__":
    df = collect_all_bls_data()
    print(df.to_string(index=False))
