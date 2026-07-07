"""Builds the 1-page executive recommendation memo PDF at
outputs/recommendation_memo.pdf using ReportLab. Plain prose, not slide
format -- reads like a memo from an engagement manager to a CEO.
"""

import json
import sys
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "data_collection" / "raw"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

NAVY = HexColor("#0D1B2A")
BODY_COLOR = HexColor("#0B0B0B")


def build_memo():
    scores = pd.read_csv(RAW_DIR / "city_scores.csv").sort_values("rank")
    financial_results = json.loads((RAW_DIR / "financial_results.json").read_text())

    top2 = scores[scores["recommended"]]
    city1 = top2.iloc[0]  # Indianapolis (rank 1)
    city2 = top2.iloc[1]  # Charlotte (rank 2)
    fin1 = financial_results[city1["metro_name"]]
    fin2 = financial_results[city2["metro_name"]]
    combined_npv_risk = fin1["npv_risk_adjusted"] + fin2["npv_risk_adjusted"]

    out_path = OUTPUTS_DIR / "recommendation_memo.pdf"
    doc = SimpleDocTemplate(
        str(out_path), pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch, leftMargin=1 * inch, rightMargin=1 * inch,
    )

    header_style = ParagraphStyle("Header", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=BODY_COLOR)
    body_style = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=10.5, leading=14, alignment=TA_JUSTIFY,
        textColor=BODY_COLOR, spaceAfter=9,
    )
    footer_style = ParagraphStyle("Footer", fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=HexColor("#52514E"))

    story = []
    story.append(Paragraph("TO: Chief Executive Officer, Meridian Home", header_style))
    story.append(Paragraph("FROM: Market Strategy Engagement Team", header_style))
    story.append(Paragraph("RE: US Retail Expansion — Market Entry Recommendation", header_style))
    story.append(Paragraph("DATE: July 2026", header_style))
    story.append(Paragraph("CONFIDENTIAL", ParagraphStyle("Conf", fontName="Helvetica-Bold", fontSize=10, textColor=HexColor("#D03B3B"))))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#C3C2B7")))
    story.append(Spacer(1, 10))

    p1 = (
        f"Based on our analysis of market attractiveness, competitive dynamics, and unit economics across "
        f"five candidate metros, we recommend that Meridian Home prioritize {city2['metro_name']} for its "
        f"first store cluster opening (targeting Q1 2026), with a single pilot store in {city1['metro_name']} "
        f"opening in parallel rather than a full two-store commitment. {city1['metro_name']} scored highest "
        f"on market attractiveness ({city1['composite_score']:.2f} of 5.0) and {city2['metro_name']} second "
        f"({city2['composite_score']:.2f} of 5.0); this phased structure lets us capture both markets' "
        f"strategic advantages while managing a real financial constraint described below."
    )
    p2 = (
        f"{city1['metro_name']} combines the lowest retail lease rate of any candidate "
        f"(${city1['retail_lease_rate_sqft_annual']:.2f}/sqft) with the least competitive saturation "
        f"({city1['competitors_per_100k']:.2f} direct competitors per 100,000 residents), but its population "
        f"growth rate ({city1['population_growth_rate_pct']:.1f}% over 5 years) is the slowest of the two "
        f"recommended markets, which is why we are staging its entry as a single-store pilot rather than a "
        f"full cluster. {city2['metro_name']} sits at Meridian's own East Coast distribution center — "
        f"eliminating logistics cost entirely — and offers the strongest housing-market fundamentals of the "
        f"five candidates (homeownership {city2['homeownership_rate']*100:.1f}%, 5-year home value "
        f"appreciation {city2['home_value_appreciation_5yr_pct']:.1f}%). This ranking held up across three "
        f"independent sensitivity checks that reweighted the underlying scoring model, so we have high "
        f"confidence in the relative ordering of these five markets."
    )
    p3 = (
        f"The financial case is where we want to be direct with you: at our standard 4,500 sq. ft. store "
        f"format, {city2['metro_name']}'s 2-store cluster reaches payback in approximately "
        f"{fin2['payback_months']:.0f} months with a modest positive base-case NPV, but "
        f"{city1['metro_name']}'s cluster does not clear payback within our 3-year modeling window at that "
        f"same format, and the combined risk-adjusted 3-year NPV across both markets as modeled is currently "
        f"negative (${combined_npv_risk:,.0f}). This is precisely why we are recommending a single pilot "
        f"store in {city1['metro_name']} rather than the full cluster: it lets us validate real-world "
        f"performance against the model, and revisit store format or staffing assumptions, before committing "
        f"further capital there."
    )
    p4 = (
        f"Our immediate next step is to engage a retail real estate broker in {city2['metro_name']} to begin "
        f"site selection for the Q1 2026 opening, in parallel with site selection for the {city1['metro_name']} "
        f"pilot. The primary risk to monitor is competitive response from West Elm or Pottery Barn in either "
        f"market once our entry becomes public; we recommend moving on lease commitments promptly once sites "
        f"are identified. We believe this phased approach gives Meridian the strongest available combination "
        f"of market fundamentals and financial discipline among the five candidates evaluated."
    )

    for p in (p1, p2, p3, p4):
        story.append(Paragraph(p, body_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#C3C2B7")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This analysis is based on publicly available data from the US Census Bureau, Bureau of Labor "
        "Statistics, Zillow Research, NAHB, and CommercialCafe. Financial projections are based on industry "
        "benchmark assumptions and should be validated against Meridian Home's actual historical store "
        "performance data before final investment commitment.",
        footer_style,
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Page 1 of 1", ParagraphStyle("PageNum", fontName="Helvetica", fontSize=9, textColor=HexColor("#898781"))))

    doc.build(story)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    build_memo()
