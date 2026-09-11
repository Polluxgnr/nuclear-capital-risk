# Nuclear Capital Risk: Debt Compounding, Construction Delays, and the Economic Supremacy of Fleet Life Extension (LTO)

**Authors:** Student Research Team (Climate Risk Analyst & Sustainability Consultant)  
**Affiliation:** ESSEC Business School / AIDAMS — *Master in Data Sciences & Business Analytics*  
**Course:** Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)  
**Keywords:** Nuclear Project Finance, Long-Term Operation (LTO), Interest During Construction (IDC), Weighted Average Cost of Capital (WACC), Levelized Cost of Electricity (LCOE), Climate Risk.

---

## Executive Abstract

Nuclear energy represents approximately 10% of global electricity generation and over 25% of low-carbon electricity. However, the commercial renaissance of nuclear power is constrained by acute financial friction: massive capital intensity, extended construction lead times, and compounding Interest During Construction (IDC). Using the August 2026 release of the Global Nuclear Power Tracker (1,825 asset records), this paper investigates the financial and risk-adjusted viability of nuclear asset renewal. We reveal that **180.99 GW across 198 operating reactors (44.38% of the global operating fleet of 407.8 GW)** has reached or exceeded its initial 40-year design lifetime. Empirically, completed reactors exhibit a mean construction lead time of **8.76 years** (median: **7.16 years**), showing that multi-year schedule delays are statistically endemic to Western new-build projects.

We develop a quantitative project finance engine integrating S-curve capital disbursements, IDC debt compounding across cost-of-capital regimes (WACC $r \in [4.0\%, 10.0\%]$), and Levelized Cost of Electricity (LCOE) formulations. Our modeling demonstrates that a 20-year Long-Term Operation (LTO / Grand Carénage) program at overnight capital costs of \$1,200/kW delivers an ultra-resilient LCOE of **\$40.47 to \$48.98/MWh**, largely immune to cost-of-capital surges. Conversely, new-build Gen-III+ reactors (\$7,500/kW overnight) suffer severe debt compounding: at 7.0% WACC, a 5-year delay elevates capital expenditure to **\$12,713/kW** (+69.5% IDC) and LCOE to **\$138.14/MWh**. Under high-friction merchant environments (10.0% WACC with a 7-year delay), Gen-III+ LCOE escalates to **\$204.60/MWh**—a **4.6-fold cost penalty over LTO**. We conclude that fleet life extension represents the single highest-yielding, lowest-risk decarbonization investment available to power utilities, and that new-build projects require de-risking mechanisms (Regulated Asset Base or Contracts for Difference) to compress WACC below 5.5%.

---

## 1. Introduction & Research Problem

The transition to a net-zero power grid requires reliable, dispatchable, low-carbon baseload electricity to balance variable renewable generation (solar PV and wind). While nuclear fission is virtually zero-carbon in operation ($< 12\ \mathrm{gCO_2eq/kWh}$ lifecycle emissions according to the IPCC and UNECE), its deployment faces prohibitive financial headwinds:

1. **Massive Capital Expenditure & Lumpiness**: A twin-unit Gen-III+ plant requires \$15B to \$25B of upfront commitment.
2. **Construction Lead-Time Delays**: Mega-projects suffer systemic schedule slippages (e.g., Olkiluoto 3, Flamanville 3, Vogtle 3 & 4), extending construction periods from an anticipated 5–7 years to 12–17 years.
3. **Compound Cost of Capital (IDC)**: During non-revenue-generating construction years, debt accrues interest and equity demands return. As central banks elevated sovereign bond yields post-2022, corporate utility WACCs rose from historical lows of 3–4% to 7–10%, triggering exponential capital escalation.
4. **The Impending Retirement Cliff**: Global nuclear fleets constructed during the 1970s and 1980s are approaching their 40-year regulatory licensing thresholds.

### Core Research Question
> *"Given the debt compounding (IDC) and capital erosion caused by construction lead-time delays in new reactors (Gen-III+ and SMRs), does long-term operation (LTO / life extension) of aging fleets offer a financially superior risk-adjusted return over new-build investments under rising cost-of-capital scenarios?"*

---

## 2. Empirical Fleet Data & Asset-Level Findings

### 2.1 Dataset Architecture
We utilize the Global Nuclear Power Tracker (Global Energy Monitor, August 2026 edition). The dataset tracks **1,825 unit records** across 39 attributes, capturing project milestones, reactor designs, operational statuses, geolocations, and nameplate capacities.

```
Total Tracked Assets:             1,825 reactors
Operational Fleet:                 424 reactors (407.80 GW)
Under Construction:                 85 reactors (90.89 GW)
Cancelled / Shelved:               535 reactors
Announced / Pre-Construction:      465 reactors
Retired Fleet:                     230 reactors
```

### 2.2 The 2026 Global Nuclear Age Pyramid & The 40-Year "Cliff Edge"
A critical empirical discovery is the concentration of global baseload power in mature cohorts:

$$\mathrm{Age}_{2026} = 2026 - \mathrm{Start\ Year}$$

* **Operating reactors $\ge 40$ years old:** **198 units** out of 424 (46.7% of operational units).
* **Capacity at stake:** **180.99 GW** out of 407.80 GW (**44.38% of global nuclear capacity**).
* **Geographic Concentration of Aging Fleet:**
  * Northern America (US & Canada): 78 reactors ($\ge 40$ years).
  * Western and Central Europe (France, Belgium, Switzerland, UK): 64 reactors.
  * Eastern Asia (Japan, South Korea): 38 reactors.

Without systematic 10- to 20-year Long-Term Operation licenses (supported by capital refurbishment programs such as EDF's *Grand Carénage* or the US NRC *Subsequent License Renewal - SLRA*), 181 GW of dispatchable zero-carbon generation will be forced offline by 2035, necessitating replacement by either high-emission fossil peakers or capital-intensive new builds.

### 2.3 Empirical Lead-Time Distribution
We calculated empirical construction durations:

$$\Delta t_{\mathrm{lead}} = \frac{\mathrm{COD} - \mathrm{Construction\ Start\ Date}}{365.25\ \mathrm{days}}$$

For the operating global fleet ($n = 424$), empirical distributions demonstrate:
* **Mean Construction Lead Time:** **8.76 years** (Standard Deviation: 5.32 years).
* **Median Lead Time:** **7.16 years** (IQR: 5.66 to 10.18 years).
* **90th Percentile:** **13.52 years**.

By technology:
* **Pressurized Water Reactors (PWR, $n=384$):** Median 7.14 years, Mean 8.61 years.
* **Boiling Water Reactors (BWR, $n=49$):** Median 6.42 years, Mean 7.78 years.
* **Geographic Differences:** Eastern Asia (China, South Korea) maintains a median build duration of 5.8 years due to series-effect standardization, whereas Western Europe and North America show empirical medians of 9.4 years and 10.2 years, respectively.

---

## 3. Quantitative Methodology & Financial Engineering

### 3.1 Technology Cost Benchmarks
Drawing from international benchmarking standards (IEA/NEA *Projected Costs of Generating Electricity* and EPRI), we establish base overnight capital expenditures ($\mathrm{Capex}_{\mathrm{overnight}}$):

1. **Gen-III+ Large GW Reactor (EPR-1600, AP1000, APR1400):**
   * Overnight Capex: **\$7,500 / kW**
   * Nominal Construction Duration ($T_0$): **7.0 years**
   * Economic Lifetime ($N$): **60 years**
   * Fixed O&M: \$110.0 / kW-yr; Variable O&M: \$3.0 / MWh; Fuel: \$7.5 / MWh; Capacity Factor ($\mathrm{CF}$): 88%.
2. **Small Modular Reactor (SMR First-of-a-Kind modular 300 MWe):**
   * Overnight Capex: **\$9,000 / kW**
   * Nominal Construction Duration ($T_0$): **4.0 years**
   * Economic Lifetime ($N$): **40 years**
   * Fixed O&M: \$125.0 / kW-yr; Variable O&M: \$3.5 / MWh; Fuel: \$8.5 / MWh; $\mathrm{CF}$: 88%.
3. **20-Year Long-Term Operation (LTO / Grand Carénage):**
   * Overnight Capex: **\$1,200 / kW** (steam generator replacement, reactor pressure vessel annealing, I&C upgrades).
   * Nominal Outage/Execution Duration ($T_0$): **2.0 years** (executed during staged refueling outages).
   * Economic Lifetime ($N$): **20 years**
   * Fixed O&M: \$135.0 / kW-yr (elevated maintenance for aging components); Variable O&M: \$3.0 / MWh; Fuel: \$7.0 / MWh; $\mathrm{CF}$: 85%.

### 3.2 S-Curve Expenditure Dynamics
Capital is not disbursed uniformly. We model annual capital expenditure $C_t$ over total duration $T = T_0 + \Delta t$ using a regularized incomplete Beta cumulative distribution function:

$$S(\tau) = I_\tau(\alpha, \beta) = \frac{\int_0^\tau u^{\alpha-1} (1-u)^{\beta-1} \mathrm{d}u}{\mathrm{B}(\alpha, \beta)}, \quad \tau = \frac{t}{T} \in [0, 1]$$

where $\alpha = 2.5, \beta = 2.5$. The annual disbursement fraction for year $t \in \{1, 2, \dots, T\}$ is:

$$w_t = S(t/T) - S((t-1)/T), \quad \sum_{t=1}^T w_t = 1.0$$

During construction delays ($\Delta t > 0$), fixed site overhead, engineering management, and preservation costs induce real cost escalation at rate $\lambda = 1.5\%$ per year of delay:

$$\mathrm{Capex}_{\mathrm{overnight, escalated}} = \mathrm{Capex}_{\mathrm{overnight}} \cdot (1 + \lambda \cdot \Delta t)$$

### 3.3 Interest During Construction (IDC) Compounding Formulation
Under mid-year cash flow disbursement conventions, interest accumulates exponentially up to the Commercial Operation Date ($t = T$):

$$\mathrm{Capex}_{\mathrm{total}}(T, r) = \sum_{t=1}^{T} w_t \cdot \mathrm{Capex}_{\mathrm{overnight, escalated}} \cdot (1 + r)^{T - t + 0.5}$$

$$\mathrm{IDC} = \mathrm{Capex}_{\mathrm{total}}(T, r) - \mathrm{Capex}_{\mathrm{overnight}}$$

$$\mathrm{IDC\ Escalation\ Multiplier} = \frac{\mathrm{Capex}_{\mathrm{total}}(T, r)}{\mathrm{Capex}_{\mathrm{overnight}}}$$

### 3.4 Levelized Cost of Electricity (LCOE)
The Levelized Cost of Electricity balances total lifetime costs against total electricity generation discounted at WACC $r$:

$$\mathrm{LCOE} = \frac{\mathrm{CRF}(r, N) \cdot \mathrm{Capex}_{\mathrm{total}} + \mathrm{Fixed\ O\&M}}{8760 \cdot \mathrm{CF}} + \mathrm{Variable\ O\&M} + \mathrm{Fuel\ Cost}$$

where the Capital Recovery Factor ($\mathrm{CRF}$) is:

$$\mathrm{CRF}(r, N) = \frac{r(1 + r)^N}{(1 + r)^N - 1}$$

---

## 4. Empirical Results & Sensitivity Tables

### 4.1 Capex Escalation Under Schedule Delays
The compounding interaction between WACC and construction duration is nonlinear. Table 1 details the resulting total capitalized costs per kilowatt for Gen-III+ reactors.

**Table 1: Gen-III+ Total Capitalized Capex ($\mathbf{\$/kW}$) Across Delays and WACC**
| Delay ($\Delta t$) | Total Build Time | WACC 4.0% | WACC 5.5% (US/EU) | WACC 7.0% (Base) | WACC 8.5% (EM) | WACC 10.0% |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **+0 yrs (On-Time)** | 7 yrs | \$8,468 | \$8,890 | \$9,335 | \$9,804 | \$10,297 |
| **+2 yrs Delay** | 9 yrs | \$9,198 | \$9,819 | \$10,488 | \$11,207 | \$11,983 |
| **+4 yrs Delay** | 11 yrs | \$9,985 | \$10,845 | \$11,791 | \$12,832 | \$13,979 |
| **+6 yrs Delay** | 13 yrs | \$10,832 | \$11,987 | \$13,287 | \$14,752 | \$16,403 |
| **+8 yrs Delay** | 15 yrs | \$11,745 | \$13,260 | \$15,007 | \$17,020 | \$19,343 |
| **+10 yrs Delay** | 17 yrs | \$12,731 | \$14,682 | \$16,988 | \$19,701 | \$22,897 |

*Key finding:* At 10% WACC with a 10-year delay (approximating Flamanville 3 or Vogtle), overnight capital of \$7,500/kW balloons to **\$22,897/kW**, representing a **305% total capital escalation** (IDC exceeding \$15,000/kW).

### 4.2 LCOE Sensitivity: LTO Dominance
Table 2 details the comparative Levelized Cost of Electricity.

**Table 2: LCOE Comparison ($\mathbf{\$/MWh}$) Across Strategic Pathways**
| Investment Strategy | WACC 4.0% | WACC 5.5% (Damodaran) | WACC 7.0% (Base) | WACC 8.5% (EM) | WACC 10.0% |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **20-Year LTO (On-Time, 2y)** | **\$40.47** | **\$42.34** | **\$44.42** | **\$46.66** | **\$48.98** |
| **20-Year LTO (+2y Outage Delay)**| **\$41.81** | **\$44.27** | **\$47.01** | **\$50.04** | **\$53.36** |
| **Gen-III+ (On-Time, 7y)** | \$74.18 | \$92.17 | \$113.01 | \$136.42 | \$162.35 |
| **Gen-III+ (+3y Delay, 10y)** | \$79.62 | \$101.48 | \$127.33 | \$157.69 | \$192.25 |
| **Gen-III+ (+5y Delay, 12y)** | \$83.54 | \$108.31 | \$138.14 | \$174.11 | \$215.86 |
| **Gen-III+ (+7y Delay, 14y)** | \$87.71 | \$115.65 | \$149.97 | \$192.36 | \$242.42 |
| **SMR FOAK (On-Time, 4y)** | \$92.05 | \$109.11 | \$128.65 | \$150.48 | \$173.17 |

*Key finding:* 20-Year LTO maintains an electricity generation cost of **\$40 to \$49/MWh**, remaining competitive with wholesale market prices in all regions (\$60–\$90/MWh). In contrast, on-time Gen-III+ requires a wholesale price of at least \$113/MWh at baseline 7% WACC, and \$162/MWh at 10% WACC. With realistic Western construction delays (+5 to +7 years), Gen-III+ generation costs exceed **\$140 to \$240/MWh**, rendering the asset non-viable without massive state intervention.

---

## 5. Strategic Recommendations for Utilities & Policy Levers

### 5.1 Asset Portfolio Sequencing: The "LTO First" Doctrine
Power utilities operating nuclear generation portfolios should prioritize life extensions for their existing fleets before committing capital to greenfield new builds. 
* **Capital Efficiency:** Refurbishing 1 kW of nuclear capacity through LTO costs \$1,200/kW, providing 20 years of clean baseload power at \$44/MWh. Greenfield Gen-III+ costs \$7,500–\$15,000/kW and requires 7–14 years before first generation.
* **System Preservation:** Executing LTO on the **181 GW of units older than 40 years** saves up to \$1.2 Trillion in capital requirements compared to equivalent capacity replacement by new builds.

### 5.2 Financing Architecture: Mitigating Debt Compounding
Private merchant markets cannot bear nuclear construction risk under current macroeconomic interest rates. If governments desire new nuclear capacity, policy mechanisms must compress project WACC below 5.0%:
1. **Regulated Asset Base (RAB) Model:** Applied to the UK Sizewell C project, RAB allows utilities to collect financing charges from consumers during construction, eliminating IDC accumulation and reducing financing costs by 30–45%.
2. **Contracts for Difference (CfD):** Long-term inflation-linked strike prices (e.g., Hinkley Point C) remove merchant market risk, enabling lower debt margins.
3. **Green Taxonomy Inclusions:** Formal qualification of nuclear LTO and compliant new builds under the EU Green Taxonomy and Green Bond Principles lowers debt spreads by 30–60 basis points.

---

## 6. External Data Integration & Project Expansion Opportunities

To extend this quantitative framework for future academic research, the following secondary data sources should be incorporated:

1. **Prof. Aswath Damodaran (NYU Stern) Regional Cost of Capital Tables:**
   * *Dataset:* Annual updates on Sector WACC, Cost of Equity, and Country Risk Premiums (CRP).
   * *Application:* Mapping plant-level geographic WACCs based on host country risk (e.g., US: 5.5%, France: 5.4%, India: 9.8%, Brazil: 10.4%).
2. **IEA World Energy Outlook (WEO 2025/2026) Nuclear Projections:**
   * *Dataset:* Regional overnight capex learning curves and Stated Policies Scenario (STEPS) vs. Net Zero Emissions (NZE) nuclear generation additions.
   * *Application:* Modeling learning-by-doing cost reductions for modular SMRs and series-built Gen-III+ units.
3. **IAEA Power Reactor Information System (PRIS):**
   * *Dataset:* Asset-level historical Energy Availability Factors (EAF) and unplanned outage frequencies across reactor vintages.
   * *Application:* Refining age-dependent degradation models for units operating between 40 and 60+ years.

---

## 7. Conclusion

Long-term operation (LTO) of the aging global nuclear fleet is not merely a stopgap measure; it is the economically superior, lowest-cost, and lowest-risk climate finance strategy available to power utilities today. Under rising interest rates and documented historical construction delays, new-build Gen-III+ and first-of-a-kind SMR reactors suffer severe debt compounding and capital erosion. Preserving the 181 GW of operational reactors currently approaching their 40-year design life must be the immediate focus of energy policy and utility capital allocation.

---

## References & Bibliography

1. **Global Energy Monitor (2026).** *Global Nuclear Power Tracker*, August 2026 Release.
2. **International Energy Agency (IEA) & Nuclear Energy Agency (NEA) (2020).** *Projected Costs of Generating Electricity 2020 Edition*, OECD Publishing, Paris.
3. **Damodaran, A. (2026).** *Cost of Capital by Sector (Green & Power Utilities)*, NYU Stern School of Business.
4. **Rothwell, G. (2016).** *Economics of Nuclear Power: Investment, Risks and Policy*, Routledge, London.
5. **Lovering, J. R., Yip, A., & Nordhaus, T. (2016).** Historical construction costs of global nuclear power reactors. *Energy Policy*, 91, 371–382.
6. **Electric Power Research Institute (EPRI) (2022).** *Nuclear Power Plant Life Extension and Asset Management Technical Report*.
7. **Cour des Comptes (2020).** *La filière EPR: Rapport public thématique*, République Française.
