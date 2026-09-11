"""Financial Engine for Nuclear Project Finance, Capital Compounding & Fleet Life Extension (LTO).

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.stats import beta

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TechnologyConfig:
    """Techno-economic parameters for a nuclear generation asset."""

    name: str
    capex_overnight_per_kw: float  # USD / kW
    nominal_duration_years: float  # T_0 in years
    lifetime_years: int  # Economic operational horizon N
    fixed_om_per_kw_year: float  # USD / kW-yr
    variable_om_per_mwh: float  # USD / MWh
    fuel_cost_per_mwh: float  # USD / MWh
    capacity_factor: float  # e.g., 0.88 (88%)
    beta_alpha: float = 2.5  # S-curve shape parameter alpha
    beta_beta: float = 2.5  # S-curve shape parameter beta


# Benchmark Technology Configurations (IEA / NEA & Industry standard data)
DEFAULT_TECHNOLOGIES: Dict[str, TechnologyConfig] = {
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
    "20-yr LTO": TechnologyConfig(
        name="20-yr LTO (Grand Carénage)",
        capex_overnight_per_kw=1200.0,
        nominal_duration_years=2.0,
        lifetime_years=20,
        fixed_om_per_kw_year=135.0,
        variable_om_per_mwh=3.0,
        fuel_cost_per_mwh=7.0,
        capacity_factor=0.85,
    ),
}

# Damodaran (NYU Stern) & Scenario WACC Benchmarks
DEFAULT_WACC_SCENARIOS: Dict[str, float] = {
    "Low (Subsidized/Green Bond)": 0.04,
    "Developed Utilities (Damodaran US/EU)": 0.055,
    "Baseline Market (7%)": 0.07,
    "Emerging Market Risk (Damodaran EM)": 0.085,
    "High Capital Friction (10%)": 0.10,
}


def calculate_s_curve_weights(
    duration_years: float,
    alpha_param: float = 2.5,
    beta_param: float = 2.5,
) -> np.ndarray:
    """Calculate annual expenditure weights following a continuous Beta cumulative distribution.

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
        Array of annual spending fractions summing to 1.0.
    """
    t_int = max(1, int(np.ceil(duration_years)))
    time_steps = np.linspace(0, 1, t_int + 1)
    cdf_values = beta.cdf(time_steps, alpha_param, beta_param)
    weights = np.diff(cdf_values)
    # Ensure exact unit sum
    return weights / np.sum(weights)


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

    Formula
    -------
    Capex_total = sum_{t=1}^T C_t * (1 + r)^(T - t + 0.5)
    IDC = Capex_total - Capex_overnight_escalated
    IDC_Multiplier = Capex_total / Capex_overnight

    Parameters
    ----------
    capex_overnight_per_kw : float
        Overnight capital cost per kW (USD).
    duration_years : float
        Total duration in years (nominal + delay).
    wacc : float
        Weighted Average Cost of Capital (discount/interest rate).
    alpha_param : float, default 2.5
        S-curve shape parameter alpha.
    beta_param : float, default 2.5
        S-curve shape parameter beta.
    mid_year_convention : bool, default True
        If True, assumes capital disbursements occur mid-year (exponent: T - t + 0.5).
    delay_overhead_escalation_rate : float, default 0.015
        Annual fixed site carrying cost inflation during delays (1.5% per year of delay).
    nominal_duration_years : float, optional
        Nominal planned construction duration. If provided and duration_years > nominal,
        adds carrying overhead to base overnight capex.

    Returns
    -------
    Dict[str, float]
        Dictionary with overnight capex, total capex, IDC, and IDC multiplier.
    """
    delay_years = max(0.0, duration_years - nominal_duration_years) if nominal_duration_years else 0.0
    escalated_overnight = capex_overnight_per_kw * (1.0 + delay_overhead_escalation_rate * delay_years)

    weights = calculate_s_curve_weights(duration_years, alpha_param, beta_param)
    t_int = len(weights)

    compounding_factors = np.zeros(t_int)
    for idx in range(t_int):
        t = idx + 1  # 1-indexed year
        exponent = (duration_years - t + 0.5) if mid_year_convention else (duration_years - t)
        compounding_factors[idx] = (1.0 + wacc) ** max(0.0, exponent)

    total_capex = np.sum(weights * escalated_overnight * compounding_factors)
    idc = total_capex - capex_overnight_per_kw
    idc_multiplier = total_capex / capex_overnight_per_kw

    return {
        "capex_overnight_nominal": float(capex_overnight_per_kw),
        "capex_overnight_escalated": float(escalated_overnight),
        "duration_years": float(duration_years),
        "wacc": float(wacc),
        "capex_total_per_kw": float(total_capex),
        "idc_per_kw": float(idc),
        "idc_multiplier": float(idc_multiplier),
    }


def calculate_capital_recovery_factor(wacc: float, lifetime_years: int) -> float:
    """Calculate Capital Recovery Factor (CRF).

    CRF = (r * (1 + r)^N) / ((1 + r)^N - 1)
    """
    if wacc <= 0:
        return 1.0 / lifetime_years
    r = wacc
    n = lifetime_years
    return (r * (1.0 + r) ** n) / (((1.0 + r) ** n) - 1.0)


def calculate_lcoe(
    capex_total_per_kw: float,
    config: TechnologyConfig,
    wacc: float,
) -> Dict[str, float]:
    """Calculate Levelized Cost of Electricity (LCOE) in USD/MWh.

    Formulation
    -----------
    Annual_MWh_per_kW = 8760 * CF / 1000 = 8.760 * CF
    Annual_CapCost = capex_total_per_kw * CRF(wacc, N)
    LCOE_cap = Annual_CapCost / (8.760 * CF)
    LCOE_fom = Fixed_OM / (8.760 * CF)
    LCOE_vom = Variable_OM
    LCOE_fuel = Fuel_Cost
    LCOE_total = LCOE_cap + LCOE_fom + LCOE_vom + LCOE_fuel

    Parameters
    ----------
    capex_total_per_kw : float
        Total capital cost including IDC and carrying cost escalation ($/kW).
    config : TechnologyConfig
        Asset operational and cost parameters.
    wacc : float
        Discount rate.

    Returns
    -------
    Dict[str, float]
        Decomposition of LCOE components in $/MWh.
    """
    crf = calculate_capital_recovery_factor(wacc, config.lifetime_years)
    annual_generation_mwh_per_kw = 8.760 * config.capacity_factor

    lcoe_capital = (capex_total_per_kw * crf) / annual_generation_mwh_per_kw
    lcoe_fixed_om = config.fixed_om_per_kw_year / annual_generation_mwh_per_kw
    lcoe_variable_om = config.variable_om_per_mwh
    lcoe_fuel = config.fuel_cost_per_mwh
    lcoe_total = lcoe_capital + lcoe_fixed_om + lcoe_variable_om + lcoe_fuel

    return {
        "lcoe_capital": float(lcoe_capital),
        "lcoe_fixed_om": float(lcoe_fixed_om),
        "lcoe_variable_om": float(lcoe_variable_om),
        "lcoe_fuel": float(lcoe_fuel),
        "lcoe_total": float(lcoe_total),
        "crf": float(crf),
        "annual_generation_mwh_per_kw": float(annual_generation_mwh_per_kw),
    }


def calculate_asset_npv_per_kw(
    lcoe_total: float,
    wholesale_price_per_mwh: float,
    config: TechnologyConfig,
    wacc: float,
) -> float:
    """Calculate Net Present Value (NPV) per kW of capacity under a constant power price.

    NPV_kW = sum_{n=1}^N (Wholesale_Price - LCOE_total) * Annual_MWh_per_kW / (1 + r)^n
    """
    annual_mwh = 8.760 * config.capacity_factor
    annual_margin = (wholesale_price_per_mwh - lcoe_total) * annual_mwh
    discount_factors = np.array([(1.0 + wacc) ** (-n) for n in range(1, config.lifetime_years + 1)])
    return float(annual_margin * np.sum(discount_factors))


def run_sensitivity_matrix(
    delays: Optional[List[float]] = None,
    wacc_rates: Optional[List[float]] = None,
    technologies: Optional[Dict[str, TechnologyConfig]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate comprehensive sensitivity matrices for Capex/kW, LCOE ($/MWh), and LTO Comparative Ratios.

    Parameters
    ----------
    delays : List[float], optional
        Delays in years [0, 1, 2, ..., 10].
    wacc_rates : List[float], optional
        WACC rates [0.04, 0.055, 0.07, 0.085, 0.10].
    technologies : Dict[str, TechnologyConfig], optional
        Technology specifications.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        DataFrames: (df_capex, df_lcoe, df_comparative)
    """
    if delays is None:
        delays = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    if wacc_rates is None:
        wacc_rates = [0.04, 0.055, 0.07, 0.085, 0.10]
    if technologies is None:
        technologies = DEFAULT_TECHNOLOGIES

    records_capex = []
    records_lcoe = []

    for tech_key, tech in technologies.items():
        for d in delays:
            # LTO has minor delays (capped at 2 years in reality, but modeled systematically)
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

                # NPV at $80/MWh base wholesale power price
                npv_80 = calculate_asset_npv_per_kw(res_lcoe["lcoe_total"], 80.0, tech, r)

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
                    "NPV_80_USD_kW": npv_80,
                })

    df_capex = pd.DataFrame(records_capex)
    df_lcoe = pd.DataFrame(records_lcoe)

    # Comparative LTO advantage table
    comparative_records = []
    for d in delays:
        for r in wacc_rates:
            lto_lcoe = df_lcoe[
                (df_lcoe["Technology"] == "20-yr LTO")
                & (df_lcoe["Delay_Years"] == min(d, 3.0))
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            gen3_lcoe = df_lcoe[
                (df_lcoe["Technology"] == "Gen-III+")
                & (df_lcoe["Delay_Years"] == d)
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            smr_lcoe = df_lcoe[
                (df_lcoe["Technology"] == "SMR")
                & (df_lcoe["Delay_Years"] == d)
                & (df_lcoe["WACC"] == r)
            ]["LCOE_Total"].values[0]

            comparative_records.append({
                "Delay_Years": d,
                "WACC": r,
                "WACC_Pct": f"{r*100:.1f}%",
                "LTO_LCOE": lto_lcoe,
                "Gen3_LCOE": gen3_lcoe,
                "SMR_LCOE": smr_lcoe,
                "Gen3_to_LTO_Ratio": gen3_lcoe / lto_lcoe,
                "SMR_to_LTO_Ratio": smr_lcoe / lto_lcoe,
                "Gen3_Premium_USD_MWh": gen3_lcoe - lto_lcoe,
                "SMR_Premium_USD_MWh": smr_lcoe - lto_lcoe,
            })

    df_comparative = pd.DataFrame(comparative_records)
    return df_capex, df_lcoe, df_comparative


def run_financial_models(
    output_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, pd.DataFrame]:
    """Execute all financial models, generate sensitivity tables and export them.

    Parameters
    ----------
    output_dir : Union[str, Path], optional
        Output directory for tables. Defaults to `outputs/tables/`.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Generated sensitivity tables.
    """
    project_root = Path(__file__).resolve().parent.parent
    if output_dir is None:
        output_dir = project_root / "outputs" / "tables"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Executing financial models and computing sensitivity grids...")

    df_capex, df_lcoe, df_comp = run_sensitivity_matrix()

    # Save to CSV
    capex_csv = output_dir / "sensitivity_capex_kw.csv"
    lcoe_csv = output_dir / "sensitivity_lcoe.csv"
    comp_csv = output_dir / "sensitivity_comparative_lto.csv"

    df_capex.to_csv(capex_csv, index=False)
    df_lcoe.to_csv(lcoe_csv, index=False)
    df_comp.to_csv(comp_csv, index=False)

    logger.info(f"Saved sensitivity tables to: {output_dir}")

    # Generate Pivot Summary Tables for Executive Report
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

    logger.info("Financial model sensitivity tables generated successfully.")
    return {
        "capex": df_capex,
        "lcoe": df_lcoe,
        "comparative": df_comp,
        "pivot_capex": pivot_capex,
        "pivot_lcoe": pivot_lcoe,
    }


if __name__ == "__main__":
    run_financial_models()
