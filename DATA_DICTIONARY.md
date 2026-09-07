# Data Dictionary

Star schema. See `BUSINESS_LOGIC.md` for the reasoning behind values; this document is the field
reference.

## Star schema diagram

```
                         dim_date (daily, PK: date_id / date)
                              |
dim_cost_center ──────── fact_actual ──────── dim_account
   (PK: cost_center_id)   (PK: transaction_id)   (PK: account_id)
        |                     |    |
   dim_business_unit    dim_customer  dim_product
   (PK: business_unit_id) (PK: customer_id) (PK: product_id)

fact_budget and fact_forecast share dim_date, dim_cost_center, dim_account with fact_actual
(same grain: month × cost_center × account). They do NOT carry customer_id / product_id —
budgets and forecasts are not set at that level of detail.
```

---

## dim_company

| Field | Type | Description |
|---|---|---|
| company_id | int | PK |
| company_name | string | "AlpenTech GmbH" |
| industry | string | Industrial Manufacturing / B2B Technology |
| country | string | Germany |
| hq_city | string | Stuttgart |
| currency | string | EUR |
| founded_year | int | 1998 |

Grain: 1 row (single legal entity, no consolidation).

## dim_date

| Field | Type | Description |
|---|---|---|
| date_id | int | PK, format YYYYMMDD |
| date | date (ISO) | Calendar date, join key used by all fact tables |
| year | int | 2023–2025 |
| quarter | string | "Q1"–"Q4" |
| month | int | 1–12 |
| month_name | string | "January"… |
| month_short | string | "Jan"… |
| year_month | string | "2023-01" |
| day | int | Day of month |
| day_of_week | int | 1 (Mon) – 7 (Sun) |
| day_name | string | "Monday"… |
| is_weekend | bool | True for Sat/Sun |
| is_month_start | bool | True on the 1st |
| fiscal_year | int | Equals calendar year (no fiscal-year offset) |

Grain: 1 row per calendar day, 2023-01-01 to 2025-12-31 (1,096 rows).

**Join note:** `fact_actual.date` hits daily rows (actual transaction dates, weekdays only).
`fact_budget.date` and `fact_forecast.date` hit only the first-of-month rows (`is_month_start` =
True) — a single date table serves all three fact tables.

## dim_business_unit

| Field | Type | Description |
|---|---|---|
| business_unit_id | int | PK (10/20/30/40) |
| business_unit_name | string | Production / Sales / Marketing / Administration |

## dim_cost_center

| Field | Type | Description |
|---|---|---|
| cost_center_id | int | PK (1000–8000) |
| cost_center_name | string | e.g. "Production", "IT" |
| business_unit_id | int | FK → dim_business_unit |

## dim_account

| Field | Type | Description |
|---|---|---|
| account_id | int | PK (4000–6200) |
| account_name | string | e.g. "Raw Materials" |
| account_category | string | Revenue / Material Costs / Personnel Costs / Operating Expenses / Depreciation / Other Costs |
| account_type | string | Revenue / Expense |
| cost_behavior | string | Fixed / Variable / Mixed / N/A (revenue rows) |

16 accounts total (3 revenue, 13 cost). See `BUSINESS_LOGIC.md` §2 for the full chart of accounts
and which cost centers post to each account.

## dim_customer

| Field | Type | Description |
|---|---|---|
| customer_id | string | PK, "CUST-001"…"CUST-035", plus "CUST-NA" |
| customer_name | string | Fictional company name |
| customer_segment | string | Automotive / Machinery & Equipment / Electronics / Other Industrial / N/A |
| country | string | Germany / Austria / Switzerland / Netherlands / France / Poland / N/A |

`CUST-NA` ("Not Applicable / Internal") is the placeholder used on every expense transaction, so
`fact_actual.customer_id` is never null while remaining a valid FK.

## dim_product

| Field | Type | Description |
|---|---|---|
| product_id | string | PK, "PROD-01"…"PROD-09", plus "PROD-NA" |
| product_name | string | e.g. "Automation Controller AC-500" |
| product_category | string | Machinery Components / Automation Systems / Spare Parts & Consumables / Engineering Services / Other Operating Items / N/A |

`PROD-NA` is the placeholder for all cost postings that are not product-attributable (everything
except revenue transactions and Raw Materials — see `BUSINESS_LOGIC.md` §5 for why Raw Materials is
the one cost account that does carry a product_id).

---

## fact_actual

**Grain: one row per transaction.**

| Field | Type | Description |
|---|---|---|
| transaction_id | string | PK, "TXN-000001"… |
| date | date (ISO) | FK → dim_date.date; a business day within the posting month |
| company_id | int | FK → dim_company |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| business_unit_id | int | FK → dim_business_unit (derived from cost center, denormalized for direct filtering) |
| customer_id | string | FK → dim_customer ("CUST-NA" on expense rows) |
| product_id | string | FK → dim_product ("PROD-NA" on rows that aren't revenue or Raw Materials) |
| transaction_type | string | "Revenue" or "Expense" |
| amount | float | EUR. **Positive for revenue, negative for expense.** |
| description | string | Human-readable posting text |

~16,600 rows. Foreign keys are 100% valid; no nulls.

## fact_budget

**Grain: one row per (month, cost_center, account).**

| Field | Type | Description |
|---|---|---|
| date | date (ISO) | First day of the budget month; FK → dim_date.date |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| budget_amount | float | EUR. Same sign convention as fact_actual. |

1,332 rows (36 months × the valid cost-center/account combinations — not every account applies to
every cost center; see `BUSINESS_LOGIC.md` §2).

## fact_forecast

**Grain: one row per (month, cost_center, account)** — identical grain to fact_budget, so
Budget-vs-Forecast-vs-Actual comparisons need no reshaping.

| Field | Type | Description |
|---|---|---|
| date | date (ISO) | First day of the forecast month |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| forecast_amount | float | EUR. Same sign convention. Jan–Jun = actual (closed months); Jul–Dec = revised full-year expectation (see `BUSINESS_LOGIC.md` §6). |

1,332 rows.

---

## Measures calculable from this model (no DAX written yet — see README)

Umsatz, Gesamtkosten, Betriebsergebnis, Deckungsbeitrag (by product), Kostenquote,
Personalkostenquote, Materialkostenquote, EBIT-Marge, Budgetabweichung / Budgetabweichung %,
Umsatzwachstum, Kostenwachstum, Forecast vs Budget, Forecast vs Actual, Actual YTD, Forecast
remaining year, Expected full-year result.
