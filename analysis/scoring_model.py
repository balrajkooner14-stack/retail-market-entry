"""7-dimension weighted city scoring model for Meridian Home's market entry
decision. See CLAUDE.md for the full methodology writeup.

Dimensions 3-5's thresholds are tuned to the actual 5-city data range rather
than round numbers, since a couple of the round-number versions barely
spread the cities apart (e.g. competitive saturation, where every candidate
sits under 0.4 per 100k).
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "data_collection" / "raw"

WEIGHTS = {
    "dim1": 0.15,  # Population & Growth
    "dim2": 0.20,  # Income & Furnishing Spend
    "dim3": 0.20,  # Homeownership & Housing Activity
    "dim4": 0.20,  # Competitive Saturation (inverted)
    "dim5": 0.10,  # Retail Lease Rate (inverted)
    "dim6": 0.10,  # Labor Cost (inverted)
    "dim7": 0.05,  # Logistics Proximity (inverted)
}

# Alternative weight profiles for sensitivity analysis, each still summing to 1.00.
WEIGHT_PROFILES = {
    "baseline": WEIGHTS,
    "financial_focus": {
        "dim1": 0.10,
        "dim2": 0.25,
        "dim3": 0.20,
        "dim4": 0.15,
        "dim5": 0.15,
        "dim6": 0.10,
        "dim7": 0.05,
    },
    "growth_focus": {
        "dim1": 0.25,
        "dim2": 0.15,
        "dim3": 0.25,
        "dim4": 0.15,
        "dim5": 0.05,
        "dim6": 0.10,
        "dim7": 0.05,
    },
}


def _bucket(value: float, bands: list[tuple[float, int]]) -> int:
    """bands is a list of (min_inclusive_threshold, score), sorted descending
    by threshold. Returns the score for the first threshold value meets."""
    for threshold, score in bands:
        if value >= threshold:
            return score
    return bands[-1][1]


def _load_merged_data() -> pd.DataFrame:
    census = pd.read_csv(RAW_DIR / "census_metro_data.csv")
    bls = pd.read_csv(RAW_DIR / "bls_data.csv")
    housing = pd.read_csv(RAW_DIR / "housing_data.csv")
    competitors = pd.read_csv(RAW_DIR / "competitor_counts.csv")
    lease = pd.read_csv(RAW_DIR / "lease_rates.csv")

    df = census.merge(bls, on="metro_name")
    df = df.merge(housing, on="metro_name")
    df = df.merge(competitors, on="metro_name")
    df = df.merge(lease, on="metro_name")
    return df


def _score_dim1_population_growth(row) -> float:
    population_score = _bucket(
        row["population"],
        [(2_500_000, 5), (1_500_000, 4), (1_000_000, 3), (750_000, 2), (0, 1)],
    )
    growth_score = _bucket(
        row["population_growth_rate_pct"], [(15, 5), (10, 4), (7, 3), (4, 2), (-999, 1)]
    )
    return 0.6 * population_score + 0.4 * growth_score


def _score_dim2_income_spend(row) -> float:
    income_score = _bucket(
        row["median_hh_income"], [(90_000, 5), (75_000, 4), (65_000, 3), (55_000, 2), (0, 1)]
    )
    spend_score = _bucket(
        row["annual_hh_spend_furnishings"], [(2200, 5), (1800, 4), (1500, 3), (1200, 2), (0, 1)]
    )
    return 0.5 * income_score + 0.5 * spend_score


def _score_dim3_homeownership_housing(row) -> float:
    ownership_score = _bucket(
        row["homeownership_rate"] * 100, [(70, 5), (65, 4), (60, 3), (55, 2), (0, 1)]
    )
    appreciation_score = _bucket(
        row["home_value_appreciation_5yr_pct"], [(25, 5), (15, 4), (0, 3), (-10, 2), (-999, 1)]
    )
    permits_score = _bucket(
        row["annual_permits"], [(20_000, 5), (15_000, 4), (10_000, 3), (7_000, 2), (0, 1)]
    )
    return 0.5 * ownership_score + 0.3 * appreciation_score + 0.2 * permits_score


def _score_dim4_competitive_saturation(row) -> float:
    return _bucket(row["competitors_per_100k"], [(0.40, 1), (0.35, 2), (0.30, 3), (0.25, 4), (0, 5)])


def _score_dim5_lease_rate(row) -> float:
    return _bucket(
        row["retail_lease_rate_sqft_annual"], [(31, 1), (28.5, 2), (26, 3), (23, 4), (0, 5)]
    )


def _score_dim6_labor_cost(row) -> float:
    return _bucket(row["mean_hourly_wage_retail"], [(23, 1), (20, 2), (18, 3), (16, 4), (0, 5)])


def _score_dim7_logistics(row) -> float:
    return _bucket(
        row["distance_miles"], [(1000, 1), (700, 2), (400, 3), (100, 4), (-1, 5)]
    )


DIMENSION_SCORERS = {
    "dim1": _score_dim1_population_growth,
    "dim2": _score_dim2_income_spend,
    "dim3": _score_dim3_homeownership_housing,
    "dim4": _score_dim4_competitive_saturation,
    "dim5": _score_dim5_lease_rate,
    "dim6": _score_dim6_labor_cost,
    "dim7": _score_dim7_logistics,
}


def _attach_logistics_distance(df: pd.DataFrame) -> pd.DataFrame:
    # local import to avoid a hard dependency loop
    from data_collection.competitor_data import get_logistics_distances

    distances = get_logistics_distances()
    df = df.copy()
    df["distance_miles"] = df["metro_name"].map(lambda m: distances[m]["distance_miles"])
    df["nearest_dc"] = df["metro_name"].map(lambda m: distances[m]["nearest_dc"])
    return df


def build_city_scores(weights: dict[str, float] = None, save: bool = True) -> pd.DataFrame:
    """Scores all 5 cities across the 7 dimensions and ranks them.

    save=False is used by the sensitivity analysis below so alternate weight
    profiles don't clobber the canonical baseline city_scores.csv.
    """
    weights = weights or WEIGHTS
    df = _load_merged_data()
    df = _attach_logistics_distance(df)

    for dim, scorer in DIMENSION_SCORERS.items():
        df[f"{dim}_score"] = df.apply(scorer, axis=1)

    df["composite_score"] = sum(df[f"{dim}_score"] * weight for dim, weight in weights.items())
    df = df.sort_values("composite_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    df["recommended"] = df["rank"] <= 2

    if save:
        out_path = RAW_DIR / "city_scores.csv"
        df.to_csv(out_path, index=False)
    return df


def run_sensitivity_analysis() -> pd.DataFrame:
    """Scores all cities under each weight profile and checks rank stability."""
    results = {}
    for profile_name, weights in WEIGHT_PROFILES.items():
        scored = build_city_scores(weights, save=False)
        results[profile_name] = scored.set_index("metro_name")["rank"]

    ranks_df = pd.DataFrame(results)
    top2_by_profile = {
        profile: set(ranks.sort_values().index[:2]) for profile, ranks in results.items()
    }
    all_top2 = list(top2_by_profile.values())
    is_robust = all(t == all_top2[0] for t in all_top2)
    ranks_df["stability"] = "Robust" if is_robust else "Sensitive"

    out_path = RAW_DIR / "sensitivity_results.csv"
    ranks_df.to_csv(out_path)
    return ranks_df, is_robust


if __name__ == "__main__":
    scores = build_city_scores()
    print("CITY RANKINGS:")
    display_cols = [
        "rank",
        "metro_name",
        "dim1_score",
        "dim2_score",
        "dim3_score",
        "dim4_score",
        "dim5_score",
        "dim6_score",
        "dim7_score",
        "composite_score",
    ]
    print(scores[display_cols].to_string(index=False))

    top2 = scores[scores["recommended"]]["metro_name"].tolist()
    print(f"\nTOP 2 RECOMMENDED: {top2[0]} and {top2[1]}")

    sensitivity, is_robust = run_sensitivity_analysis()
    print("\nSENSITIVITY CHECK (rank per weight profile):")
    print(sensitivity.to_string())
    print(f"\nSENSITIVITY RESULT: {'Robust' if is_robust else 'Sensitive'} recommendation")
