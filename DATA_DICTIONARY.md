# Datenkatalog

Sternschema. Siehe `BUSINESS_LOGIC.md` für die Begründung hinter den Werten; dieses Dokument ist
die Feldreferenz.

## Sternschema-Diagramm

```
                         dim_date (täglich, PK: date_id / date)
                              |
dim_cost_center ──────── fact_actual ──────── dim_account
   (PK: cost_center_id)   (PK: transaction_id)   (PK: account_id)
        |                     |    |
   dim_business_unit    dim_customer  dim_product
   (PK: business_unit_id) (PK: customer_id) (PK: product_id)

fact_budget und fact_forecast teilen sich dim_date, dim_cost_center, dim_account mit fact_actual
(gleiche Granularität: Monat × Kostenstelle × Konto). Sie führen KEINE customer_id / product_id –
Budgets und Forecasts werden nicht auf dieser Detailebene gesetzt.
```

---

## dim_company

| Feld | Typ | Beschreibung |
|---|---|---|
| company_id | int | PK |
| company_name | string | "AlpenTech GmbH" |
| industry | string | Industrielle Fertigung / B2B-Technologie |
| country | string | Deutschland |
| hq_city | string | Stuttgart |
| currency | string | EUR |
| founded_year | int | 1998 |

Granularität: 1 Zeile (einzelne Rechtsgesellschaft, keine Konsolidierung).

## dim_date

| Feld | Typ | Beschreibung |
|---|---|---|
| date_id | int | PK, Format YYYYMMDD |
| date | date (ISO) | Kalenderdatum, Join-Schlüssel für alle Fakt-Tabellen |
| year | int | 2023–2025 |
| quarter | string | "Q1"–"Q4" |
| month | int | 1–12 |
| month_name | string | "January"… |
| month_short | string | "Jan"… |
| year_month | string | "2023-01" |
| day | int | Tag des Monats |
| day_of_week | int | 1 (Mo) – 7 (So) |
| day_name | string | "Monday"… |
| is_weekend | bool | True für Sa/So |
| is_month_start | bool | True am 1. |
| fiscal_year | int | Entspricht dem Kalenderjahr (kein Geschäftsjahres-Versatz) |

Granularität: 1 Zeile pro Kalendertag, 2023-01-01 bis 2025-12-31 (1.096 Zeilen).

**Join-Hinweis:** `fact_actual.date` trifft Tageszeilen (tatsächliche Transaktionsdaten, nur
Werktage). `fact_budget.date` und `fact_forecast.date` treffen nur die Zeilen des Monatsersten
(`is_month_start` = True) – eine einzige Datumstabelle bedient alle drei Fakt-Tabellen.

## dim_business_unit

| Feld | Typ | Beschreibung |
|---|---|---|
| business_unit_id | int | PK (10/20/30/40) |
| business_unit_name | string | Produktion / Vertrieb / Marketing / Verwaltung |

## dim_cost_center

| Feld | Typ | Beschreibung |
|---|---|---|
| cost_center_id | int | PK (1000–8000) |
| cost_center_name | string | z. B. "Production", "IT" |
| business_unit_id | int | FK → dim_business_unit |

## dim_account

| Feld | Typ | Beschreibung |
|---|---|---|
| account_id | int | PK (4000–6200) |
| account_name | string | z. B. "Raw Materials" |
| account_category | string | Revenue / Material Costs / Personnel Costs / Operating Expenses / Depreciation / Other Costs |
| account_type | string | Revenue / Expense |
| cost_behavior | string | Fixed / Variable / Mixed / N/A (Umsatzzeilen) |

16 Konten insgesamt (3 Umsatz, 13 Kosten). Siehe `BUSINESS_LOGIC.md` §2 für den vollständigen
Kontenplan und welche Kostenstellen auf welches Konto buchen.

## dim_customer

| Feld | Typ | Beschreibung |
|---|---|---|
| customer_id | string | PK, "CUST-001"…"CUST-035", plus "CUST-NA" |
| customer_name | string | Fiktiver Firmenname |
| customer_segment | string | Automotive / Machinery & Equipment / Electronics / Other Industrial / N/A |
| country | string | Deutschland / Österreich / Schweiz / Niederlande / Frankreich / Polen / N/A |

`CUST-NA` ("Not Applicable / Internal") ist der Platzhalter, der auf jeder Aufwandstransaktion
verwendet wird, sodass `fact_actual.customer_id` nie null ist und trotzdem ein gültiger FK bleibt.

## dim_product

| Feld | Typ | Beschreibung |
|---|---|---|
| product_id | string | PK, "PROD-01"…"PROD-09", plus "PROD-NA" |
| product_name | string | z. B. "Automation Controller AC-500" |
| product_category | string | Machinery Components / Automation Systems / Spare Parts & Consumables / Engineering Services / Other Operating Items / N/A |

`PROD-NA` ist der Platzhalter für alle Kostenbuchungen, die nicht produktzurechenbar sind (alles
außer Umsatztransaktionen und Rohstoffen – siehe `BUSINESS_LOGIC.md` §5 dafür, warum Rohstoffe das
eine Kostenkonto ist, das eine product_id trägt).

---

## fact_actual

**Granularität: eine Zeile pro Transaktion.**

| Feld | Typ | Beschreibung |
|---|---|---|
| transaction_id | string | PK, "TXN-000001"… |
| date | date (ISO) | FK → dim_date.date; ein Werktag innerhalb des Buchungsmonats |
| company_id | int | FK → dim_company |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| business_unit_id | int | FK → dim_business_unit (aus der Kostenstelle abgeleitet, denormalisiert zum direkten Filtern) |
| customer_id | string | FK → dim_customer ("CUST-NA" auf Aufwandszeilen) |
| product_id | string | FK → dim_product ("PROD-NA" auf Zeilen, die nicht Umsatz oder Rohstoffe sind) |
| transaction_type | string | "Revenue" oder "Expense" |
| amount | float | EUR. **Positiv für Umsatz, negativ für Aufwand.** |
| description | string | Menschenlesbarer Buchungstext |

~16.600 Zeilen. Fremdschlüssel sind zu 100 % gültig; keine Nullwerte.

## fact_budget

**Granularität: eine Zeile pro (Monat, Kostenstelle, Konto).**

| Feld | Typ | Beschreibung |
|---|---|---|
| date | date (ISO) | Erster Tag des Budgetmonats; FK → dim_date.date |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| budget_amount | float | EUR. Gleiche Vorzeichenkonvention wie fact_actual. |

1.332 Zeilen (36 Monate × die gültigen Kostenstellen-/Konto-Kombinationen – nicht jedes Konto gilt
für jede Kostenstelle; siehe `BUSINESS_LOGIC.md` §2).

## fact_forecast

**Granularität: eine Zeile pro (Monat, Kostenstelle, Konto)** – identische Granularität zu
fact_budget, sodass Budget-vs-Forecast-vs-Ist-Vergleiche keine Umformung benötigen.

| Feld | Typ | Beschreibung |
|---|---|---|
| date | date (ISO) | Erster Tag des Forecast-Monats |
| cost_center_id | int | FK → dim_cost_center |
| account_id | int | FK → dim_account |
| forecast_amount | float | EUR. Gleiche Vorzeichenkonvention. Jan–Jun = Ist (abgeschlossene Monate); Jul–Dez = revidierte Ganzjahres-Erwartung (siehe `BUSINESS_LOGIC.md` §6). |

1.332 Zeilen.

---

## Aus diesem Modell berechenbare Kennzahlen (noch kein DAX geschrieben – siehe README)

Umsatz, Gesamtkosten, Betriebsergebnis, Deckungsbeitrag (nach Produkt), Kostenquote,
Personalkostenquote, Materialkostenquote, EBIT-Marge, Budgetabweichung / Budgetabweichung %,
Umsatzwachstum, Kostenwachstum, Forecast vs Budget, Forecast vs Ist, Ist YTD, Forecast Restjahr,
erwartetes Ganzjahresergebnis.
