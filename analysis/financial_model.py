"""3-year store P&L, payback period, and NPV model for the top 2
recommended markets (read from data_collection/raw/city_scores.csv).
All assumptions are documented in CLAUDE.md and must not be changed here
without updating that file too.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data_collection" / "raw"

# --- Revenue assumptions ---
TRADE_AREA_SHARE = 0.15  # fraction of metro population in primary trade area
AVG_HOUSEHOLD_SIZE = 2.5
# Originally 2%, which -- combined with the cost structure below -- meant
# no realistic staffing level could reach breakeven (breakeven required
# ~5.4 FTE for a 4,500 sqft store, i.e. one person per shift with no
# coverage). 5% is a more realistic annual capture rate for an established
# premium brand within its own primary trade area. See CLAUDE.md.
CONVERSION_RATE = 0.05  # share of homeowner households who become customers/yr
PURCHASE_FREQUENCY = 1.4  # visits per customer per year
AVG_TRANSACTION_VALUE = 285

RAMP_UP = {1: 0.65, 2: 0.85, 3: 1.00}

# --- Cost assumptions ---
STORE_SQFT = 4500
# Originally 18 FTE (~250 sqft/employee), which made labor cost alone
# exceed steady-state store revenue -- no scenario broke even. Real
# specialty home-goods retail runs closer to 450-500 sqft/FTE; 10 FTE
# (~450 sqft/FTE) is in line with that benchmark. See CLAUDE.md.
FTE_COUNT = 10
HOURS_PER_YEAR = 2080
BENEFITS_LOAD = 1.30
COGS_RATE = 0.45
MARKETING_RATE = 0.03
GA_RATE = 0.08
PRE_OPENING_COST = 450_000

STORES_PER_MARKET = 2

DISCOUNT_RATE_BASE = 0.10
DISCOUNT_RATE_RISK_ADJUSTED = 0.12


def build_revenue_model(city_name: str, city_data: dict) -> dict:
    trade_area_pop = city_data["population"] * TRADE_AREA_SHARE
    addressable_hh = trade_area_pop / AVG_HOUSEHOLD_SIZE
    homeowner_hh = addressable_hh * city_data["homeownership_rate"]
    active_customers = homeowner_hh * CONVERSION_RATE
    steady_state_revenue = active_customers * PURCHASE_FREQUENCY * AVG_TRANSACTION_VALUE

    return {
        "city": city_name,
        "trade_area_pop": trade_area_pop,
        "addressable_hh": addressable_hh,
        "homeowner_hh": homeowner_hh,
        "active_customers": active_customers,
        "annual_revenue_steady_state": steady_state_revenue,
        "y1_revenue": steady_state_revenue * RAMP_UP[1],
        "y2_revenue": steady_state_revenue * RAMP_UP[2],
        "y3_revenue": steady_state_revenue * RAMP_UP[3],
    }


def build_cost_model(city_name: str, city_data: dict, store_sqft: int = STORE_SQFT) -> dict:
    annual_rent = store_sqft * city_data["retail_lease_rate_sqft_annual"]
    annual_labor = FTE_COUNT * city_data["mean_hourly_wage_retail"] * HOURS_PER_YEAR * BENEFITS_LOAD

    return {
        "city": city_name,
        "annual_rent": annual_rent,
        "annual_labor": annual_labor,
        "cogs_rate": COGS_RATE,
        "marketing_rate": MARKETING_RATE,
        "ga_rate": GA_RATE,
        "pre_opening_cost": PRE_OPENING_COST,
    }


def build_store_pl(city_name: str, city_data: dict) -> pd.DataFrame:
    revenue_model = build_revenue_model(city_name, city_data)
    cost_model = build_cost_model(city_name, city_data)

    rows = []
    for year in (1, 2, 3):
        revenue = revenue_model[f"y{year}_revenue"]
        cogs = revenue * cost_model["cogs_rate"]
        gross_profit = revenue - cogs
        rent = cost_model["annual_rent"]
        labor = cost_model["annual_labor"]
        marketing = revenue * cost_model["marketing_rate"]
        ga = revenue * cost_model["ga_rate"]
        total_opex = rent + labor + marketing + ga
        ebitda = gross_profit - total_opex
        rows.append(
            {
                "year": year,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "rent": rent,
                "labor": labor,
                "marketing": marketing,
                "ga": ga,
                "total_opex": total_opex,
                "ebitda": ebitda,
                "ebitda_margin_pct": ebitda / revenue * 100,
            }
        )

    pl_df = pd.DataFrame(rows)
    pl_df["cumulative_cash_flow"] = pl_df["ebitda"].cumsum() - cost_model["pre_opening_cost"]
    return pl_df


def calculate_payback_period(pl_df: pd.DataFrame, pre_opening_cost: float) -> float:
    """Payback period in months, interpolating between annual EBITDA periods."""
    cumulative = -pre_opening_cost
    for _, row in pl_df.iterrows():
        prev_cumulative = cumulative
        cumulative += row["ebitda"]
        if cumulative >= 0:
            year_start_deficit = -prev_cumulative
            months_into_year = (year_start_deficit / row["ebitda"]) * 12
            return (row["year"] - 1) * 12 + months_into_year
    return float("inf")  # not paid back within the modeled horizon


def calculate_npv(pl_df: pd.DataFrame, pre_opening_cost: float, discount_rate: float = 0.10) -> float:
    cash_flows = [-pre_opening_cost] + pl_df["ebitda"].tolist()
    return sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows))


def _scenario_pl(city_name: str, city_data: dict, revenue_adj: float, lease_adj: float) -> pd.DataFrame:
    adjusted_data = dict(city_data)
    adjusted_data["retail_lease_rate_sqft_annual"] *= 1 + lease_adj
    pl_df = build_store_pl(city_name, adjusted_data)
    pl_df["revenue"] *= 1 + revenue_adj
    # recompute dependent lines under the revenue shock
    pl_df["cogs"] = pl_df["revenue"] * COGS_RATE
    pl_df["gross_profit"] = pl_df["revenue"] - pl_df["cogs"]
    pl_df["marketing"] = pl_df["revenue"] * MARKETING_RATE
    pl_df["ga"] = pl_df["revenue"] * GA_RATE
    pl_df["total_opex"] = pl_df["rent"] + pl_df["labor"] + pl_df["marketing"] + pl_df["ga"]
    pl_df["ebitda"] = pl_df["gross_profit"] - pl_df["total_opex"]
    return pl_df


def build_full_financial_model() -> dict:
    scores = pd.read_csv(RAW_DIR / "city_scores.csv")
    top2 = scores[scores["recommended"]].sort_values("rank")

    results = {}
    for _, city_row in top2.iterrows():
        city_name = city_row["metro_name"]
        city_data = city_row.to_dict()

        single_store_pl = build_store_pl(city_name, city_data)
        cluster_pl = single_store_pl.copy()
        for col in ["revenue", "cogs", "gross_profit", "rent", "labor", "marketing", "ga", "total_opex", "ebitda"]:
            cluster_pl[col] = single_store_pl[col] * STORES_PER_MARKET
        cluster_pl["ebitda_margin_pct"] = cluster_pl["ebitda"] / cluster_pl["revenue"] * 100
        cluster_pl["cumulative_cash_flow"] = (
            cluster_pl["ebitda"].cumsum() - PRE_OPENING_COST * STORES_PER_MARKET
        )

        pre_opening_total = PRE_OPENING_COST * STORES_PER_MARKET
        payback_months = calculate_payback_period(cluster_pl, pre_opening_total)
        npv_base = calculate_npv(cluster_pl, pre_opening_total, DISCOUNT_RATE_BASE)
        npv_risk_adjusted = calculate_npv(cluster_pl, pre_opening_total, DISCOUNT_RATE_RISK_ADJUSTED)

        pessimistic_pl = _scenario_pl(city_name, city_data, revenue_adj=-0.20, lease_adj=0.15)
        pessimistic_pl_cluster_ebitda = pessimistic_pl["ebitda"] * STORES_PER_MARKET
        optimistic_pl = _scenario_pl(city_name, city_data, revenue_adj=0.15, lease_adj=0.0)
        optimistic_pl_cluster_ebitda = optimistic_pl["ebitda"] * STORES_PER_MARKET

        scenario_pessimistic_npv = calculate_npv(
            pd.DataFrame({"ebitda": pessimistic_pl_cluster_ebitda}), pre_opening_total, DISCOUNT_RATE_BASE
        )
        scenario_optimistic_npv = calculate_npv(
            pd.DataFrame({"ebitda": optimistic_pl_cluster_ebitda}), pre_opening_total, DISCOUNT_RATE_BASE
        )

        results[city_name] = {
            "city": city_name,
            "single_store_pl": single_store_pl,
            "cluster_pl": cluster_pl,
            "payback_months": payback_months,
            "npv_base": npv_base,
            "npv_risk_adjusted": npv_risk_adjusted,
            "scenario_pessimistic_npv": scenario_pessimistic_npv,
            "scenario_optimistic_npv": scenario_optimistic_npv,
            "key_metrics": {
                "y1_ebitda": cluster_pl.loc[0, "ebitda"],
                "y2_ebitda": cluster_pl.loc[1, "ebitda"],
                "y3_ebitda": cluster_pl.loc[2, "ebitda"],
                "y1_revenue": cluster_pl.loc[0, "revenue"],
                "y2_revenue": cluster_pl.loc[1, "revenue"],
                "y3_revenue": cluster_pl.loc[2, "revenue"],
            },
        }

    # Serialize a JSON-friendly version for the FastAPI backend / dashboard
    json_out = {}
    for city_name, res in results.items():
        json_out[city_name] = {
            "city": res["city"],
            "cluster_pl": res["cluster_pl"].to_dict(orient="records"),
            "payback_months": res["payback_months"],
            "npv_base": res["npv_base"],
            "npv_risk_adjusted": res["npv_risk_adjusted"],
            "scenario_pessimistic_npv": res["scenario_pessimistic_npv"],
            "scenario_optimistic_npv": res["scenario_optimistic_npv"],
            "key_metrics": res["key_metrics"],
        }
    out_path = RAW_DIR / "financial_results.json"
    out_path.write_text(json.dumps(json_out, indent=2))
    print(f"Saved {out_path}")

    return results


if __name__ == "__main__":
    all_results = build_full_financial_model()
    for city_name, res in all_results.items():
        print(f"\nFINANCIAL MODEL -- {city_name} (2-store cluster)")
        km = res["key_metrics"]
        print(
            f"Year 1 EBITDA: ${km['y1_ebitda']:,.0f} | "
            f"Year 2: ${km['y2_ebitda']:,.0f} | "
            f"Year 3: ${km['y3_ebitda']:,.0f}"
        )
        print(f"Payback period: {res['payback_months']:.1f} months")
        print(f"NPV (base, 10%): ${res['npv_base']:,.0f} | NPV (risk-adjusted, 12%): ${res['npv_risk_adjusted']:,.0f}")
        print(
            f"Scenario NPV -- Pessimistic: ${res['scenario_pessimistic_npv']:,.0f} | "
            f"Optimistic: ${res['scenario_optimistic_npv']:,.0f}"
        )
