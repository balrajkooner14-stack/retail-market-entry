"""FastAPI backend serving pre-computed scoring/financial results to the
Next.js dashboard. All heavy computation happened in analysis/ at build
time -- this just serves the results as JSON, plus the static deliverable
files for download.
"""

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data_collection" / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

app = FastAPI(title="Meridian Home Market Entry Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_data_exists():
    """Runs the analysis pipeline if pre-computed results aren't present yet."""
    required = [
        RAW_DIR / "city_scores.csv",
        RAW_DIR / "financial_results.json",
        RAW_DIR / "sensitivity_results.csv",
    ]
    if all(p.exists() for p in required):
        return
    analysis_dir = PROJECT_ROOT / "analysis"
    subprocess.run([sys.executable, str(analysis_dir / "scoring_model.py")], check=True, cwd=PROJECT_ROOT)
    subprocess.run([sys.executable, str(analysis_dir / "financial_model.py")], check=True, cwd=PROJECT_ROOT)


_ensure_data_exists()

if (OUTPUTS_DIR).exists():
    app.mount("/api/files", StaticFiles(directory=str(OUTPUTS_DIR)), name="files")


def _fmt_dim_raw(row: pd.Series, dim: int) -> str:
    if dim == 1:
        return f"{row['population']/1e6:.2f}M pop, {row['population_growth_rate_pct']:.1f}% 5yr growth"
    if dim == 2:
        return f"${row['median_hh_income']:,.0f} median income, ${row['annual_hh_spend_furnishings']:,.0f}/yr furnishing spend"
    if dim == 3:
        return f"{row['homeownership_rate']*100:.1f}% homeownership, {row['home_value_appreciation_5yr_pct']:.1f}% 5yr appreciation"
    if dim == 4:
        return f"{row['total_direct_competitors']} competitors ({row['competitors_per_100k']:.2f} per 100k)"
    if dim == 5:
        return f"${row['retail_lease_rate_sqft_annual']:.2f}/sqft/yr"
    if dim == 6:
        return f"${row['mean_hourly_wage_retail']:.2f}/hr"
    if dim == 7:
        return f"{row['distance_miles']:.0f} mi to {row['nearest_dc']}"
    raise ValueError(dim)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "Meridian Home Market Entry Analysis"}


@app.get("/api/scores")
def get_scores():
    df = pd.read_csv(RAW_DIR / "city_scores.csv").sort_values("rank")
    sensitivity = pd.read_csv(RAW_DIR / "sensitivity_results.csv", index_col=0)
    is_robust = bool((sensitivity["stability"] == "Robust").all())

    cities = []
    for _, row in df.iterrows():
        city_name, state = row["metro_name"].split(", ")
        cities.append(
            {
                "city": city_name,
                "state": state,
                "composite_score": round(row["composite_score"], 2),
                "rank": int(row["rank"]),
                "recommended": bool(row["recommended"]),
                **{f"dim{i}_score": row[f"dim{i}_score"] for i in range(1, 8)},
                **{f"dim{i}_raw": _fmt_dim_raw(row, i) for i in range(1, 8)},
            }
        )

    recommended = df[df["recommended"]].sort_values("rank")["metro_name"].tolist()
    return {
        "cities": cities,
        "recommendation": " and ".join(recommended),
        "sensitivity": (
            "Robust — ranking stable across all 3 weight profiles"
            if is_robust
            else "Sensitive — see caveats"
        ),
    }


@app.get("/api/financial")
def get_financial():
    financial_results = json.loads((RAW_DIR / "financial_results.json").read_text())
    cities = []
    for city_name, data in financial_results.items():
        pl = {row["year"]: row for row in data["cluster_pl"]}
        cities.append(
            {
                "city": city_name,
                "y1_revenue": pl[1]["revenue"],
                "y2_revenue": pl[2]["revenue"],
                "y3_revenue": pl[3]["revenue"],
                "y1_ebitda": pl[1]["ebitda"],
                "y2_ebitda": pl[2]["ebitda"],
                "y3_ebitda": pl[3]["ebitda"],
                "payback_months": (
                    data["payback_months"] if data["payback_months"] != float("inf") else None
                ),
                "npv_base": data["npv_base"],
                "npv_risk_adjusted": data["npv_risk_adjusted"],
                "scenario_pessimistic_npv": data["scenario_pessimistic_npv"],
                "scenario_optimistic_npv": data["scenario_optimistic_npv"],
            }
        )
    return {"cities": cities}


@app.get("/api/methodology")
def get_methodology():
    return {
        "issue_tree": {
            "central_question": (
                "Which two of the five candidate markets offer Meridian Home the best "
                "risk-adjusted return on a new store cluster over a 3-year horizon?"
            ),
            "branches": [
                {
                    "name": "Is the market attractive?",
                    "sub_questions": [
                        "Is the market large enough to support the stores?",
                        "Is consumer behavior aligned with Meridian's product?",
                        "Are retail conditions favorable?",
                    ],
                },
                {
                    "name": "Can Meridian compete effectively?",
                    "sub_questions": [
                        "How saturated is the competitive landscape?",
                        "What is the risk of cannibalizing existing stores?",
                        "Is the supply chain and logistics cost manageable?",
                    ],
                },
                {
                    "name": "What is the financial return?",
                    "sub_questions": [
                        "What revenue can realistically be generated?",
                        "What are the costs?",
                        "What is the breakeven timeline?",
                    ],
                },
            ],
        },
        "dimensions": [
            {"name": "Population & Growth", "weight": 0.15, "source": "US Census ACS"},
            {"name": "Income & Furnishing Spend", "weight": 0.20, "source": "BLS Consumer Expenditure Survey"},
            {"name": "Homeownership & Housing Activity", "weight": 0.20, "source": "Census + Zillow Research + NAHB"},
            {"name": "Competitive Saturation", "weight": 0.20, "source": "Brand store locators"},
            {"name": "Retail Real Estate Cost", "weight": 0.10, "source": "CommercialCafe"},
            {"name": "Labor Cost", "weight": 0.10, "source": "BLS Occupational Employment Statistics"},
            {"name": "Logistics Proximity", "weight": 0.05, "source": "Driving distance to nearest DC"},
        ],
    }


@app.get("/api/downloads")
def get_downloads():
    files = {
        "deck_pptx": "meridian_home_deck.pptx",
        "deck_pdf": "meridian_home_deck.pdf",
        "excel_model": "scoring_model.xlsx",
        "memo_pdf": "recommendation_memo.pdf",
    }
    return {
        key: f"/api/files/{filename}"
        for key, filename in files.items()
        if (OUTPUTS_DIR / filename).exists()
    }
