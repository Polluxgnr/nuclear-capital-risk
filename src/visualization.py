"""Publication-Ready Visualizations Module for Nuclear Capital Risk Analysis.

Generates 4 high-resolution (300 DPI) figures:
- Fig 1: Empirical distribution of construction durations by reactor type and geography.
- Fig 2: The 2026 Global Nuclear Age Pyramid highlighting the 40+ year cliff (181 GW at stake).
- Fig 3: Capex escalation & IDC compounding curve as a function of construction delays (0 to 10 years).
- Fig 4: LCOE comparison chart: 20-year LTO vs On-time Gen-III+ vs Delayed Gen-III+.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Style parameters for academic journal aesthetics
PALETTE = {
    "lto": "#1b9e77",        # Emerald green
    "gen3": "#2b5c8f",       # Institutional navy
    "smr": "#d95f02",        # Warm terracotta
    "cliff": "#d73027",      # Alert crimson
    "wacc4": "#4575b4",      # Blue
    "wacc55": "#74add1",     # Light blue
    "wacc7": "#f46d43",      # Coral
    "wacc85": "#d73027",     # Deep red
    "wacc10": "#7f0000",     # Dark maroon
    "neutral_dark": "#2b2b2b",
    "neutral_light": "#f8f9fa",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 15,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "grid.color": "#e5e5e5",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})


def plot_figure_1_construction_durations(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 1: Empirical distribution of construction durations by reactor type and geography.

    Panel A: Distribution by Reactor Type (PWR, BWR, PHWR, SMR/Other)
    Panel B: Distribution by Major Geographic Region
    """
    logger.info("Generating Figure 1: Construction Duration Distributions...")

    # Filter for units with valid lead times (operating + completed)
    valid_df = df[
        (df["Construction_Lead_Time_Years"].notna())
        & (df["Construction_Lead_Time_Years"] > 0)
        & (df["Construction_Lead_Time_Years"] <= 35)  # remove extreme frozen outliers > 35y
    ].copy()

    # Consolidate reactor types
    type_map = {
        "PWR": "PWR",
        "BWR": "BWR",
        "PHWR": "PHWR (CANDU)",
        "SMR": "SMR / Demo",
    }
    valid_df["Plot_Type"] = valid_df["Reactor_Type_Clean"].map(lambda x: type_map.get(x, "Other"))
    # Keep top 4 categories
    valid_df = valid_df[valid_df["Plot_Type"].isin(["PWR", "BWR", "PHWR (CANDU)", "Other"])]

    # Filter regions with sufficient sample size
    top_regions = ["Northern America", "Eastern Asia", "Eastern Europe", "Western Europe"]
    valid_geo = valid_df[valid_df["Subregion"].isin(top_regions)].copy()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

    # Panel A: By Reactor Type
    sns.boxplot(
        data=valid_df,
        x="Plot_Type",
        y="Construction_Lead_Time_Years",
        hue="Plot_Type",
        legend=False,
        palette=["#3182bd", "#6baed6", "#9ecae1", "#bdbdbd"],
        ax=axes[0],
        width=0.45,
        boxprops=dict(alpha=0.85),
        showmeans=True,
        meanprops={"marker": "D", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 6},
    )
    sns.stripplot(
        data=valid_df,
        x="Plot_Type",
        y="Construction_Lead_Time_Years",
        color="#252525",
        alpha=0.25,
        jitter=0.2,
        size=4,
        ax=axes[0],
    )

    axes[0].set_title("(A) Construction Duration by Reactor Technology", fontweight="bold", pad=12)
    axes[0].set_xlabel("Reactor Technology Class", labelpad=8)
    axes[0].set_ylabel("Empirical Construction Lead Time (Years)", labelpad=8)
    axes[0].grid(True, axis="y")
    axes[0].axhline(7.0, color="#d95f02", linestyle=":", linewidth=1.5, label="Standard Budget Nominal ($T_0=7$ yrs)")
    axes[0].legend(loc="upper left", framealpha=0.9)

    # Annotate stats on Panel A
    pwr_median = valid_df[valid_df["Plot_Type"] == "PWR"]["Construction_Lead_Time_Years"].median()
    pwr_mean = valid_df[valid_df["Plot_Type"] == "PWR"]["Construction_Lead_Time_Years"].mean()
    axes[0].text(
        0, 28,
        f"PWR Fleet:\nMedian: {pwr_median:.1f}y\nMean: {pwr_mean:.1f}y",
        ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#aaaaaa", alpha=0.9),
    )

    # Panel B: By Geography
    sns.boxplot(
        data=valid_geo,
        x="Subregion",
        y="Construction_Lead_Time_Years",
        hue="Subregion",
        legend=False,
        palette=["#74c476", "#31a354", "#006d2c", "#a1d99b"],
        ax=axes[1],
        width=0.45,
        boxprops=dict(alpha=0.85),
        showmeans=True,
        meanprops={"marker": "D", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 6},
    )
    sns.stripplot(
        data=valid_geo,
        x="Subregion",
        y="Construction_Lead_Time_Years",
        color="#252525",
        alpha=0.25,
        jitter=0.2,
        size=4,
        ax=axes[1],
    )

    axes[1].set_title("(B) Construction Lead Times Across Key Global Geographies", fontweight="bold", pad=12)
    axes[1].set_xlabel("Global Subregion", labelpad=8)
    axes[1].set_ylabel("")  # shared y
    axes[1].grid(True, axis="y")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].axhline(7.0, color="#d95f02", linestyle=":", linewidth=1.5, label="Standard Budget Nominal ($T_0=7$ yrs)")
    axes[1].legend(loc="upper left", framealpha=0.9)

    plt.suptitle(
        "Figure 1: Empirical Distribution of Global Nuclear Construction Lead Times (Historical Fleet)",
        fontweight="bold", y=1.02, fontsize=14,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 1 saved to: {output_path}")


def plot_figure_2_age_pyramid_cliff(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 2: The 2026 Global Nuclear Age Pyramid highlighting the 40+ year cliff (181 GW at stake)."""
    logger.info("Generating Figure 2: 2026 Global Nuclear Age Pyramid & 40+ Cliff...")

    op_df = df[df["Clean_Status"] == "operating"].copy()

    # Bin into age bins of 5 years: [0-5), [5-10), ..., [50-55)
    bin_edges = list(range(0, 60, 5))
    bin_labels = [f"{b}-{b+4}" for b in bin_edges[:-1]]
    op_df["Age_Bin"] = pd.cut(op_df["Age_2026"], bins=bin_edges, labels=bin_labels, right=False)

    # Group by age bin and cliff edge status
    bin_summary = op_df.groupby("Age_Bin", observed=False).agg(
        Capacity_GW=("Capacity_GW", "sum"),
        Unit_Count=("Project Name", "count"),
    ).reset_index()

    bin_summary["Is_Cliff"] = bin_summary["Age_Bin"].apply(
        lambda b: int(str(b).split("-")[0]) >= 40 if pd.notna(b) else False
    )

    fig, ax = plt.subplots(figsize=(12, 6.5))

    colors = [PALETTE["cliff"] if is_cliff else "#2b5c8f" for is_cliff in bin_summary["Is_Cliff"]]

    bars = ax.bar(
        bin_summary["Age_Bin"],
        bin_summary["Capacity_GW"],
        color=colors,
        edgecolor="#1a1a1a",
        linewidth=0.8,
        width=0.65,
        alpha=0.9,
    )

    # Add data labels on top of bars
    for bar, count in zip(bars, bin_summary["Unit_Count"]):
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{height:.1f} GW\n({count} units)",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=8.5,
                fontweight="bold",
            )

    # Vertical threshold line separating < 40 and >= 40
    # Bin '40-44' is index 8
    cliff_idx = bin_labels.index("40-44")
    ax.axvline(cliff_idx - 0.5, color="#b2182b", linestyle="--", linewidth=2.0)

    # Annotation callout box for 181 GW cliff
    cliff_capacity = op_df[op_df["Cliff_Edge_40plus"]]["Capacity_GW"].sum()
    cliff_units = op_df[op_df["Cliff_Edge_40plus"]]["Project Name"].count()
    total_capacity = op_df["Capacity_GW"].sum()
    cliff_share = (cliff_capacity / total_capacity) * 100

    ax.annotate(
        f"THE 40-YEAR 'CLIFF EDGE'\n"
        f"Capacity at Stake: {cliff_capacity:.1f} GW ({cliff_share:.1f}% of Global Fleet)\n"
        f"Affected Reactors: {cliff_units} operational units\n"
        f"Decision Horizon: LTO / Life Extension vs Decommissioning",
        xy=(cliff_idx + 1.2, 75),
        xytext=(cliff_idx + 0.2, 85),
        arrowprops=dict(facecolor="#b2182b", shrink=0.08, width=1.5, headwidth=8),
        fontsize=10.5,
        fontweight="bold",
        color="#7f0000",
        bbox=dict(boxstyle="square,pad=0.6", facecolor="#fee8c8", edgecolor="#e34a33", linewidth=1.5),
    )

    # Styling
    ax.set_title(
        "Figure 2: The 2026 Global Nuclear Fleet Age Pyramid & Impending 40+ Year Operational Cliff",
        fontweight="bold", pad=16, fontsize=13,
    )
    ax.set_xlabel("Operating Fleet Age Bracket (Years in Operation as of 2026)", labelpad=10, fontweight="bold")
    ax.set_ylabel("Installed Operating Capacity (Gigawatts - GW)", labelpad=10, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    # Custom Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2b5c8f", edgecolor="#1a1a1a", label="Operating Fleet (< 40 Years: 226.8 GW)"),
        Patch(facecolor=PALETTE["cliff"], edgecolor="#1a1a1a", label="Cliff Edge Fleet (≥ 40 Years: 181.0 GW)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", framealpha=0.95)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 2 saved to: {output_path}")


def plot_figure_3_idc_compounding_curve(
    df_capex: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 3: Capex escalation & IDC compounding curve as a function of construction delays (0 to 10 years)."""
    logger.info("Generating Figure 3: Capex Escalation & IDC Compounding Curve...")

    fig, ax = plt.subplots(figsize=(11, 6.5))

    # Plot Gen-III+ under various WACCs
    gen3_data = df_capex[df_capex["Technology"] == "Gen-III+"].copy()

    wacc_styles = [
        (0.04, "4.0% (Subsidized / Green Bond)", "#4575b4", "--", 1.8),
        (0.055, "5.5% (Damodaran Developed Utilities)", "#2b5c8f", "-", 2.5),
        (0.07, "7.0% (Baseline Market WACC)", "#f46d43", "-", 2.5),
        (0.085, "8.5% (Damodaran Emerging Markets)", "#d73027", "-.", 2.2),
        (0.10, "10.0% (High Capital Friction / Merchant)", "#7f0000", "-", 3.0),
    ]

    for w, label, color, lstyle, lwidth in wacc_styles:
        sub = gen3_data[gen3_data["WACC"] == w].sort_values("Delay_Years")
        ax.plot(
            sub["Delay_Years"],
            sub["Capex_Total_kW"],
            label=f"Gen-III+ @ WACC {label}",
            color=color,
            linestyle=lstyle,
            linewidth=lwidth,
            marker="o",
            markersize=5,
        )

    # Plot SMR at 7% and 10%
    smr_7 = df_capex[(df_capex["Technology"] == "SMR") & (df_capex["WACC"] == 0.07)].sort_values("Delay_Years")
    ax.plot(
        smr_7["Delay_Years"],
        smr_7["Capex_Total_kW"],
        label="SMR FOAK @ WACC 7.0% ($T_0=4$ yrs)",
        color=PALETTE["smr"],
        linestyle=":",
        linewidth=2.2,
        marker="s",
        markersize=5,
    )

    # Plot 20-yr LTO as reference flat line
    lto_cost = df_capex[(df_capex["Technology"] == "20-yr LTO") & (df_capex["Delay_Years"] == 0) & (df_capex["WACC"] == 0.07)]["Capex_Total_kW"].values[0]
    ax.axhline(
        lto_cost,
        color=PALETTE["lto"],
        linestyle="--",
        linewidth=2.5,
        label=f"20-yr LTO Refurbishment (~${lto_cost:,.0f}/kW)",
    )

    # Highlight Overnight Benchmark
    ax.axhline(7500, color="#737373", linestyle=":", linewidth=1.2, label="Gen-III+ Overnight Capex ($7,500/kW)")

    # Annotation of IDC escalation
    cost_ontime_10 = gen3_data[(gen3_data["WACC"] == 0.10) & (gen3_data["Delay_Years"] == 0)]["Capex_Total_kW"].values[0]
    cost_delayed_10 = gen3_data[(gen3_data["WACC"] == 0.10) & (gen3_data["Delay_Years"] == 7)]["Capex_Total_kW"].values[0]
    ax.annotate(
        f"+7 Yr Delay @ 10% WACC:\nCapex surges from ${cost_ontime_10:,.0f}/kW to ${cost_delayed_10:,.0f}/kW\n(+{((cost_delayed_10/cost_ontime_10)-1)*100:.0f}% Capital Erosion)",
        xy=(7, cost_delayed_10),
        xytext=(3.5, cost_delayed_10 + 2000),
        arrowprops=dict(facecolor="#7f0000", shrink=0.08, width=1.5, headwidth=8),
        fontsize=9.5,
        fontweight="bold",
        color="#7f0000",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee8c8", edgecolor="#b2182b", alpha=0.95),
    )

    ax.set_title(
        "Figure 3: Capital Expenditure Escalation & IDC Compounding as a Function of Construction Delays",
        fontweight="bold", pad=15, fontsize=13,
    )
    ax.set_xlabel("Construction Delay Beyond Nominal Schedule (Years)", labelpad=10, fontweight="bold")
    ax.set_ylabel("Total Capitalized Expenditure (USD / kW including IDC)", labelpad=10, fontweight="bold")
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.set_ylim(0, 26000)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(loc="upper left", framealpha=0.95, fontsize=8.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 3 saved to: {output_path}")


def plot_figure_4_lcoe_comparison(
    df_lcoe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 4: LCOE comparison chart: 20-year LTO vs On-time Gen-III+ vs Delayed Gen-III+ across WACC scenarios."""
    logger.info("Generating Figure 4: LCOE Comparison LTO vs New-Build...")

    # Filter specific representative investment cases
    wacc_list = [0.04, 0.055, 0.07, 0.085, 0.10]
    wacc_labels = ["4.0%\n(Green)", "5.5%\n(Damodaran Dev)", "7.0%\n(Baseline)", "8.5%\n(Damodaran EM)", "10.0%\n(Merchant)"]

    cases = [
        ("20-yr LTO (Grand Carénage)", "20-yr LTO", 0, PALETTE["lto"]),
        ("Gen-III+ On-Time (7y COD)", "Gen-III+", 0, "#2b5c8f"),
        ("Gen-III+ Delayed +3y (10y COD)", "Gen-III+", 3, "#f46d43"),
        ("Gen-III+ Delayed +7y (14y COD)", "Gen-III+", 7, "#d73027"),
        ("SMR Modular FOAK (4y COD)", "SMR", 0, PALETTE["smr"]),
    ]

    x = np.arange(len(wacc_list))
    width = 0.16

    fig, ax = plt.subplots(figsize=(13, 7))

    for i, (label, tech, delay, color) in enumerate(cases):
        lcoe_vals = []
        for w in wacc_list:
            val = df_lcoe[
                (df_lcoe["Technology"] == tech)
                & (df_lcoe["Delay_Years"] == delay)
                & (df_lcoe["WACC"] == w)
            ]["LCOE_Total"].values[0]
            lcoe_vals.append(val)

        offset = (i - 2) * width
        rects = ax.bar(
            x + offset,
            lcoe_vals,
            width,
            label=label,
            color=color,
            edgecolor="#1a1a1a",
            linewidth=0.7,
            alpha=0.9,
        )

    # Wholesale Power Price benchmark bands ($60 - $90 / MWh)
    ax.axhspan(60, 90, color="#d9d9d9", alpha=0.3, label="Wholesale Baseload Power Price Range ($60–$90/MWh)")

    # Annotation of the LTO resilience
    lto_4 = df_lcoe[(df_lcoe["Technology"] == "20-yr LTO") & (df_lcoe["Delay_Years"] == 0) & (df_lcoe["WACC"] == 0.04)]["LCOE_Total"].values[0]
    lto_10 = df_lcoe[(df_lcoe["Technology"] == "20-yr LTO") & (df_lcoe["Delay_Years"] == 0) & (df_lcoe["WACC"] == 0.10)]["LCOE_Total"].values[0]
    gen3_del_10 = df_lcoe[(df_lcoe["Technology"] == "Gen-III+") & (df_lcoe["Delay_Years"] == 7) & (df_lcoe["WACC"] == 0.10)]["LCOE_Total"].values[0]

    ax.annotate(
        f"LTO Resilience:\nLCOE stays tightly bounded (${lto_4:.0f} - ${lto_10:.0f}/MWh)\neven as WACC surges to 10%",
        xy=(0, lto_4),
        xytext=(0.2, 160),
        arrowprops=dict(facecolor=PALETTE["lto"], shrink=0.08, width=1.5, headwidth=7),
        fontsize=9,
        fontweight="bold",
        color="#006d2c",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#edf8fb", edgecolor="#2ca25f", alpha=0.95),
    )

    ax.annotate(
        f"Delayed New-Build Fragility:\nLCOE balloons to ${gen3_del_10:.0f}/MWh\n(4.8x higher than LTO)",
        xy=(4 + 2 * width, gen3_del_10),
        xytext=(2.6, 230),
        arrowprops=dict(facecolor="#d73027", shrink=0.08, width=1.5, headwidth=7),
        fontsize=9,
        fontweight="bold",
        color="#7f0000",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee8c8", edgecolor="#d73027", alpha=0.95),
    )

    ax.set_title(
        "Figure 4: Levelized Cost of Electricity (LCOE) Across Nuclear Strategies Under Rising Cost-of-Capital",
        fontweight="bold", pad=15, fontsize=13,
    )
    ax.set_xlabel("Cost of Capital Environment (WACC Scenarios)", labelpad=10, fontweight="bold")
    ax.set_ylabel("Levelized Cost of Electricity (USD / MWh)", labelpad=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(wacc_labels, fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.set_ylim(0, 270)
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)
    ax.legend(loc="upper left", framealpha=0.95, fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 4 saved to: {output_path}")


def generate_all_figures(
    data_path: Optional[Union[str, Path]] = None,
    tables_dir: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> None:
    """Orchestrate generation and export of all 4 publication-ready figures."""
    project_root = Path(__file__).resolve().parent.parent

    if data_path is None:
        data_path = project_root / "data" / "processed" / "clean_nuclear_fleet.csv"
    else:
        data_path = Path(data_path)

    if tables_dir is None:
        tables_dir = project_root / "outputs" / "tables"
    else:
        tables_dir = Path(tables_dir)

    if output_dir is None:
        output_dir = project_root / "outputs" / "figures"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {data_path}. Run data_processing first.")

    logger.info(f"Reading processed data from: {data_path}")
    df = pd.read_csv(data_path)

    capex_path = tables_dir / "sensitivity_capex_kw.csv"
    lcoe_path = tables_dir / "sensitivity_lcoe.csv"

    if not capex_path.exists() or not lcoe_path.exists():
        raise FileNotFoundError(f"Sensitivity tables not found in {tables_dir}. Run model.py first.")

    df_capex = pd.read_csv(capex_path)
    df_lcoe = pd.read_csv(lcoe_path)

    fig1_path = output_dir / "fig1_construction_durations.png"
    fig2_path = output_dir / "fig2_nuclear_age_pyramid_cliff.png"
    fig3_path = output_dir / "fig3_idc_compounding_escalation.png"
    fig4_path = output_dir / "fig4_lcoe_comparison_lto_vs_newbuild.png"

    plot_figure_1_construction_durations(df, fig1_path)
    plot_figure_2_age_pyramid_cliff(df, fig2_path)
    plot_figure_3_idc_compounding_curve(df_capex, fig3_path)
    plot_figure_4_lcoe_comparison(df_lcoe, fig4_path)

    logger.info("All 4 publication figures generated successfully at 300 DPI.")


if __name__ == "__main__":
    generate_all_figures()
