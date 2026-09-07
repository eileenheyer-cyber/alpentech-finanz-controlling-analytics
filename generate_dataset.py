"""
AlpenTech GmbH - Synthetic Financial Controlling Dataset Generator
=====================================================================

Generates a clean, internally-consistent star-schema dataset for a fictional
German industrial B2B manufacturer, covering 36 months (2023-01 to 2025-12).

Sign convention: Revenue amounts are POSITIVE, Expense amounts are NEGATIVE.
SUM(amount) over fact_actual therefore equals Betriebsergebnis directly.

See BUSINESS_LOGIC.md for the full financial-modeling rationale behind every
growth rate, seasonality curve and scenario built into this generator.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
import calendar
import os

SEED = 42
rng = np.random.default_rng(SEED)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 1. TIME AXIS
# ---------------------------------------------------------------------------

YEARS = [2023, 2024, 2025]
MONTHS = [(y, m) for y in YEARS for m in range(1, 13)]  # 36 (year, month) tuples

def month_start(y, m):
    return date(y, m, 1)

def days_in_month(y, m):
    return calendar.monthrange(y, m)[1]

# Seasonality index per calendar month, sums to 12.00 across the year.
SEASONALITY = {
    1: 0.95, 2: 0.95, 3: 1.02, 4: 1.00, 5: 1.00, 6: 1.03,
    7: 0.98, 8: 0.75, 9: 1.05, 10: 1.08, 11: 1.10, 12: 1.09,
}
assert abs(sum(SEASONALITY.values()) - 12.00) < 1e-9

# Marketing campaign months get an extra ACTUAL-side (not budget-side) multiplier
MARKETING_CAMPAIGN_MONTHS = {4: 1.55, 5: 1.35, 11: 1.65}  # spring launch + year-end campaign

# ---------------------------------------------------------------------------
# 2. DIMENSION MASTER DATA
# ---------------------------------------------------------------------------

COMPANY = dict(
    company_id=1,
    company_name="AlpenTech GmbH",
    industry="Industrial Manufacturing / B2B Technology",
    country="Germany",
    hq_city="Stuttgart",
    currency="EUR",
    founded_year=1998,
)

BUSINESS_UNITS = [
    dict(business_unit_id=10, business_unit_name="Production"),
    dict(business_unit_id=20, business_unit_name="Sales"),
    dict(business_unit_id=30, business_unit_name="Marketing"),
    dict(business_unit_id=40, business_unit_name="Administration"),
]

COST_CENTERS = [
    dict(cost_center_id=1000, cost_center_name="Production", business_unit_id=10),
    dict(cost_center_id=2000, cost_center_name="Procurement", business_unit_id=10),
    dict(cost_center_id=3000, cost_center_name="Logistics", business_unit_id=10),
    dict(cost_center_id=4000, cost_center_name="Sales", business_unit_id=20),
    dict(cost_center_id=5000, cost_center_name="Marketing", business_unit_id=30),
    dict(cost_center_id=6000, cost_center_name="IT", business_unit_id=40),
    dict(cost_center_id=7000, cost_center_name="HR", business_unit_id=40),
    dict(cost_center_id=8000, cost_center_name="Finance & Administration", business_unit_id=40),
]

ACCOUNTS = [
    dict(account_id=4000, account_name="Product Revenue", account_category="Revenue", account_type="Revenue", cost_behavior="N/A"),
    dict(account_id=4100, account_name="Service Revenue", account_category="Revenue", account_type="Revenue", cost_behavior="N/A"),
    dict(account_id=4200, account_name="Other Operating Revenue", account_category="Revenue", account_type="Revenue", cost_behavior="N/A"),
    dict(account_id=5000, account_name="Raw Materials", account_category="Material Costs", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=5100, account_name="External Services", account_category="Operating Expenses", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=5200, account_name="Logistics", account_category="Operating Expenses", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=5300, account_name="Energy", account_category="Operating Expenses", account_type="Expense", cost_behavior="Mixed"),
    dict(account_id=5400, account_name="Rent", account_category="Operating Expenses", account_type="Expense", cost_behavior="Fixed"),
    dict(account_id=5500, account_name="Personnel", account_category="Personnel Costs", account_type="Expense", cost_behavior="Fixed"),
    dict(account_id=5600, account_name="IT & Software", account_category="Operating Expenses", account_type="Expense", cost_behavior="Mixed"),
    dict(account_id=5700, account_name="Marketing", account_category="Operating Expenses", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=5800, account_name="Travel", account_category="Operating Expenses", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=5900, account_name="Insurance", account_category="Operating Expenses", account_type="Expense", cost_behavior="Fixed"),
    dict(account_id=6000, account_name="Consulting", account_category="Operating Expenses", account_type="Expense", cost_behavior="Variable"),
    dict(account_id=6100, account_name="Depreciation", account_category="Depreciation", account_type="Expense", cost_behavior="Fixed"),
    dict(account_id=6200, account_name="Other Operating Expenses", account_category="Other Costs", account_type="Expense", cost_behavior="Mixed"),
]
ACCOUNTS_BY_ID = {a["account_id"]: a for a in ACCOUNTS}

# Product categories -> revenue account mapping
PRODUCTS = [
    dict(product_id="PROD-01", product_name="CNC Mounting Frame X200", product_category="Machinery Components", revenue_account_id=4000),
    dict(product_id="PROD-02", product_name="Precision Gear Assembly G12", product_category="Machinery Components", revenue_account_id=4000),
    dict(product_id="PROD-03", product_name="Automation Controller AC-500", product_category="Automation Systems", revenue_account_id=4000),
    dict(product_id="PROD-04", product_name="Robotic Arm Interface RAI-3", product_category="Automation Systems", revenue_account_id=4000),
    dict(product_id="PROD-05", product_name="Spare Parts Kit Standard", product_category="Spare Parts & Consumables", revenue_account_id=4000),
    dict(product_id="PROD-06", product_name="Spare Parts Kit Premium", product_category="Spare Parts & Consumables", revenue_account_id=4000),
    dict(product_id="PROD-07", product_name="Installation & Commissioning", product_category="Engineering Services", revenue_account_id=4100),
    dict(product_id="PROD-08", product_name="Maintenance Contract Service", product_category="Engineering Services", revenue_account_id=4100),
    dict(product_id="PROD-09", product_name="Scrap & Rental Income", product_category="Other Operating Items", revenue_account_id=4200),
    dict(product_id="PROD-NA", product_name="Not Applicable / Internal Cost", product_category="N/A", revenue_account_id=None),
]
PRODUCTS_BY_ACCOUNT = {}
for p in PRODUCTS:
    if p["revenue_account_id"] is not None:
        PRODUCTS_BY_ACCOUNT.setdefault(p["revenue_account_id"], []).append(p["product_id"])

# Relative revenue weight per product within its account (baseline 2023, sums per account below)
PRODUCT_WEIGHTS_2023 = {
    "PROD-01": 0.42, "PROD-02": 0.58,               # Product Revenue: Machinery Components ~50% combined... see below
    "PROD-03": 0.18, "PROD-04": 0.12,               # Automation Systems share of Product Revenue
    "PROD-05": 0.10, "PROD-06": 0.08,                # Spare Parts share of Product Revenue
    "PROD-07": 0.60, "PROD-08": 0.40,                # Service Revenue split
    "PROD-09": 1.00,                                 # Other Operating Revenue - single line
}
# Normalize weights within each revenue account so they sum to 1.0
_PROD_NORM = {}
for acct, prod_ids in PRODUCTS_BY_ACCOUNT.items():
    total = sum(PRODUCT_WEIGHTS_2023[p] for p in prod_ids)
    for p in prod_ids:
        _PROD_NORM[p] = PRODUCT_WEIGHTS_2023[p] / total
PRODUCT_WEIGHTS_2023 = _PROD_NORM

# Product-level annual growth multipliers (2024, 2025) relative to prior year,
# layered ON TOP of the overall Product/Service Revenue account growth.
# Machinery Components goes flat/pressured in 2025 (Scenario 5); Automation
# Systems (higher-margin, newer line) compensates by growing faster.
PRODUCT_GROWTH_ADJ = {
    "PROD-01": {2024: 1.00, 2025: 0.97},
    "PROD-02": {2024: 1.00, 2025: 0.97},
    "PROD-03": {2024: 1.05, 2025: 1.10},
    "PROD-04": {2024: 1.05, 2025: 1.10},
    "PROD-05": {2024: 1.00, 2025: 1.00},
    "PROD-06": {2024: 1.00, 2025: 1.00},
    "PROD-07": {2024: 1.00, 2025: 1.00},
    "PROD-08": {2024: 1.00, 2025: 1.00},
    "PROD-09": {2024: 1.00, 2025: 1.00},
}

CUSTOMER_SEGMENTS = ["Automotive", "Machinery & Equipment", "Electronics", "Other Industrial"]
CUSTOMER_COUNTRIES = ["Germany", "Austria", "Switzerland", "Netherlands", "France", "Poland"]
COUNTRY_WEIGHTS = [0.56, 0.12, 0.10, 0.08, 0.08, 0.06]

CUSTOMER_NAME_STEMS = [
    "Rheinmetall Komponenten", "Nordbau Systeme", "Alpin Fertigungstechnik", "BayernDrive",
    "Ruhrtal Maschinenbau", "SchwarzwaldTech", "Vogel Automotive Zulieferer", "Berlin Elektronik",
    "Hanseatic Antriebstechnik", "Elbtal Prazision", "Donau Systemtechnik", "Weser Industriebau",
    "Kraftwerk Mechatronik", "Alpenrand Logistik", "Muenchner Praezisionsteile", "Stuttgarter Antriebe",
    "Frankfurter Automationstechnik", "Sachsen Elektromechanik", "Wien Industriepartner", "Zurich Precision AG",
    "Amsterdam Machinefabriek", "Lyon Systemes Industriels", "Krakow Komponenty Przemyslowe", "Linz Antriebssysteme",
    "Basel Fertigungstechnik", "Rotterdam Machinebouw", "Toulouse Mecatronique", "Poznan Automatyka",
    "Graz Systemtechnik", "Genf Praezisionswerk", "Koeln Industriegeraete", "Dresden Mechatronik",
    "Nuernberg Fertigungssysteme", "Hamburg Antriebstechnik",
]

def build_customers():
    rows = []
    n = len(CUSTOMER_NAME_STEMS)
    countries = rng.choice(CUSTOMER_COUNTRIES, size=n, p=COUNTRY_WEIGHTS)
    segments = rng.choice(CUSTOMER_SEGMENTS, size=n)
    # Pareto-like revenue weight: a handful of key accounts, long tail of smaller ones
    raw_weights = rng.pareto(a=2.2, size=n) + 0.3
    weights = raw_weights / raw_weights.sum()
    for i, stem in enumerate(CUSTOMER_NAME_STEMS):
        rows.append(dict(
            customer_id=f"CUST-{i+1:03d}",
            customer_name=f"{stem} GmbH" if countries[i] in ("Germany", "Austria", "Switzerland") else f"{stem}",
            customer_segment=segments[i],
            country=countries[i],
            revenue_weight=weights[i],
        ))
    rows.append(dict(customer_id="CUST-NA", customer_name="Not Applicable / Internal", customer_segment="N/A", country="N/A", revenue_weight=0.0))
    return pd.DataFrame(rows)

dim_customer_df = build_customers()
_cust_active = dim_customer_df[dim_customer_df["customer_id"] != "CUST-NA"].reset_index(drop=True)

# ---------------------------------------------------------------------------
# 3. COST CENTER <-> ACCOUNT MAP with allocation shares
# ---------------------------------------------------------------------------
# Each entry: account_id -> {cost_center_id: share_of_account_total}
# Shares within one account across cost centers sum to 1.0 (except revenue,
# handled separately since 100% of revenue is booked to the Sales CC 4000).

ACCOUNT_CC_SHARES = {
    5000: {1000: 1.00},                                                   # Raw Materials -> Production only
    5100: {1000: 0.55, 2000: 0.45},                                       # External Services -> Production (maintenance) / Procurement
    5200: {3000: 1.00},                                                   # Logistics -> Logistics CC only
    5300: {1000: 0.70, 3000: 0.30},                                       # Energy -> Production / Logistics
    5400: {8000: 1.00},                                                   # Rent -> Finance & Admin
    5500: {1000: 0.35, 2000: 0.07, 3000: 0.09, 4000: 0.16, 5000: 0.05, 6000: 0.09, 7000: 0.08, 8000: 0.11},  # Personnel
    5600: {6000: 1.00},                                                   # IT & Software -> IT
    5700: {5000: 1.00},                                                   # Marketing -> Marketing CC
    5800: {4000: 0.55, 5000: 0.20, 7000: 0.25},                           # Travel -> Sales / Marketing / HR
    5900: {8000: 1.00},                                                   # Insurance -> Finance & Admin
    6000: {6000: 0.35, 7000: 0.30, 8000: 0.35},                           # Consulting -> IT / HR / Finance & Admin
    6100: {1000: 0.65, 6000: 0.35},                                       # Depreciation -> Production / IT
    6200: {1000: 0.20, 2000: 0.10, 3000: 0.12, 4000: 0.15, 5000: 0.10, 6000: 0.10, 7000: 0.08, 8000: 0.15},  # Other OpEx
}
for acct, shares in ACCOUNT_CC_SHARES.items():
    assert abs(sum(shares.values()) - 1.00) < 1e-9, acct

REVENUE_ACCOUNTS = [4000, 4100, 4200]
REVENUE_CC = 4000  # all revenue booked through the Sales cost center

# 2023 baseline revenue split across the three revenue accounts
REVENUE_ACCOUNT_SPLIT_2023 = {4000: 0.75, 4100: 0.20, 4200: 0.05}

# ---------------------------------------------------------------------------
# 4. FINANCIAL BASELINE & GROWTH ASSUMPTIONS
# ---------------------------------------------------------------------------

ANNUAL_REVENUE_BASELINE_2023 = 18_000_000.0

# Cost accounts as % of 2023 annual revenue (baseline cost structure)
COST_SHARE_OF_REVENUE_2023 = {
    5000: 0.35, 5100: 0.04, 5200: 0.045, 5300: 0.030, 5400: 0.013,
    5500: 0.28, 5600: 0.020, 5700: 0.025, 5800: 0.012, 5900: 0.007,
    6000: 0.015, 6100: 0.033, 6200: 0.015,
}

# ---- BUDGET-side annual growth multipliers (management's planning assumptions) ----
BUDGET_GROWTH = {
    "revenue_total": {2024: 1.070, 2025: 1.050},
    4000: {2024: 1.070, 2025: 1.050}, 4100: {2024: 1.070, 2025: 1.050}, 4200: {2024: 1.030, 2025: 1.020},
    5000: {2024: 1.06, 2025: 1.05},
    5100: {2024: 1.05, 2025: 1.04},
    5200: {2024: 1.06, 2025: 1.05},
    5300: {2024: 1.08, 2025: 1.05},
    5400: {2024: 1.02, 2025: 1.02},
    5500: {2024: 1.05, 2025: 1.05},
    5600: {2024: 1.20, 2025: 1.10},
    5700: {2024: 1.04, 2025: 1.03},
    5800: {2024: 1.05, 2025: 1.04},
    5900: {2024: 1.03, 2025: 1.03},
    6000: {2024: 1.06, 2025: 1.05},
    6100: {2024: 1.08, 2025: 1.06},
    6200: {2024: 1.04, 2025: 1.04},
}

# ---- ACTUAL-side "true" annual growth multipliers ----
ACTUAL_GROWTH = {
    4000: {2024: 1.075, 2025: 1.030}, 4100: {2024: 1.080, 2025: 1.035}, 4200: {2024: 1.040, 2025: 1.010},
    5000: {2024: 1.09, 2025: 1.07},
    5100: {2024: 1.05, 2025: 1.06},
    5200: {2024: 1.14, 2025: 1.18},   # Scenario 4/7: logistics outgrows revenue
    5300: {2024: 1.35, 2025: 1.10},   # Scenario 1: energy spike
    5400: {2024: 1.02, 2025: 1.02},
    5500: {2024: 1.07, 2025: 1.06},   # Scenario 3: gradual personnel growth
    5600: {2024: 1.25, 2025: 1.15},   # Scenario 6: cloud/software investment overshoot
    5700: {2024: 1.04, 2025: 1.03},   # base trend; campaign spikes layered separately (Scenario 2)
    5800: {2024: 1.06, 2025: 1.04},
    5900: {2024: 1.03, 2025: 1.03},
    6000: {2024: 1.08, 2025: 1.05},
    6100: {2024: 1.10, 2025: 1.08},
    6200: {2024: 1.04, 2025: 1.04},
}

# Procurement-specific savings factor applied to actual (Scenario 8): consistently
# under its own trend on the accounts it owns at that cost center.
PROCUREMENT_SAVINGS_FACTOR = 0.90  # -10% vs normal trend, every year

# Small bounded random noise applied to every actual monthly figure (normal business variation)
NOISE_STD = 0.04
NOISE_CLIP = 0.12

def apply_noise(value):
    n = rng.normal(0, NOISE_STD)
    n = float(np.clip(n, -NOISE_CLIP, NOISE_CLIP))
    return value * (1 + n)

# ---------------------------------------------------------------------------
# 5. BUILD MONTHLY (CC, ACCOUNT) TARGET TABLES  -- BUDGET & ACTUAL
# ---------------------------------------------------------------------------

def year_mult(table, key, year):
    if year == 2023:
        return 1.0
    m = 1.0
    for y in range(2024, year + 1):
        m *= table[key].get(y, 1.0)
    return m

records_budget = []
records_actual_target = []  # monthly (cc, account) actual target BEFORE transaction split, WITH product/customer breakdown for revenue & raw materials

for (y, m) in MONTHS:
    season = SEASONALITY[m]

    # ---------------- REVENUE ----------------
    for racc in REVENUE_ACCOUNTS:
        annual_base = ANNUAL_REVENUE_BASELINE_2023 * REVENUE_ACCOUNT_SPLIT_2023[racc]
        budget_annual = annual_base * year_mult(BUDGET_GROWTH, racc, y)
        actual_annual = annual_base * year_mult(ACTUAL_GROWTH, racc, y)

        budget_month = budget_annual / 12 * season
        actual_month = actual_annual / 12 * season
        actual_month = apply_noise(actual_month)

        records_budget.append(dict(year=y, month=m, cost_center_id=REVENUE_CC, account_id=racc, amount=round(budget_month, 2)))

        # split into products for this revenue account
        for pid in PRODUCTS_BY_ACCOUNT[racc]:
            w = PRODUCT_WEIGHTS_2023[pid]
            padj = PRODUCT_GROWTH_ADJ[pid].get(y, 1.0) if y > 2023 else 1.0
            # compound product-level adjustment across years already-applied via ACTUAL_GROWTH on the account;
            # product adjustment is layered multiplicatively per year on top of the account trend
            prod_mult = 1.0
            if y >= 2024:
                prod_mult *= PRODUCT_GROWTH_ADJ[pid].get(2024, 1.0)
            if y >= 2025:
                prod_mult *= PRODUCT_GROWTH_ADJ[pid].get(2025, 1.0)
            prod_amount = actual_month * w * prod_mult
            records_actual_target.append(dict(
                year=y, month=m, cost_center_id=REVENUE_CC, account_id=racc,
                product_id=pid, customer_id=None, amount=prod_amount,
            ))

    # ---------------- COST ACCOUNTS ----------------
    for acct_id, cc_shares in ACCOUNT_CC_SHARES.items():
        annual_base = ANNUAL_REVENUE_BASELINE_2023 * COST_SHARE_OF_REVENUE_2023[acct_id]
        budget_annual = annual_base * year_mult(BUDGET_GROWTH, acct_id, y)
        actual_annual = annual_base * year_mult(ACTUAL_GROWTH, acct_id, y)

        for cc_id, share in cc_shares.items():
            budget_month = budget_annual * share / 12 * season
            actual_month = actual_annual * share / 12 * season

            # Scenario 2: marketing campaign-month overspend (actual only)
            if acct_id == 5700 and m in MARKETING_CAMPAIGN_MONTHS:
                actual_month *= MARKETING_CAMPAIGN_MONTHS[m]

            # Scenario 8: Procurement consistently beats budget via sourcing savings
            if cc_id == 2000 and acct_id in (5100, 6200):
                actual_month *= PROCUREMENT_SAVINGS_FACTOR

            actual_month = apply_noise(actual_month)

            records_budget.append(dict(year=y, month=m, cost_center_id=cc_id, account_id=acct_id, amount=round(-budget_month, 2)))

            if acct_id == 5000 and cc_id == 1000:
                # Raw materials at Production: attribute to products so a genuine
                # Deckungsbeitrag I (Revenue - Material Cost) by product is possible.
                for pid in PRODUCTS_BY_ACCOUNT[4000]:  # material cost only backs physical Product Revenue lines
                    w = PRODUCT_WEIGHTS_2023[pid]
                    extra = 1.0
                    if pid in ("PROD-01", "PROD-02") and y == 2025:
                        extra = 1.06  # Scenario 5: material-cost pressure concentrated on Machinery Components in 2025
                    prod_amount = actual_month * w * extra
                    records_actual_target.append(dict(
                        year=y, month=m, cost_center_id=cc_id, account_id=acct_id,
                        product_id=pid, customer_id=None, amount=-prod_amount,
                    ))
            else:
                records_actual_target.append(dict(
                    year=y, month=m, cost_center_id=cc_id, account_id=acct_id,
                    product_id="PROD-NA", customer_id="CUST-NA", amount=-actual_month,
                ))

budget_target_df = pd.DataFrame(records_budget)
actual_target_df = pd.DataFrame(records_actual_target)

# ---------------------------------------------------------------------------
# 6. DISAGGREGATE ACTUAL MONTHLY TARGETS INTO TRANSACTIONS
# ---------------------------------------------------------------------------

TXN_COUNT_RANGE = {
    4000: (28, 42), 4100: (14, 22), 4200: (2, 4),
    5000: (9, 15), 5100: (3, 6), 5200: (7, 13), 5300: (4, 8), 5400: (1, 1),
    5500: (2, 3), 5600: (5, 9), 5700: (6, 12), 5800: (5, 9), 5900: (1, 1),
    6000: (3, 6), 6100: (1, 2), 6200: (3, 6),
}

DESCRIPTION_TEMPLATES = {
    4000: "Product revenue - {ref}",
    4100: "Service revenue - {ref}",
    4200: "Other operating revenue - {ref}",
    5000: "Raw material purchase - {cc}",
    5100: "External service invoice - {cc}",
    5200: "Freight & warehousing - {cc}",
    5300: "Energy invoice - {cc}",
    5400: "Facility rent - {cc}",
    5500: "Payroll run - {cc}",
    5600: "Software / cloud subscription - {cc}",
    5700: "Marketing campaign spend - {cc}",
    5800: "Travel expenses - {cc}",
    5900: "Insurance premium - {cc}",
    6000: "Consulting services - {cc}",
    6100: "Monthly depreciation - {cc}",
    6200: "Other operating expense - {cc}",
}

cc_name_lookup = {c["cost_center_id"]: c["cost_center_name"] for c in COST_CENTERS}
product_name_lookup = {p["product_id"]: p["product_name"] for p in PRODUCTS}
customer_name_lookup = dict(zip(_cust_active["customer_id"], _cust_active["customer_name"]))
customer_weights = dict(zip(_cust_active["customer_id"], _cust_active["revenue_weight"]))

def business_day_dates(y, m):
    ndays = days_in_month(y, m)
    all_days = [date(y, m, d) for d in range(1, ndays + 1)]
    return [d for d in all_days if d.weekday() < 5] or all_days

transactions = []
txn_seq = 1

for row in actual_target_df.itertuples(index=False):
    y, m, cc_id, acct_id, product_id, customer_id, amount = (
        row.year, row.month, row.cost_center_id, row.account_id, row.product_id, row.customer_id, row.amount
    )
    lo, hi = TXN_COUNT_RANGE[acct_id]
    n_txn = int(rng.integers(lo, hi + 1))

    weights = rng.dirichlet(np.ones(n_txn) * 2.5)
    amounts = amount * weights
    # fix rounding drift on the last transaction
    amounts = np.round(amounts, 2)
    drift = round(amount - amounts.sum(), 2)
    amounts[-1] = round(amounts[-1] + drift, 2)

    day_pool = business_day_dates(y, m)
    txn_dates = rng.choice(day_pool, size=n_txn, replace=True)

    acct_type = ACCOUNTS_BY_ID[acct_id]["account_type"]

    # customer assignment for revenue rows
    cust_ids_for_txn = [None] * n_txn
    if acct_id in REVENUE_ACCOUNTS:
        cust_ids = list(customer_weights.keys())
        cust_w = np.array(list(customer_weights.values()))
        cust_w = cust_w / cust_w.sum()
        cust_ids_for_txn = rng.choice(cust_ids, size=n_txn, p=cust_w)

    for i in range(n_txn):
        d = pd.Timestamp(txn_dates[i]).date()
        cust_id = cust_ids_for_txn[i] if cust_ids_for_txn[i] is not None else "CUST-NA"
        ref = product_name_lookup.get(product_id, "N/A") if acct_id in REVENUE_ACCOUNTS else None
        if acct_id in REVENUE_ACCOUNTS:
            desc = DESCRIPTION_TEMPLATES[acct_id].format(ref=ref)
        else:
            desc = DESCRIPTION_TEMPLATES[acct_id].format(cc=cc_name_lookup[cc_id])

        transactions.append(dict(
            transaction_id=f"TXN-{txn_seq:06d}",
            date=d.isoformat(),
            company_id=COMPANY["company_id"],
            cost_center_id=cc_id,
            account_id=acct_id,
            business_unit_id=next(c["business_unit_id"] for c in COST_CENTERS if c["cost_center_id"] == cc_id),
            customer_id=cust_id,
            product_id=product_id,
            transaction_type=acct_type,
            amount=float(amounts[i]),
            description=desc,
        ))
        txn_seq += 1

fact_actual_df = pd.DataFrame(transactions)
fact_actual_df = fact_actual_df.sort_values(["date", "transaction_id"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 7. AGGREGATE BUDGET TO FINAL fact_budget (month x cost_center x account)
# ---------------------------------------------------------------------------

budget_agg = budget_target_df.groupby(["year", "month", "cost_center_id", "account_id"], as_index=False)["amount"].sum()
budget_agg["date"] = budget_agg.apply(lambda r: month_start(int(r["year"]), int(r["month"])).isoformat(), axis=1)
fact_budget_df = budget_agg[["date", "cost_center_id", "account_id", "amount"]].rename(columns={"amount": "budget_amount"})
fact_budget_df = fact_budget_df.sort_values(["date", "cost_center_id", "account_id"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 8. BUILD fact_forecast  ("Jahreshochrechnung" mid-year rolling forecast)
# ---------------------------------------------------------------------------

actual_agg = fact_actual_df.copy()
actual_agg["year"] = pd.to_datetime(actual_agg["date"]).dt.year
actual_agg["month"] = pd.to_datetime(actual_agg["date"]).dt.month
actual_by_month = actual_agg.groupby(["year", "month", "cost_center_id", "account_id"], as_index=False)["amount"].sum()
actual_by_month = actual_by_month.rename(columns={"amount": "actual_amount"})

forecast_rows = []
merged = pd.merge(fact_budget_df.assign(
        year=lambda d: pd.to_datetime(d["date"]).dt.year,
        month=lambda d: pd.to_datetime(d["date"]).dt.month),
    actual_by_month, on=["year", "month", "cost_center_id", "account_id"], how="left")
merged["actual_amount"] = merged["actual_amount"].fillna(0.0)

FORECAST_CAPTURE_RATE = 0.65  # H2 forecast captures ~65% of the eventual actual-vs-budget deviation
FORECAST_NOISE_STD = 0.02

for row in merged.itertuples(index=False):
    if row.month <= 6:
        fc = row.actual_amount  # H1 already closed -> forecast = actual
    else:
        deviation = row.actual_amount - row.budget_amount
        fc = row.budget_amount + FORECAST_CAPTURE_RATE * deviation
        noise = rng.normal(0, FORECAST_NOISE_STD)
        fc *= (1 + float(np.clip(noise, -0.06, 0.06)))
    forecast_rows.append(dict(date=row.date, cost_center_id=row.cost_center_id, account_id=row.account_id, forecast_amount=round(fc, 2)))

fact_forecast_df = pd.DataFrame(forecast_rows).sort_values(["date", "cost_center_id", "account_id"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 9. DATE DIMENSION
# ---------------------------------------------------------------------------

start_d = date(2023, 1, 1)
end_d = date(2025, 12, 31)
all_dates = pd.date_range(start_d, end_d, freq="D")
dim_date_rows = []
for d in all_dates:
    dim_date_rows.append(dict(
        date_id=int(d.strftime("%Y%m%d")),
        date=d.date().isoformat(),
        year=d.year,
        quarter=f"Q{((d.month - 1)//3) + 1}",
        month=d.month,
        month_name=d.strftime("%B"),
        month_short=d.strftime("%b"),
        year_month=d.strftime("%Y-%m"),
        day=d.day,
        day_of_week=d.dayofweek + 1,
        day_name=d.strftime("%A"),
        is_weekend=d.dayofweek >= 5,
        is_month_start=(d.day == 1),
        fiscal_year=d.year,
    ))
dim_date_df = pd.DataFrame(dim_date_rows)

# ---------------------------------------------------------------------------
# 10. FINALIZE DIMENSION DATAFRAMES
# ---------------------------------------------------------------------------

dim_company_df = pd.DataFrame([COMPANY])
dim_business_unit_df = pd.DataFrame(BUSINESS_UNITS)
dim_cost_center_df = pd.DataFrame(COST_CENTERS)
dim_account_df = pd.DataFrame(ACCOUNTS)
dim_product_df = pd.DataFrame(PRODUCTS)[["product_id", "product_name", "product_category"]]
dim_customer_out_df = dim_customer_df[["customer_id", "customer_name", "customer_segment", "country"]]

# ---------------------------------------------------------------------------
# 11. WRITE CSVs
# ---------------------------------------------------------------------------

def w(df, name):
    path = os.path.join(OUT_DIR, name)
    df.to_csv(path, index=False)
    print(f"wrote {name}: {len(df):,} rows")

w(dim_company_df, "dim_company.csv")
w(dim_date_df, "dim_date.csv")
w(dim_business_unit_df, "dim_business_unit.csv")
w(dim_cost_center_df, "dim_cost_center.csv")
w(dim_account_df, "dim_account.csv")
w(dim_customer_out_df, "dim_customer.csv")
w(dim_product_df, "dim_product.csv")
w(fact_actual_df, "fact_actual.csv")
w(fact_budget_df, "fact_budget.csv")
w(fact_forecast_df, "fact_forecast.csv")

print("\nDone. Run validate_dataset.py next to produce data_validation_report.md")
