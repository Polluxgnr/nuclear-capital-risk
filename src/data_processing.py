"""Data Processing and Fleet Ingestion Module for Global Nuclear Power Tracker.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)

This module handles the ingestion, cleaning, feature engineering, and statistical
validation of global nuclear power assets from the Global Energy Monitor (GEM) tracker.
It is decomposed into single-purpose functions with extensive educational comments
designed for clear academic understanding.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_flexible_date(val: Any) -> pd.Timestamp:
    """Parse irregular date strings (YYYY, YYYY-MM, YYYY-MM-DD) into pandas Timestamp.

    Why this helper is needed:
    Real-world historical energy datasets from international registries often mix
    precise dates ('1974-06-24') with approximate dates ('1974-06') or year-only
    estimates ('1974' or '1974.0') for older units or announced projects.
    To avoid discarding hundreds of valid reactors, we standardize year-only
    entries to mid-year (July 1st) and year-month entries to mid-month (15th).

    Parameters
    ----------
    val : Any
        Date representation (string, float, int, Timestamp, or NaN).

    Returns
    -------
    pd.Timestamp
        Standardized pandas Timestamp or pd.NaT if invalid or missing.
    """
    if pd.isna(val):
        return pd.NaT

    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return pd.to_datetime(val)

    s = str(val).strip()
    if not s or s.lower() in ("nan", "nat", "none", ""):
        return pd.NaT

    # Strip floating point string representations like '1984.0'
    if s.endswith(".0"):
        s = s[:-2]

    # Case 1: Year-only (e.g., '1984') -> set to mid-year (July 1st)
    if len(s) == 4 and s.isdigit():
        return pd.to_datetime(f"{s}-07-01", errors="coerce")

    # Case 2: Year-Month (e.g., '1984-06') -> set to mid-month (15th)
    if len(s) == 7 and s[:4].isdigit() and s[4] == "-":
        return pd.to_datetime(f"{s}-15", errors="coerce")

    # Case 3: Standard ISO date ('YYYY-MM-DD') or standard parseable string
    return pd.to_datetime(s, errors="coerce")


def clean_status_category(raw_status: Any) -> str:
    """Standardize raw operational status strings into clean analytical categories.

    Why this helper is needed:
    The raw dataset contains nuanced operational labels like 'cancelled - inferred 4 y'
    or 'shelved - inferred 2 y'. For rigorous statistical aggregation, we collapse
    these into 7 mutually exclusive industry-standard categories.

    Parameters
    ----------
    raw_status : Any
        Raw status string from the GEM tracker.

    Returns
    -------
    str
        Standardized status string ('operating', 'construction', 'cancelled',
        'pre-construction', 'announced', 'retired', 'shelved', or 'unknown').
    """
    if pd.isna(raw_status):
        return "unknown"

    s = str(raw_status).strip().lower()
    if "operating" in s:
        return "operating"
    if "construction" in s and "pre" not in s:
        return "construction"
    if "pre-construction" in s or "preconstruction" in s:
        return "pre-construction"
    if "announced" in s:
        return "announced"
    if "cancelled" in s:
        return "cancelled"
    if "retired" in s:
        return "retired"
    if "shelved" in s or "mothballed" in s:
        return "shelved"
    return s


def clean_reactor_type(raw_type: Any) -> str:
    """Standardize diverse reactor technologies into standard engineering classes.

    Why this helper is needed:
    Nuclear engineering uses various cooling and moderation mechanisms.
    Pressurized Water Reactors (PWR) represent the vast majority of Western fleets,
    while Boiling Water Reactors (BWR) and Heavy Water (CANDU/PHWR) follow distinct
    refurbishment and component replacement cycles. Small Modular Reactors (SMR)
    represent the emerging Gen-IV/modular paradigm.

    Parameters
    ----------
    raw_type : Any
        Raw descriptive reactor technology string.

    Returns
    -------
    str
        Clean classification code ('PWR', 'BWR', 'SMR', 'PHWR', 'FBR',
        'HTGR', 'LWGR', 'GCR', or 'Other').
    """
    if pd.isna(raw_type):
        return "Unknown"

    s = str(raw_type).strip().lower()
    if "small modular" in s or "microreactor" in s:
        return "SMR"
    if "pressurized water" in s:
        return "PWR"
    if "boiling water" in s:
        return "BWR"
    if "heavy water" in s:
        return "PHWR"
    if "fast breeder" in s or "liquid-metal" in s:
        return "FBR"
    if "high temperature gas" in s:
        return "HTGR"
    if "graphite" in s or "rbmk" in s:
        return "LWGR"
    if "gas-cooled" in s:
        return "GCR"
    return "Other"


def calculate_construction_lead_times(df: pd.DataFrame) -> pd.Series:
    """Calculate empirical construction duration in fractional years.

    Why this helper is needed:
    Construction lead time (COD - Construction Start Date) is the primary driver
    of Interest During Construction (IDC). We calculate duration in exact days
    divided by 365.25 to account for leap years, with a fallback to year-level
    differences when day-level timestamps are unavailable.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing cleaned date and year columns.

    Returns
    -------
    pd.Series
        Lead time in fractional years (NaN for uncompleted or unbuilt units).
    """
    # 1. High-precision calculation based on exact parsed dates
    exact_lead_time = (df["COD_Clean"] - df["Const_Start_Date_Clean"]).dt.days / 365.25

    # 2. Fallback to integer year difference where exact dates are missing
    fallback_mask = exact_lead_time.isna() & df["COD_Year"].notna() & df["Const_Start_Year"].notna()
    lead_time = exact_lead_time.copy()
    lead_time.loc[fallback_mask] = df.loc[fallback_mask, "COD_Year"] - df.loc[fallback_mask, "Const_Start_Year"]

    # 3. Filter out anomalous negative durations (data entry errors in tracker)
    lead_time.loc[lead_time < 0] = np.nan
    return lead_time


def calculate_fleet_age_and_cliff(
    df: pd.DataFrame,
    reference_year: int = 2026,
    cliff_threshold_years: int = 40,
) -> Tuple[pd.Series, pd.Series]:
    """Compute operating reactor age and identify the 40+ year 'Cliff Edge' cohort.

    Why the 40-year threshold matters in Nuclear Project Finance:
    In the United States, France, and Japan, initial commercial licenses were granted
    for 40 years based on financial debt amortization horizons and antitrust rules,
    rather than physical metallurgic limitations.
    When a unit reaches 40 years, utilities face a mandatory binary choice:
    1. Decommission the plant (incurring $500M+ in retirement costs and losing baseload cash flow), OR
    2. Execute Long-Term Operation (LTO / Grand Carénage) to extend life to 60 or 80 years.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    reference_year : int, default 2026
        Evaluation baseline year.
    cliff_threshold_years : int, default 40
        Design lifetime limit flagging units at risk of mandatory shutdown.

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        (Age_2026, Cliff_Edge_40plus boolean series).
    """
    age_series = pd.Series(index=df.index, dtype=float)
    operating_mask = df["Clean_Status"] == "operating"

    # Age is strictly calculated for actively operating units
    age_series.loc[operating_mask] = reference_year - df.loc[operating_mask, "Start_Year_Clean"]

    # Binary cliff edge flag: operating and age >= 40
    cliff_edge_flag = operating_mask & (age_series >= cliff_threshold_years)
    return age_series, cliff_edge_flag


def calculate_avoided_carbon_emissions(
    cliff_capacity_gw: float,
    ccgt_emission_factor_g_kwh: float = 400.0,
    capacity_factor: float = 0.88,
    car_annual_emissions_metric_tons: float = 4.6,
) -> Dict[str, float]:
    """Calculate the Carbon Opportunity Cost of retiring the 40+ year nuclear fleet.

    The Climate Risk Logic:
    Nuclear power provides dispatchable, weather-independent, spinning baseload.
    If 181 GW of nuclear capacity is retired, power grid operators cannot replace
    it solely with non-dispatchable solar or wind without massive unbuilt storage.
    Empirically (as observed in Germany post-Atomausstieg and California post-San Onofre),
    retiring nuclear baseload is directly replaced by dispatchable Natural Gas
    Combined Cycle (CCGT) turbines.

    Parameters
    ----------
    cliff_capacity_gw : float
        Total capacity of operating reactors >= 40 years old (approx. 181 GW).
    ccgt_emission_factor_g_kwh : float, default 400.0
        Lifecycle carbon intensity of modern CCGT natural gas in gCO2 / kWh.
    capacity_factor : float, default 0.88
        Nuclear baseload annual availability factor (88%).
    car_annual_emissions_metric_tons : float, default 4.6
        Average annual CO2 emissions of a typical passenger gasoline vehicle (EPA benchmark).

    Returns
    -------
    Dict[str, float]
        Dictionary with annual generation (TWh), avoided CO2 (Mt/yr), and car equivalents (Millions).
    """
    # 1. Total electricity that would need replacement (kWh and TWh)
    annual_generation_kwh = cliff_capacity_gw * 1e6 * 8760.0 * capacity_factor
    annual_generation_twh = annual_generation_kwh / 1e9

    # 2. Avoided CO2 emissions in Metric Tons and Million Metric Tons (Mt)
    # (kWh * gCO2/kWh) / 1e6 g per ton = metric tons
    annual_avoided_co2_metric_tons = (annual_generation_kwh * ccgt_emission_factor_g_kwh) / 1e6
    annual_avoided_co2_mt = annual_avoided_co2_metric_tons / 1e6

    # 3. Relatable macro benchmark: Equivalent passenger cars removed from the road
    equivalent_cars_millions = (annual_avoided_co2_metric_tons / car_annual_emissions_metric_tons) / 1e6

    return {
        "annual_generation_twh": float(round(annual_generation_twh, 2)),
        "annual_avoided_co2_mt": float(round(annual_avoided_co2_mt, 2)),
        "equivalent_cars_millions": float(round(equivalent_cars_millions, 1)),
        "ccgt_emission_factor_g_kwh": float(ccgt_emission_factor_g_kwh),
    }


def process_nuclear_data(
    raw_file_path: Optional[Union[str, Path]] = None,
    output_file_path: Optional[Union[str, Path]] = None,
    reference_year: int = 2026,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Ingest, clean, enrich, and validate the Global Nuclear Power Tracker dataset.

    Execution Pipeline
    ------------------
    1. Ingest sheet 'Data' from raw Excel tracker.
    2. Clean text fields and standardize classifications (Status, Reactor Type).
    3. Parse flexible timestamps and compute empirical construction lead times.
    4. Compute asset age as of reference year and identify the 40+ year cliff edge.
    5. Calculate the Carbon Opportunity Cost (avoided emissions vs. CCGT replacement).
    6. Export clean tabular dataset and executive summary table to disk.

    Parameters
    ----------
    raw_file_path : Union[str, Path], optional
        Path to raw Excel file.
    output_file_path : Union[str, Path], optional
        Path to processed CSV file.
    reference_year : int, default 2026
        Reference evaluation year.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Cleaned fleet DataFrame and summary metrics dictionary.
    """
    project_root = Path(__file__).resolve().parent.parent

    if raw_file_path is None:
        raw_file_path = project_root / "data" / "raw" / "Global-Nuclear-Power-Tracker-August-2026.xlsx"
    else:
        raw_file_path = Path(raw_file_path)

    if output_file_path is None:
        output_file_path = project_root / "data" / "processed" / "clean_nuclear_fleet.csv"
    else:
        output_file_path = Path(output_file_path)

    if not raw_file_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {raw_file_path}")

    logger.info(f"Ingesting raw tracker from: {raw_file_path} (Sheet: 'Data')")
    df = pd.read_excel(raw_file_path, sheet_name="Data")
    logger.info(f"Loaded {len(df)} initial reactor units across {len(df.columns)} features.")

    # 1. Standardize string attributes
    for col in ["Project Name", "Unit Name", "Country/Area", "Region", "Subregion"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 2. Standardize categorical classifications
    df["Clean_Status"] = df["Status"].apply(clean_status_category)
    df["Reactor_Type_Clean"] = df["Reactor Type"].apply(clean_reactor_type)

    # 3. Clean and parse date fields
    logger.info("Parsing flexible timestamps (Construction Start Date, COD, Start Year)...")
    df["Const_Start_Date_Clean"] = df["Construction Start Date"].apply(parse_flexible_date)
    df["COD_Clean"] = df["Commercial Operation Date"].apply(parse_flexible_date)

    df["Start_Year_Clean"] = pd.to_numeric(df["Start Year"], errors="coerce")
    df["Cancellation_Year_Clean"] = pd.to_numeric(df["Cancellation Year"], errors="coerce")
    df["Retirement_Year_Clean"] = pd.to_numeric(df["Retirement Year"], errors="coerce")

    # If COD is missing but Start Year exists, approximate COD to mid-year
    missing_cod = df["COD_Clean"].isna() & df["Start_Year_Clean"].notna()
    df.loc[missing_cod, "COD_Clean"] = pd.to_datetime(
        df.loc[missing_cod, "Start_Year_Clean"].astype(int).astype(str) + "-07-01",
        errors="coerce",
    )

    df["Const_Start_Year"] = df["Const_Start_Date_Clean"].dt.year
    df["COD_Year"] = df["COD_Clean"].dt.year.fillna(df["Start_Year_Clean"])

    # 4. Compute empirical lead times in fractional years
    df["Construction_Lead_Time_Years"] = calculate_construction_lead_times(df)

    # 5. Compute age and identify 40+ cliff edge fleet
    df["Age_2026"], df["Cliff_Edge_40plus"] = calculate_fleet_age_and_cliff(df, reference_year=reference_year)

    # Convert capacity to numeric
    df["Capacity (MW)"] = pd.to_numeric(df["Capacity (MW)"], errors="coerce").fillna(0.0)
    df["Capacity_GW"] = df["Capacity (MW)"] / 1000.0

    # 6. Statistical Aggregations & Carbon Opportunity Cost
    operating_units = df[df["Clean_Status"] == "operating"]
    cliff_units = df[df["Cliff_Edge_40plus"]]

    total_op_gw = operating_units["Capacity_GW"].sum()
    cliff_gw = cliff_units["Capacity_GW"].sum()
    cliff_pct = (cliff_gw / total_op_gw) * 100.0 if total_op_gw > 0 else 0.0

    carbon_metrics = calculate_avoided_carbon_emissions(cliff_gw)
    valid_lead_times = operating_units["Construction_Lead_Time_Years"].dropna()

    summary_metrics = {
        "total_records": len(df),
        "operating_reactors": len(operating_units),
        "total_operating_capacity_gw": float(round(total_op_gw, 2)),
        "cliff_edge_reactors_40plus": len(cliff_units),
        "cliff_edge_capacity_gw": float(round(cliff_gw, 2)),
        "cliff_edge_pct_of_operating": float(round(cliff_pct, 2)),
        "cliff_edge_avoided_co2_mt_per_year": carbon_metrics["annual_avoided_co2_mt"],
        "cliff_edge_equivalent_cars_millions": carbon_metrics["equivalent_cars_millions"],
        "mean_operating_lead_time_years": float(round(valid_lead_times.mean(), 2)),
        "median_operating_lead_time_years": float(round(valid_lead_times.median(), 2)),
        "under_construction_reactors": int((df["Clean_Status"] == "construction").sum()),
        "under_construction_capacity_gw": float(round(df[df["Clean_Status"] == "construction"]["Capacity_GW"].sum(), 2)),
        "cancelled_reactors": int((df["Clean_Status"] == "cancelled").sum()),
    }

    logger.info("=== Fleet Data Ingestion & Statistical Validation ===")
    for k, v in summary_metrics.items():
        logger.info(f"  {k}: {v}")

    # 7. Save outputs
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file_path, index=False, encoding="utf-8")
    logger.info(f"Clean fleet data saved to: {output_file_path}")

    # Save executive metrics table
    exec_table_path = project_root / "outputs" / "tables" / "executive_metrics_summary.csv"
    exec_table_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary_metrics]).to_csv(exec_table_path, index=False)
    logger.info(f"Executive metrics table saved to: {exec_table_path}")

    return df, summary_metrics


if __name__ == "__main__":
    process_nuclear_data()
