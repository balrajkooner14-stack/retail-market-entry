"""Generates the 7 analysis charts used in the PowerPoint deck (and reused
as static images in the Next.js dashboard). All charts saved as high-res
PNGs to outputs/charts/.

Color usage follows two different encodings depending on what the chart is
showing (see the project's dataviz guidance):
  - Radar / dimension-breakdown / heatmap charts show CITY IDENTITY (which
    of the 5 cities is which) -> a fixed-order 5-hue categorical palette,
    validated for CVD-safety (see palette below).
  - Composite-score / financial charts show RECOMMENDED STATUS (this city
    made the cut or didn't) -> a green "good" status shade for the 2
    recommended cities and a neutral grey for the other 3, which is a
    status distinction, not an identity one.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data_collection" / "raw"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]

# Fixed-order 5-hue categorical palette (validated CVD-safe, see dataviz skill)
CITY_COLORS = {
    "Nashville, TN": "#2a78d6",  # blue
    "Austin, TX": "#1baf7a",  # aqua
    "Denver, CO": "#eda100",  # yellow
    "Charlotte, NC": "#008300",  # green
    "Indianapolis, IN": "#4a3aa7",  # violet
}

STATUS_GOOD = "#0ca30c"
STATUS_GOOD_DARK = "#006300"
STATUS_MUTED = "#898781"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRIDLINE = "#e1e0d9"

DIMENSION_LABELS = [
    "Population\n& Growth",
    "Income &\nFurnishing Spend",
    "Homeownership\n& Housing",
    "Competitive\nSaturation",
    "Retail Lease\nCost",
    "Labor\nCost",
    "Logistics\nProximity",
]
DIMENSION_COLS = [f"dim{i}_score" for i in range(1, 8)]


def _load_scores() -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / "city_scores.csv")


def _status_color(recommended: bool, rank: int) -> str:
    if not recommended:
        return STATUS_MUTED
    return STATUS_GOOD_DARK if rank == 1 else STATUS_GOOD


def chart_radar(df: pd.DataFrame):
    angles = np.linspace(0, 2 * np.pi, len(DIMENSION_COLS), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    for _, row in df.iterrows():
        values = row[DIMENSION_COLS].tolist()
        values += values[:1]
        color = CITY_COLORS[row["metro_name"]]
        ax.plot(angles, values, color=color, linewidth=2, label=row["metro_name"])
        ax.fill(angles, values, color=color, alpha=0.06)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(DIMENSION_LABELS, fontsize=11, color=TEXT_PRIMARY)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=9, color=TEXT_SECONDARY)
    ax.spines["polar"].set_color(GRIDLINE)
    ax.grid(color=GRIDLINE)
    ax.set_title(
        "Market Attractiveness Scorecard — 5 Candidate Markets",
        fontsize=15, color=TEXT_PRIMARY, pad=30, fontweight="bold",
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=10, frameon=False)
    fig.savefig(CHARTS_DIR / "radar_chart.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_composite_scores(df: pd.DataFrame):
    df = df.sort_values("composite_score", ascending=True)
    colors = [_status_color(r["recommended"], r["rank"]) for _, r in df.iterrows()]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    bars = ax.barh(df["metro_name"], df["composite_score"], color=colors, height=0.6)
    for bar, score in zip(bars, df["composite_score"]):
        ax.text(
            bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}", va="center", fontsize=12, color=TEXT_PRIMARY, fontweight="bold",
        )
    ax.set_xlim(0, 5.5)
    ax.set_xlabel("Composite Weighted Score (max 5.0)", fontsize=11, color=TEXT_SECONDARY)
    ax.set_title(
        "Composite Market Score — Meridian Home Expansion Analysis",
        fontsize=15, color=TEXT_PRIMARY, fontweight="bold", pad=15,
    )
    ax.tick_params(axis="y", labelsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.savefig(CHARTS_DIR / "composite_scores.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_dimension_breakdown(df: pd.DataFrame):
    df = df.sort_values("rank")
    x = np.arange(len(DIMENSION_COLS))
    n_cities = len(df)
    width = 0.8 / n_cities

    fig, ax = plt.subplots(figsize=(15, 6.5))
    for i, (_, row) in enumerate(df.iterrows()):
        offset = (i - n_cities / 2) * width + width / 2
        color = _status_color(row["recommended"], row["rank"])
        ax.bar(x + offset, row[DIMENSION_COLS].tolist(), width=width, label=row["metro_name"], color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(DIMENSION_LABELS, fontsize=10)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Score (1-5)", fontsize=11, color=TEXT_SECONDARY)
    ax.set_title("Scoring Breakdown by Dimension", fontsize=15, color=TEXT_PRIMARY, fontweight="bold", pad=15)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=5, frameon=False, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.savefig(CHARTS_DIR / "dimension_breakdown.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_competitive_heatmap(df: pd.DataFrame):
    brands = ["crate_barrel", "west_elm", "pottery_barn", "rh_stores", "williams_sonoma"]
    brand_labels = ["Crate & Barrel", "West Elm", "Pottery Barn", "RH", "Williams-Sonoma"]
    df = df.sort_values("rank")

    matrix = df[brands].values
    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Sequential-style shading (0 -> light, higher counts -> darker), but
    # capped as discrete bands so it doubles as a simple status read: 0 (light),
    # 1-2 (mid), 3+ (dark) -- consistent with the "green good / grey neutral"
    # idiom used elsewhere: here darker = more competitive saturation (worse).
    def cell_color(v):
        if v == 0:
            return "#eaf7ec"
        if v <= 2:
            return "#f5d78e"
        return "#e34948"

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=cell_color(v), edgecolor="white", linewidth=2))
            ax.text(j + 0.5, i + 0.5, str(int(v)), ha="center", va="center", fontsize=13, color=TEXT_PRIMARY)

    ax.set_xlim(0, len(brands))
    ax.set_ylim(0, len(df))
    ax.set_xticks(np.arange(len(brands)) + 0.5)
    ax.set_xticklabels(brand_labels, fontsize=10)
    ax.set_yticks(np.arange(len(df)) + 0.5)
    ax.set_yticklabels(df["metro_name"], fontsize=11)
    ax.invert_yaxis()
    ax.set_title(
        "Competitive Saturation — Store Counts by Brand and Metro",
        fontsize=14, color=TEXT_PRIMARY, fontweight="bold", pad=15,
    )
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.savefig(CHARTS_DIR / "competitive_heatmap.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_financial_waterfall(financial_results: dict):
    cities = list(financial_results.keys())
    fig, axes = plt.subplots(1, len(cities), figsize=(13, 6), sharey=True)
    if len(cities) == 1:
        axes = [axes]

    for ax, city in zip(axes, cities):
        pl = pd.DataFrame(financial_results[city]["cluster_pl"])
        years = pl["year"].tolist()
        ebitda = pl["ebitda"].tolist()
        colors = [STATUS_GOOD if v >= 0 else "#e34948" for v in ebitda]
        bars = ax.bar([f"Year {y}" for y in years], ebitda, color=colors, width=0.55)
        for bar, v in zip(bars, ebitda):
            va = "bottom" if v >= 0 else "top"
            offset = 15000 if v >= 0 else -15000
            ax.text(
                bar.get_x() + bar.get_width() / 2, v + offset, f"${v:,.0f}",
                ha="center", va=va, fontsize=10, color=TEXT_PRIMARY,
            )
        ax.axhline(0, color=TEXT_SECONDARY, linewidth=1)
        ax.set_title(city, fontsize=13, color=TEXT_PRIMARY, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRIDLINE, linewidth=0.8)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("2-Store Cluster EBITDA ($)", fontsize=11, color=TEXT_SECONDARY)
    fig.suptitle(
        f"3-Year Financial Projection — {' vs '.join(cities)} Store Clusters",
        fontsize=15, color=TEXT_PRIMARY, fontweight="bold", y=1.02,
    )
    fig.savefig(CHARTS_DIR / "financial_waterfall.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_npv_comparison(financial_results: dict):
    cities = list(financial_results.keys())
    npv_base = [financial_results[c]["npv_base"] for c in cities]
    npv_risk = [financial_results[c]["npv_risk_adjusted"] for c in cities]

    x = np.arange(len(cities))
    width = 0.32

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x - width / 2, npv_base, width, label="NPV (Base, 10%)", color=STATUS_GOOD)
    ax.bar(x + width / 2, npv_risk, width, label="NPV (Risk-Adjusted, 12%)", color="#4a3aa7")
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(cities, fontsize=12)
    ax.set_ylabel("3-Year NPV ($)", fontsize=11, color=TEXT_SECONDARY)
    ax.set_title(
        "NPV Comparison — Recommended Markets (2-Store Cluster)",
        fontsize=14, color=TEXT_PRIMARY, fontweight="bold", pad=15,
    )
    ax.legend(frameon=False, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.savefig(CHARTS_DIR / "npv_comparison.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_sensitivity_table():
    sensitivity = pd.read_csv(RAW_DIR / "sensitivity_results.csv", index_col=0)
    display_df = sensitivity.drop(columns=["stability"]) if "stability" in sensitivity.columns else sensitivity
    display_df = display_df.sort_values("baseline")

    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.axis("off")
    col_labels = ["Metro"] + [c.replace("_", " ").title() for c in display_df.columns]
    cell_text = [[metro] + [str(int(v)) for v in row] for metro, row in display_df.iterrows()]

    table = ax.table(cellText=cell_text, colLabels=col_labels, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRIDLINE)
        if row == 0:
            cell.set_facecolor("#f0efec")
            cell.set_text_props(fontweight="bold", color=TEXT_PRIMARY)
        elif col == 0:
            cell.set_text_props(fontweight="bold", color=TEXT_PRIMARY)

    ax.set_title(
        "Sensitivity Analysis — City Rank by Weight Profile",
        fontsize=13, color=TEXT_PRIMARY, fontweight="bold", pad=10,
    )
    fig.savefig(CHARTS_DIR / "sensitivity_table.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_all_charts():
    df = _load_scores()
    financial_results = json.loads((RAW_DIR / "financial_results.json").read_text())

    chart_radar(df)
    print("  1/7 radar_chart.png")
    chart_composite_scores(df)
    print("  2/7 composite_scores.png")
    chart_dimension_breakdown(df)
    print("  3/7 dimension_breakdown.png")
    chart_competitive_heatmap(df)
    print("  4/7 competitive_heatmap.png")
    chart_financial_waterfall(financial_results)
    print("  5/7 financial_waterfall.png")
    chart_npv_comparison(financial_results)
    print("  6/7 npv_comparison.png")
    chart_sensitivity_table()
    print("  7/7 sensitivity_table.png")


if __name__ == "__main__":
    generate_all_charts()
    n = len(list(CHARTS_DIR.glob("*.png")))
    print(f"\nGenerated {n} charts to {CHARTS_DIR}")
