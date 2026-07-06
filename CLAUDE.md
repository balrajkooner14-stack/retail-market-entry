# US Retail Market Entry Strategy — Project Memory

## What this project is
A full McKinsey-style market entry consulting analysis for a simulated specialty
retailer called Meridian Home — a premium home goods and lifestyle retailer with
47 stores, looking to open 8 new locations across 2 new US markets.

The engagement question: which 2 of 5 candidate US metros should Meridian Home
prioritize for expansion? The 5 candidates: Nashville TN, Austin TX, Denver CO,
Charlotte NC, Indianapolis IN.

## Portfolio context
Masters in Business Analytics portfolio project targeting: Management Consultant,
Business Analyst, Strategy Analyst roles at McKinsey, BCG, Deloitte, Oliver Wyman,
and Tier 2 boutiques. This project demonstrates MECE structured thinking,
hypothesis-driven analysis, weighted scoring models, financial modelling,
and client-facing deliverable creation — the core consulting skill set.
Connects to existing Target Assortment Optimization project in portfolio.

## The simulated client — Meridian Home
- Name: Meridian Home
- Sector: Specialty home goods and lifestyle retail (comparable: West Elm / Crate & Barrel)
- Current footprint: 47 stores, concentrated in Northeast and West Coast
- Revenue: ~$890M annually (fictional but realistic)
- Distribution centers: Charlotte NC and Salt Lake City UT (fictional)
- The decision: open 8 stores across 2 new markets in 24 months

## The 5 candidate markets
Nashville TN, Austin TX, Denver CO, Charlotte NC, Indianapolis IN

## The 7 scoring dimensions and weights (DO NOT CHANGE)
1. Population & Growth — weight 15%
   Data: US Census ACS metro population + 5-year growth rate
   Scoring: Raw population score (larger = better) + growth rate score (faster = better)

2. Income & Home Furnishing Spend — weight 20%
   Data: BLS Consumer Expenditure Survey (home furnishings spending per HH) + median HH income
   Scoring: Higher spend per household = higher score

3. Homeownership & Housing Activity — weight 20%
   Data: Census homeownership rate + Zillow home value index + Census building permits
   Scoring: Higher homeownership rate + rising home values + more permits = higher score

4. Competitive Saturation — weight 20%
   Data: Manual store count of direct competitors (Crate & Barrel, West Elm, Pottery Barn,
   RH, Williams-Sonoma) divided by metro population
   Scoring: INVERTED — fewer competitors per 100K population = higher score (less saturated)

5. Retail Real Estate Cost — weight 10%
   Data: CBRE/JLL published retail lease rates per sq ft by market
   Scoring: INVERTED — lower lease rate = higher score (cheaper = better for economics)

6. Retail Labor Cost — weight 10%
   Data: BLS OES mean hourly wage for retail salespersons (SOC 41-2031) by metro
   Scoring: INVERTED — lower labor cost = higher score

7. Logistics Proximity — weight 5%
   Data: Driving distance from nearest Meridian DC (Charlotte NC or Salt Lake City UT)
   Scoring: INVERTED — shorter distance = higher score

## Scoring methodology (DO NOT CHANGE)
For each dimension:
1. Collect the raw data value for all 5 cities
2. Convert to a 1-5 score using explicit thresholds (defined in scoring_model.py)
3. Multiply score x weight to get weighted score for that dimension
4. Sum all 7 weighted scores to get composite city score (max 5.0)
5. Rank cities 1-5 by composite score
6. Top 2 = recommended markets

For inverted dimensions (4, 5, 6, 7): higher raw value = lower score (1-5 reversed)

## Financial model assumptions (DO NOT CHANGE)
Revenue model:
- Trade area population = metro MSA population x 0.15 (15-mile primary trade area)
- Addressable households = trade area population / 2.5 (avg household size)
- Homeowner households = addressable households x homeownership rate
- Conversion rate = 2.0% of homeowner households per year are active Meridian customers
- Purchase frequency = 1.4 visits per customer per year
- Average transaction value = $285
- Annual revenue per store = homeowner HH x conversion rate x frequency x ATV

Ramp-up schedule:
- Year 1 = 65% of steady-state revenue (store awareness building)
- Year 2 = 85% of steady-state revenue
- Year 3 = 100% of steady-state revenue

Cost model (per store):
- COGS = 45% of revenue (55% gross margin, premium home goods benchmark)
- Rent = store sq ft (4,500 sq ft target size) x annual lease rate per sq ft
- Labor = 18 FTE x BLS mean hourly wage x 2,080 hours x 1.30 benefits load
- Marketing = 3% of revenue
- Allocated G&A = 8% of revenue
- Pre-opening cost = $450,000 (buildout, initial inventory, grand opening)

Financial outputs:
- Annual EBITDA per store (Year 1, 2, 3)
- Payback period in months from pre-opening investment
- 3-year cumulative cash flow per store cluster (2 stores per market)
- NPV at 10% discount rate (base) and 12% (risk-adjusted)

## Output deliverables (DO NOT CHANGE)
1. outputs/scoring_model.xlsx — 6-tab Excel scoring + sensitivity + financial model
2. outputs/meridian_home_deck.pptx — 10-slide PowerPoint deck
3. outputs/recommendation_memo.pdf — 1-page executive recommendation memo
4. outputs/charts/ — All chart PNG files for deck and dashboard
5. Vercel dashboard — Interactive version of the scoring and financial model

## Architecture (DO NOT CHANGE)
- Data collection: Python scripts in data_collection/ pulling Census + BLS APIs,
  plus researched manual data (competitor counts, lease rates)
- Analysis: Python scripts in analysis/ building scoring and financial models
- Static outputs: Python generates Excel (openpyxl), PPT (python-pptx), PDF (ReportLab)
- Interactive: FastAPI backend + Next.js frontend deployed on Vercel
- All file paths use pathlib.Path(__file__).parent for portability

## Vercel deployment rules
- vercel.json routes /api/* to api/index.py and /* to frontend/
- The FastAPI backend reads from outputs/ static files — no live API calls at request time
- All heavy computation done at build time; API just serves pre-computed results
- Frontend is primarily static — chart images + scoring table from API

## Verified logistics distances (July 2026 web research)
- Nashville -> Charlotte DC: 409 miles
- Austin -> Salt Lake City DC: 1,291 miles
- Denver -> Salt Lake City DC: 521 miles
- Charlotte -> Charlotte DC: 0 miles
- Indianapolis -> Charlotte DC: 576 miles

## Data sourcing notes (this build)
- Census ACS, BLS OES/CEX, Zillow ZHVI: pulled programmatically where the public
  API/CSV endpoint is verified to work; if an endpoint is unavailable, fall back
  to a manually-researched CSV with the source cited in comments and in the
  Excel "Data Sources" tab.
- Competitor store counts and retail lease rates: researched via web search
  (brand store locators, published CBRE/JLL/CoStar market reports) rather than
  the illustrative placeholder figures in the original plan doc. Any figure
  that could not be verified from a public source is labeled as an estimate.
- Building permits: Census's own metro-annual permits page is frozen at 2021.
  Switched to NAHB's "Building Permits by State and Metro Area" workbook,
  which republishes the same underlying Census monthly permit survey at
  metro granularity and is current (FY2025 totals used, refreshed through
  May 2026 at pull time). See data_collection/zillow_collector.py.

## Original hypothesis (stated before data collection, for comparison)
Nashville and Charlotte are the recommended markets. Nashville: highest population
growth rate, strong millennial demographic, limited premium home goods competition,
and proximity to Charlotte DC. Charlotte: major Southeast growth hub, strong
homeownership, finance industry salary base, and located at the DC itself (zero
logistics cost). Austin is the expected runner-up that gets displaced by saturation
and real estate cost. Indianapolis is the wildcard — low cost but limited upside.
Denver is solid but high labor and real estate costs hurt the economics.

## Actual recommendation (revised by real data -- see analysis/scoring_model.py)
The scoring model recommends **Indianapolis and Charlotte**, not Nashville.
Composite scores: Indianapolis 4.25, Charlotte 4.08, Austin 3.77, Nashville
3.55, Denver 3.36. Robust across all 3 sensitivity weight profiles (baseline,
financial-focus, growth-focus) -- Indianapolis and Charlotte occupy the top 2
slots in all three (they swap #1/#2 order under growth-focus only).

Why the hypothesis was revised: Nashville's real estate market has caught up
since the hypothesis was written -- it has the HIGHEST retail lease rate of
all 5 candidates ($30.12/sqft, real 2026 data) and above-average competitive
density, eroding the unit economics that made it the presumed favorite.
Indianapolis, by contrast, is genuinely underrated on cost: the cheapest
lease rate ($22.20/sqft), tied-lowest competitive saturation, and solid
housing fundamentals -- its only real weakness is slower population growth,
which the 15%-weighted dimension 1 isn't enough to offset given how much
cheaper it is to operate there. This is the intended behavior of a
hypothesis-driven analysis: forming a view, testing it against real data,
and revising it when the data disagrees -- not a data or modeling error.

All downstream deliverables (financial model, deck, memo, dashboard) are
built around **Indianapolis + Charlotte** as the two recommended markets.
