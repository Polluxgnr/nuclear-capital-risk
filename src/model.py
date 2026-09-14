"""Financial Engine for Nuclear Project Finance, Capital Compounding & Fleet Life Extension (LTO).

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)

This module implements the quantitative financial mathematics of nuclear capital projects:
1. S-Curve capital disbursement modeling via continuous Beta distributions.
2. Interest During Construction (IDC) debt compounding under mid-year conventions.
3. Levelized Cost of Electricity (LCOE) decomposition and Capital Recovery Factors (CRF).
4. Carbon Opportunity Cost quantification (avoided CO2 vs. CCGT replacement).
5. Comprehensive sensitivity stress testing across delays and cost-of-capital (WACC) scenarios.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.stats import beta

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# 1. TECHNO-ECONOMIC BENCHMARK SPECIFICATIONS
# =============================================================================

@dataclass(frozen=True)
class TechnologyConfig:
    """Techno-economic parameters defining a nuclear generation asset class.

    Attributes
    ----------
    name : str
        Human-readable identifier of the asset technology.
    capex_overnight_per_kw : float
        Overnight capital cost in USD per kilowatt ($/kW).
        Overnight capex represents the cost of building the plant as if it could
        be constructed instantaneously (overnight), excluding interest and financing.
    nominal_duration_years : float
        Baseline planned construction schedule (T_0) in years.
    lifetime_years : int
        Economic operational horizon (N) over which capital is amortized.
    fixed_om_per_kw_year : float
        Annual fixed operations and maintenance costs ($/kW-year).
    variable_om_per_mwh : float
        Variable operating costs per unit of electricity generated ($/MWh).
    fuel_cost_per_mwh : float
        Nuclear fuel cycle costs including fabrication and waste provisions ($/MWh).
    capacity_factor : float
        Fraction of time the plant generates electricity at nameplate capacity (e.g. 0.88).
    beta_alpha : float
        Shape parameter alpha for the S-curve Beta cumulative distribution.
    beta_beta : float
        Shape parameter beta for the S-curve Beta cumulative distribution.
    """

    name: str
    capex_overnight_per_kw: float
    nominal_duration_years: float
    lifetime_years: int
    fixed_om_per_kw_year: float
    variable_om_per_mwh: float
    fuel_cost_per_mwh: float
    capacity_factor: float
    beta_alpha: float = 2.5
    beta_beta: float = 2.5


# Benchmark Technology Configurations (Calibrated from IEA/NEA 2020 and EPRI 2022)
DEFAULT_TECHNOLOGIES: Dict[str, TechnologyConfig] = {
    # Gen-III+ Large Gigawatt Reactors (EPR-1600, AP1000, APR1400)
    # Overnight benchmark ($7,500/kW) mirrors empirical audited costs from Flamanville 3,
    # Olkiluoto 3, and Vogtle 3&4 before debt compounding.
    "Gen-III+": TechnologyConfig(
        name="Gen-III+ (EPR/AP1000)",
        capex_overnight_per_kw=7500.0,
        nominal_duration_years=7.0,
        lifetime_years=60,
        fixed_om_per_kw_year=110.0,
        variable_om_per_mwh=3.0,
        fuel_cost_per_mwh=7.5,
        capacity_factor=0.88,
    ),
    # Small Modular Reactors (SMR Modular First-of-a-Kind, 300 MWe)
    # Higher overnight cost ($9,000/kW) reflects FOAK factory tooling and initial supply-chain friction.
    "SMR": TechnologyConfig(
        name="SMR (Modular FOAK)",
        capex_overnight_per_kw=9000.0,
        nominal_duration_years=4.0,
        lifetime_years=40,
        fixed_om_per_kw_year=125.0,
        variable_om_per_mwh=3.5,
        fuel_cost_per_mwh=8.5,
        capacity_factor=0.88,
    ),
    # 20-Year Long-Term Operation (LTO / Grand Carénage / Subsequent License Renewal)
    # Overnight benchmark ($1,200/kW) reflects heavy component replacement (steam generators,
    # reactor vessel annealing, digital I&C) calibrated from EDF's €50B Grand Carénage.
    "20-yr LTO": TechnologyConfig(
        name="20-yr LTO (Grand Carénage)",
        capex_overnight_per_kw=1200.0,
        nominal_duration_years=2.0,
        lifetime_years=20,
        fixed_om_per_kw_year=135.0,
        variable_om_per_mwh=3.0,
        fuel_cost_per_mwh=7.0,
        capacity_factor=0.85,  # Slightly lower due to quadrennial regulatory inspections
    ),
}

# Cost of Capital (WACC) Scenarios (Calibrated from Prof. Aswath Damodaran, NYU Stern, 2026)
DEFAULT_WACC_SCENARIOS: Dict[str, float] = {
    "Low (Subsidized/Green Bond)": 0.04,
    "Developed Utilities (Damodaran US/EU)": 0.055,
    "Baseline Market WACC": 0.07,
    "Emerging Market Risk (Damodaran EM)": 0.085,
    "High Capital Friction (Merchant)": 0.10,
}


# =============================================================================
# 2. S-CURVE EXPENDITURE MODELING
# =============================================================================

def calculate_s_curve_weights(
    duration_years: float,
    alpha_param: float = 2.5,
    beta_param: float = 2.5,
) -> np.ndarray:
    """Calculate annual capital expenditure weights using a Beta cumulative distribution.

    Why Beta(2.5, 2.5) is used for Nuclear S-Curves:
    In large-scale civil engineering, capital outlays are never uniformly distributed.
    Instead, they follow a classic 'bell-shaped' disbursement pattern:
    1. Early Years (Slow Start): Site surveying, ground excavation, and licensing
       incur relatively low annual capital spend (approx. 5-10% per year).
    2. Middle Years (Peak Expenditure): Heavy structural concrete pouring, nuclear
       containment building, and nuclear steam supply system (NSSS) installation
       consume the majority of the capital budget (approx. 25-30% per year).
    3. Final Years (Tapering): Cold and hot functional testing, instrumentation and
       control (I&C) integration, and fuel loading taper spending before COD.

    A symmetric Beta distribution with alpha = 2.5 and beta = 2.5 models this
    empirical civil engineering reality with high fidelity.

    Parameters
    ----------
    duration_years : float
        Total construction duration in years (T_0 + delta_t).
    alpha_param : float, default 2.5
        Beta distribution shape parameter alpha.
    beta_param : float, default 2.5
        Beta distribution shape parameter beta.

    Returns
    -------
    np.ndarray
        Array of annual spending fractions strictly summing to 1.0.
    """
    # Round duration up to full integer years for annual cash flow modeling
    t_int = max(1, int(np.ceil(duration_years)))

    # Generate normalized time intervals [0, 1/T, 2/T, ..., 1.0]
    time_steps = np.linspace(0.0, 1.0, t_int + 1)

    # Evaluate the regularized incomplete Beta cumulative distribution function
    cdf_values = beta.cdf(time_steps, alpha_param, beta_param)

    # First difference gives the incremental annual disbursement weights
    annual_weights = np.diff(cdf_values)

    # Normalize to eliminate floating-point rounding errors and ensure exact unit sum
    return annual_weights / np.sum(annual_weights)


# =============================================================================
# 3. IDC DEBT COMPOUNDING ENGINE
# =============================================================================

def calculate_total_capex_and_idc(
    capex_overnight_per_kw: float,
    duration_years: float,
    wacc: float,
    alpha_param: float = 2.5,
    beta_param: float = 2.5,
    mid_year_convention: bool = True,
    delay_overhead_escalation_rate: float = 0.015,
    nominal_duration_years: Optional[float] = None,
) -> Dict[str, float]:
    """Calculate compounded capital expenditure including Interest During Construction (IDC).

    Why Mid-Year Convention (T - t + 0.5) is essential:
    In real-world project finance, engineering contractors draw down debt tranches
    progressively throughout each month of the year, rather than in a lump sum on
    January 1st (start of year) or December 31st (end of year).
    Assuming cash is disbursed continuously over the year means the average dollar
    spent in year t is held for (T - t + 0.5) years before commercial operation.
    Using an end-of-year convention would understate financing costs by half a year of interest.

    Why Delay Overhead Escalation (1.5%/year) is added:
    When a nuclear project is delayed, capital costs escalate not only through interest,
    but also through real carrying costs: maintaining the construction site, retaining
    specialized engineering staff, preservation of stored equipment, and management overhead.

    Mathematical Formula:
    --------------------
    Capex_total = sum_{t=1}^T [ w_t * Capex_esc * (1 + r)^(T - t + 0.5) ]
    IDC = Capex_total - Capex_overnight
    IDC_Multiplier = Capex_total / Capex_overnight

    Parameters
    ----------
    capex_overnight_per_kw : float
        Overnight capital cost per kilowatt in USD ($/kW).
    duration_years : float
        Total duration in years (nominal duration T_0 + delay delta_t).
    wacc : float
        Weighted Average Cost of Capital (discount / borrowing rate).
    alpha_param : float, default 2.5
        S-curve shape parameter alpha.
    beta_param : float, default 2.5
        S-curve shape parameter beta.
    mid_year_convention : bool, default True
        If True, applies mid-year compounding (exponent: T - t + 0.5).
    delay_overhead_escalation_rate : float, default 0.015
        Annual fixed site carrying overhead rate (1.5% per year of delay).
    nominal_duration_years : float, optional
        Nominal planned construction schedule.

    Returns
    -------
    Dict[str, float]
        Dictionary with overnight capex, total capex, IDC, and IDC multiplier.
    """
    # 1. Calculate carrying overhead escalation if project is delayed beyond nominal schedule
    delay_years = max(0.0, duration_years - nominal_duration_years) if nominal_duration_years else 0.0
    escalated_overnight = capex_overnight_per_kw * (1.0 + delay_overhead_escalation_rate * delay_years)

    # 2. Derive annual disbursement fractions from S-curve
    weights = calculate_s_curve_weights(duration_years, alpha_param, beta_param)
    t_int = len(weights)

    # 3. Compound each annual disbursement forward to COD (t = T)
    compounding_factors = np.zeros(t_int)
    for idx in range(t_int):
        t = idx + 1  # 1-indexed construction year
        exponent = (duration_years - t + 0.5) if mid_year_convention else (duration_years - t)
        compounding_factors[idx] = (1.0 + wacc) ** max(0.0, exponent)

    total_capex = np.sum(weights * escalated_overnight * compounding_factors)
    idc = total_capex - capex_overnight_per_kw
    idc_multiplier = total_capex / capex_overnight_per_kw

    return {
        "capex_overnight_nominal": float(capex_overnight_per_kw),
        "capex_overnight_escalated": float(escalated_overnight),
        "duration_years": float(duration_years),
        "delay_years": float(delay_years),
        "wacc": float(wacc),
        "capex_total_per_kw": float(total_capex),
        "idc_per_kw": float(idc),
        "idc_multiplier": float(idc_multiplier),
    }


# =============================================================================
# 4. LEVELIZED COST OF ELECTRICITY (LCOE) ENGINE
# =============================================================================

def calculate_capital_recovery_factor(wacc: float, lifetime_years: int) -> float:
    """Calculate the Capital Recovery Factor (CRF).

    Why CRF is used:
    The Capital Recovery Factor converts a present lump-sum capital expenditure
    into an equivalent stream of equal annual payments over N operational years,
    discounted at the project WACC (annuity formula).

    Formula:
    --------
    CRF = (r * (1 + r)^N) / ((1 + r)^N - 1)

    Parameters
    ----------
    wacc : float
        Discount rate / WACC (r).
    lifetime_years : int
        Operational amortization horizon (N).

    Returns
    -------
    float
        Capital Recovery Factor.
    """
    if wacc <= 0.0:
        return 1.0 / lifetime_years
    r = wacc
    n = lifetime_years
    return (r * (1.0 + r) ** n) / (((1.0 + r) ** n) - 1.0)


def calculate_lcoe(
    capex_total_per_kw: float,
    config: TechnologyConfig,
    wacc: float,
) -> Dict[str, float]:
    """Calculate the Levelized Cost of Electricity (LCOE) in USD per Megawatt-hour ($/MWh).

    Why LCOE is the Gold Standard for Energy Project Finance:
    LCOE represents the constant revenue per unit of electricity that an asset must
    earn over its entire operational lifetime to cover all capital outlays, interest,
    fixed operations, maintenance, and fuel, while achieving an equity return equal to WACC.

    Formulation:
    ------------
    Annual_Generation_MWh_per_kW = 8760 * CF / 1000 * 1000 / 1000 = 8.760 * CF
    LCOE_Capital = (Capex_total * CRF) / (8.760 * CF)
    LCOE_Fixed_OM = Fixed_OM_per_kW_yr / (8.760 * CF)
    LCOE_Variable = Var_OM_per_MWh + Fuel_Cost_per_MWh
    LCOE_Total = LCOE_Capital + LCOE_Fixed_OM + LCOE_Variable

    Parameters
    ----------
    capex_total_per_kw : float
        Total capitalized investment including IDC and carrying escalation ($/kW).
    config : TechnologyConfig
        Techno-economic parameters of the reactor design.
    wacc : float
        Discount rate / WACC.

    Returns
    -------
    Dict[str, float]
        Decomposition of LCOE components in $/MWh.
    """
    crf = calculate_capital_recovery_factor(wacc, config.lifetime_years)
    annual_generation_mwh = 8.760 * config.capacity_factor

    lcoe_capital = (capex_total_per_kw * crf) / annual_generation_mwh
    lcoe_fixed_om = config.fixed_om_per_kw_year / annual_generation_mwh
    lcoe_variable = config.variable_om_per_mwh + config.fuel_cost_per_mwh
    lcoe_total = lcoe_capital + lcoe_fixed_om + lcoe_variable

    return {
        "lcoe_capital": float(lcoe_capital),
        "lcoe_fixed_om": float(lcoe_fixed_om),
        "lcoe_variable_om": float(config.variable_om_per_mwh),
        "lcoe_fuel": float(config.fuel_cost_per_mwh),
        "lcoe_total": float(lcoe_total),
        "crf": float(crf),
        "annual_generation_mwh_per_kw": float(annual_generation_mwh),
    }


def calculate_carbon_opportunity_cost(
    capacity_gw: float = 180.99,
    capacity_factor: float = 0.88,
    ccgt_emissions_g_kwh: float = 400.0,
    car_annual_emissions_metric_tons: float = 4.6,
) -> Dict[str, float]:
    """Calculate the Carbon Opportunity Cost of retiring the 40+ year nuclear fleet.

    The Logic:
    Nuclear power provides dispatchable low-carbon baseload. If 181 GW of aging
    reactors retire without LTO, grid reliability requires replacement with
    dispatchable thermal power. Under modern grid economics, this means Natural Gas
    Combined Cycle (CCGT) emitting 400 grams of CO2 per kWh.

    Formula:
    --------
    Annual_MWh = Capacity_GW * 1e6 kW * 8760 h * CF / 1000 = Capacity_GW * 8.760e6 * CF
    Avoided_CO2_Mt = (Capacity_GW * 1e6 * 8760 * CF * 400 g) / 1e12 g per Mt

    Parameters
    ----------
    capacity_gw : float, default 180.99
        Total capacity of the 40+ year cliff fleet in GW.
    capacity_factor : float, default 0.88
        Baseload capacity factor (88%).
    ccgt_emissions_g_kwh : float, default 400.0
        Lifecycle carbon intensity of natural gas CCGT in gCO2/kWh.
    car_annual_emissions_metric_tons : float, default 4.6
        Average annual CO2 emissions of a passenger vehicle (EPA standard).

    Returns
    -------
    Dict[str, float]
        Dictionary with generation in TWh, avoided CO2 in Mt/yr, and car equivalents in millions.
    """
    generation_kwh = capacity_gw * 1e6 * 8760.0 * capacity_factor
    generation_twh = generation_kwh / 1e9

    avoided_co2_metric_tons = (generation_kwh * ccgt_emissions_g_kwh) / 1e6
    avoided_co2_mt = avoided_co2_metric_tons / 1e6

    cars_millions = (avoided_co2_metric_tons / car_annual_emissions_metric_tons) / 1e6

    return {
        "generation_twh": float(round(generation_twh, 2)),
        "avoided_co2_mt": float(round(avoided_co2_mt, 2)),
        "equivalent_cars_millions": float(round(cars_millions, 1)),
    }


# =============================================================================
# 5. SENSITIVITY MATRIX GENERATION & ORCHESTRATION
# =============================================================================

def run_sensitivity_matrix(
    delays: Optional[List[float]] = None,
    wacc_rates: Optional[List[float]] = None,
    technologies: Optional[Dict[str, TechnologyConfig]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate multi-dimensional sensitivity grids across delays and WACC scenarios.

    Parameters
    ----------
    delays : List[float], optional
        Construction schedule delays in years (0 to 10).
    wacc_rates : List[float], optional
        Cost of capital discount rates (4% to 10%).
    technologies : Dict[str, TechnologyConfig], optional
        Dictionary of technology parameter configurations.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (df_capex, df_lcoe, df_comparative_lto)
    """
    if delays is None:
        delays = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    if wacc_rates is None:
        wacc_rates = [0.04, 0.055, 0.07, 0.085, 0.10]
    if technologies is None:
        technologies = DEFAULT_TECHNOLOGIES

    records_capex: List[Dict[str, Any]] = []
    records_lcoe: List[Dict[str, Any]] = []

    for tech_key, tech in technologies.items():
        for d in delays:
            # LTO programs are executed during refueling outages; maximum realistic delay is 2-3 years
            actual_delay = min(d, 3.0) if tech_key == "20-yr LTO" else d
            total_duration = tech.nominal_duration_years + actual_delay

            for r in wacc_rates:
                res_idc = calculate_total_capex_and_idc(
                    capex_overnight_per_kw=tech.capex_overnight_per_kw,
                    duration_years=total_duration,
                    wacc=r,
                    alpha_param=tech.beta_alpha,
                    beta_param=tech.beta_beta,
                    nominal_duration_years=tech.nominal_duration_years,
                )

                res_lcoe = calculate_lcoe(
                    capex_total_per_kw=res_idc["capex_total_per_kw"],
                    config=tech,
                    wacc=r,
                )

                records_capex.append({
                    "Technology": tech_key,
                    "Delay_Years": d,
                    "Total_Duration_Years": total_duration,
                    "WACC": r,
                    "WACC_Pct": f"{r*100:.1f}%",
                    "Capex_Overnight_kW": tech.capex_overnight_per_kw,
                    "Capex_Total_kW": res_idc["capex_total_per_kw"],
                    "IDC_kW": res_idc["idc_per_kw"],
                    "IDC_Multiplier": res_idc["idc_multiplier"],
                })

                records_lcoe.append({
                    "Technology": tech_key,
                    "Delay_Years": d,
                    "Total_Duration_Years": total_duration,
                    "WACC": r,
                    "WACC_Pct": f"{r*100:.1f}%",
                    "Capex_Total_kW": res_idc["capex_total_per_kw"],
                    "LCOE_Capital": res_lcoe["lcoe_capital"],
                    "LCOE_Fixed_OM": res_lcoe["lcoe_fixed_om"],
                    "LCOE_Var_Fuel": res_lcoe["lcoe_variable_om"] + res_lcoe["lcoe_fuel"],
                    "LCOE_Total": res_lcoe["lcoe_total"],
                })

    df_capex = pd.DataFrame(records_capex)
    df_lcoe = pd.DataFrame(records_lcoe)

    # Build Comparative Arbitrage Table (Gen-III+ vs. LTO)
    comp_records: List[Dict[str, Any]] = []
    for d in delays:
        for r in wacc_rates:
            lto_val = df_lcoe[
                (df_lcoe["Technology"] == "20-yr LTO")
                & (df_lcoe["Delay_Years"] == min(d, 3.0))
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            gen3_val = df_lcoe[
                (df_lcoe["Technology"] == "Gen-III+")
                & (df_lcoe["Delay_Years"] == d)
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            smr_val = df_lcoe[
                (df_lcoe["Technology"] == "SMR")
                & (df_lcoe["Delay_Years"] == d)
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            comp_records.append({
                "Delay_Years": d,
                "WACC": r,
                "WACC_Pct": f"{r*100:.1f}%",
                "LTO_LCOE": lto_val,
                "Gen3_LCOE": gen3_val,
                "SMR_LCOE": smr_val,
                "Gen3_to_LTO_Ratio": gen3_val / lto_val,
                "SMR_to_LTO_Ratio": smr_val / lto_val,
                "Gen3_Premium_USD_MWh": gen3_val - lto_val,
                "SMR_Premium_USD_MWh": smr_val - lto_val,
            })

    df_comparative = pd.DataFrame(comp_records)
    return df_capex, df_lcoe, df_comparative


def run_financial_models(
    output_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, pd.DataFrame]:
    """Execute the complete quantitative financial modeling engine and export tables.

    Parameters
    ----------
    output_dir : Union[str, Path], optional
        Directory where CSV tables will be saved. Defaults to `outputs/tables/`.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of generated DataFrames.
    """
    project_root = Path(__file__).resolve().parent.parent
    if output_dir is None:
        output_dir = project_root / "outputs" / "tables"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Running financial models and generating sensitivity grids...")

    df_capex, df_lcoe, df_comp = run_sensitivity_matrix()

    df_capex.to_csv(output_dir / "sensitivity_capex_kw.csv", index=False)
    df_lcoe.to_csv(output_dir / "sensitivity_lcoe.csv", index=False)
    df_comp.to_csv(output_dir / "sensitivity_comparative_lto.csv", index=False)

    # Pivot summaries for executive viewing
    pivot_capex = df_capex.pivot_table(
        index=["Technology", "Delay_Years"],
        columns="WACC_Pct",
        values="Capex_Total_kW",
    )
    pivot_lcoe = df_lcoe.pivot_table(
        index=["Technology", "Delay_Years"],
        columns="WACC_Pct",
        values="LCOE_Total",
    )

    pivot_capex.to_csv(output_dir / "pivot_capex_by_wacc.csv")
    pivot_lcoe.to_csv(output_dir / "pivot_lcoe_by_wacc.csv")

    logger.info(f"Financial sensitivity matrices successfully saved to: {output_dir}")
    return {
        "capex": df_capex,
        "lcoe": df_lcoe,
        "comparative": df_comp,
        "pivot_capex": pivot_capex,
        "pivot_lcoe": pivot_lcoe,
    }


if __name__ == "__main__":
    run_financial_models()
