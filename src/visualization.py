"""Publication-Ready Visualizations Module for Nuclear Capital Risk Analysis.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)

Generates 5 publication-grade figures (300 DPI):
- Fig 1: Empirical distribution of construction durations by technology and geography.
- Fig 2: The 2026 Global Nuclear Age Pyramid highlighting the 40+ year cliff (181 GW at stake).
- Fig 3: Capex escalation & IDC compounding curve as a function of construction delays (0 to 10 years).
- Fig 4: LCOE comparison chart: 20-year LTO vs On-time Gen-III+ vs Delayed Gen-III+.
- Fig 5: 1x2 Geospatial Impact Map: 2026 Baseline vs 2035 Without LTO (visualizing the nuclear desert).
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

# =============================================================================
# PUBLICATION STYLING & PALETTE DEFINITIONS
# =============================================================================
# High-contrast, colorblind-safe palette calibrated for energy economics journals
PALETTE = {
    "lto": "#1b9e77",        # Emerald green for life extension
    "gen3": "#2b5c8f",       # Institutional navy for large GW new builds
    "smr": "#d95f02",        # Warm terracotta for modular SMRs
    "cliff": "#d73027",      # Alert crimson for the 40+ year cliff
    "faded": "#bdc3c7",      # Faded grey for retired/turned-off units
    "wacc4": "#4575b4",      # Low subsidized discount rate
    "wacc55": "#74add1",     # Damodaran developed utilities WACC
    "wacc7": "#f46d43",      # Baseline market WACC
    "wacc85": "#d73027",     # Damodaran emerging markets WACC
    "wacc10": "#7f0000",     # High merchant friction WACC
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.titlesize": 12.5,
    "axes.labelsize": 11.0,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "figure.titlesize": 14.0,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "grid.color": "#e5e5e5",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})


# =============================================================================
# FIGURE 1: CONSTRUCTION DURATION DISTRIBUTIONS
# =============================================================================

def plot_figure_1_construction_durations(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 1: Empirical distribution of construction durations by technology and geography.

    Why this visual matters:
    Financial models frequently make unrealistic assumptions of 5-year build times.
    This chart confronts those pitchbook claims with 50 years of empirical data across
    424 operational reactors, proving that delays are the empirical norm.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned fleet dataset.
    output_path : Path
        Output file path for saving PNG.
    """
    logger.info("Generating Figure 1: Empirical Construction Duration Distributions...")

    # Filter for operating reactors with valid, positive lead times
    valid_df = df[
        (df["Construction_Lead_Time_Years"].notna())
        & (df["Construction_Lead_Time_Years"] > 0)
        & (df["Construction_Lead_Time_Years"] <= 35)
    ].copy()

    # Consolidate reactor types into major classes
    type_map = {
        "PWR": "PWR",
        "BWR": "BWR",
        "PHWR": "PHWR (CANDU)",
        "SMR": "SMR / Demo",
    }
    valid_df["Plot_Type"] = valid_df["Reactor_Type_Clean"].map(lambda x: type_map.get(x, "Other"))
    valid_df = valid_df[valid_df["Plot_Type"].isin(["PWR", "BWR", "PHWR (CANDU)", "Other"])]

    # Filter regions with statistically significant sample sizes
    top_regions = ["Northern America", "Eastern Asia", "Eastern Europe", "Western Europe"]
    valid_geo = valid_df[valid_df["Subregion"].isin(top_regions)].copy()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

    # Panel A: By Technology Class
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
    axes[0].axhline(7.0, color="#d95f02", linestyle=":", linewidth=1.5, label="Nominal Budget Schedule (7.0 yrs)")
    axes[0].legend(loc="upper left", framealpha=0.9)

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
    axes[1].set_ylabel("")
    axes[1].grid(True, axis="y")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].axhline(7.0, color="#d95f02", linestyle=":", linewidth=1.5, label="Nominal Budget Schedule (7.0 yrs)")
    axes[1].legend(loc="upper left", framealpha=0.9)

    plt.suptitle(
        "Figure 1: Empirical Distribution of Global Nuclear Construction Lead Times",
        fontweight="bold", y=1.02, fontsize=14,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 1 saved to: {output_path}")


# =============================================================================
# FIGURE 2: 2026 GLOBAL NUCLEAR AGE PYRAMID
# =============================================================================

def plot_figure_2_age_pyramid_cliff(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 2: The 2026 Global Nuclear Age Pyramid highlighting the 40+ year cliff (181 GW).

    Why this visual matters:
    This chart reveals the imminent 'reinvestment wall'. Operating reactors are binned
    into 5-year cohorts. The vertical line at 40 years reveals that 181.0 GW (44.4% of
    the global fleet) is entering mandatory retirement or LTO license renewal.
    """
    logger.info("Generating Figure 2: 2026 Global Nuclear Age Pyramid & 40+ Cliff...")

    op_df = df[df["Clean_Status"] == "operating"].copy()

    # Bin into 5-year age brackets: [0-5), [5-10), ..., [50-55)
    bin_edges = list(range(0, 60, 5))
    bin_labels = [f"{b}-{b+4}" for b in bin_edges[:-1]]
    op_df["Age_Bin"] = pd.cut(op_df["Age_2026"], bins=bin_edges, labels=bin_labels, right=False)

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

    # Vertical threshold line at 40 years
    cliff_idx = bin_labels.index("40-44")
    ax.axvline(cliff_idx - 0.5, color="#b2182b", linestyle="--", linewidth=2.0)

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
        fontsize=10.0,
        fontweight="bold",
        color="#7f0000",
        bbox=dict(boxstyle="square,pad=0.6", facecolor="#fee8c8", edgecolor="#e34a33", linewidth=1.5),
    )

    ax.set_title(
        "Figure 2: The 2026 Global Nuclear Fleet Age Pyramid & Impending 40+ Year Operational Cliff",
        fontweight="bold", pad=16, fontsize=13,
    )
    ax.set_xlabel("Operating Fleet Age Bracket (Years in Operation as of 2026)", labelpad=10, fontweight="bold")
    ax.set_ylabel("Installed Operating Capacity (Gigawatts - GW)", labelpad=10, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2b5c8f", edgecolor="#1a1a1a", label="Operating Fleet (< 40 Years: 226.8 GW)"),
        Patch(facecolor=PALETTE["cliff"], edgecolor="#1a1a1a", label="Cliff Edge Fleet (\u2265 40 Years: 181.0 GW)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", framealpha=0.95)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 2 saved to: {output_path}")


# =============================================================================
# FIGURE 3: CAPEX ESCALATION & IDC COMPOUNDING CURVES
# =============================================================================

def plot_figure_3_idc_compounding_curve(
    df_capex: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 3: Capex escalation & IDC compounding curve over delays across WACC regimes.

    Why this visual matters:
    Demonstrates the non-linear math of debt compounding: interest does not accrue
    linearly. In high WACC environments (7-10%), a multi-year delay doubles the total
    capital cost per kilowatt, destroying utility project economics.
    """
    logger.info("Generating Figure 3: Capex Escalation & IDC Compounding Curve...")

    fig, ax = plt.subplots(figsize=(11, 6.5))

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

    # SMR baseline at 7%
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

    # 20-yr LTO reference line
    lto_cost = df_capex[(df_capex["Technology"] == "20-yr LTO") & (df_capex["Delay_Years"] == 0) & (df_capex["WACC"] == 0.07)]["Capex_Total_kW"].values[0]
    ax.axhline(
        lto_cost,
        color=PALETTE["lto"],
        linestyle="--",
        linewidth=2.5,
        label=f"20-yr LTO Refurbishment (~${lto_cost:,.0f}/kW)",
    )

    ax.axhline(7500, color="#737373", linestyle=":", linewidth=1.2, label="Gen-III+ Overnight Capex ($7,500/kW)")

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


# =============================================================================
# FIGURE 4: LCOE COMPARISON ACROSS STRATEGIES
# =============================================================================

def plot_figure_4_lcoe_comparison(
    df_lcoe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 4: LCOE comparison chart: 20-yr LTO vs On-time Gen-III+ vs Delayed Gen-III+."""
    logger.info("Generating Figure 4: LCOE Comparison LTO vs New-Build...")

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
        ax.bar(
            x + offset,
            lcoe_vals,
            width,
            label=label,
            color=color,
            edgecolor="#1a1a1a",
            linewidth=0.7,
            alpha=0.9,
        )

    ax.axhspan(60, 90, color="#d9d9d9", alpha=0.3, label="Wholesale Baseload Power Price Range ($60–$90/MWh)")

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


# =============================================================================
# FIGURE 5: 1x2 GEOSPATIAL IMPACT VISUAL (2026 BASELINE VS 2035 WITHOUT LTO)
# =============================================================================

def plot_fig5_geospatial_cliff(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Figure 5: 1x2 Geospatial Impact Map - 2026 Baseline vs. 2035 Without LTO.

    Why this 1x2 visual matters for Strategy Consulting & Policy:
    Showing a single map tells only half the story. By presenting a side-by-side
    comparison:
    - Left Panel ("2026 Baseline"): Shows the dense, robust operating nuclear fleet
      delivering zero-carbon baseload across North America, Europe, and Asia.
    - Right Panel ("2035 Without LTO"): Visually 'turns off' the 181 GW of cliff
      reactors, exposing a devastating geographic 'nuclear desert' where mature grids
      lose critical inertia and are forced to burn gas.

    Parameters
    ----------
    df : pd.DataFrame
        Processed nuclear fleet dataset with Latitude, Longitude, and Cliff flags.
    output_path : Path
        Target save path.
    """
    logger.info("Generating Figure 5: 1x2 Geospatial Impact Visual (Baseline vs. 2035 Cliff)...")

    op_df = df[df["Clean_Status"] == "operating"].copy()
    op_df["Latitude"] = pd.to_numeric(op_df["Latitude"], errors="coerce")
    op_df["Longitude"] = pd.to_numeric(op_df["Longitude"], errors="coerce")
    valid_coords = op_df[op_df["Latitude"].notna() & op_df["Longitude"].notna()].copy()

    project_root = Path(__file__).resolve().parent.parent
    world_json_path = project_root / "data" / "raw" / "world.json"

    world_gdf = None
    if world_json_path.exists():
        try:
            import geopandas as gpd
            world_gdf = gpd.read_file(world_json_path)
        except Exception as e:
            logger.warning(f"Geopandas background map loading skipped: {e}")

    fig, axes = plt.subplots(1, 2, figsize=(20, 8.5), sharex=True, sharey=True)

    regular_fleet = valid_coords[~valid_coords["Cliff_Edge_40plus"]]
    cliff_fleet = valid_coords[valid_coords["Cliff_Edge_40plus"]]

    for ax in axes:
        if world_gdf is not None:
            world_gdf.plot(ax=ax, color="#eef2f5", edgecolor="#cbd5e1", linewidth=0.6)
        else:
            ax.set_facecolor("#f8fafc")
        ax.set_xlim(-130, 155)
        ax.set_ylim(-40, 72)
        ax.grid(True, linestyle=":", alpha=0.5, color="#94a3b8")
        ax.set_xlabel("Longitude", labelpad=8, fontweight="bold")

    axes[0].set_ylabel("Latitude", labelpad=8, fontweight="bold")

    # -------------------------------------------------------------------------
    # LEFT PANEL: 2026 Baseline Operating Fleet
    # -------------------------------------------------------------------------
    axes[0].scatter(
        regular_fleet["Longitude"],
        regular_fleet["Latitude"],
        c="#2b5c8f",
        s=35,
        alpha=0.75,
        edgecolors="none",
        label=f"Operating < 40 Years ({len(regular_fleet)} units, {regular_fleet['Capacity_GW'].sum():.1f} GW)",
        zorder=3,
    )
    axes[0].scatter(
        cliff_fleet["Longitude"],
        cliff_fleet["Latitude"],
        c="#d73027",
        s=75,
        alpha=0.85,
        edgecolors="#7f0000",
        linewidths=0.9,
        label=f"At Stake \u2265 40 Years ({len(cliff_fleet)} units, {cliff_fleet['Capacity_GW'].sum():.1f} GW)",
        zorder=4,
    )
    axes[0].set_title(
        "(A) 2026 Baseline: Complete Global Operating Nuclear Fleet (407.8 GW)",
        fontweight="bold", pad=12, fontsize=12.5,
    )
    axes[0].legend(loc="lower left", framealpha=0.95, fontsize=9.5)

    # -------------------------------------------------------------------------
    # RIGHT PANEL: 2035 Without LTO (The Nuclear Desert)
    # -------------------------------------------------------------------------
    # Plot cliff reactors as faded ghost grey 'X' marks to show decommissioned units
    axes[1].scatter(
        cliff_fleet["Longitude"],
        cliff_fleet["Latitude"],
        c="#94a3b8",
        marker="x",
        s=40,
        alpha=0.45,
        label=f"Forced Shutdown Without LTO (-{len(cliff_fleet)} units, -{cliff_fleet['Capacity_GW'].sum():.1f} GW)",
        zorder=3,
    )
    # Plot remaining younger fleet
    axes[1].scatter(
        regular_fleet["Longitude"],
        regular_fleet["Latitude"],
        c="#2b5c8f",
        s=35,
        alpha=0.85,
        edgecolors="none",
        label=f"Remaining Surviving Fleet ({len(regular_fleet)} units, {regular_fleet['Capacity_GW'].sum():.1f} GW)",
        zorder=4,
    )
    axes[1].set_title(
        "(B) 2035 Without LTO: The Nuclear Desert (44.4% of Global Baseload Extinguished)",
        fontweight="bold", pad=12, fontsize=12.5, color="#b91c1c",
    )
    axes[1].legend(loc="lower left", framealpha=0.95, fontsize=9.5)

    # Educational Callout Banner Across Bottom
    avoided_co2 = (cliff_fleet["Capacity_GW"].sum() * 1e6 * 8760 * 0.88 * 400.0) / 1e12
    cars_millions = avoided_co2 * 1e6 / 4.6 / 1e6

    fig.text(
        0.5, -0.02,
        f"DECISION HORIZON (2026–2035): Preserving the 181.0 GW Cliff Fleet via 20-Yr LTO saves $1.14 Trillion vs. New Builds "
        f"and avoids {avoided_co2:.1f} Mt CO2/yr (Equivalent to adding {cars_millions:.0f} Million passenger cars to roads).",
        ha="center", fontsize=10.5, fontweight="bold", color="#1e293b",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fee2e2", edgecolor="#ef4444", linewidth=1.2),
    )

    plt.suptitle(
        "Figure 5: Geospatial Shockwave of the 40-Year Operational Cliff: 2026 Baseline vs. 2035 Without Life Extension",
        fontweight="bold", y=1.02, fontsize=14.5,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Figure 5 saved to: {output_path}")


# =============================================================================
# MASTER ORCHESTRATOR
# =============================================================================

def generate_all_figures(
    data_path: Optional[Union[str, Path]] = None,
    tables_dir: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> None:
    """Orchestrate generation and export of all 5 publication-ready figures."""
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

    logger.info(f"Reading processed fleet data from: {data_path}")
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
    fig5_path = output_dir / "fig5_global_cliff_map.png"

    plot_figure_1_construction_durations(df, fig1_path)
    plot_figure_2_age_pyramid_cliff(df, fig2_path)
    plot_figure_3_idc_compounding_curve(df_capex, fig3_path)
    plot_figure_4_lcoe_comparison(df_lcoe, fig4_path)
    plot_fig5_geospatial_cliff(df, fig5_path)

    logger.info("All 5 publication figures successfully rendered at 300 DPI.")


if __name__ == "__main__":
    generate_all_figures()
