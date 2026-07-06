"""Pulls US Census Bureau ACS 5-year data for the 5 candidate metros.

Requires a free Census API key (https://api.census.gov/data/key_signup.html)
in a `.env` file at the project root as CENSUS_API_KEY. As of 2026 the Census
API rejects all requests without a key -- the "no key required" behavior
described in older docs no longer holds.
"""

from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env")

CENSUS_API_KEY = os.environ["CENSUS_API_KEY"]

CURRENT_VINTAGE = 2023
BASELINE_VINTAGE = 2018  # 5 years prior, for population growth rate

METROS = {
    "Nashville, TN": "34980",
    "Austin, TX": "12420",
    "Denver, CO": "19740",
    "Charlotte, NC": "16740",
    "Indianapolis, IN": "26900",
}

VARIABLES = [
    "B01003_001E",  # Total population
    "B19013_001E",  # Median household income
    "B25003_002E",  # Owner-occupied housing units
    "B25003_001E",  # Total occupied housing units
    "B01002_001E",  # Median age
]


def _fetch_vintage(vintage: int, variables: list[str]) -> pd.DataFrame:
    base_url = f"https://api.census.gov/data/{vintage}/acs/acs5"
    rows = []
    for metro_name, cbsa_code in METROS.items():
        params = {
            "get": ",".join(["NAME", *variables]),
            "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa_code}",
            "key": CENSUS_API_KEY,
        }
        resp = requests.get(base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        header, values = data[0], data[1]
        record = dict(zip(header, values))
        record["metro_name"] = metro_name
        record["cbsa_code"] = cbsa_code
        rows.append(record)
        print(f"  {vintage} ACS5: {metro_name} OK")
    return pd.DataFrame(rows)


def collect_census_data() -> pd.DataFrame:
    """Pulls current + baseline ACS data and derives homeownership rate and growth rate."""
    print(f"Pulling {CURRENT_VINTAGE} ACS5 data...")
    current = _fetch_vintage(CURRENT_VINTAGE, VARIABLES)
    print(f"Pulling {BASELINE_VINTAGE} ACS5 data (for 5-year growth rate)...")
    baseline = _fetch_vintage(BASELINE_VINTAGE, ["B01003_001E"])

    for col in VARIABLES:
        current[col] = pd.to_numeric(current[col])
    baseline["B01003_001E"] = pd.to_numeric(baseline["B01003_001E"])

    merged = current.merge(
        baseline[["cbsa_code", "B01003_001E"]].rename(
            columns={"B01003_001E": "population_5yr_ago"}
        ),
        on="cbsa_code",
    )

    merged["population"] = merged["B01003_001E"]
    merged["population_growth_rate_pct"] = (
        (merged["population"] - merged["population_5yr_ago"]) / merged["population_5yr_ago"] * 100
    )
    merged["median_hh_income"] = merged["B19013_001E"]
    merged["homeownership_rate"] = merged["B25003_002E"] / merged["B25003_001E"]
    merged["median_age"] = merged["B01002_001E"]
    merged["population_in_millions"] = merged["population"] / 1_000_000

    out = merged[
        [
            "metro_name",
            "cbsa_code",
            "population",
            "population_5yr_ago",
            "population_growth_rate_pct",
            "median_hh_income",
            "homeownership_rate",
            "median_age",
        ]
    ].sort_values("metro_name")

    out_path = Path(__file__).parent / "raw" / "census_metro_data.csv"
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    return out


if __name__ == "__main__":
    df = collect_census_data()
    print(df.to_string(index=False))
