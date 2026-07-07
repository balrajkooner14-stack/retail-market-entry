# US Retail Market Entry Strategy — Meridian Home

![Python](https://img.shields.io/badge/Python-3.13-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.128-teal) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![Vercel](https://img.shields.io/badge/Deploy-Vercel-black) ![Census](https://img.shields.io/badge/Data-US%20Census-blue) ![BLS](https://img.shields.io/badge/Data-BLS-blue)

A market entry analysis for a simulated specialty retailer, built the way a consulting team would approach it: an issue tree, a weighted scoring model across 5 candidate metros, and a 3-year financial model — all on real public data.

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

**Financial model assumptions:** 4,500 sqft store, 10 FTE, 5% annual conversion of trade-area homeowner households, $285 average transaction value, 1.4 visits/year, 3-year ramp-up (65% / 85% / 100% of steady state), NPV at 10% (base) and 12% (risk-adjusted) discount rates. Full assumptions in `analysis/financial_model.py`.

## Key Findings

**Recommendation: Charlotte first (Q1 2026), with a single pilot store in Indianapolis running in parallel** — not a full 2-store cluster in both markets.

Indianapolis actually comes out on top of the composite ranking (4.25/5.0) — the cheapest lease rate of any candidate and the lowest competitive density — but its population growth is the slowest of the two finalists, so its financial case needs more runway than the 3-year model gives it. Charlotte (4.08/5.0) sits at Meridian's own East Coast distribution hub, so logistics cost is zero, and it's the only market that clears payback within the model window, at roughly 31 months.

That ranking held up across three different weight profiles (baseline, financial-focus, growth-focus), so it's not an artifact of one particular set of assumptions. It also isn't what I expected going in — my working hypothesis was Nashville + Charlotte, but Nashville's lease rate turned out to be the highest of all five candidates once I had real numbers, which is what pushed it out of the top two.

Combined risk-adjusted NPV across both markets at the standard store format is currently negative (-$695,888), which is the real reason behind the phased recommendation rather than committing to two full store clusters up front.

## Deliverables

- **Interactive dashboard:** [retail-market-entry.vercel.app](https://retail-market-entry.vercel.app)
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

Pairs with a **Target Assortment Optimization** project elsewhere in my portfolio — that one models how a retailer should configure its product mix across existing stores; this one models where the next stores should go.
