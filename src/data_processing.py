"""Data Processing and Fleet Ingestion Module for Global Nuclear Power Tracker.

ESSEC / AIDAMS - Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)
Course Project: Nuclear Project Finance & Fleet Life Extension (LTO)
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

    Parameters
    ----------
    val : Any
        Date representation (string, float, int, Timestamp, or NaN).

    Returns
    -------
    pd.Timestamp
        Parsed Timestamp or pd.NaT if invalid or missing.
    """
    if pd.isna(val):
        return pd.NaT

    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return pd.to_datetime(val)

    s = str(val).strip()
    if not s or s.lower() in ("nan", "nat", "none", ""):
        return pd.NaT

    # Format: YYYY (e.g., '1984' or '1984.0')
    if s.endswith(".0"):
        s = s[:-2]

    if len(s) == 4 and s.isdigit():
        return pd.to_datetime(f"{s}-07-01", errors="coerce")

    # Format: YYYY-MM
    if len(s) == 7 and s[:4].isdigit() and s[4] == "-":
        return pd.to_datetime(f"{s}-15", errors="coerce")

    # Standard YYYY-MM-DD or standard parseable string
    return pd.to_datetime(s, errors="coerce")


def clean_status_category(raw_status: Any) -> str:
    """Standardize raw status strings into analytical categories.

    Categories:
    - 'operating'
    - 'construction'
    - 'cancelled'
    - 'pre-construction'
    - 'announced'
    - 'retired'
    - 'shelved'

    Parameters
    ----------
    raw_status : Any
        Raw status string.

    Returns
    -------
    str
        Standardized status string.
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
    """Standardize reactor technologies into recognized industry classifications.

    Categories:
    - 'PWR' (Pressurized Water Reactor)
    - 'BWR' (Boiling Water Reactor)
    - 'SMR' (Small Modular Reactor)
    - 'PHWR' (Pressurized Heavy Water Reactor / CANDU)
    - 'FBR' (Fast Breeder / Liquid Metal)
    - 'HTGR' (High Temperature Gas Reactor)
    - 'LWGR' (Light Water Graphite / RBMK)
    - 'GCR' (Gas-Cooled Reactor)
    - 'Other'

    Parameters
    ----------
    raw_type : Any
        Raw reactor type description.

    Returns
    -------
    str
        Standardized reactor type.
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


def process_nuclear_data(
    raw_file_path: Optional[Union[str, Path]] = None,
    output_file_path: Optional[Union[str, Path]] = None,
    reference_year: int = 2026,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Ingest, clean, and enrich the Global Nuclear Power Tracker dataset.

    Parameters
    ----------
    raw_file_path : Union[str, Path], optional
        Path to raw Excel file. Defaults to `data/raw/Global-Nuclear-Power-Tracker-August-2026.xlsx`.
    output_file_path : Union[str, Path], optional
        Path to output CSV file. Defaults to `data/processed/clean_nuclear_fleet.csv`.
    reference_year : int, default 2026
        Reference evaluation year for age and cliff edge assessment.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Cleaned DataFrame and summary metrics dictionary.
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
        raise FileNotFoundError(f"Raw data file not found at: {raw_file_path}")

    logger.info(f"Ingesting raw data from: {raw_file_path} (Sheet: 'Data')")
    df = pd.read_excel(raw_file_path, sheet_name="Data")
    logger.info(f"Loaded {len(df)} initial reactor units across {len(df.columns)} features.")

    # 1. Standardize text columns
    df["Project Name"] = df["Project Name"].astype(str).str.strip()
    df["Unit Name"] = df["Unit Name"].astype(str).str.strip()
    df["Country/Area"] = df["Country/Area"].astype(str).str.strip()
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Subregion"] = df["Subregion"].astype(str).str.strip()

    # 2. Clean status and reactor classifications
    df["Clean_Status"] = df["Status"].apply(clean_status_category)
    df["Reactor_Type_Clean"] = df["Reactor Type"].apply(clean_reactor_type)

    # 3. Clean and parse dates
    logger.info("Parsing dates (Construction Start, Commercial Operation, Start Year, Cancellation Year)...")
    df["Const_Start_Date_Clean"] = df["Construction Start Date"].apply(parse_flexible_date)
    df["COD_Clean"] = df["Commercial Operation Date"].apply(parse_flexible_date)

    # Clean numeric years
    df["Start_Year_Clean"] = pd.to_numeric(df["Start Year"], errors="coerce")
    df["Cancellation_Year_Clean"] = pd.to_numeric(df["Cancellation Year"], errors="coerce")
    df["Retirement_Year_Clean"] = pd.to_numeric(df["Retirement Year"], errors="coerce")

    # If COD is missing but Start Year exists, approximate COD
    missing_cod_mask = df["COD_Clean"].isna() & df["Start_Year_Clean"].notna()
    df.loc[missing_cod_mask, "COD_Clean"] = pd.to_datetime(
        df.loc[missing_cod_mask, "Start_Year_Clean"].astype(int).astype(str) + "-07-01",
        errors="coerce",
    )

    # If Const Start Date is missing but Construction Start Date has year
    df["Const_Start_Year"] = df["Const_Start_Date_Clean"].dt.year
    df["COD_Year"] = df["COD_Clean"].dt.year.fillna(df["Start_Year_Clean"])

    # 4. Calculate Construction Lead Time in years (COD - Const Start)
    # Precise days difference divided by 365.25
    df["Construction_Lead_Time_Years"] = (
        (df["COD_Clean"] - df["Const_Start_Date_Clean"]).dt.days / 365.25
    )

    # Fallback to year difference if exact dates are missing but years are known
    fallback_lead_mask = (
        df["Construction_Lead_Time_Years"].isna()
        & df["COD_Year"].notna()
        & df["Const_Start_Year"].notna()
    )
    df.loc[fallback_lead_mask, "Construction_Lead_Time_Years"] = (
        df.loc[fallback_lead_mask, "COD_Year"] - df.loc[fallback_lead_mask, "Const_Start_Year"]
    )

    # Filter out anomalous negative lead times if any
    df.loc[df["Construction_Lead_Time_Years"] < 0, "Construction_Lead_Time_Years"] = np.nan

    # 5. Calculate Fleet Age and Cliff Edge Flag for Operating Fleet
    df["Age_2026"] = np.nan
    operating_mask = df["Clean_Status"] == "operating"
    df.loc[operating_mask, "Age_2026"] = reference_year - df.loc[operating_mask, "Start_Year_Clean"]

    # Binary Cliff Edge Flag: Operating unit age >= 40 years
    df["Cliff_Edge_40plus"] = False
    df.loc[operating_mask & (df["Age_2026"] >= 40), "Cliff_Edge_40plus"] = True

    # Capacity in MW
    df["Capacity (MW)"] = pd.to_numeric(df["Capacity (MW)"], errors="coerce").fillna(0.0)
    df["Capacity_GW"] = df["Capacity (MW)"] / 1000.0

    # 6. Summary Validation Metrics
    operating_units = df[operating_mask]
    cliff_units = df[df["Cliff_Edge_40plus"]]
    total_operating_capacity_gw = operating_units["Capacity_GW"].sum()
    cliff_capacity_gw = cliff_units["Capacity_GW"].sum()
    cliff_pct = (cliff_capacity_gw / total_operating_capacity_gw) * 100 if total_operating_capacity_gw > 0 else 0

    valid_lead_times = operating_units["Construction_Lead_Time_Years"].dropna()

    summary_metrics = {
        "total_records": len(df),
        "operating_reactors": len(operating_units),
        "total_operating_capacity_gw": float(round(total_operating_capacity_gw, 2)),
        "cliff_edge_reactors_40plus": len(cliff_units),
        "cliff_edge_capacity_gw": float(round(cliff_capacity_gw, 2)),
        "cliff_edge_pct_of_operating": float(round(cliff_pct, 2)),
        "mean_operating_lead_time_years": float(round(valid_lead_times.mean(), 2)),
        "median_operating_lead_time_years": float(round(valid_lead_times.median(), 2)),
        "under_construction_reactors": int((df["Clean_Status"] == "construction").sum()),
        "under_construction_capacity_gw": float(round(df[df["Clean_Status"] == "construction"]["Capacity_GW"].sum(), 2)),
        "cancelled_reactors": int((df["Clean_Status"] == "cancelled").sum()),
    }

    logger.info("=== Dataset Ingestion & Validation Summary ===")
    for k, v in summary_metrics.items():
        logger.info(f"  {k}: {v}")

    # 7. Export Processed Data
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file_path, index=False, encoding="utf-8")
    logger.info(f"Cleaned dataset successfully saved to: {output_file_path}")

    return df, summary_metrics


if __name__ == "__main__":
    process_nuclear_data()
