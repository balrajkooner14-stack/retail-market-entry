# US Retail Market Entry Strategy — Meridian Home

![Python](https://img.shields.io/badge/Python-3.13-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.128-teal) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![Vercel](https://img.shields.io/badge/Deploy-Vercel-black) ![Census](https://img.shields.io/badge/Data-US%20Census-blue) ![BLS](https://img.shields.io/badge/Data-BLS-blue)

A McKinsey-style market entry analysis identifying the two best US expansion markets for a simulated specialty retailer — built with real public data, MECE structured thinking, a weighted scoring model, and a 3-year financial model.

## The Engagement

**Client:** Meridian Home — a simulated mid-size specialty home goods and lifestyle retailer (comparable to West Elm / Crate & Barrel), 47 stores concentrated in the Northeast and West Coast, ~$890M annual revenue.

**The central question:** Which two of five candidate US metros should Meridian Home prioritize for its next expansion cluster over a 3-year horizon?

**The five candidates:** Nashville TN, Austin TX, Denver CO, Charlotte NC, Indianapolis IN.

## The Analytical Framework

**Issue tree (MECE):**

```
Which two of five candidate markets offer the best risk-adjusted return?
├── Is the market attractive?
│   ├── Is it large enough to support the stores?
│   ├── Is consumer behavior aligned with Meridian's product?
│   └── Are retail conditions favorable?
├── Can Meridian compete effectively?
│   ├── How saturated is the competitive landscape?
│   ├── What is the cannibalization risk?
│   └── Is the supply chain / logistics cost manageable?
└── What is the financial return?
    ├── What revenue can realistically be generated?
    ├── What are the costs?
    └── What is the breakeven timeline?
```

**7 weighted scoring dimensions:**

| Dimension | Weight | Data Source |
|---|---|---|
| Population & Growth | 15% | US Census ACS |
| Income & Furnishing Spend | 20% | BLS Consumer Expenditure Survey |
| Homeownership & Housing Activity | 20% | Census + Zillow Research + NAHB |
| Competitive Saturation (inverted) | 20% | Brand store locators |
| Retail Lease Cost (inverted) | 10% | CommercialCafe |
| Labor Cost (inverted) | 10% | BLS OEWS |
| Logistics Proximity (inverted) | 5% | Driving distance to nearest DC |

**Financial model assumptions:** 4,500 sqft store, 10 FTE, 5% annual conversion of trade-area homeowner households, $285 average transaction value, 1.4 visits/year, 3-year ramp-up (65% / 85% / 100% of steady state), NPV at 10% (base) and 12% (risk-adjusted) discount rates. Full assumptions documented in `CLAUDE.md`.

## Key Findings

**Recommendation: Charlotte, NC first (Q1 2026), with a single pilot store in Indianapolis, IN in parallel** — not a full 2-store commitment in both markets.

- Indianapolis ranks #1 on market attractiveness (composite 4.25/5.0) — cheapest lease rate of any candidate ($22.20/sqft) and lowest competitive density — but slower population growth means its financial case needs more runway than the 3-year model window.
- Charlotte ranks #2 (composite 4.08/5.0), sits at Meridian's own East Coast distribution hub (zero logistics cost), and is the only recommended market that clears payback within the model horizon (~31 months).
- This ranking is **robust across 3 independent sensitivity weight profiles** (baseline, financial-focus, growth-focus) — Indianapolis and Charlotte occupy the top 2 slots in all three.
- The original pre-data hypothesis was Nashville + Charlotte. Real 2026 data revised that: Nashville turned out to have the *highest* lease rate and above-average competitive density of the 5 candidates, eroding the economics that made it the presumed favorite.
- Combined risk-adjusted 3-year NPV at the standard store format is currently negative (-$695,888) — a real constraint, which is why the recommendation is a phased entry (Charlotte's full cluster, Indianapolis as a single pilot) rather than a 2-store commitment in both markets.

## Deliverables

- **Interactive dashboard:** deployed on Vercel *(link added after deployment)*
- **Executive deck (PDF):** `outputs/meridian_home_deck.pdf` — 10-slide boardroom-ready deck
- **Excel scoring & financial model:** `outputs/scoring_model.xlsx` — 6 tabs (scoring, thresholds, sensitivity, 2 financial models, data sources)
- **1-page recommendation memo:** `outputs/recommendation_memo.pdf`

## Data Sources

| Data | Source | Notes |
|---|---|---|
| Population, income, homeownership, age | [US Census ACS 5-Year](https://www.census.gov/data.html) | Requires a free API key as of 2026 |
| Home furnishings spend by region | [BLS Consumer Expenditure Survey](https://www.bls.gov/cex/) | Table 1800, region of residence, 2023-2024 |
| Retail wages | [BLS Occupational Employment and Wage Statistics](https://www.bls.gov/oes/) | SOC 41-2031, Retail Salespersons |
| Home value index & appreciation | [Zillow Research](https://www.zillow.com/research/data/) | ZHVI, metro-level |
| Building permits | [NAHB](https://www.nahb.org/news-and-economics/housing-economics/state-and-local-data/building-permits-by-state-and-metro-area) | Aggregates Census's monthly permit survey at metro level |
| Competitor store counts | Brand official store locators | Crate & Barrel, West Elm, Pottery Barn, RH, Williams-Sonoma — counted within each city's Census-defined MSA |
| Retail lease rates | [CommercialCafe](https://www.commercialcafe.com/) | CoStar-backed live listings aggregator |

## Local Setup

```bash
# Clone and enter the repo
git clone <repo-url> && cd retail-market-entry

# Python environment
pip install -r requirements.txt

# Census API key (free, instant): https://api.census.gov/data/key_signup.html
echo "CENSUS_API_KEY=your_key_here" > .env

# Run the pipeline in order
python data_collection/census_collector.py
python data_collection/bls_collector.py
python data_collection/zillow_collector.py
python data_collection/competitor_data.py
python analysis/scoring_model.py
python analysis/financial_model.py
python analysis/generate_charts.py
python analysis/build_excel_model.py
python analysis/build_powerpoint.py   # also converts to PDF via LibreOffice if installed
python analysis/build_memo.py

# Backend
uvicorn api.index:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Visit `http://localhost:3000`.

## Portfolio Context

This project sits alongside a **Target Assortment Optimization** project in the same portfolio. Together they tell a complete retail strategy story: that project modeled how a retailer should configure its product mix across existing locations; this one models where the next locations should be. Both apply the same MECE / hypothesis-driven / financial-modeling toolkit that consulting engagements require.

**Skills demonstrated:** MECE structured thinking, hypothesis-driven analysis (and honest hypothesis revision when data disagreed), weighted multi-criteria scoring with sensitivity analysis, 3-year financial modeling (NPV, payback, scenario analysis), and full-stack delivery of consulting artifacts (Excel, PowerPoint, memo, and a live interactive dashboard).

## Interview Talking Points

**30-second version:** "I completed a full McKinsey-style market entry analysis for a simulated specialty retailer, identifying which two of five US metros to prioritize for expansion. I built a 7-dimension weighted scoring model using real Census, BLS, and Zillow data, and a 3-year financial model with NPV and payback analysis. The data actually revised my initial hypothesis — Indianapolis turned out to beat Nashville once I accounted for real 2026 lease rates and competitive density — which is exactly how a hypothesis-driven analysis is supposed to work. The output is a 10-slide deck, an Excel model, a 1-page memo, and a live dashboard."

**Methodology version:** "I structured the problem with a MECE issue tree — market attractiveness, competitive positioning, financial returns — then formed a hypothesis and tested it against 7 weighted dimensions. When the real estate and competitive data came in, the ranking flipped from my initial hypothesis, and I revised the recommendation rather than forcing the data to fit. The sensitivity analysis confirmed the revised ranking was robust across three different weighting profiles before I built the financial model on top of it."

**Data version:** "All data came from free public sources — Census ACS, BLS's Consumer Expenditure Survey and OEWS wage data, Zillow Research, and NAHB's permit data. Competitor counts were hand-collected from each brand's official store locator. Two of my financial model's original assumptions (staffing level and customer conversion rate) didn't hold up against real specialty-retail benchmarks — every scenario was permanently loss-making until I recalibrated them, which is documented in the code."
