# AlpenTech GmbH – Datensatz Finanzcontrolling

Ein sauberer, in sich konsistenter **synthetischer Datensatz für das Finanzcontrolling** eines
fiktiven deutschen Industrie-B2B-Herstellers, aufgebaut als Power-BI-Portfolioprojekt mit Fokus auf
**Werkstudenten-Stellen im Controlling / Finance** in Deutschland.

## Zweck

Dieses Projekt zeigt das Verständnis von Controlling-Konzepten – **nicht** Datenbereinigung,
Betrugserkennung oder Anomalie-Suche. Der Datensatz ist bewusst sauber: keine doppelten Schlüssel,
keine fehlenden Werte, keine gebrochenen Fremdschlüssel, keine künstlich erzeugten
Datenqualitätsprobleme. Jede Abweichung zwischen Budget, Forecast und Ist ist ein **bewusstes,
erklärbares Geschäftsszenario** – so, wie es ein Controller untersuchen und in einem
Management-Bericht darstellen würde.

Konzepte, die durch das Datenmodell und die daraus entstehenden Zahlen abgebildet werden:

- Plan-Ist-Vergleich (Budget vs. Ist)
- Kostenstellenrechnung & Kostenartenrechnung
- Kostenabweichungsanalyse
- Deckungsbeitragsrechnung / Profitabilitätsanalyse (nach Produktlinie und Kundensegment)
- Rollierender Forecast ("Jahreshochrechnung") und Forecast-Genauigkeit
- Management-KPIs: Umsatzwachstum, Kostenquote, Personalkostenquote, Materialkostenquote,
  EBIT-Marge, Budgetabweichung %

## Das Unternehmen

**AlpenTech GmbH** – Industrielle Fertigung / B2B-Technologie, Hauptsitz in Stuttgart,
Deutschland. Verkauft Maschinenkomponenten, Automatisierungssysteme, Ersatzteile und
Engineering-Dienstleistungen an Industriekunden in Deutschland und benachbarten europäischen
Märkten (Österreich, Schweiz, Niederlande, Frankreich, Polen).

4 Geschäftsbereiche → 8 Kostenstellen:

| Geschäftsbereich | Kostenstellen |
|---|---|
| Produktion | 1000 Produktion, 2000 Einkauf, 3000 Logistik |
| Vertrieb | 4000 Vertrieb |
| Marketing | 5000 Marketing |
| Verwaltung | 6000 IT, 7000 HR, 8000 Finanzen & Verwaltung |

## Zeitraum

36 Monate, **Januar 2023 – Dezember 2025**, mit realistischer Saisonalität (Q4-Stärke,
August-Delle, nicht-lineares Wachstum im Jahresvergleich).

## Dateien

| Datei | Beschreibung |
|---|---|
| `dim_company.csv` | Unternehmensdimension (Einzelgesellschaft) |
| `dim_date.csv` | Tageskalender, 2023-01-01 – 2025-12-31 |
| `dim_business_unit.csv` | 4 Geschäftsbereiche |
| `dim_cost_center.csv` | 8 Kostenstellen, den Geschäftsbereichen zugeordnet |
| `dim_account.csv` | Kontenplan mit 16 Konten (Kostenarten) |
| `dim_customer.csv` | 35 Kunden mit Segment & Land |
| `dim_product.csv` | 10 Produkte in 4 Produktkategorien |
| `fact_actual.csv` | ~16.600 Ist-Buchungen auf Transaktionsebene |
| `fact_budget.csv` | Monatsbudget auf Ebene Kostenstelle × Konto |
| `fact_forecast.csv` | Monatlicher rollierender Forecast auf derselben Ebene |
| `generate_dataset.py` | Vollständige Generierungslogik (zuerst ausführen) |
| `validate_dataset.py` | Validierungsprüfungen (nach der Generierung ausführen) |
| `data_validation_report.md` | Erzeugte Validierungsergebnisse |
| `DATA_DICTIONARY.md` | Vollständige feldweise Referenz |
| `BUSINESS_LOGIC.md` | Finanzielle Annahmen, Wachstumslogik, alle 8 Szenarien erklärt |

## Neu erzeugen

```bash
python3 generate_dataset.py     # schreibt alle dim_*.csv und fact_*.csv
python3 validate_dataset.py     # schreibt data_validation_report.md
```

Beide Skripte verwenden einen festen Zufalls-Seed (42), sodass ein erneuter Lauf byte-identische
Ausgaben erzeugt.

## Vorzeichenkonvention

**Umsatz ist positiv. Aufwendungen sind negativ.** `SUM(amount)` über `fact_actual` ergibt direkt
das Betriebsergebnis – ohne bedingte Logik für die Kern-GuV-Kennzahl. Siehe `BUSINESS_LOGIC.md`
für die vollständige Begründung und wie sich das auf `fact_budget` und `fact_forecast` überträgt.

## Was dieses Projekt bewusst (noch) NICHT enthält

Gemäß Projektumfang endet diese Phase bei einem validierten, dokumentierten Finanzdatenmodell. Sie
enthält **keine** Power-BI-Datei, keine DAX-Measures und kein Dashboard-Design – das ist die
nächste Phase.
