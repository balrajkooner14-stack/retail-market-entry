"""Pulls Zillow Home Value Index (ZHVI) data and Census building permits
data for the 5 candidate metros.

ZHVI is pulled live from Zillow Research's public CSV (updated monthly).

Census's Building Permits Survey metro-level ANNUAL file (msaannual.html)
has not been updated past 2021 (Final) as of this run -- Census continues to
publish permits at national/state/county granularity but the metro-annual
Excel breakdown Census hosts directly stops at 2021. Rather than leave this
input stale-and-unlabeled or guess, we use that most recent officially
published metro total and clearly flag its vintage. This is a 20%
sub-component of one scoring dimension (dimension 3, 20% weight), so the
staleness has limited impact on the overall model.
Source: https://www.census.gov/construction/bps/xls/msaannual_202199.xls
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

# SOURCE: US Census Bureau, Building Permits Survey, Permits by Metropolitan
# Area Annual, 2021 (Final) -- most recent metro-level annual total Census
# has published as of this data pull (verified July 2026).
# https://www.census.gov/construction/bps/xls/msaannual_202199.xls
BUILDING_PERMITS_2021_FINAL = {
    "Nashville, TN": 32191,
    "Austin, TX": 50907,
    "Denver, CO": 30006,
    "Charlotte, NC": 30126,
    "Indianapolis, IN": 13451,
}
BUILDING_PERMITS_YEAR = 2021


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
        for metro_name, permits in BUILDING_PERMITS_2021_FINAL.items()
    ]
    return pd.DataFrame(rows)


def collect_all_housing_data() -> pd.DataFrame:
    print("Pulling Zillow ZHVI data...")
    zhvi = download_zillow_zhvi()
    print(f"Loading Census building permits ({BUILDING_PERMITS_YEAR} Final, most recent metro-level annual published)...")
    permits = get_housing_permit_data()

    merged = zhvi.merge(permits, on="metro_name")
    out_path = Path(__file__).parent / "raw" / "housing_data.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    return merged


if __name__ == "__main__":
    df = collect_all_housing_data()
    print(df.to_string(index=False))
