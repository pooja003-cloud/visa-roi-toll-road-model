# Visa: The Digital Toll Road — ROIC vs WACC Analysis

A return-on-capital study of **Visa Inc. (NYSE: V)** built in Excel from SEC filings, testing whether Visa really behaves like a high-certainty "toll road" on global commerce. It covers a five-year audited history (FY21–FY25), a five-year base-case projection (FY26P–FY30P), and a like-for-like peer comparison against **Mastercard (NYSE: MA)**.

> **Thesis:** Visa earns a ~42-point spread over its cost of capital and grows with almost no new capital. Each extra revenue dollar needs only 3–4 cents of CapEx, and ~93% of free cash flow goes straight back to shareholders.

**Model file:** [`Visa_Toll_Road_Model.xlsx`](Visa_Toll_Road_Model.xlsx)

---

## Key findings (FY25, fiscal year ended Sep 30, 2025)

| Metric | Value |
|---|---|
| Net revenue | $40.0B (FY21–25 CAGR 13.5%) |
| Core take rate | 28.2 bps of payments volume (up from 23.2 bps in FY21) |
| Operating margin, ex-litigation | 66.4% (GAAP 60.0%) |
| ROIC (NOPAT / average invested capital) | **51.6%** |
| WACC | **9.7%** |
| ROIC – WACC spread | **+41.9 pts** |
| Economic profit | **$17.9B** (81% of NOPAT) |
| Capital intensity (CapEx / revenue) | 3.7% |
| FCF returned to shareholders, FY21–25 | **93%** (~78% via buybacks) |

### Five insights the model surfaces

1. **The operating leverage is in capital, not margins.** Excluding litigation, the degree of operating leverage is ~1.0x every year, so margins stay flat at 66–67%. But 68% of incremental revenue over FY21–25 became EBIT and 44% became FCF, on almost no new capital.
2. **Tangible invested capital is negative in every year** (FY25: –$4.4B). Strip out the Visa Europe goodwill and intangibles, and the network is funded by operating liabilities, not shareholders.
3. **GAAP margins are distorted by litigation.** FY25 GAAP operating margin fell to 60.0% because of a $2.6B provision for U.S. covered litigation. That cost is largely borne by legacy class B holders through the retrospective responsibility plan, which is why the analysis adds it back.
4. **Visa is returning more than it earns.** Capital returned was 112% of FCF in FY24, 106% in FY25 and 134% in the first nine months of FY26, funded by cash and new debt. About 80% is the sustainable run-rate.
5. **Mastercard's ROIC is ~2x Visa's (98% vs 52%), but Visa is the stronger engine.** The entire gap is acquisition goodwill and intangibles ($47.5B vs $15.1B, mostly the 2016 Visa Europe deal). Visa earns a 7-point higher margin and more absolute economic profit ($17.9B vs $14.1B), and the market prices both at ~35–37x earnings.

---

## Model structure

| Tab | Contents |
|---|---|
| **Tab1_Drivers** | Payments volume, transactions, revenue build (service, data processing, international, other, less client incentives), take rate, revenue yields |
| **Tab2_Core_Returns** | Income statement, GAAP vs ex-litigation EBIT, operating leverage, balance sheet, invested capital, FCF, FCF conversion, capital intensity |
| **Tab3_ROIC_WACC** | CAPM cost of equity, market cost of debt, WACC, ROIC (with and without goodwill), economic spread, economic profit, WACC and economic-profit sensitivity grids |
| **Tab4_Capital_Allocation** | Dividends, buybacks, payout ratio, dividend growth, share count, shareholder yield, FCF yield |
| **Tab5_Peer_Mastercard** | Mastercard rebuilt with identical definitions; FY25 head-to-head |
| **Data / Data_MA** | Every hardcoded input in one place, each with a source link |

**Conventions:** blue = hardcoded input from filings · black = formula · green = link to another tab · yellow = judgement-call assumption · grey columns = projections. All hardcodes live on the Data tabs; Tabs 1–5 are formulas only.

---

## Methodology

- **ROIC** = NOPAT / average invested capital, where NOPAT = EBIT ex-litigation × (1 – tax rate) and invested capital = total debt + equity – (cash + investment securities). The restricted litigation escrow is *not* treated as excess cash. FY21 tax is normalised to 17.0% (the GAAP rate of 23.4% includes a one-off ~$1.0B deferred-tax charge).
- **Operating ROIC** excludes goodwill only. Excluding intangibles as well makes the denominator negative, which is a finding in its own right.
- **WACC:** risk-free rate 5.19% (10-yr Treasury par yield, Oct 14, 2026) · Blume-adjusted beta 0.85 · ERP 5.5% (conservative; Damodaran's implied ERP was 4.20% on Oct 1, 2026) · pre-tax cost of debt 5.42% (traded yield on Visa's 4.15% 2035 notes) · market-value weights (~97% equity).
- **Take rate** = net revenue / payments volume. Visa recognises service revenue on the prior quarter's volume, so the ratio carries about one quarter of timing offset.
- **Projections (base case):** revenue is built bottom-up (volume × yield, transactions × price, input growth for international and other revenue, incentives as % of gross). FY26P is calibrated to the nine months to Jun 30, 2026. The balance sheet rolls forward from cash flows.

## Base-case projections

| | FY25 | FY26P | FY30P |
|---|---|---|---|
| Net revenue | $40.0B | $45.6B | $66.3B |
| Take rate | 28.2 bps | 29.2 bps | 31.7 bps |
| Operating margin, ex-litigation | 66.4% | 66.0% | 66.8% |
| Net income | $20.1B | $24.1B | $36.2B |
| ROIC | 51.6% | 56.6% | 74.9% |
| Economic profit | $17.9B | $21.0B | $32.0B |
| Dividend per share | $2.36 | $2.72 | $4.64 |

Projected ROIC rises because invested capital barely grows (only acquisitions of ~$0.8B a year) while NOPAT grows ~10% a year. Treat the outer years as an upper bound.

---

## Validation

- Historicals tie to the 10-K: net revenue, operating income, pre-tax income and net income reconcile to zero in every year.
- 34 key outputs (take rate, EBIT, FCF, invested capital, NOPAT, ROIC, shareholder yield) were independently recomputed outside Excel with zero mismatches. WACC was recomputed by hand.
- Projection formulas are consistent across FY26P–FY30P, and the cash and invested-capital roll-forward identities hold every year.
- Stress-tested under zero volume growth, a 14.5% WACC, opex at 40% of revenue and other cases, with no formula errors. Even in the harshest case ROIC stays above 4x WACC.
- A minimum-cash check flags any scenario where buybacks would drive projected cash below a $5B floor.

Run `python scripts/audit_model.py Visa_Toll_Road_Model.xlsx` to repeat the checks. The workbook must have been saved by Excel so that cached values exist.

---

## Data sources

- Visa Form 10-K filings FY2021–FY2025 and Q4 earnings releases (SEC EDGAR), including stockholders' equity notes for as-converted share counts and dividend rates
- Visa FY2025 Annual Report key statistics (payments volume, processed transactions)
- Visa Q3 FY2026 Form 10-Q and earnings release (share count, debt, nine-month results)
- U.S. Treasury Daily Par Yield Curve (risk-free rate)
- Aswath Damodaran, implied equity risk premium (Damodaran Online)
- SEC free-writing prospectus for Visa's 4.15% notes due 2035; traded yield from a public bond quote
- Mastercard Form 10-K FY2025, Q4 earnings releases 2022–2025 and Q2 2026 Form 10-Q
- Yahoo Finance daily history (fiscal year-end closing prices, Oct 14, 2026 closes, betas)

**Known limitations:** betas are third-party figures. FY21–22 Visa payments volume comes from a secondary source, though it is consistent with Visa's reported growth rates. Mastercard's fiscal year (December) runs 3 months later than Visa's (September). Projections ignore share-based compensation.

## Next update

Visa reports FY26 results in late October 2026 and files the 10-K in mid-November. FY26P will then be replaced with actuals.

---

*This is an independent educational analysis built from public filings. It is not investment advice.*
