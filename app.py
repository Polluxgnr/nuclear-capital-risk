"""Interactive Streamlit Dashboard: Nuclear Capital Risk & Fleet LTO.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import streamlit as st

# Import quantitative financial functions and technology configurations
from src.model import (
    DEFAULT_TECHNOLOGIES,
    calculate_lcoe,
    calculate_total_capex_and_idc,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nuclear Capital Risk & Fleet LTO",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_nuclear_fleet.csv"
FIG2_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig2_nuclear_age_pyramid_cliff.png"
FIG5_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig5_global_cliff_map.png"


@st.cache_data
def load_fleet_data() -> pd.DataFrame:
    """Load cleaned nuclear fleet dataset."""
    if not DATA_PATH.exists():
        st.error(f"Dataset not found at {DATA_PATH}. Run `python main.py` first.")
        st.stop()
    return pd.read_csv(DATA_PATH)


df = load_fleet_data()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.shields.io/badge/ESSEC%20%2F%20AIDAMS-Climate%20Risks%202026-navy.svg", use_container_width=True)
st.sidebar.title("Simulation Controls")
st.sidebar.markdown(
    "Adjust the macroeconomic cost of capital (WACC) and greenfield construction delays "
    "to observe Interest During Construction (IDC) debt compounding and LCOE divergence."
)

wacc_pct = st.sidebar.slider(
    "Weighted Average Cost of Capital (WACC %)",
    min_value=4.0,
    max_value=12.0,
    value=7.0,
    step=0.5,
    help="Discount rate and debt cost. Damodaran developed utilities: 5.5%, emerging markets: 8.5–10%.",
)
wacc = wacc_pct / 100.0

delay_years = st.sidebar.slider(
    "Gen-III+ Construction Delay (Years beyond nominal 7y)",
    min_value=0,
    max_value=10,
    value=3,
    step=1,
    help="Schedule slippage beyond nominal 7-year budget schedule.",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Project Finance Parameters:**\n"
    "- **Gen-III+ Overnight:** $7,500 / kW\n"
    "- **20-Yr LTO Overnight:** $1,200 / kW\n"
    "- **SMR FOAK Overnight:** $9,000 / kW\n"
    "- **Baseload CF:** 88% (Gen-III+) / 85% (LTO)\n"
    "- **Avoided CO2 Benchmark:** 400 gCO2 / kWh (CCGT Gas)"
)

# -----------------------------------------------------------------------------
# 1. KEY TOP-LEVEL METRICS
# -----------------------------------------------------------------------------
st.title("⚛️ Nuclear Project Finance & Fleet Life Extension (LTO)")
st.caption(
    "Master's Research Defense Dashboard | ESSEC Business School / AIDAMS (Fall 2026) | "
    "Pollux Gronier, Eliott Beghin, Saty Viard Laroque, Neel Sabarwhal"
)

op_fleet = df[df["Clean_Status"] == "operating"].copy()
total_gw = op_fleet["Capacity_GW"].sum()
total_units = len(op_fleet)

cliff_fleet = op_fleet[op_fleet["Cliff_Edge_40plus"]].copy()
cliff_gw = cliff_fleet["Capacity_GW"].sum()
cliff_units = len(cliff_fleet)
cliff_pct = (cliff_gw / total_gw) * 100.0

# Annual Avoided CO2 emissions in Million metric tons
avoided_co2_mt = (cliff_gw * 1e6 * 8760 * 0.88 * 400.0) / 1e12

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Global Operating Fleet",
        value=f"{total_gw:.1f} GW",
        delta=f"{total_units} Active Reactors",
    )

with col2:
    st.metric(
        label="Operational Cliff (≥ 40 Years)",
        value=f"{cliff_gw:.1f} GW",
        delta=f"{cliff_pct:.1f}% of Global Fleet ({cliff_units} units)",
        delta_color="inverse",
    )

with col3:
    st.metric(
        label="Annual Avoided CO2 (Cliff Fleet)",
        value=f"{avoided_co2_mt:.1f} Mt CO2 / yr",
        delta="vs. CCGT Natural Gas Replacement",
    )

with col4:
    st.metric(
        label="LTO Capital Arbitrage",
        value="$1.14 Trillion",
        delta="Savings vs. Greenfield Rebuild",
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. DYNAMIC FINANCIAL MODEL & LCOE COMPARISON
# -----------------------------------------------------------------------------
st.subheader("📊 Dynamic LCOE Comparison: 20-Yr LTO vs. Delayed Gen-III+ New Build")

# Model Calculations for Current Slider Values
gen3_cfg = DEFAULT_TECHNOLOGIES["Gen-III+"]
lto_cfg = DEFAULT_TECHNOLOGIES["20-yr LTO"]
smr_cfg = DEFAULT_TECHNOLOGIES["SMR"]

# Gen-III+ at selected delay and WACC
total_duration_gen3 = gen3_cfg.nominal_duration_years + delay_years
gen3_idc = calculate_total_capex_and_idc(
    capex_overnight_per_kw=gen3_cfg.capex_overnight_per_kw,
    duration_years=total_duration_gen3,
    wacc=wacc,
    alpha_param=gen3_cfg.beta_alpha,
    beta_param=gen3_cfg.beta_beta,
    nominal_duration_years=gen3_cfg.nominal_duration_years,
)
gen3_lcoe = calculate_lcoe(gen3_idc["capex_total_per_kw"], gen3_cfg, wacc)

# LTO at selected WACC (on-time 2-year planned outage)
lto_idc = calculate_total_capex_and_idc(
    capex_overnight_per_kw=lto_cfg.capex_overnight_per_kw,
    duration_years=lto_cfg.nominal_duration_years,
    wacc=wacc,
    alpha_param=lto_cfg.beta_alpha,
    beta_param=lto_cfg.beta_beta,
    nominal_duration_years=lto_cfg.nominal_duration_years,
)
lto_lcoe = calculate_lcoe(lto_idc["capex_total_per_kw"], lto_cfg, wacc)

# SMR FOAK (4-year on-time)
smr_idc = calculate_total_capex_and_idc(
    capex_overnight_per_kw=smr_cfg.capex_overnight_per_kw,
    duration_years=smr_cfg.nominal_duration_years,
    wacc=wacc,
    alpha_param=smr_cfg.beta_alpha,
    beta_param=smr_cfg.beta_beta,
    nominal_duration_years=smr_cfg.nominal_duration_years,
)
smr_lcoe = calculate_lcoe(smr_idc["capex_total_per_kw"], smr_cfg, wacc)

cost_ratio = gen3_lcoe["lcoe_total"] / lto_lcoe["lcoe_total"]
cost_spread = gen3_lcoe["lcoe_total"] - lto_lcoe["lcoe_total"]

col_chart, col_details = st.columns([2, 1])

with col_chart:
    categories = [
        "20-Yr LTO\n(Grand Carénage)",
        f"Gen-III+ New Build\n(+{delay_years}y Delay, {total_duration_gen3:.0f}y COD)",
        "SMR FOAK\n(4y COD)",
    ]
    lcoe_totals = [
        lto_lcoe["lcoe_total"],
        gen3_lcoe["lcoe_total"],
        smr_lcoe["lcoe_total"],
    ]
    colors = ["#1b9e77", "#d73027" if delay_years >= 3 else "#2b5c8f", "#d95f02"]

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    bars = ax.bar(categories, lcoe_totals, color=colors, width=0.5, edgecolor="#1a1a1a", linewidth=0.8)

    # Wholesale power price benchmark band ($60 - $90 / MWh)
    ax.axhspan(60, 90, color="#cccccc", alpha=0.35, label="Wholesale Power Price Band ($60–$90/MWh)")

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 3,
            f"${h:.1f}/MWh",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10.5,
        )

    ax.set_ylabel("Levelized Cost of Electricity ($/MWh)", fontweight="bold")
    ax.set_ylim(0, max(lcoe_totals) * 1.25)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.6)
    ax.set_title(
        f"Real-Time LCOE Simulation at WACC = {wacc_pct:.1f}%",
        fontweight="bold",
        pad=10,
    )
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)

with col_details:
    st.markdown("#### Scenario Breakdown")
    st.markdown(
        f"- **Cost Ratio (Gen-III+ / LTO):** <span style='font-size:1.3em; font-weight:bold; color:#d73027;'>{cost_ratio:.2f}×</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"- **LCOE Premium:** **+${cost_spread:.1f} / MWh**"
    )
    st.markdown(
        f"- **Gen-III+ Total Capitalized Capex:** **${gen3_idc['capex_total_per_kw']:,.0f} / kW** "
        f"(Overnight: ${gen3_cfg.capex_overnight_per_kw:,.0f} + IDC: ${gen3_idc['idc_per_kw']:,.0f})"
    )
    st.markdown(
        f"- **20-Yr LTO Total Capitalized Capex:** **${lto_idc['capex_total_per_kw']:,.0f} / kW** "
        f"(IDC: ${lto_idc['idc_per_kw']:,.0f})"
    )
    st.info(
        "💡 **Key Insight:** Because 85% of an LTO asset is already paid for, its generation cost remains "
        "rock-solid under $50/MWh even when interest rates climb to 12%."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. STATIC PUBLICATION FIGURES
# -----------------------------------------------------------------------------
st.subheader("🗺️ Global Asset Evidence & Operational Vintage")

tab1, tab2 = st.tabs(["The 2026 Nuclear Age Pyramid (Figure 2)", "Global Geospatial Cliff Map (Figure 5)"])

with tab1:
    if FIG2_PATH.exists():
        st.image(
            str(FIG2_PATH),
            caption="Figure 2: The 2026 Global Nuclear Age Pyramid highlighting the 181.0 GW (44.4%) operational cliff edge.",
            use_container_width=True,
        )
    else:
        st.warning("Figure 2 not found. Run `python main.py` to generate it.")

with tab2:
    if FIG5_PATH.exists():
        st.image(
            str(FIG5_PATH),
            caption="Figure 5: Global Geospatial Map of Operating Fleet (< 40y in blue, ≥ 40y Cliff in red bubbles).",
            use_container_width=True,
        )
    else:
        st.warning("Figure 5 not found. Run `python main.py` to generate it.")
