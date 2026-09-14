# Business Presentation Slide Deck Outline (December Final Defense)

**Course:** Research & Emerging Topics in Data Science: Climate Risks (Fall 2026)  
**Institution:** ESSEC Business School / AIDAMS  
**Title:** Nuclear Project Finance & Fleet Life Extension (LTO): Managing Debt Compounding, Lead-Time Escalation, and Asset Renewal Risk  
**Target Duration:** 15–20 minutes + Q&A (10 slides)  
**Speakers:**
* **Climate Risk Analyst (Quant):** Quantitative modeling, dataset analytics, empirical lead times, IDC formulas, sensitivity stress testing.
* **Sustainability Consultant (Strategy):** Macro decarbonization transition, project finance structuring, policy levers (RAB, CfD, Taxonomy), executive utility recommendations.

---

## Slide 1: Title, Research Context & Team Roles
* **Visual Layout:** Clean corporate title slide; logos of ESSEC, AIDAMS; high-contrast split banner.
* **Header:** *Nuclear Project Finance & Fleet Life Extension (LTO): Managing Capital Compounding in High Cost-of-Capital Regimes*
* **Context:** Course: *Research & Emerging Topics in Data Science: Climate Risks* (Fall 2026)
* **Team Roles & Speaker Distribution:**
  * **Climate Risk Analyst (Quant Lead):** Empirical fleet econometrics, GEM dataset parsing, S-curve expenditure modeling, discrete IDC compounding, sensitivity matrices.
  * **Sustainability Consultant (Strategy Lead):** Macro grid transition, utility capital allocation, policy instruments (RAB, CfD, Taxonomy), corporate decarbonization roadmaps.
* **Speaker Notes (Consultant):**
  > *"Welcome everyone. Today, we address a multi-trillion dollar bottleneck in the global energy transition: why nuclear project finance is vulnerable to rising interest rates and delays, and why extending the life of the existing fleet is the single most capital-efficient climate investment available today."*

---

## Slide 2: The Macro Transition Problem: Baseload Decarbonization vs. Capital Frictions
* **Visual Layout:** Three-pillar infographic contrasting Grid Stability (Inertia), Capital Intensity (\$B/GW), and Macro Interest Rates (WACC 3% $\to$ 8%+).
* **Key Content:**
  * **The Grid Dilemma:** Decarbonization requires firm, dispatchable power ($< 12\ \text{gCO}_2\text{eq/kWh}$) to balance non-synchronous intermittent renewables (solar/wind).
  * **The Capital Trap:** Nuclear projects are the most capital-lumpy civil engineering projects in modern economies (\$10B to \$20B per twin-unit station).
  * **The Post-2022 Macro Shift:** Rising risk-free rates and corporate bond spreads increased utility WACCs from 3–4% to 7–10%, turning Interest During Construction (IDC) into a balance-sheet destroyer.
* **Speaker Notes (Consultant):**
  > *"Historically, nuclear economics assumed 3% capital. In a post-2022 high-rate environment, the financial penalty of spending 10 years building a reactor before earning a single dollar of revenue has become fatal for private developers."*

---

## Slide 3: The 2026 Age Cliff (181 GW / 44.4% Reinvestment Wall)
* **Visual Layout:** Full-width high-resolution chart of **Figure 2** (`outputs/figures/fig2_nuclear_age_pyramid_cliff.png`) with callout banner on the 40+ year cohort.
* **Key Quantitative Data:**
  * **Global Operating Fleet (August 2026):** 407.8 GW across 424 reactors.
  * **The 40-Year 'Cliff Edge':** **180.99 GW across 198 reactors (44.38% of global operating capacity)** is currently $\ge 40$ years old.
  * **Geographic Breakdown:** North America: 76.4 GW (78 units); Western Europe: 62.1 GW (64 units); Eastern Asia: 31.8 GW (38 units).
  * **The Looming Replacement Wall:** Without Long-Term Operation (LTO), nearly half the zero-carbon generation in Western power markets faces mandatory shutdown by 2035.
* **Speaker Notes (Quant):**
  > *"Using the GEM tracker, we uncovered that 44.4% of all operating nuclear reactors on Earth have already passed their initial 40-year design life. This is not a distant 2050 problem—this 181 GW cliff is happening right now, between 2026 and 2035."*

---

## Slide 4: Empirical Lead-Time Reality (Median 7.2y vs Tail Delays)
* **Visual Layout:** Side-by-side boxplots and stripplots from **Figure 1** (`outputs/figures/fig1_construction_durations.png`) showing technology classes and regional splits.
* **Key Quantitative Data:**
  * **Mean Historical Lead Time:** **8.76 years** (vs. 5–7 year initial budget claims).
  * **Median Lead Time:** **7.16 years**; Standard Deviation: 5.32 years.
  * **Technology Performance:** PWRs median 7.14y; BWRs median 6.42y.
  * **The Regional Divide:** Eastern Asia demonstrates strong industrial repeatability (median 5.8y), whereas Western Europe (median 9.4y) and North America (median 10.2y) suffer systemic multi-year tail delays.
* **Speaker Notes (Quant):**
  > *"When project finance models assume 5 years of construction, they fly in the face of 50 years of empirical data. In Western markets, the median build duration is over 9 years, with significant right-skewed tail delays. Delays are not black swans; they are the statistical baseline."*

---

## Slide 5: The Financial Mechanics: How Delays Compound IDC Debt
* **Visual Layout:** Exponential compounding trajectories from **Figure 3** (`outputs/figures/fig3_idc_compounding_escalation.png`) highlighting cost escalation per kW.
* **Financial Formulas & Dynamics:**
  * **S-Curve Spend:** $\tau = t/T \sim \text{Beta}(2.5, 2.5)$ spending profile.
  * **Compounded Capex:** $\text{Capex}_{\text{total}} = \sum_{t=1}^T w_t \cdot \text{Capex}_{\text{esc}} \cdot (1 + r)^{T - t + 0.5}$.
  * **The Debt Compounding Spiral:**
    * *On-Time @ 5.5% WACC (Damodaran Developed):* \$7,500/kW $\to$ **\$8,890/kW** (+18.5% IDC).
    * *+5y Delay @ 7.0% WACC:* \$7,500/kW $\to$ **\$12,713/kW** (+69.5% IDC).
    * *+7y Delay @ 10.0% WACC:* \$7,500/kW $\to$ **\$17,358/kW** (+131.4% IDC).
  * **LTO Contrast:** 20-year LTO (\$1,200/kW overnight, 2y outage) accrues only \$48 to \$148/kW in IDC, keeping total capex strictly under **\$1,350/kW**.
* **Speaker Notes (Quant):**
  > *"Notice how the curves bend upwards in Figure 3. Because interest compounds on previously disbursed capital and carrying overhead, a 7-year delay at a 10% commercial WACC turns a \$7,500/kW plant into a \$17,358/kW balance-sheet catastrophe."*

---

## Slide 6: LCOE Economic Dominance: Why 20-Year LTO is 2.5x–3.3x Superior
* **Visual Layout:** Grouped comparison bar chart from **Figure 4** (`outputs/figures/fig4_lcoe_comparison_lto_vs_newbuild.png`) benchmarked against wholesale power bands (\$60–\$90/MWh).
* **Key Economic Findings:**
  * **20-Year LTO Resilient Range:** **\$40.47 to \$48.98/MWh** across all WACC regimes (4.0% to 10.0%).
  * **Gen-III+ New Build Range:**
    * *On-Time (7% WACC):* **\$113.01/MWh** (2.54$\times$ LTO).
    * *+5y Delay (7% WACC):* **\$138.14/MWh** (2.94$\times$ LTO).
    * *+7y Delay (10% WACC):* **\$204.60/MWh** (4.54$\times$ LTO).
  * **Competitive Positioning:** LTO generates power significantly below wholesale market prices, generating massive economic rent, whereas delayed new builds require extensive government subsidies to avoid bankruptcy.
* **Speaker Notes (Consultant):**
  > *"As shown in Figure 4, LTO generates power at \$40 to \$49/MWh regardless of the macroeconomic environment. Meanwhile, new builds exceed wholesale power prices even when delivered on time, and explode past \$200/MWh when delayed."*

---

## Slide 7: The SMR Reality Check: Innovation Promise vs. Commercial Reality
* **Visual Layout:** Matrix comparing Gen-III+, SMR (Modular FOAK), and 20-year LTO across 4 metrics: Overnight Capex, Construction Lead Time, LCOE, and Commercial Maturity.
* **Key Analytical Insights:**
  * **Theoretical SMR Advantage:** Shorter construction schedule (4 years), lower absolute upfront check (\$1B–\$3B vs \$15B), modular factory repeatability.
  * **The First-of-a-Kind (FOAK) Penalty:** High initial overnight capex (**\$9,000/kW**), resulting in an on-time LCOE of **\$128.65/MWh** at 7% WACC.
  * **Current Tracker Status:** Out of 184 tracked SMRs in the dataset, only **4 units are under active construction**, while 21 units are cancelled/shelved and 123 are in early pre-construction/announced stages.
  * **Strategic Verdict:** SMRs are not ready to solve the 2026–2035 cliff. They are a post-2035 technology option that requires decades of factory learning curves.
* **Speaker Notes (Quant):**
  > *"SMRs offer modularity, but FOAK units cost \$9,000/kW and produce electricity at \$129/MWh. With only 4 commercial units currently under construction globally, SMRs cannot deploy in time to replace the 181 GW of retiring capacity."*

---

## Slide 8: Strategic Decarbonization Roadmap & Policy Levers
* **Visual Layout:** Policy toolbox diagram detailing RAB, CfD, and Green Taxonomy mechanisms.
* **Core Policy Levers to De-Risk Nuclear Finance:**
  1. **Regulated Asset Base (RAB):**
     * Consumers pay a financing charge during the construction phase.
     * Eliminates compounding IDC accumulation, reducing project WACC from 8–9% to 4.5–5.5% (e.g., UK Sizewell C).
     * Cuts total lifecycle generation costs by 35–40%.
  2. **Contracts for Difference (CfD):**
     * Guarantees long-term indexed strike prices, shielding developers from merchant power volatility and enabling high-leverage debt.
  3. **EU Green Taxonomy & Sustainable Finance Standards:**
     * Unlocks low-cost green bonds and institutional ESG liquidity, compressing debt risk spreads by 30–60 bps.
* **Speaker Notes (Consultant):**
  > *"If policymakers want new gigawatt reactors, they must eliminate merchant market risk. Regulated Asset Base models compress WACCs to 5%, eliminating IDC debt compounding and saving billions for consumers over the asset lifecycle."*

---

## Slide 9: Risk Matrix & Portfolio Stress Testing
* **Visual Layout:** 2x2 Heatmap Matrix: Execution Risk (Construction Delays) vs. Macro Financial Risk (WACC Surges).
* **Scenario Stress Testing:**
  * **Scenario 1 (The Perfect Storm):** 10% WACC + 7-year delay $\to$ Gen-III+ Capex \$17,358/kW, LCOE \$204.60/MWh $\implies$ Asset impairment & utility rating downgrade.
  * **Scenario 2 (State-De-Risked New Build):** 4.5% WACC (RAB) + on-time $\to$ Capex \$8,600/kW, LCOE \$79/MWh $\implies$ Financially viable baseload replacement.
  * **Scenario 3 (LTO Portfolio Extension):** Refurbishing 10 GW of aging fleet $\to$ Total Capex \$12.5B, LCOE \$44/MWh $\implies$ \$70B+ capital savings vs. greenfield replacement.
* **Speaker Notes (Quant):**
  > *"Our stress testing shows that private utilities cannot survive Scenario 1. LTO represents the only portfolio strategy that has zero probability of solvency-threatening capital erosion under stress."*

---

## Slide 10: Executive Recommendations for Utilities and Institutional Lenders
* **Visual Layout:** Executive action plan with 3 distinct pillars: Immediate Actions (2026–2028), Medium-Term Structuring (2028–2032), and Long-Term Horizon (Post-2035).
* **Final Strategic Takeaways:**
  1. **For Power Utilities:** Implement an immediate **"LTO First" doctrine**. Secure 10- to 20-year license renewals and execute Grand Carénage investments on all mature units to protect cash flows and zero-carbon market share.
  2. **For Energy Ministries & Regulators:** Fast-track safety authorizations for $\ge 40$-year operations; mandate RAB financing structures before committing ratepayer capital to greenfield Gen-III+ new builds.
  3. **For Infrastructure Funds & Lenders:** Prioritize LTO debt facilities as premium green bond assets (stable revenue, low execution risk); price greenfield new builds strictly with sovereign guarantees.
* **Speaker Notes (Consultant):**
  > *"To summarize: extending our existing nuclear fleet for 20 years saves \$1.1 trillion in capital, secures 181 GW of clean electricity, and generates power at \$44/MWh. It is the single best climate finance decision on the table today. Thank you, and we welcome your questions."*
