"""Pulls Zillow Home Value Index (ZHVI) and building permit data for the
5 candidate metros.

ZHVI is pulled live from Zillow Research's public CSV (updated monthly).
Permits come from NAHB's metro-level workbook rather than Census's own
metro-annual page, which stalled at 2021 -- NAHB aggregates the same
underlying Census monthly survey and stays current.
Source: nahb.org/news-and-economics/housing-economics/state-and-local-data/building-permits-by-state-and-metro-area
"""

from pathlib import Path

import pandas as pd
import requests

ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)

METRO_ZILLOW_NAMES = {
    "Nashville, TN": "Nashville, TN",
    "Austin, TX": "Austin, TX",
    "Denver, CO": "Denver, CO",
    "Charlotte, NC": "Charlotte, NC",
    "Indianapolis, IN": "Indianapolis, IN",
}

# NAHB workbook (table32-building-permits-by-state-and-msa.xlsx), FY2025
# TOTAL column, housing units authorized.
BUILDING_PERMITS_FY2025 = {
    "Nashville, TN": 19203,
    "Austin, TX": 27322,
    "Denver, CO": 15948,
    "Charlotte, NC": 22233,
    "Indianapolis, IN": 11463,
}
BUILDING_PERMITS_YEAR = 2025


def download_zillow_zhvi() -> pd.DataFrame:
    """Downloads ZHVI CSV and computes 5-year home value appreciation."""
    resp = requests.get(ZHVI_URL, timeout=60)
    resp.raise_for_status()
    tmp_path = Path(__file__).parent / "raw" / "_zhvi_raw.csv"
    tmp_path.write_bytes(resp.content)
    df = pd.read_csv(tmp_path)
    tmp_path.unlink()

    date_cols = [c for c in df.columns if c[:2] == "20"]
    latest_col = date_cols[-1]
    baseline_col = date_cols[-61]  # ~60 months (5 years) prior

    rows = []
    for metro_name, zillow_name in METRO_ZILLOW_NAMES.items():
        match = df[(df["RegionName"] == zillow_name) & (df["RegionType"] == "msa")]
        if match.empty:
            raise ValueError(f"No Zillow ZHVI row found for {zillow_name}")
        row = match.iloc[0]
        current = row[latest_col]
        baseline = row[baseline_col]
        appreciation_pct = (current - baseline) / baseline * 100
        rows.append(
            {
                "metro_name": metro_name,
                "zhvi_current": current,
                "zhvi_5yr_ago": baseline,
                "zhvi_as_of": latest_col,
                "home_value_appreciation_5yr_pct": appreciation_pct,
            }
        )
        print(f"  Zillow ZHVI: {metro_name} -> ${current:,.0f} ({appreciation_pct:.1f}% / 5yr)")
    return pd.DataFrame(rows)


def get_housing_permit_data() -> pd.DataFrame:
    rows = [
        {
            "metro_name": metro_name,
            "annual_permits": permits,
            "permits_year": BUILDING_PERMITS_YEAR,
        }
        for metro_name, permits in BUILDING_PERMITS_FY2025.items()
    ]
    return pd.DataFrame(rows)


def collect_all_housing_data() -> pd.DataFrame:
    print("Pulling Zillow ZHVI data...")
    zhvi = download_zillow_zhvi()
    print(f"Loading building permits (FY{BUILDING_PERMITS_YEAR}, via NAHB/Census monthly survey)...")
    permits = get_housing_permit_data()

    merged = zhvi.merge(permits, on="metro_name")
    out_path = Path(__file__).parent / "raw" / "housing_data.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    return merged


if __name__ == "__main__":
    df = collect_all_housing_data()
    print(df.to_string(index=False))
