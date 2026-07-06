"""Manually-researched datasets that have no clean public API:
1. Direct competitor store counts per metro (from each brand's official
   store locator, counted July 2026)
2. Retail lease rates per sq ft per metro (from CommercialCafe, a CoStar-
   data-backed market listings aggregator, pulled July 2026)
3. Driving distance from each metro to Meridian's nearest fictional DC

Competitor counts were counted by visiting each brand's official store
locator and counting full-price retail locations within each city's Census-
defined MSA (matching the CBSA boundaries used for the Census/BLS pulls
elsewhere in this project) -- NOT a fixed-mile radius from downtown, since
MSA boundaries are the more reproducible and consistent unit used throughout
this analysis. Outlet-only locations are excluded (different economics/
channel than a full-price flagship). Store locators checked:
  - Crate & Barrel: crateandbarrel.com store list (via storelocators.com)
  - West Elm: westelm.com/stores/
  - Pottery Barn: potterybarn.com/stores/
  - RH: rh.com/us/en/store-locations/stores.jsp
  - Williams-Sonoma: williams-sonoma.com/stores/
"""

from pathlib import Path

import pandas as pd

# metro_name -> {brand: store_count}
COMPETITOR_COUNTS = {
    "Nashville, TN": {
        "crate_barrel": 1,
        "west_elm": 1,
        "pottery_barn": 2,  # Nashville Hill Center + Franklin CoolSprings Galleria
        "rh_stores": 1,
        "williams_sonoma": 2,  # Nashville Hill Center + Franklin CoolSprings Galleria
    },
    "Austin, TX": {
        "crate_barrel": 1,
        "west_elm": 1,
        "pottery_barn": 1,
        "rh_stores": 1,
        "williams_sonoma": 1,
    },
    "Denver, CO": {
        "crate_barrel": 2,  # Broomfield + Lone Tree
        "west_elm": 1,  # Denver Cherry Creek North
        "pottery_barn": 3,  # Broomfield + Littleton + Lone Tree
        "rh_stores": 1,
        "williams_sonoma": 4,  # Broomfield + Denver Cherry Creek + Littleton x2
    },
    "Charlotte, NC": {
        "crate_barrel": 2,
        "west_elm": 1,
        "pottery_barn": 2,  # South Park Mall + Huntersville Birkdale
        "rh_stores": 1,
        "williams_sonoma": 2,  # Spec Shops in the Park + Huntersville Birkdale
    },
    "Indianapolis, IN": {
        "crate_barrel": 1,
        "west_elm": 1,
        "pottery_barn": 1,
        "rh_stores": 1,
        "williams_sonoma": 1,
    },
}

# SOURCE: commercialcafe.com metro retail-space listing averages, pulled
# July 2026 (CoStar-backed live-listings aggregator, not a formal CBRE PDF
# report, but a consistent same-methodology source across all 5 metros).
LEASE_RATES_SQFT_ANNUAL = {
    "Nashville, TN": 30.12,
    "Austin, TX": 28.15,
    "Denver, CO": 25.19,
    "Charlotte, NC": 27.87,
    "Indianapolis, IN": 22.20,
}
LEASE_RATE_SOURCE = "commercialcafe.com retail market averages, July 2026"

# Driving distance (miles) from each metro to the nearest of Meridian's two
# fictional distribution centers (Charlotte NC or Salt Lake City UT).
# Verified via web search, July 2026.
LOGISTICS_DISTANCES_MILES = {
    "Nashville, TN": {"nearest_dc": "Charlotte, NC", "distance_miles": 409},
    "Austin, TX": {"nearest_dc": "Salt Lake City, UT", "distance_miles": 1291},
    "Denver, CO": {"nearest_dc": "Salt Lake City, UT", "distance_miles": 521},
    "Charlotte, NC": {"nearest_dc": "Charlotte, NC", "distance_miles": 0},
    "Indianapolis, IN": {"nearest_dc": "Charlotte, NC", "distance_miles": 576},
}


def load_competitor_data() -> pd.DataFrame:
    census_path = Path(__file__).parent / "raw" / "census_metro_data.csv"
    population = pd.read_csv(census_path)[["metro_name", "population"]]

    rows = []
    for metro_name, counts in COMPETITOR_COUNTS.items():
        total = sum(counts.values())
        rows.append({"metro_name": metro_name, **counts, "total_direct_competitors": total})
    df = pd.DataFrame(rows).merge(population, on="metro_name")
    df["metro_population_millions"] = df["population"] / 1_000_000
    df["competitors_per_100k"] = df["total_direct_competitors"] / (df["population"] / 100_000)
    return df.drop(columns=["population"])


def load_lease_rates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "metro_name": metro_name,
                "retail_lease_rate_sqft_annual": rate,
                "source": LEASE_RATE_SOURCE,
                "year": 2026,
            }
            for metro_name, rate in LEASE_RATES_SQFT_ANNUAL.items()
        ]
    )


def get_logistics_distances() -> dict:
    return LOGISTICS_DISTANCES_MILES


if __name__ == "__main__":
    competitors = load_competitor_data()
    competitors.to_csv(Path(__file__).parent / "raw" / "competitor_counts.csv", index=False)
    print("Competitor counts:")
    print(competitors.to_string(index=False))

    lease = load_lease_rates()
    lease.to_csv(Path(__file__).parent / "raw" / "lease_rates.csv", index=False)
    print("\nLease rates:")
    print(lease.to_string(index=False))

    print("\nLogistics distances:")
    for metro, info in get_logistics_distances().items():
        print(f"  {metro}: {info['distance_miles']} mi to {info['nearest_dc']}")
