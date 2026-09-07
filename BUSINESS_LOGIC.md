# Business Logic & Financial Assumptions

This document explains **why the numbers look the way they do** — the assumptions, growth curves,
and deliberate scenarios built into `generate_dataset.py`. All figures quoted below are the actual
computed output of the generator (seed = 42), copied from `data_validation_report.md`, not
hand-picked illustrations.

## 1. Baseline

- 2023 annual revenue baseline: **EUR 18,000,000**, split 75% Product Revenue / 20% Service Revenue
  / 5% Other Operating Revenue.
- 2023 baseline cost structure (as % of 2023 revenue): Raw Materials 35%, Personnel 28%,
  Logistics 4.5%, External Services 4%, Energy 3%, Depreciation 3.3%, Marketing 2.5%,
  IT & Software 2%, Rent 1.3%, Travel 1.2%, Consulting 1.5%, Other OpEx 1.5%, Insurance 0.7%.
- This produces a 2023 baseline operating margin around 10–12% — a healthy starting point, before
  the cost pressures of 2024–2025 compress it (see §7).

## 2. Chart of accounts and cost-center ownership (Kostenartenrechnung / Kostenstellenrechnung)

Costs are **not** assigned randomly. Each account is booked only to the cost centers that would
realistically incur it:

| Account | Cost centers that post to it | Allocation share |
|---|---|---|
| 5000 Raw Materials | Production only | 100% |
| 5100 External Services | Production (maintenance contracts) 55%, Procurement (supplier services) 45% |
| 5200 Logistics | Logistics only | 100% |
| 5300 Energy | Production 70%, Logistics 30% |
| 5400 Rent | Finance & Administration only | 100% |
| 5500 Personnel | Production 35%, Procurement 7%, Logistics 9%, Sales 16%, Marketing 5%, IT 9%, HR 8%, Finance & Admin 11% |
| 5600 IT & Software | IT only | 100% |
| 5700 Marketing | Marketing only | 100% |
| 5800 Travel | Sales 55%, Marketing 20%, HR 25% |
| 5900 Insurance | Finance & Administration only | 100% |
| 6000 Consulting | IT 35%, HR 30%, Finance & Admin 35% |
| 6100 Depreciation | Production 65%, IT 35% |
| 6200 Other Operating Expenses | spread across all 8 cost centers, weighted by activity |

**Revenue is booked entirely through the Sales cost center (4000).** This is a simplification:
in this model, cost centers are cost-responsibility centers, and Sales is the single
revenue-owning center for management reporting — a common lean-Mittelstand setup where production
cost centers are not run as internal profit centers with transfer pricing.

## 3. Sign convention

**Revenue = positive, Expense = negative**, in `fact_actual`, `fact_budget`, and `fact_forecast`
alike. `SUM(amount)` = Betriebsergebnis directly. `account_type` and `account_category` remain
available for ratio-style KPIs (Materialkostenquote, Personalkostenquote, etc.) that need cost
values as a share of revenue.

## 4. Revenue logic

- Seasonality index (sums to 12.0 across the year): trough in August (0.75, Betriebsferien),
  peaks in November/December (1.10/1.09, year-end industrial capex), moderate Q1 softness
  (0.95/0.95 in Jan/Feb).
- Growth: 2024 ≈ +6.7% (actual), 2025 ≈ +4.5% (actual) — deliberately non-linear, with monthly
  noise (±4%, clipped at ±12%) so no two months look mechanically identical.
- Product mix: Machinery Components and Automation Systems (Product Revenue), Installation/
  Maintenance (Service Revenue), and a small Other Operating Revenue line (scrap/rental income).
  Automation Systems is the newer, faster-growing line (+5%/+10% product-level growth adjustment
  in 2024/2025 on top of the account trend) while Machinery Components goes flat/negative in 2025
  (see Scenario 5).
- Customers: 35 customers across 4 segments (Automotive, Machinery & Equipment, Electronics, Other
  Industrial) and 6 countries, weighted Pareto-style (`numpy.random.pareto`) so a handful of key
  accounts carry disproportionate revenue share, like a real B2B customer base.

## 5. Cost logic and the Raw-Materials/product link

Most cost accounts are **period costs**: Rent, Personnel, Insurance, Depreciation, etc. are not
tied to a specific product, so they carry `product_id = "PROD-NA"` on every transaction.

**Raw Materials is the one exception.** Direct material cost genuinely is attributable to what was
manufactured, so Raw Materials transactions at the Production cost center carry a real `product_id`
proportional to that product's revenue weight. This is what makes a genuine **Deckungsbeitrag I**
(Revenue − direct material cost) calculable *by product* — not just by cost center — without
inventing a full cost-accounting allocation engine.

## 6. Budget logic (Plan-Ist-Vergleich foundation)

Budget is generated **first**, as a smooth planning baseline: 2023 baseline × management's growth
assumption for that account/year, run through the same seasonality curve but **without** the random
noise or the scenario shocks applied to actuals. This mirrors how annual budgets are actually set —
before the year starts, using known seasonality and a growth/inflation assumption, but without
foresight into the specific surprises that follow.

Budget growth assumptions are deliberately **more conservative or simply wrong** wherever a scenario
is meant to produce a variance:

- Energy budget growth: +8% (2024), +5% (2025) — actual comes in at +35%/+10%. Management did not
  budget for the scale of the energy cost increase (Scenario 1).
- Marketing budget growth: +4%/+3%, flat — no campaign-specific budget uplift, because actual
  campaign overspend is exactly the thing a controller should flag (Scenario 2).
- Logistics budget growth: +6%/+5% (assumes cost scales with modest revenue growth) — actual comes
  in at +14%/+18% (Scenario 4/7).
- Revenue budget growth: management still budgets +7%/+5% growth for 2025 — actual comes in at
  only +3%, i.e. the market slowdown was not anticipated at planning time.
- IT & Software budget growth: +20%/+10% — the cloud/software investment **is** budgeted (it's a
  planned project), but actual still overshoots slightly and the run-rate stays elevated for longer
  than planned (Scenario 6).
- Everything else (Rent, Insurance, Depreciation, External Services, Travel, Consulting, Other
  OpEx) gets a budget growth rate close to its actual trend — not every line item needs a dramatic
  story; most of the P&L is, realistically, well-forecasted.

2023 has no in-dataset prior year, so its budget is simply the 2023 baseline itself (i.e., modeled
as if a 2022 actual/budget cycle existed off-dataset, which is a standard and disclosed
simplification for a single-year-start synthetic dataset).

## 7. Forecast logic — "Jahreshochrechnung" (mid-year rolling forecast)

The forecast represents a single rolling forecast produced as of end of Q2 each year — a standard
German controlling practice (Hochrechnung):

- **January–June**: forecast = actual (these months are already closed, so the "latest
  expectation" simply equals what happened).
- **July–December**: forecast = budget + 65% × (actual − budget), plus small independent noise
  (±6% max). This means the mid-year forecast catches most, but not all, of the eventual deviation
  from budget — it is neither a copy of budget nor a copy of actual, and it is not random: it is
  mechanically derived from the real gap between budget and actual, discounted to represent
  imperfect (but directionally correct) foresight.

This produces a genuinely useful full-year Betriebsergebnis comparison:

| Year | Budget | Forecast | Actual |
|---|---|---|---|
| 2023 | 2,070,000 | 2,192,311 | 2,152,376 |
| 2024 | 2,352,420 | 2,126,647 | 1,945,394 |
| 2025 | 2,445,968 | 1,480,260 | 1,294,247 |

Note how the forecast **correctly signals the direction** of the 2024 and 2025 shortfalls relative
to budget, while still under-estimating their full magnitude — exactly the kind of "we saw it
coming, but not how bad it would get" story that motivates a forecast-accuracy slide in a real
management report.

## 8. The 8 built-in controlling scenarios

All figures are the generator's actual output (seed 42), not illustrative round numbers.

**Scenario 1 — Energy costs increase significantly in 2024.**
Actual: 2023 = −540,432 / 2024 = −726,365 / 2025 = −799,948.
Budget: 2023 = −540,000 / 2024 = −583,200 / 2025 = −612,360.
→ Actual exceeds budget by **+30.6%** by 2025.

**Scenario 2 — Marketing spending exceeds budget during campaigns.**
2024 monthly actuals (account 5700) spike in April (−60,879) and November (−74,852) against a
~−35,000 to −43,000 baseline in other months — the spring product-launch and year-end campaigns.

**Scenario 3 — Personnel costs increase gradually.**
Actual: 2023 = −4,996,607 / 2024 = −5,361,550 / 2025 = −5,763,013 — a steady ~7%/6% annual increase
from salary raises and hiring, company-wide across all 8 cost centers.

**Scenario 4 / 7 — Sales revenue grows but logistics costs grow faster; Logistics consistently over
budget.**
Actual: 2023 = −805,992 / 2024 = −919,263 / 2025 = −1,067,504.
Budget: 2023 = −810,000 / 2024 = −858,600 / 2025 = −901,530.
→ Variance vs budget widens from ~0% (2023) to +7% (2024) to **+18%** (2025), while revenue grew
only +6.7%/+4.5% over the same years — logistics cost inflation (freight, warehousing) is clearly
outpacing the business it serves.

**Scenario 5 — Margin pressure in one business unit in 2025.**
Deckungsbeitrag I (Revenue − direct material cost) for the Machinery Components product line
(PROD-01 + PROD-02): 2023 = 4,908,113 / 2024 = 5,056,961 / **2025 = 4,656,645** — a decline despite
company-wide revenue still growing, because raw-material cost inflation is concentrated on this
product line while Automation Systems (the newer line) keeps growing.

**Scenario 6 — IT costs increase due to a planned software/cloud investment.**
IT cost center actual: 2023 = −1,151,009 / 2024 = −1,289,016 / 2025 = −1,416,794.
IT cost center budget: 2023 = −1,143,000 / 2024 = −1,261,062 / 2025 = −1,347,680.
→ Actual runs slightly ahead of an already-elevated budget in both years — the investment was
planned, but execution overshot and the higher run-rate persisted longer than budgeted.

**Scenario 8 — Procurement consistently outperforms budget.**
Procurement actual: 2023 = −665,751 / 2024 = −706,632 / 2025 = −748,120.
Procurement budget: 2023 = −703,800 / 2024 = −738,720 / 2025 = −771,973.
→ Actual comes in below budget in **all three years** — a successful sourcing/negotiation story,
the positive counterpart to Logistics's overrun.

## 9. What's deliberately simple (assumptions to disclose, not defects)

- Single legal entity, no multi-company consolidation.
- Revenue booked only through the Sales cost center, not split by producing business unit.
- Budget for 2023 has no true prior-year actual to derive from (documented, not fabricated).
- Forecast is a single annual vintage (mid-year Hochrechnung), not a full quarterly rolling-forecast
  history — sufficient for Budget/Forecast/Actual analysis without inflating data volume.
