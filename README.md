# AlpenTech GmbH – Financial Controlling Dataset

A clean, internally-consistent **synthetic financial controlling dataset** for a fictional German
industrial B2B manufacturer, built as a Power BI portfolio project targeting **Werkstudent
Controlling / Finance** roles in Germany.

## Purpose

This project demonstrates understanding of financial controlling concepts — **not** data cleaning,
fraud detection, or anomaly hunting. The dataset is intentionally clean: no duplicate keys, no
missing values, no broken foreign keys, no fabricated data-quality problems. Every variance between
budget, forecast, and actual is a **deliberate, explainable business scenario**, the kind a
controller would investigate and present in a management report.

Concepts demonstrated by the data model and the numbers it produces:

- Plan-Ist-Vergleich (budget vs. actual)
- Kostenstellenrechnung & Kostenartenrechnung
- Kostenabweichungsanalyse
- Deckungsbeitragsrechnung / Profitabilitätsanalyse (by product line and customer segment)
- Rolling forecast ("Jahreshochrechnung") and forecast accuracy
- Management KPIs: Umsatzwachstum, Kostenquote, Personalkostenquote, Materialkostenquote,
  EBIT-Marge, Budgetabweichung %

## The company

**AlpenTech GmbH** — industrial manufacturing / B2B technology, headquartered in Stuttgart,
Germany. Sells machinery components, automation systems, spare parts and engineering services to
industrial customers in Germany and neighbouring European markets (Austria, Switzerland,
Netherlands, France, Poland).

4 business units → 8 cost centers:

| Business Unit | Cost Centers |
|---|---|
| Production | 1000 Production, 2000 Procurement, 3000 Logistics |
| Sales | 4000 Sales |
| Marketing | 5000 Marketing |
| Administration | 6000 IT, 7000 HR, 8000 Finance & Administration |

## Time period

36 months, **January 2023 – December 2025**, with realistic seasonality (Q4 strength, August dip,
non-linear year-over-year growth).

## Files

| File | Description |
|---|---|
| `dim_company.csv` | Single-entity company dimension |
| `dim_date.csv` | Daily calendar, 2023-01-01 – 2025-12-31 |
| `dim_business_unit.csv` | 4 business units |
| `dim_cost_center.csv` | 8 cost centers, mapped to business units |
| `dim_account.csv` | 16-account chart of accounts (Kostenarten) |
| `dim_customer.csv` | 35 customers with segment & country |
| `dim_product.csv` | 10 products across 4 product categories |
| `fact_actual.csv` | ~16,600 transaction-level actuals |
| `fact_budget.csv` | Monthly budget at cost-center × account grain |
| `fact_forecast.csv` | Monthly rolling forecast at the same grain |
| `generate_dataset.py` | Full generation logic (run this first) |
| `validate_dataset.py` | Validation checks (run after generation) |
| `data_validation_report.md` | Generated validation results |
| `DATA_DICTIONARY.md` | Full field-by-field reference |
| `BUSINESS_LOGIC.md` | Financial assumptions, growth logic, all 8 scenarios explained |

## How to regenerate

```bash
python3 generate_dataset.py     # writes all dim_*.csv and fact_*.csv
python3 validate_dataset.py     # writes data_validation_report.md
```

Both scripts use a fixed random seed (42), so re-running produces byte-identical output.

## Sign convention

**Revenue is positive. Expenses are negative.** `SUM(amount)` over `fact_actual` equals
Betriebsergebnis (operating result) directly — no conditional logic needed for the core P&L measure.
See `BUSINESS_LOGIC.md` for the full rationale and how this extends to `fact_budget` and
`fact_forecast`.

## What this project deliberately does NOT include (yet)

Per the project scope, this phase stops at a validated, documented financial data model. It does
**not** include a Power BI file, DAX measures, or dashboard design — that is the next phase.
