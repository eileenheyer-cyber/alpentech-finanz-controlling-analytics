# Forecast-Methodik – Modell vs. Praxis

Dieses Dokument erklärt zwei Dinge:

1. **Wie der Forecast in `generate_dataset.py` berechnet wird** (die Mechanik im synthetischen
   Datensatz).
2. **Wie eine Jahreshochrechnung in einem realen Controlling tatsächlich zustande kommt** – und wo
   das Modell bewusst vereinfacht.

Alle genannten Zahlen sind die tatsächliche Generator-Ausgabe (Seed = 42), übernommen aus
`data_validation_report.md`.

---

## 1. Was der Forecast in diesem Datensatz ist

Der Forecast ist **kein eigenes Szenario**. Er stellt eine **einzelne rollierende Hochrechnung**
dar, erstellt zum Ende von Q2 – eine gängige deutsche Controlling-Praxis (»Hochrechnung« /
»Forecast per Stichtag«). Er wird **mechanisch** aus Budget und Ist abgeleitet, Zeile für Zeile je
`date × cost_center × account`.

Relevanter Code: `generate_dataset.py`, Abschnitt 8 (»BUILD fact_forecast«), Zeilen ~480–510.

### 1.1 Die Formel

| Zeitraum | Regel | Begründung |
|---|---|---|
| **Januar–Juni** (`month <= 6`) | `forecast = ist` | H1 ist bereits abgeschlossen – die »aktuellste Erwartung« ist schlicht das, was passiert ist. |
| **Juli–Dezember** (`month > 6`) | `forecast = budget + 0,65 × (ist − budget)`, danach `× (1 ± Rauschen)` | Die Hochrechnung zur Jahresmitte erfasst die **Richtung** der Abweichung, aber nicht ihr volles Ausmaß. |

Konstanten im Code:

- `FORECAST_CAPTURE_RATE = 0.65` – die H2-Hochrechnung greift ca. 65 % der später tatsächlich
  eintretenden Budget-Ist-Lücke ab.
- `FORECAST_NOISE_STD = 0.02`, gekappt bei ±6 % – kleines unabhängiges Rauschen, damit der Forecast
  weder eine exakte Kopie des Budgets noch des Ist ist.

Der H2-Forecast ist also eine **abgezinste Version der realen Budget-Ist-Lücke** – bewusst
unvollkommene, aber richtungssichere Voraussicht.

### 1.2 Woher die Abweichungen kommen

Die 8 eingebauten Controlling-Szenarien (Energiekostenanstieg, Marketing-Kampagnen-Mehrausgabe,
Logistikkosteninflation usw.) stecken in den **Ist-Zahlen**, nicht im Forecast:

- `ACTUAL_GROWTH` – die »wahren« jährlichen Wachstumsmultiplikatoren, z. B. `5300: {2024: 1.35}` =
  Energie +35 % (Szenario 1).
- `BUDGET_GROWTH` – die Planungsannahmen des Managements, bewusst zu konservativ oder schlicht
  falsch, wo ein Szenario eine Abweichung erzeugen soll (Energie nur mit +8 % budgetiert).
- Monatsbezogene Schocks: `MARKETING_CAMPAIGN_MONTHS` (Szenario 2), `PROCUREMENT_SAVINGS_FACTOR`
  (Szenario 8), Materialkostendruck auf `PROD-01/02` in 2025 (Szenario 5).

Da der Forecast aus `ist − budget` abgeleitet wird, **erbt** er diese Szenario-Abweichungen mit
65 % Stärke.

### 1.3 Ergebnis auf Jahresebene (Betriebsergebnis)

| Jahr | Budget | Forecast | Ist |
|---|---|---|---|
| 2023 | 2.070.000 | 2.192.311 | 2.152.376 |
| 2024 | 2.352.420 | 2.126.647 | 1.945.394 |
| 2025 | 2.445.968 | 1.480.260 | 1.294.247 |

Der Forecast signalisiert die **Richtung** der Unterschreitungen 2024/2025 korrekt, unterschätzt
aber ihr volles Ausmaß – genau die »wir haben es kommen sehen, aber nicht, wie schlimm es wird«-
Geschichte, die eine Forecast-Genauigkeits-Folie im Management-Bericht motiviert.

---

## 2. Wie eine Hochrechnung in der Praxis erstellt wird

Das Grundgerüst ist identisch – **Ist für abgeschlossene Monate + Schätzung für den Rest des
Jahres**. Der Unterschied liegt darin, **wie die Rest-des-Jahres-Schätzung entsteht**.

### 2.1 Ist einfrieren (Year-to-Date)

Wie im Modell: Die abgeschlossenen Monate kommen unverändert aus der Buchhaltung. Kein
Ermessensspielraum.

### 2.2 Restjahr bottom-up neu schätzen (nicht per Formel)

Das ist der zentrale Unterschied. Statt `budget + 0,65 × (ist − budget)` schätzen die
Kostenstellenverantwortlichen und der Vertrieb die Monate Juli–Dezember **Position für Position**
neu:

| Bereich | Wie in der Praxis hochgerechnet wird |
|---|---|
| **Umsatz** | Aus Auftragsbestand und Vertriebs-Pipeline: bestätigte Aufträge, gewichtete Opportunities, Run-Rate der letzten Monate, bekannte Kundengewinne/-verluste, Preisänderungen. Oft »YTD-Ist + Restjahr aus dem CRM«. |
| **Variable Kosten** (Material, Logistik, Energie) | Als Satz × neue Mengenannahme, aktualisiert um bekannte Preisbewegungen (neue Lieferantenverträge, Energie-Hedges, Frachtraten). |
| **Personal** | Aus dem aktuellen Personalplan: heutige FTE + genehmigte Einstellungen + geplante Fluktuation + vereinbarte Tarif-/Gehaltsrunde. Meist die genaueste Zeile. |
| **Fixkosten** (Miete, Versicherung, Abschreibung) | Im Wesentlichen zum Plan fortgeschrieben, kaum Neuschätzung nötig. |
| **Einmaleffekte** | Projekte, Rechtsfälle, Restrukturierung, Großinstandhaltung – explizit ergänzt. |

### 2.3 Übliche Abkürzungen, wenn keine Zeit für volles Bottom-up bleibt

- **Run-Rate-Extrapolation**: die letzten 3 Monate auf das Jahr hochrechnen.
- **»Budget für den Rest des Jahres«**: H2 = Plan belassen, nur das Ist bewegt sich (verbreitet,
  aber schwach – im Kern das, was dieses Modell mit `capture_rate = 0` täte).
- **Trend + bekannte Deltas**: H2-Ist des Vorjahres × Wachstumsfaktor + Anpassungen für
  identifizierte Änderungen.
- **Treiberbasierte / rollierende Modelle**: Umsatztreiber speisen automatisch die Kostenformeln.

### 2.4 Review, Challenge, Konsolidierung

Das Controlling hinterfragt jede Einreichung (»Deine Pipeline-Abdeckung liegt bei 60 %, warum
rechnest Du 100 % hoch?«), aggregiert Kostenstellen → Geschäftsbereiche → Konzern-GuV und
stimmt gegen Cash und Bilanz ab. Mehrere Iterationen, bevor der Forecast final ist.

### 2.5 Governance

- Feste **Stichtage**: oft FC1 (nach Q1), FC2 (nach H1), FC3 (nach Q3); größere Unternehmen fahren
  einen **rollierenden 12- oder 18-Monats-Forecast**, monatlich oder quartalsweise aktualisiert.
- Freigabe durch CFO / Geschäftsführung, danach zur Jahressteuerung genutzt: Kostenstopps,
  Einstellungsstopps, Neupriorisierung von Investitionen.
- Frühere Forecasts werden aufbewahrt, und die **Forecast-Genauigkeit** (Forecast vs. späteres Ist)
  wird gemessen – dieser Rückkopplungsloop ist selbst eine Controlling-Kennzahl.

---

## 3. Wo das Modell vereinfacht

| Praxis | Dieser Datensatz |
|---|---|
| Bottom-up-Neuschätzung je Position, treiberbasiert | Eine Formel: `budget + 0,65 × (ist − budget)` |
| Urteil des Forecasters, Pipeline, Personalpläne | Keine Inputs; die »Capture Rate« 0,65 steht stellvertretend für unvollkommene Voraussicht |
| Mehrere Stichtage / rollierende Aktualisierung | Ein einzelner Jahrgang zur Jahresmitte |
| Verzerrung, Politik, Sandbagging, Optimismus | Symmetrisch, unverzerrt; nur kleines Zufallsrauschen |
| Forecast kann in beide Richtungen vom Ist abweichen | Landet stets 65 % des Wegs vom Budget zum Ist |

Der Datensatz reproduziert also **Form und Aussage** einer Hochrechnung (H1 = Ist, H2 = informierte
Schätzung, Forecast trifft die Richtung einer Abweichung, unterschätzt aber ihr Ausmaß), **ohne**
den menschlichen Forecasting-Prozess nachzubilden, der diese Zahlen in einem realen Unternehmen
erzeugt.
