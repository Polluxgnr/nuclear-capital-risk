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

## 5. Methodology & Key Assumptions Justification

To ensure institutional academic rigor, our modeling parameters are anchored in empirical industry benchmarks:

### A. Carbon Opportunity Cost Logic (CCGT Replacement)
* **The Rationale:** Nuclear power provides non-intermittent, spinning grid inertia. If the 181.0 GW mature fleet retires without LTO, grid reliability operators cannot balance loads exclusively with variable solar or wind without gigawatt-scale multi-day storage.
* **The Benchmark:** In modern power markets (e.g. California post-San Onofre, Germany post-Atomausstieg), retired nuclear generation is empirically replaced by **Natural Gas Combined Cycle (CCGT)** turbines emitting **$400\ \mathrm{gCO_2/kWh}$** at an **$88\%$ baseload capacity factor**.
* **Macro Impact:**
  $$\text{Avoided Emissions} = 180.99\ \text{GW} \times 8,760\ \text{h} \times 0.88 \times 0.400\ \text{t/MWh} = \mathbf{558.07\ \text{Mt CO}_2\text{ / year}}$$
  This is equivalent to adding **121.3 Million passenger vehicles** to the road annually, exceeding the combined national annual emissions of France and Belgium.

### B. Beta(2.5, 2.5) S-Curve Spend Distribution
* **The Rationale:** Civil engineering megaprojects exhibit a bell-shaped spending profile:
  1. *Early Phase (5–10%/yr):* Preliminary site preparation, seismic geotechnical surveying, and regulatory licensing.
  2. *Peak Phase (25–30%/yr):* Heavy structural concrete pouring, nuclear containment erection, and Nuclear Steam Supply System (NSSS) installation.
  3. *Taper Phase (10–15%/yr):* Instrumentation and Control (I&C) cabling, cold/hot functional hydro-testing, and initial core fuel loading.
* **The Math:** Modeled via the regularized incomplete Beta cumulative distribution function $S(\tau) = I_\tau(2.5, 2.5)$ over normalized construction time $\tau = t / T$.

### C. Mid-Year Compounding Convention $(T - t + 0.5)$
* In nuclear project finance, capital expenditures are drawn down in progressive monthly installments throughout each calendar year. Assuming a mid-year disbursement date means debt incurred in year $t$ accrues interest for exactly $(T - t + 0.5)$ years until commercial operation, avoiding the underestimation of carrying costs.

### D. Cost of Capital (WACC) Benchmarks (Damodaran NYU Stern)
* Sourced from Prof. Aswath Damodaran's 2026 sector tables for *Green & Power Utilities*:
  * **Subsidized / Green Bonds ($4.0\%$):** Sovereign-backed low-cost financing.
  * **Developed Utilities ($5.5\%$):** Regulated investor-owned utilities in the US and Western Europe.
  * **Baseline Market ($7.0\%$):** Unhedged commercial power utility financing.
  * **Emerging Markets ($8.5\%–10.0\%$):** Higher country risk premiums and sovereign credit spreads (e.g. Brazil, India).

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
