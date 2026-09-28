# AlpenTech GmbH – Datenvalidierungsbericht

Erzeugt von `validate_dataset.py`. Geprüft wird der Datenstand 2023–2025; die Prüfungen für 2026
sind in `BUSINESS_LOGIC.md` §10 aufgeführt.

## 1. Zeilenanzahl

- `dim_company`: 1 Zeile
- `dim_date`: 1.096 Zeilen
- `dim_business_unit`: 4 Zeilen
- `dim_cost_center`: 8 Zeilen
- `dim_account`: 16 Zeilen
- `dim_customer`: 35 Zeilen
- `dim_product`: 10 Zeilen
- `fact_actual`: 16.649 Zeilen
- `fact_budget`: 1.332 Zeilen
- `fact_forecast`: 1.332 Zeilen

## 2. Eindeutigkeit der Primärschlüssel

- [OK] dim_date.date_id eindeutig
- [OK] dim_cost_center.cost_center_id eindeutig
- [OK] dim_account.account_id eindeutig
- [OK] dim_customer.customer_id eindeutig
- [OK] dim_product.product_id eindeutig
- [OK] dim_business_unit.business_unit_id eindeutig
- [OK] fact_actual.transaction_id eindeutig
- [OK] fact_budget (date, cost_center_id, account_id) eindeutig
- [OK] fact_forecast (date, cost_center_id, account_id) eindeutig

## 3. Fehlende Werte

- [OK] fact_actual hat in keiner Spalte Nullwerte
- [OK] fact_budget hat in keiner Spalte Nullwerte
- [OK] fact_forecast hat in keiner Spalte Nullwerte

## 4. Referenzielle Integrität (Fremdschlüssel)

- [OK] fact_actual.cost_center_id alle gültig
- [OK] fact_actual.account_id alle gültig
- [OK] fact_actual.business_unit_id alle gültig
- [OK] fact_actual.customer_id alle gültig
- [OK] fact_actual.product_id alle gültig
- [OK] fact_actual.date alle in dim_date vorhanden
- [OK] fact_budget.cost_center_id alle gültig
- [OK] fact_budget.account_id alle gültig
- [OK] fact_budget.date alle in dim_date vorhanden
- [OK] fact_forecast.cost_center_id alle gültig
- [OK] fact_forecast.account_id alle gültig
- [OK] fact_forecast.date alle in dim_date vorhanden
- [OK] cost_center_id auf jedem zugeordneten Konto konsistent mit der Zuordnung zum Geschäftsbereich

## 5. Gültigkeit der Datumswerte

- [OK] dim_date deckt 2023-01-01 bis 2025-12-31 lückenlos ab (1.096 Tage)
- [OK] Datumswerte in fact_actual liegen zwischen 2023-01-01 und 2025-12-31
- [OK] Transaktionen in fact_actual fallen nur auf Werktage (Mo–Fr)
- [OK] Datumswerte in fact_budget/fact_forecast sind alle Monatserste

## 6. Konsistenz der Vorzeichenkonvention (Umsatz positiv / Aufwand negativ)

- [OK] fact_actual: alle Zeilen auf Umsatzkonten sind positiv
- [OK] fact_actual: alle Zeilen auf Aufwandskonten sind negativ
- [OK] fact_budget: alle Zeilen auf Umsatzkonten sind positiv
- [OK] fact_budget: alle Zeilen auf Aufwandskonten sind negativ
- [OK] fact_forecast: alle Zeilen auf Umsatzkonten sind positiv
- [OK] fact_forecast: alle Zeilen auf Aufwandskonten sind negativ

## 7. Zuordnungsregeln für Umsatz, Kunde und Produkt

- [OK] customer_id ist nur auf Umsatzzeilen inhaltlich befüllt (sonst CUST-NA)
- [OK] product_id ist auf allen Zeilen, die weder Umsatz noch Rohstoffe sind, der Platzhalter PROD-NA

## 8. Abgleich Plan vs. Ist (Jahressummen, EUR)

| Jahr | Umsatz (Ist) | Umsatz (Plan) | Gesamtkosten (Ist) | Betriebsergebnis (Ist) | Betriebsergebnis (Plan) | EBIT-Marge (Ist) |
|---|---|---|---|---|---|---|
| 2023 | 18.066.529 | 18.000.000 | −15.914.153 | 2.152.376 | 2.070.000 | 11,91 % |
| 2024 | 19.284.404 | 19.224.000 | −17.339.010 | 1.945.394 | 2.352.420 | 10,09 % |
| 2025 | 20.159.729 | 20.157.390 | −18.865.482 | 1.294.247 | 2.445.968 | 6,42 % |

## 9. Nachweis der Szenarien (wie erzeugt)

**Szenario 1 – Anstieg der Energiekosten:**
- Ist: 2023: −540.432 · 2024: −726.365 · 2025: −799.948
- Plan: 2023: −540.000 · 2024: −583.200 · 2025: −612.360
- Abweichung Ist zu Plan 2025: 30,6 %

**Szenario 2 – Mehrausgaben für Marketingkampagnen (2024 monatlich, Konto 5700):**
- Monatliche Ist-Ausgaben: Jan −37.351 · Feb −35.461 · Mär −39.079 · **Apr −60.879** · Mai −50.909 ·
  Jun −40.264 · Jul −36.263 · Aug −30.537 · Sep −43.823 · Okt −42.073 · **Nov −74.852** · Dez −40.533

**Szenario 3 – Schrittweiser Anstieg der Personalkosten:**
- Ist je Jahr: 2023: −4.996.607 · 2024: −5.361.550 · 2025: −5.763.013

**Szenario 4/7 – Logistikkosten wachsen schneller als der Umsatz, Kostenstelle dauerhaft über Plan:**
- Ist: 2023: −805.992 · 2024: −919.263 · 2025: −1.067.504
- Plan: 2023: −810.000 · 2024: −858.600 · 2025: −901.530
- Abweichung zum Plan je Jahr (%): 2023: 0,0 · 2024: 7,0 · 2025: 18,0

**Szenario 5 – Margendruck bei Maschinenkomponenten 2025 (Deckungsbeitrag I):**
- DB I (Maschinenkomponenten, PROD-01 + PROD-02) je Jahr: 2023: 4.908.113 · 2024: 5.056.961 ·
  2025: 4.656.645

**Szenario 6 – Geplante IT-/Cloud-Investition:**
- Ist Kostenstelle IT: 2023: −1.151.009 · 2024: −1.289.016 · 2025: −1.416.794
- Plan Kostenstelle IT: 2023: −1.143.000 · 2024: −1.261.062 · 2025: −1.347.680

**Szenario 8 – Einkauf schlägt den Plan dauerhaft:**
- Ist Einkauf: 2023: −665.751 · 2024: −706.632 · 2025: −748.120
- Plan Einkauf: 2023: −703.800 · 2024: −738.720 · 2025: −771.973
- Ist liegt in allen 3 Jahren unter Plan: ja

## 10. Plausibilität der Forecast-Logik

- [OK] Forecast im ersten Halbjahr entspricht dem Ist (Hochrechnung: abgeschlossene Monate)

**Betriebsergebnis Gesamtjahr: Plan vs. Forecast vs. Ist**

| Jahr | Plan | Forecast | Ist |
|---|---|---|---|
| 2023 | 2.070.000 | 2.192.311 | 2.152.376 |
| 2024 | 2.352.420 | 2.126.647 | 1.945.394 |
| 2025 | 2.445.968 | 1.480.260 | 1.294.247 |

## 11. Gesamtergebnis

**Alle Validierungsprüfungen bestanden.** Der Datensatz ist sauber, in sich konsistent und frei von
gebrochenen Fremdschlüsseln, fehlenden Werten, doppelten Schlüsseln und Verstößen gegen die
Vorzeichenkonvention.
