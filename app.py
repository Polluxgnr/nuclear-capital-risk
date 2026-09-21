"""Interactive Streamlit Defense Dashboard: Nuclear Capital Risk & Fleet LTO.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)
Authors: Pollux Gronier, Eliott Beghin, Saty Viard Laroque, Neel Sabarwhal

This interactive dashboard serves as the live defense demonstrator for our master's thesis.
It is decomposed into modular functions:
- load_data(): Cached ingestion of cleaned global fleet assets.
- sidebar_ui(): Parameter sliders for macroeconomic WACC and construction delay,
  along with an educational "Assumptions & Methodology" expander.
- main_dashboard(): Dynamic KPI metrics cards, an interactive Plotly LCOE simulator,
  and side-by-side asset vintage and geospatial evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Quantitative financial modeling functions
from src.model import (
    DEFAULT_TECHNOLOGIES,
    calculate_lcoe,
    calculate_total_capex_and_idc,
)

# -----------------------------------------------------------------------------
# 1. APPLICATION SETUP & PATH RESOLUTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nuclear Capital Risk & Fleet LTO Simulator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_nuclear_fleet.csv"
FIG2_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig2_nuclear_age_pyramid_cliff.png"
FIG5_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig5_global_cliff_map.png"
FIG6_PATH = PROJECT_ROOT / "outputs" / "figures" / "fig6_decarbonization_pathways.png"


# -----------------------------------------------------------------------------
# 2. DATA INGESTION & CACHING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the cleaned global nuclear fleet dataset.

    Returns
    -------
    pd.DataFrame
        Asset-level nuclear fleet dataframe with 1,825 tracked units.
    """
    if not DATA_PATH.exists():
        st.error(f"Clean dataset not found at: {DATA_PATH}. Please run `python main.py` first.")
        st.stop()
    return pd.read_csv(DATA_PATH)


# -----------------------------------------------------------------------------
# 3. SIDEBAR INTERACTION & METHODOLOGY EXPLAINER
# -----------------------------------------------------------------------------
def sidebar_ui() -> Tuple[float, int]:
    """Render the sidebar simulation controls and methodology expanders.

    Returns
    -------
    Tuple[float, int]
        (WACC as float, Construction delay in years as int).
    """
    st.sidebar.image(
        "https://img.shields.io/badge/ESSEC%20%2F%20AIDAMS-Climate%20Risks%202026-navy.svg",
        use_container_width=True,
    )
    st.sidebar.title("🎛️ Simulation Parameters")
    st.sidebar.markdown(
        "Explore how **Interest During Construction (IDC)** compounds as macroeconomic "
        "discount rates (WACC) and schedule delays escalate."
    )

    # WACC Slider (4.0% to 12.0%, step 0.5%)
    wacc_pct = st.sidebar.slider(
        "Weighted Average Cost of Capital (WACC %)",
        min_value=4.0,
        max_value=12.0,
        value=7.0,
        step=0.5,
        help="Project discount rate. Developed regulated utilities ~5.5%, emerging markets ~8.5-10%.",
    )
    wacc = wacc_pct / 100.0

    # Construction Delay Slider (0 to 10 years, step 1 year)
    delay_years = st.sidebar.slider(
        "Gen-III+ Schedule Delay (Years beyond nominal 7y)",
        min_value=0,
        max_value=10,
        value=3,
        step=1,
        help="Construction lead time slippage beyond the standard 7-year turnkey schedule.",
    )

    st.sidebar.markdown("---")

    # Educational Methodology Expander for Jury Inspection
    with st.sidebar.expander("📚 Methodology & Key Assumptions", expanded=False):
        st.markdown(
            """
            **1. Capital Expenditure Benchmarks:**
            * **Gen-III+ ($7,500/kW):** Calibrated from audited empirical outlays of Flamanville 3, Olkiluoto 3, and Vogtle 3&4.
            * **20-Yr LTO ($1,200/kW):** Calibrated from EDF's €50B *Grand Carénage* program across 56 reactors and US NRC subsequent license renewals.
            * **SMR FOAK ($9,000/kW):** Captures First-of-a-Kind factory tooling and licensing friction.
            
            **2. Cost of Capital (WACC):**
            * Sourced from Prof. Aswath Damodaran (NYU Stern, 2026) industry tables for *Green & Power Utilities*:
              - Subsidized / Green Bond: 4.0%
              - Developed Utilities (US/EU): 5.5%
              - Baseline Market: 7.0%
              - Emerging Markets: 8.5%–10.0%
            
            **3. Carbon Opportunity Cost Logic:**
            * When 181 GW of baseload nuclear retires, it cannot be replaced solely by non-synchronous wind/solar without unbuilt seasonal storage.
            * Grid reliability mandates dispatchable replacement by Natural Gas Combined Cycle (CCGT) emitting 400 gCO2/kWh at an 88% capacity factor.
            
            **4. S-Curve & Mid-Year Compounding:**
            * S-curve uses $\\text{Beta}(2.5, 2.5)$ to reflect slow site prep, peak structural civil works, and tapering pre-commissioning.
            * Mid-year convention $(T - t + 0.5)$ reflects continuous monthly debt drawdowns.
            """
        )

    # Educational Limitations Expander for Jury Inspection
    with st.sidebar.expander("⚠️ Study & Data Limitations", expanded=False):
        st.markdown(
            """
            **1. Data Reporting & Historical Approximation:**
            * The GEM Tracker relies on reported utility filings. Older units built in the 1970s often report commercial operation by year or year-month, which our pipeline standardizes to mid-year/mid-month.

            **2. Generic Overnight Capex Benchmarks:**
            * Standard capital outlays ($1,200/kW for LTO, $7,500/kW for Gen-III+) represent industry averages and do not capture unit-specific metallurgy, unique reactor containment designs, or site-specific supply chain bottlenecks.

            **3. 100% CCGT Replacement Simplification:**
            * We model complete replacement by natural gas CCGT as an empirical proxy for firm dispatchable baseload. While intermittent renewables + battery storage will capture part of this generation, lack of multi-day seasonal storage forces real-world grids to burn natural gas to maintain grid inertia.

            **4. Regulatory & Licensing Feasibility:**
            * 20-Year LTO requires decennial safety reviews (*visites décennales* in France, Subsequent License Renewals in the US) approved by nuclear safety authorities (ASN, NRC, ONR). Financial feasibility does not bypass regulatory safety mandates.

            **5. High-Level Nuclear Waste & Fuel Cycle:**
            * Extending reactor lifetimes expands the inventory of spent nuclear fuel requiring long-term deep geological repositories (e.g., Cigéo in France, Onkalo in Finland).
            """
        )

    st.sidebar.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
        "ESSEC Business School / AIDAMS — Fall 2026"
        "</div>",
        unsafe_allow_html=True,
    )
    return wacc, delay_years


# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD UI & METRICS ENGINE
# -----------------------------------------------------------------------------
def main_dashboard(df: pd.DataFrame, wacc: float, delay_years: int) -> None:
    """Render main interactive dashboard, KPI metrics, dynamic chart, and figures.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned fleet dataframe.
    wacc : float
        Selected WACC discount rate.
    delay_years : int
        Selected construction delay in years.
    """
    st.title("⚛️ Nuclear Project Finance & Fleet Life Extension (LTO)")
    st.markdown(
        "**Sustainability Strategy & Clean Energy Transition Advisory** | ESSEC Business School / AIDAMS | "
        "Pollux Gronier, Eliott Beghin, Saty Viard Laroque, Neel Sabarwhal"
    )

    # -------------------------------------------------------------------------
    # A. TOP-LEVEL KPI METRICS CARDS
    # -------------------------------------------------------------------------
    op_fleet = df[df["Clean_Status"] == "operating"].copy()
    total_gw = op_fleet["Capacity_GW"].sum()
    total_units = len(op_fleet)

    cliff_fleet = op_fleet[op_fleet["Cliff_Edge_40plus"]].copy()
    cliff_gw = cliff_fleet["Capacity_GW"].sum()
    cliff_units = len(cliff_fleet)
    cliff_pct = (cliff_gw / total_gw) * 100.0 if total_gw > 0 else 0.0

    # Avoided CO2 calculation vs. CCGT replacement
    annual_generation_kwh = cliff_gw * 1e6 * 8760.0 * 0.88
    avoided_co2_mt = (annual_generation_kwh * 400.0) / 1e12
    equivalent_cars_millions = (avoided_co2_mt * 1e6 / 4.6) / 1e6

    # Model Calculations for Current Slider Settings
    gen3_cfg = DEFAULT_TECHNOLOGIES["Gen-III+"]
    lto_cfg = DEFAULT_TECHNOLOGIES["20-yr LTO"]
    smr_cfg = DEFAULT_TECHNOLOGIES["SMR"]

    total_duration_gen3 = gen3_cfg.nominal_duration_years + delay_years

    gen3_res = calculate_total_capex_and_idc(
        capex_overnight_per_kw=gen3_cfg.capex_overnight_per_kw,
        duration_years=total_duration_gen3,
        wacc=wacc,
        alpha_param=gen3_cfg.beta_alpha,
        beta_param=gen3_cfg.beta_beta,
        nominal_duration_years=gen3_cfg.nominal_duration_years,
    )
    gen3_lcoe = calculate_lcoe(gen3_res["capex_total_per_kw"], gen3_cfg, wacc)

    lto_res = calculate_total_capex_and_idc(
        capex_overnight_per_kw=lto_cfg.capex_overnight_per_kw,
        duration_years=lto_cfg.nominal_duration_years,
        wacc=wacc,
        alpha_param=lto_cfg.beta_alpha,
        beta_param=lto_cfg.beta_beta,
        nominal_duration_years=lto_cfg.nominal_duration_years,
    )
    lto_lcoe = calculate_lcoe(lto_res["capex_total_per_kw"], lto_cfg, wacc)

    # Reference on-time baseline at 5.5% WACC for dynamic delta
    gen3_base_res = calculate_total_capex_and_idc(7500.0, 7.0, 0.055, nominal_duration_years=7.0)
    gen3_base_lcoe = calculate_lcoe(gen3_base_res["capex_total_per_kw"], gen3_cfg, 0.055)
    lcoe_delta = gen3_lcoe["lcoe_total"] - gen3_base_lcoe["lcoe_total"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Global Operating Fleet",
            value=f"{total_gw:.1f} GW",
            delta=f"{total_units} Active Reactors",
        )
    with col2:
        st.metric(
            label="40+ Year Operational Cliff",
            value=f"{cliff_gw:.1f} GW",
            delta=f"{cliff_pct:.1f}% of Fleet ({cliff_units} units)",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="Avoided Carbon Cliff",
            value=f"{avoided_co2_mt:.1f} Mt CO2/yr",
            delta=f"≈ {equivalent_cars_millions:.1f}M Cars Added",
            delta_color="off",
        )
    with col4:
        st.metric(
            label="Gen-III+ LCOE (Current Simulation)",
            value=f"${gen3_lcoe['lcoe_total']:.1f} / MWh",
            delta=f"+${lcoe_delta:.1f}/MWh vs. On-Time Developed",
            delta_color="inverse",
        )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # B. DYNAMIC PLOTLY INTERACTIVE LCOE CHART
    # -------------------------------------------------------------------------
    st.subheader("📊 Dynamic LCOE Comparison: 20-Yr LTO vs. Delayed Gen-III+ vs. SMR")

    smr_res = calculate_total_capex_and_idc(
        capex_overnight_per_kw=smr_cfg.capex_overnight_per_kw,
        duration_years=smr_cfg.nominal_duration_years,
        wacc=wacc,
        alpha_param=smr_cfg.beta_alpha,
        beta_param=smr_cfg.beta_beta,
        nominal_duration_years=smr_cfg.nominal_duration_years,
    )
    smr_lcoe = calculate_lcoe(smr_res["capex_total_per_kw"], smr_cfg, wacc)

    col_chart, col_stats = st.columns([2, 1])

    with col_chart:
        # Build interactive stacked bar chart using Plotly
        tech_names = [
            "20-Yr LTO<br>(Grand Carénage)",
            f"Gen-III+ New Build<br>(+{delay_years}y Delay, {total_duration_gen3:.0f}y COD)",
            "SMR Modular FOAK<br>(4y COD)",
        ]

        capital_costs = [lto_lcoe["lcoe_capital"], gen3_lcoe["lcoe_capital"], smr_lcoe["lcoe_capital"]]
        fixed_om_costs = [lto_lcoe["lcoe_fixed_om"], gen3_lcoe["lcoe_fixed_om"], smr_lcoe["lcoe_fixed_om"]]
        var_fuel_costs = [
            lto_lcoe["lcoe_variable_om"] + lto_lcoe["lcoe_fuel"],
            gen3_lcoe["lcoe_variable_om"] + gen3_lcoe["lcoe_fuel"],
            smr_lcoe["lcoe_variable_om"] + smr_lcoe["lcoe_fuel"],
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Capital Recovery (Capex + IDC)", x=tech_names, y=capital_costs, marker_color="#2b5c8f"))
        fig.add_trace(go.Bar(name="Fixed Operations & Maintenance", x=tech_names, y=fixed_om_costs, marker_color="#41b6c4"))
        fig.add_trace(go.Bar(name="Variable O&M + Fuel Cycle", x=tech_names, y=var_fuel_costs, marker_color="#a1dab4"))

        # Add Wholesale Baseload Power Price reference band ($60 - $90 / MWh)
        fig.add_hrect(
            y0=60, y1=90,
            fillcolor="#e2e8f0", opacity=0.5,
            layer="below", line_width=0,
            annotation_text="Wholesale Baseload Power Price Band ($60–$90/MWh)",
            annotation_position="top left",
        )

        fig.update_layout(
            barmode="stack",
            title=f"Levelized Cost of Electricity at WACC = {wacc*100:.1f}% ($/MWh)",
            yaxis=dict(title="Levelized Cost of Electricity ($/MWh)", tickprefix="$", gridcolor="#e2e8f0"),
            xaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_stats:
        ratio = gen3_lcoe["lcoe_total"] / lto_lcoe["lcoe_total"]
        spread = gen3_lcoe["lcoe_total"] - lto_lcoe["lcoe_total"]

        st.markdown("#### Scenario Arbitrage")
        st.markdown(
            f"**Cost Ratio (Gen-III+ / LTO):** <span style='font-size:1.4em; font-weight:bold; color:#dc2626;'>{ratio:.2f}×</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**LCOE Cost Penalty:** **+${spread:.1f} / MWh**")
        st.markdown(f"**Gen-III+ Compounded Capex:** **${gen3_res['capex_total_per_kw']:,.0f} / kW**")
        st.markdown(f"**Gen-III+ Accrued IDC:** **${gen3_res['idc_per_kw']:,.0f} / kW** (+{((gen3_res['idc_multiplier'])-1)*100:.1f}%)")
        st.markdown(f"**20-Yr LTO Compounded Capex:** **${lto_res['capex_total_per_kw']:,.0f} / kW** (IDC: ${lto_res['idc_per_kw']:,.0f}/kW)")

        st.info(
            f"💡 **Executive Takeaway:** Even with a {delay_years}-year delay at {wacc*100:.1f}% WACC, "
            f"20-Yr LTO generates power at **${lto_lcoe['lcoe_total']:.1f}/MWh**, capturing massive economic rent "
            f"below wholesale market prices."
        )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # C. STATIC PUBLICATION ASSETS & GEOSPATIAL IMPACT
    # -------------------------------------------------------------------------
    st.subheader("🗺️ Global Empirical Assets & 2035 Impact Shockwave")

    tab1, tab2, tab3 = st.tabs([
        "Strategic Decarbonization Pathways (Figure 6)",
        "1x2 Geospatial Impact Map (Figure 5)",
        "The 2026 Global Nuclear Age Pyramid (Figure 2)",
    ])

    with tab1:
        if FIG6_PATH.exists():
            st.image(
                str(FIG6_PATH),
                caption="Figure 6: Sustainability Advisory Matrix: Capital Outlay vs. Cumulative Decarbonization Lag (2026–2045).",
                use_container_width=True,
            )
        else:
            st.warning("Figure 6 not found. Run `python main.py` to render it.")

    with tab2:
        if FIG5_PATH.exists():
            st.image(
                str(FIG5_PATH),
                caption="Figure 5: Geospatial shockwave of the 40-year cliff: 2026 Baseline vs. 2035 Without LTO (The Nuclear Desert).",
                use_container_width=True,
            )
        else:
            st.warning("Figure 5 not found. Run `python main.py` to render it.")

    with tab3:
        if FIG2_PATH.exists():
            st.image(
                str(FIG2_PATH),
                caption="Figure 2: The 2026 Global Nuclear Age Pyramid highlighting the 181.0 GW (44.4%) operational cliff edge.",
                use_container_width=True,
            )
        else:
            st.warning("Figure 2 not found. Run `python main.py` to render it.")


# -----------------------------------------------------------------------------
# 5. ENTRY POINT
# -----------------------------------------------------------------------------
def main() -> None:
    """Execute the dashboard application."""
    fleet_df = load_data()
    selected_wacc, selected_delay = sidebar_ui()
    main_dashboard(fleet_df, selected_wacc, selected_delay)


if __name__ == "__main__":
    main()
