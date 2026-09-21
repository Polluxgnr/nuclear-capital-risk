# Nuclear Capital Risk: Project Finance & Fleet Life Extension (LTO)
## Strategic Decarbonization Advisory for Utility Boards & Energy Ministries

[![Python: >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/)
[![Package Manager: Pixi](https://img.shields.io/badge/package%20manager-pixi-yellow.svg)](https://pixi.sh/)
[![License: Academic Research](https://img.shields.io/badge/license-Academic%20Open-green.svg)]()
[![Course: ESSEC / AIDAMS](https://img.shields.io/badge/ESSEC%20%2F%20AIDAMS-Climate%20Risks%202026-navy.svg)]()
[![Role: Sustainability Consultant](https://img.shields.io/badge/Role-Sustainability%20Consultant-brightgreen.svg)]()

> **ESSEC Business School / AIDAMS — Fall 2026**  
> **Course:** Research & Emerging Topics in Data Science: Climate Risks (Lead: Prof. Hamada Saleh)  
> **Authors:** Pollux Gronier, Eliott Beghin, Saty Viard Laroque, Neel Sabarwhal  
> **Designated Course Role:** **Sustainability Consultant** (*Clean Energy Transition & Capital Allocation Advisory*)  
> **GitHub Repository:** [https://github.com/Polluxgnr/nuclear-capital-risk](https://github.com/Polluxgnr/nuclear-capital-risk)

---

## 1. Executive Summary & Strategic Context

As energy transition advisors, we address a multi-trillion-dollar capital allocation question facing utilities and energy ministries between 2026 and 2035:

> *"Given the multi-year construction lead-time delays and exponential Interest During Construction (IDC) compounding inherent to greenfield reactors, does 20-year Long-Term Operation (LTO / life extension) of aging fleets provide a superior risk-adjusted decarbonization pathway compared to new builds under rising cost-of-capital regimes?"*

### Key Strategic Findings:
1. **The 181 GW Reinvestment Wall:** Out of 407.8 GW of global operating nuclear capacity, **180.99 GW (44.4% across 198 reactors)** has reached or exceeded its initial 40-year design life in 2026. Without 20-year life extension investments, this baseload capacity will be permanently decommissioned by 2035.
2. **The Carbon Cliff:** If this 181 GW fleet retires and is replaced by dispatchable natural gas (CCGT @ 400 gCO2/kWh, 88% capacity factor), power grids will emit **558.1 Million Metric Tons of CO2 every year**. This avoided carbon volume is equivalent to adding **121.3 Million passenger vehicles** to the road—erasing decades of renewable progress.
3. **The Greenfield Lead-Time Trap:** Across 424 operating commercial reactors, the empirical mean build duration is **8.76 years** (median: 7.16 years), with Western builds routinely taking 12 to 17 years (e.g. Flamanville 3, Vogtle 3&4). Waiting for new gigawatt builds creates a 12-year generation vacuum that releases **6.70 Gigatons of cumulative replacement CO2**.
4. **The $1.14 Trillion Capital Arbitrage:** Refurbishing the 181 GW fleet via 20-Yr LTO costs **$217 Billion** ($1,200/kW), delivering electricity at an ultra-stable LCOE of **$40.5–$49.0/MWh**. Replacing it with greenfield reactors costs **$1.36 Trillion on paper** and **over $2.30 Trillion under real-world delays**, saving utilities over **$1.14 Trillion** in direct capital outlay.

---

## 2. What Datasets Are Used in This Study?

Our analytical pipeline is built on five empirical and academic data sources:

| Dataset / Source | Scope & Format | Specific Parameters Extracted | Role in Our Analysis |
| :--- | :--- | :--- | :--- |
| **Global Nuclear Power Tracker (GEM, Aug 2026)** | Asset-level global registry (1,825 units, 39 attributes, `.xlsx`) | Status, nameplate capacity (MW), reactor technology, start of construction, commercial operation date, geographic coordinates. | Ingested by `src/data_processing.py` to calculate empirical lead times, construct the 2026 age pyramid, and map the 181 GW cliff edge. |
| **IEA & NEA (2020) *Projected Costs of Generating Electricity*** | Audited international techno-economic benchmarks | Overnight capex ($7,500/kW Gen-III+, $1,200/kW LTO, $9,000/kW SMR), Fixed O&M ($110–$135/kW-yr), Variable O&M ($3.0/MWh), Fuel cycle ($7.0–$8.5/MWh). | Calibrates baseline capital expenditures and operating cash flows in `src/model.py`. |
| **Prof. Aswath Damodaran (NYU Stern, 2026)** | Industry cost of capital benchmarks for *Power & Green Utilities* | WACC discount rates across financial regimes: 4.0% (Subsidized/Green Bonds), 5.5% (Developed Utilities), 7.0% (Baseline Market), 8.5%–10.0% (Merchant/EM). | Drives the multi-dimensional sensitivity grids for IDC debt compounding. |
| **IPCC AR6 WGIII (2022) & US EPA** | Lifecycle greenhouse gas emissions and vehicle conversion standards | Natural Gas CCGT lifecycle factor (400 gCO2/kWh), Nuclear lifecycle factor (<12 gCO2/kWh), EPA vehicle factor (4.6 tCO2/car/year). | Powers the Avoided Carbon Cliff and vehicle equivalence calculations. |
| **Natural Earth Vector GIS (`data/raw/world.json`)** | Global landmass vector boundaries (GeoJSON) | Geographic polygon boundaries of continents and national borders. | Renders high-resolution spatial maps in `src/visualization.py` (Figure 5). |

---

## 3. Methodology & Financial Mathematics

### A. S-Curve Expenditure Dynamics: Why $\text{Beta}(2.5, 2.5)$?
In large civil engineering projects, capital is never spent linearly. Disbursements follow a classic bell-shaped profile:
1. *Slow Site Mobilization (5–10%/yr):* Ground excavation, seismic surveying, and nuclear safety licensing.
2. *Peak Structural Civil Works (25–30%/yr):* Heavy structural concrete pouring, reactor containment erection, and Nuclear Steam Supply System (NSSS) assembly.
3. *Tapering & Cold Commissioning (10–15%/yr):* Instrumentation and Control (I&C) cabling, hydrostatic pressure testing, and initial core fuel loading.

We model this spending profile via the continuous regularized incomplete Beta cumulative distribution function:
$$S(\tau) = I_\tau(\alpha, \beta) = \frac{\mathrm{B}(\tau; \alpha, \beta)}{\mathrm{B}(\alpha, \beta)}, \quad \tau = \frac{t}{T} \in [0, 1], \quad \alpha = 2.5, \ \beta = 2.5$$

### B. Discrete Mid-Year IDC Compounding $(T - t + 0.5)$
In project finance, engineering contractors draw down debt continuously throughout the year rather than in lump sums on January 1st or December 31st. Debt drawn down in year $t$ accrues interest for the remaining construction duration plus half a year:
$$\text{Capex}_{\text{total}}(T, r) = \sum_{t=1}^T \left[ w_t \cdot \text{Capex}_{\text{esc}} \cdot (1 + r)^{T - t + 0.5} \right]$$
where $\text{Capex}_{\text{esc}} = \text{Capex}_{\text{overnight}} \cdot (1 + \lambda \cdot \Delta t)$, with site carrying escalation $\lambda = 1.5\%/\text{year}$ of delay $\Delta t$.

### C. Levelized Cost of Electricity (LCOE) Decomposition
$$\text{LCOE} = \frac{\text{Capex}_{\text{total}} \cdot \text{CRF}}{8,760 \cdot \text{CF}} + \frac{\text{Fixed O\&M}}{8,760 \cdot \text{CF}} + \text{Variable O\&M} + \text{Fuel Cost}$$
where the Capital Recovery Factor is:
$$\text{CRF}(r, N) = \frac{r(1 + r)^N}{(1 + r)^N - 1}$$

---

## 4. Strategic Decarbonization Pathways (Figure 6)

Our analysis benchmarks three 20-year transition pathways (2026–2045) to preserve or replace the 181 GW baseload cliff:
* **Pathway 1 (20-Year LTO):** Capital outlay of **$217 Billion** ($1,200/kW), completed within standard 2-year refueling outages, incurring **0.0 Gt in replacement emissions**. Generates power at $40.5–$49.0/MWh.
* **Pathway 2 (Greenfield Megaprojects):** Capital outlay of **$2,301 Billion** ($12,713/kW). Due to the 12-year empirical construction lag, grids must burn natural gas in the interim, releasing **6.70 Gigatons of replacement CO2**.
* **Pathway 3 (Fossil Lock-in):** Replacing the fleet with CCGT incurs $217 Billion in plant capex but emits **11.16 Gigatons of CO2** over 20 years, exposing utilities to severe carbon pricing and stranded asset write-downs.

---

## 5. Limitations of the Study & Data Boundaries

To maintain rigorous academic and consulting integrity, we highlight the analytical boundaries of our modeling:

1. **Data Completeness & Reporting Latency:**
   * The GEM Global Nuclear Power Tracker aggregates official government and utility filings. Historical units from the 1970s often report commercial operation only by year or year-month. Our pipeline standardizes these to mid-year/mid-month, which could introduce slight lead-time variances of $\pm 3$ months.
2. **Generic Overnight Capex Benchmarks:**
   * We apply standardized overnight costs ($1,200/kW for LTO, $7,500/kW for Gen-III+, $9,000/kW for SMR). In reality, refurbishment costs vary by reactor design (e.g. CANDU feeder tube replacement vs. PWR steam generator replacement vs. BWR stress corrosion cracking remediation).
3. **The 100% CCGT Replacement Assumption:**
   * We model complete replacement by natural gas CCGT as a conservative empirical proxy for firm, dispatchable capacity. While wind and solar will capture part of the volume, the absence of commercial terawatt-hour seasonal storage means thermal plants empirically balance the loss of nuclear baseload (as observed in Germany post-2022 and California post-San Onofre).
4. **Nuclear Safety Authority Regulatory Hurdles:**
   * 20-Year LTO is not an automatic administrative renewal. It requires rigorous decennial safety reassessments (*visites décennales* by ASN in France, Subsequent License Renewals by the US NRC) and public hearings. Economic superiority does not bypass safety constraints.
5. **Nuclear Fuel Cycle & Waste Management:**
   * Extending the operating fleet for 20 years increases high-level nuclear waste inventory, requiring continued investment in deep geological repositories (such as Cigéo in France and Onkalo in Finland).

---

## 6. Repository Layout

```text
nuclear-capital-risk/
├── app.py                                 # Interactive Streamlit defense dashboard (Plotly + dynamic KPIs)
├── pixi.toml                              # Multi-platform Pixi environment & task runner
├── pyproject.toml                         # Standard PEP 518/621 dependency specification
├── README.md                              # Institutional research documentation & methodology
├── main.py                                # Single executable entry point (runs full pipeline in ~15s)
├── data/
│   ├── raw/
│   │   ├── Global-Nuclear-Power-Tracker-August-2026.xlsx  # 1,825 tracked units (39 attributes)
│   │   └── world.json                     # GeoJSON boundary dataset for geospatial mapping
│   └── processed/
│       └── clean_nuclear_fleet.csv        # Cleaned dataset with lead times & cliff edge flags
├── src/
│   ├── __init__.py
│   ├── data_processing.py                 # Decomposed ingestion, date parsing, cliff edge & CO2 metrics
│   ├── model.py                           # Decomposed Beta S-curve, mid-year IDC compounding, LCOE
│   └── visualization.py                   # 6 publication figures at 300 DPI (including 1x2 maps & pathways)
├── outputs/
│   ├── figures/                           # High-resolution PNG figures (300 DPI)
│   │   ├── fig1_construction_durations.png
│   │   ├── fig2_nuclear_age_pyramid_cliff.png
│   │   ├── fig3_idc_compounding_escalation.png
│   │   ├── fig4_lcoe_comparison_lto_vs_newbuild.png
│   │   ├── fig5_global_cliff_map.png      # 1x2 Side-by-side: 2026 Baseline vs. 2035 Nuclear Desert
│   │   └── fig6_decarbonization_pathways.png # Strategic Pathways: Capital Outlay vs. Cumulative CO2
│   └── tables/                            # Quantitative CSV matrices & summary metrics
│       ├── executive_metrics_summary.csv
│       ├── sensitivity_capex_kw.csv
│       ├── sensitivity_lcoe.csv
│       ├── sensitivity_comparative_lto.csv
│       ├── pivot_capex_by_wacc.csv
│       └── pivot_lcoe_by_wacc.csv
├── docs/
│   ├── paper.tex                          # Overleaf scientific paper (two-column article, max 5 pages)
│   ├── references.bib                     # Academic BibTeX bibliography (GEM, IEA, Damodaran, IPCC)
│   ├── business_presentation_slides.md    # 10-slide, 5-Act consulting pitch narrative outline
│   └── project_report_draft.md            # Comprehensive extended research draft
└── .gitignore                             # Git exclusion rules
```

---

## 7. Setup & Reproducibility Guide

### Option A: Using Pixi (Recommended)
```bash
# Clone the repository
git clone https://github.com/Polluxgnr/nuclear-capital-risk.git
cd nuclear-capital-risk

# Install isolated environment
pixi install

# Run the complete headless research pipeline (generates all 6 figures & tables)
pixi run python main.py

# Launch the interactive Streamlit defense dashboard
pixi run dashboard
```

### Option B: Using Standard Python (pip / venv)
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or: .venv\Scripts\activate    # On Windows PowerShell

# Install dependencies
pip install -r pyproject.toml
# or: pip install pandas numpy openpyxl matplotlib seaborn scipy streamlit plotly geopandas

# Run pipeline
python main.py

# Launch dashboard
streamlit run app.py
```

---

## 8. Publication Figures Overview

| Figure | Description | Strategic Insight for Sustainability Consultant |
| :--- | :--- | :--- |
| **Figure 1** | Empirical Lead-Time Distributions (`fig1_construction_durations.png`) | Proves historical mean build time is 8.76y; pitchbook 5-year schedules are statistically unrealistic. |
| **Figure 2** | 2026 Global Nuclear Age Pyramid (`fig2_nuclear_age_pyramid_cliff.png`) | Identifies the 181 GW (44.4%) cliff edge of reactors reaching 40 years. |
| **Figure 3** | IDC Debt Compounding Curves (`fig3_idc_compounding_escalation.png`) | Shows capex surging to $17,358/kW (+131% IDC) under delays and 10% WACC. |
| **Figure 4** | LCOE Comparison LTO vs. New Builds (`fig4_lcoe_comparison_lto_vs_newbuild.png`) | Proves LTO generates power at $40.5–$49/MWh, beating new builds by 2.5x to 4.6x. |
| **Figure 5** | 1x2 Geospatial Impact Shockwave (`fig5_global_cliff_map.png`) | Contrasts 2026 Baseline vs. 2035 "Nuclear Desert" if life extension is foregone. |
| **Figure 6** | Strategic Decarbonization Pathways (`fig6_decarbonization_pathways.png`) | Compares capital outlay ($217B vs. $2.3T) and reveals the 6.7 Gt replacement carbon gap. |

---

## 9. Academic Course Deliverables Index

* **Scientific Paper (Overleaf, Max 5 Pages):** [`docs/paper.tex`](docs/paper.tex) with bibliography in [`docs/references.bib`](docs/references.bib).
* **Business Pitch Deck (10 Slides):** [`docs/business_presentation_slides.md`](docs/business_presentation_slides.md).
* **Interactive Defense Simulator:** [`app.py`](app.py) (run via `streamlit run app.py`).

