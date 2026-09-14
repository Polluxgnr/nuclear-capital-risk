# Nuclear Capital Risk: Project Finance & Fleet Life Extension (LTO)

[![Python: >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/)
[![Package Manager: Pixi](https://img.shields.io/badge/package%20manager-pixi-yellow.svg)](https://pixi.sh/)
[![License: Academic Research](https://img.shields.io/badge/license-Academic%20Open-green.svg)]()
[![Course: ESSEC / AIDAMS](https://img.shields.io/badge/ESSEC%20%2F%20AIDAMS-Climate%20Risks%202026-navy.svg)]()

> **Master's Research Repository:** Quantitative assessment of Interest During Construction (IDC), lead-time escalation risk, and the economic dominance of Long-Term Operation (LTO) vs. Gen-III+ and Small Modular Reactor (SMR) new builds under rising cost-of-capital regimes.

---

## 1. Executive Research Question & Academic Context

* **Course**: *Research & Emerging Topics in Data Science: Climate Risks* (ESSEC Business School / AIDAMS, Fall 2026).
* **Core Research Question**:
  > *"Given the debt compounding (IDC) and capital erosion caused by construction lead-time delays in new reactors (Gen-III+ and SMRs), does long-term operation (LTO / life extension) of aging fleets offer a financially superior risk-adjusted return over new-build investments under rising cost-of-capital scenarios?"*

### Key Analytical Takeaways
1. **The 181 GW Operational Cliff**: Out of 407.8 GW of global operating nuclear capacity, **180.99 GW (44.4% across 198 reactors)** is $\ge 40$ years old in 2026. This creates an imminent replacement crisis if life extensions are delayed.
2. **Empirical Delay Normalcy**: Analysis of the Global Nuclear Power Tracker reveals a historical mean construction lead time of **8.76 years** (median: **7.16 years**), showing that multi-year schedule slippages are structurally normal, not anomalous outliers.
3. **Compound Capital Erosion**: At a 7.0% WACC, a 5-year delay inflates Gen-III+ overnight capex from \$7,500/kW to **\$12,713/kW** (+69.5% IDC). At 10.0% WACC with 7-year delay, total capex reaches **\$17,358/kW** (+131.4% IDC).
4. **LCOE Resilience**: 20-year LTO provides an LCOE of **\$40.5–\$49.0/MWh** across all cost-of-capital scenarios (4% to 10% WACC), while delayed Gen-III+ LCOE escalates to **\$138–\$205/MWh** (2.5x to 4.6x higher).

---

## 2. Team Role Mapping

| Role | Primary Responsibilities | Deliverables |
| :--- | :--- | :--- |
| **Climate Risk Analyst** | Empirical asset-level analysis, construction lead-time econometrics, 40+ year cliff mapping, technology risk profiles. | Data cleaning pipeline (`data_processing.py`), Empirical Lead-Time analysis, Age pyramid & cliff mapping (`Fig 1`, `Fig 2`). |
| **Sustainability & Financial Consultant** | Project finance structuring, S-curve expenditure modeling, IDC compounding formulas, WACC sensitivity grids, policy mechanisms (RAB, CfD). | Financial engine (`model.py`), IDC curves & LCOE comparison (`Fig 3`, `Fig 4`), Overleaf paper draft (`docs/project_report_draft.md`). |

---

## 3. Directory Layout

```text
nuclear-capital-risk/
├── pixi.toml                              # Multi-platform Pixi environment configuration
├── pyproject.toml                         # Standard PEP 518/621 dependency specification
├── README.md                              # Institutional documentation & run guide
├── main.py                                # Master orchestrator & console executive summary
├── data/
│   ├── raw/
│   │   └── Global-Nuclear-Power-Tracker-August-2026.xlsx  # Primary asset-level dataset
│   └── processed/
│       └── clean_nuclear_fleet.csv        # Cleaned dataset (1,825 units, parsed dates & lead times)
├── src/
│   ├── __init__.py
│   ├── data_processing.py                 # Fleet ingestion, date parsing, cliff edge detection
│   ├── model.py                           # S-curve expenditure, IDC compounding & LCOE engine
│   └── visualization.py                   # Publication-grade plotting module (300 DPI)
├── outputs/
│   ├── figures/                           # High-resolution PNG figures (300 DPI)
│   │   ├── fig1_construction_durations.png
│   │   ├── fig2_nuclear_age_pyramid_cliff.png
│   │   ├── fig3_idc_compounding_escalation.png
│   │   └── fig4_lcoe_comparison_lto_vs_newbuild.png
│   └── tables/                            # Quantitative sensitivity grids
│       ├── sensitivity_capex_kw.csv
│       ├── sensitivity_lcoe.csv
│       ├── sensitivity_comparative_lto.csv
│       ├── pivot_capex_by_wacc.csv
│       └── pivot_lcoe_by_wacc.csv
├── docs/
│   └── project_report_draft.md            # 5-page Overleaf scientific paper draft
└── .gitignore                             # Git exclusion rules
```

---

## 3. Setup & Reproducibility Guide

### Option A: Using Pixi (Recommended)
Pixi provides reproducible, multi-platform dependency isolation directly from `pixi.toml`:

```bash
# 1. Clone the repository
git clone https://github.com/Polluxgnr/nuclear-capital-risk.git
cd nuclear-capital-risk

# 2. Install dependencies into isolated environment
pixi install

# 3. Run the complete quantitative pipeline
pixi run python main.py

# 4. Launch the Interactive Streamlit Defense Dashboard
pixi run dashboard
```

### Option B: Using Standard Python (pip / venv)
If `pixi` is not installed on your system:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or: .venv\Scripts\activate    # On Windows PowerShell

# 2. Install requirements
pip install -r pyproject.toml
# or: pip install pandas numpy openpyxl matplotlib seaborn scipy streamlit geopandas

# 3. Execute the pipeline & launch dashboard
python main.py
streamlit run app.py
```

---

## 5. Quantitative Methodology & Key Equations

### S-Curve Expenditure Profile
Annual capital disbursement follows a continuous Beta cumulative distribution:
$$S(\tau) = I_\tau(\alpha, \beta) = \frac{1}{\mathrm{B}(\alpha, \beta)} \int_0^\tau u^{\alpha-1} (1-u)^{\beta-1} \mathrm{d}u, \quad \tau = \frac{t}{T} \in [0, 1]$$
where $\alpha = 2.5, \beta = 2.5$, modeling engineering acceleration and testing taper.

### Interest During Construction (IDC) Compounding
For construction duration $T = T_0 + \Delta t$ and WACC $r$, disbursements $C_t = w_t \cdot \mathrm{Capex}_{\mathrm{overnight}}$ compound via:
$$\mathrm{Capex}_{\mathrm{total}}(T, r) = \sum_{t=1}^{T} C_t \cdot (1 + r)^{T - t + 0.5}$$
$$\mathrm{IDC} = \mathrm{Capex}_{\mathrm{total}} - \mathrm{Capex}_{\mathrm{overnight}}, \quad \mathrm{IDC\ Multiplier} = \frac{\mathrm{Capex}_{\mathrm{total}}}{\mathrm{Capex}_{\mathrm{overnight}}}$$

### Levelized Cost of Electricity (LCOE)
$$\mathrm{LCOE} = \frac{\mathrm{CRF}(r, N) \cdot \mathrm{Capex}_{\mathrm{total}} + \mathrm{Fixed\ O\&M}}{8760 \cdot \mathrm{CF}} + \mathrm{Var\ O\&M} + \mathrm{Fuel\ Cost}$$
$$\mathrm{CRF}(r, N) = \frac{r(1+r)^N}{(1+r)^N - 1}$$
* $N = 20$ years for LTO; $N = 60$ years for Gen-III+; $N = 40$ years for SMR.
* $\mathrm{CF} = 0.88$ (88% baseload capacity factor).

---

## 6. Generated Publication Figures

| Figure | Description | High-Res Output Path |
| :--- | :--- | :--- |
| **Figure 1** | Empirical lead time distributions across technologies (PWR, BWR, CANDU) and geographies. | `outputs/figures/fig1_construction_durations.png` |
| **Figure 2** | 2026 Global Nuclear Age Pyramid highlighting the **181 GW (198 reactors)** 40+ year cliff. | `outputs/figures/fig2_nuclear_age_pyramid_cliff.png` |
| **Figure 3** | Debt escalation & IDC compounding curve over delays ($\Delta t \in [0, 10]$ yrs) across WACCs. | `outputs/figures/fig3_idc_compounding_escalation.png` |
| **Figure 4** | LCOE comparison between 20-yr LTO, on-time Gen-III+, delayed Gen-III+, and SMRs. | `outputs/figures/fig4_lcoe_comparison_lto_vs_newbuild.png` |
| **Figure 5** | Global geospatial distribution of operating reactors highlighting the 40+ year cliff. | `outputs/figures/fig5_global_cliff_map.png` |

---

## 7. Secondary Data Integration & Extensions

To expand the quantitative depth, the repository integrates:
1. **IEA / NEA (*Projected Costs of Generating Electricity*)**: Overnight Capex benchmarks (\$1,200/kW for Grand Carénage LTO, \$7,500/kW for Gen-III+, \$9,000/kW for SMR).
2. **Prof. Aswath Damodaran (NYU Stern)**: Regional sector WACC tables for *Green & Power Utilities* (5.5% in US/Europe, 8.5%–10% in Emerging Markets).

Detailed academic write-up, literature references, and Overleaf formatting are located in [`docs/project_report_draft.md`](docs/project_report_draft.md).

---

## 8. GitHub Remote Repository Synchronization

To push this repository to GitHub via the GitHub CLI:

```bash
# Verify git status
git status

# Create and push to a remote public repository
gh repo create nuclear-capital-risk --public --source=. --remote=origin --push
```
