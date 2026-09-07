# Geschäftslogik & finanzielle Annahmen

Dieses Dokument erklärt, **warum die Zahlen so aussehen, wie sie aussehen** – die Annahmen,
Wachstumskurven und bewussten Szenarien, die in `generate_dataset.py` eingebaut sind. Alle unten
genannten Zahlen sind die tatsächlich berechnete Ausgabe des Generators (Seed = 42), übernommen aus
`data_validation_report.md`, keine handverlesenen Illustrationen.

## 1. Ausgangsbasis

- Umsatz-Ausgangsbasis 2023: **EUR 18.000.000**, aufgeteilt in 75 % Produktumsatz / 20 %
  Serviceumsatz / 5 % sonstiger betrieblicher Ertrag.
- Kostenstruktur-Basis 2023 (als % des Umsatzes 2023): Rohstoffe 35 %, Personal 28 %,
  Logistik 4,5 %, Fremdleistungen 4 %, Energie 3 %, Abschreibungen 3,3 %, Marketing 2,5 %,
  IT & Software 2 %, Miete 1,3 %, Reisekosten 1,2 %, Beratung 1,5 %, sonstiger betrieblicher
  Aufwand 1,5 %, Versicherungen 0,7 %.
- Daraus ergibt sich eine operative Marge 2023 von rund 10–12 % – ein gesunder Ausgangspunkt,
  bevor der Kostendruck 2024–2025 sie zusammendrückt (siehe §7).

## 2. Kontenplan und Kostenstellen-Zuordnung (Kostenartenrechnung / Kostenstellenrechnung)

Kosten werden **nicht** zufällig zugeordnet. Jedes Konto wird nur den Kostenstellen belastet, die
diese Kosten realistischerweise verursachen würden:

| Konto | Kostenstellen, die darauf buchen | Verteilungsanteil |
|---|---|---|
| 5000 Rohstoffe | nur Produktion | 100 % |
| 5100 Fremdleistungen | Produktion (Wartungsverträge) 55 %, Einkauf (Lieferantenleistungen) 45 % |
| 5200 Logistik | nur Logistik | 100 % |
| 5300 Energie | Produktion 70 %, Logistik 30 % |
| 5400 Miete | nur Finanzen & Verwaltung | 100 % |
| 5500 Personal | Produktion 35 %, Einkauf 7 %, Logistik 9 %, Vertrieb 16 %, Marketing 5 %, IT 9 %, HR 8 %, Finanzen & Verwaltung 11 % |
| 5600 IT & Software | nur IT | 100 % |
| 5700 Marketing | nur Marketing | 100 % |
| 5800 Reisekosten | Vertrieb 55 %, Marketing 20 %, HR 25 % |
| 5900 Versicherungen | nur Finanzen & Verwaltung | 100 % |
| 6000 Beratung | IT 35 %, HR 30 %, Finanzen & Verwaltung 35 % |
| 6100 Abschreibungen | Produktion 65 %, IT 35 % |
| 6200 Sonstiger betrieblicher Aufwand | über alle 8 Kostenstellen verteilt, gewichtet nach Aktivität |

**Umsatz wird vollständig über die Kostenstelle Vertrieb (4000) gebucht.** Das ist eine
Vereinfachung: In diesem Modell sind Kostenstellen Kostenverantwortungsbereiche, und der Vertrieb
ist die einzige umsatztragende Stelle für das Management-Reporting – ein üblicher schlanker
Mittelstands-Aufbau, in dem Produktionskostenstellen nicht als interne Profitcenter mit
Verrechnungspreisen geführt werden.

## 3. Vorzeichenkonvention

**Umsatz = positiv, Aufwand = negativ**, in `fact_actual`, `fact_budget` und `fact_forecast`
gleichermaßen. `SUM(amount)` = Betriebsergebnis direkt. `account_type` und `account_category`
bleiben für kennzahlenbasierte KPIs verfügbar (Materialkostenquote, Personalkostenquote usw.), die
Kostenwerte als Anteil am Umsatz benötigen.

## 4. Umsatzlogik

- Saisonindex (summiert sich über das Jahr auf 12,0): Tiefpunkt im August (0,75, Betriebsferien),
  Spitzen im November/Dezember (1,10/1,09, Jahresend-Investitionen der Industrie), moderate
  Q1-Schwäche (0,95/0,95 im Jan/Feb).
- Wachstum: 2024 ≈ +6,7 % (Ist), 2025 ≈ +4,5 % (Ist) – bewusst nicht-linear, mit monatlichem
  Rauschen (±4 %, begrenzt auf ±12 %), sodass keine zwei Monate mechanisch identisch aussehen.
- Produktmix: Maschinenkomponenten und Automatisierungssysteme (Produktumsatz),
  Installation/Wartung (Serviceumsatz) und eine kleine Position sonstiger betrieblicher Ertrag
  (Schrott-/Mieteinnahmen). Automatisierungssysteme ist die neuere, schneller wachsende Linie
  (+5 %/+10 % Wachstumsanpassung auf Produktebene in 2024/2025 zusätzlich zum Kontentrend),
  während Maschinenkomponenten 2025 flach/negativ wird (siehe Szenario 5).
- Kunden: 35 Kunden über 4 Segmente (Automotive, Maschinen & Anlagen, Elektronik, sonstige
  Industrie) und 6 Länder, Pareto-artig gewichtet (`numpy.random.pareto`), sodass einige
  Schlüsselkunden einen überproportionalen Umsatzanteil tragen – wie bei einer realen
  B2B-Kundenbasis.

## 5. Kostenlogik und der Rohstoff-Produkt-Bezug

Die meisten Kostenkonten sind **Periodenkosten**: Miete, Personal, Versicherungen, Abschreibungen
usw. sind nicht an ein bestimmtes Produkt gebunden und tragen daher auf jeder Transaktion
`product_id = "PROD-NA"`.

**Rohstoffe sind die eine Ausnahme.** Direkte Materialkosten sind tatsächlich dem zurechenbar, was
gefertigt wurde, daher tragen Rohstoff-Transaktionen an der Kostenstelle Produktion eine echte
`product_id` proportional zum Umsatzgewicht des jeweiligen Produkts. Das macht einen echten
**Deckungsbeitrag I** (Umsatz − direkte Materialkosten) *je Produkt* berechenbar – nicht nur je
Kostenstelle – ohne eine vollständige Kostenrechnungs-Umlage zu erfinden.

## 6. Budgetlogik (Grundlage des Plan-Ist-Vergleichs)

Das Budget wird **zuerst** erzeugt, als glatte Planungsbasis: Basis 2023 × Wachstumsannahme des
Managements für das jeweilige Konto/Jahr, durch dieselbe Saisonkurve geführt, aber **ohne** das
Zufallsrauschen oder die Szenario-Schocks, die auf die Ist-Zahlen angewendet werden. Das spiegelt
wider, wie Jahresbudgets tatsächlich aufgestellt werden – vor Jahresbeginn, auf Basis bekannter
Saisonalität und einer Wachstums-/Inflationsannahme, aber ohne Vorwissen über die konkreten
Überraschungen, die folgen.

Die Budget-Wachstumsannahmen sind bewusst **konservativer oder schlicht falsch**, wo immer ein
Szenario eine Abweichung erzeugen soll:

- Energie-Budgetwachstum: +8 % (2024), +5 % (2025) – Ist kommt bei +35 %/+10 % an. Das Management
  hat das Ausmaß des Energiekostenanstiegs nicht budgetiert (Szenario 1).
- Marketing-Budgetwachstum: +4 %/+3 %, flach – kein kampagnenspezifischer Budgetaufschlag, weil
  die tatsächliche Kampagnen-Mehrausgabe genau das ist, was ein Controller kennzeichnen sollte
  (Szenario 2).
- Logistik-Budgetwachstum: +6 %/+5 % (nimmt an, dass Kosten mit moderatem Umsatzwachstum skalieren)
  – Ist kommt bei +14 %/+18 % an (Szenario 4/7).
- Umsatz-Budgetwachstum: Das Management budgetiert für 2025 weiterhin +7 %/+5 % Wachstum – Ist
  kommt bei nur +3 % an, d. h. die Marktabschwächung wurde zum Planungszeitpunkt nicht antizipiert.
- IT-&-Software-Budgetwachstum: +20 %/+10 % – die Cloud-/Software-Investition **ist** budgetiert
  (es ist ein geplantes Projekt), aber das Ist übersteigt es trotzdem leicht, und die Run-Rate
  bleibt länger als geplant erhöht (Szenario 6).
- Alles Übrige (Miete, Versicherungen, Abschreibungen, Fremdleistungen, Reisekosten, Beratung,
  sonstiger betrieblicher Aufwand) erhält eine Budget-Wachstumsrate nahe seinem Ist-Trend – nicht
  jede Position braucht eine dramatische Geschichte; der Großteil der GuV ist realistischerweise
  gut prognostiziert.

2023 hat keinen datensatzinternen Vorjahreswert, daher ist sein Budget einfach die Basis 2023
selbst (d. h. modelliert, als hätte ein Ist-/Budgetzyklus 2022 außerhalb des Datensatzes existiert,
was eine übliche und offengelegte Vereinfachung für einen synthetischen Datensatz mit
Einjahres-Start ist).

## 7. Forecast-Logik – "Jahreshochrechnung" (rollierender Forecast zur Jahresmitte)

Der Forecast stellt einen einzelnen rollierenden Forecast dar, erstellt zum Ende von Q2 jedes
Jahres – eine gängige deutsche Controlling-Praxis (Hochrechnung):

- **Januar–Juni**: Forecast = Ist (diese Monate sind bereits abgeschlossen, daher entspricht die
  "aktuellste Erwartung" schlicht dem, was tatsächlich passiert ist).
- **Juli–Dezember**: Forecast = Budget + 65 % × (Ist − Budget), plus kleines unabhängiges Rauschen
  (max. ±6 %). Das bedeutet, der Forecast zur Jahresmitte erfasst den Großteil, aber nicht die
  gesamte spätere Abweichung vom Budget – er ist weder eine Kopie des Budgets noch eine Kopie des
  Ist, und er ist nicht zufällig: Er ist mechanisch aus der realen Lücke zwischen Budget und Ist
  abgeleitet, abgezinst, um unvollkommene (aber richtungssichere) Voraussicht darzustellen.

Das erzeugt einen wirklich brauchbaren Ganzjahres-Vergleich des Betriebsergebnisses:

| Jahr | Budget | Forecast | Ist |
|---|---|---|---|
| 2023 | 2.070.000 | 2.192.311 | 2.152.376 |
| 2024 | 2.352.420 | 2.126.647 | 1.945.394 |
| 2025 | 2.445.968 | 1.480.260 | 1.294.247 |

Man beachte, wie der Forecast die **Richtung** der Unterschreitungen 2024 und 2025 gegenüber dem
Budget korrekt signalisiert, ihr volles Ausmaß aber weiterhin unterschätzt – genau die Art von
"wir haben es kommen sehen, aber nicht, wie schlimm es wird"-Geschichte, die eine
Forecast-Genauigkeits-Folie in einem realen Management-Bericht motiviert.

## 8. Die 8 eingebauten Controlling-Szenarien

Alle Zahlen sind die tatsächliche Generator-Ausgabe (Seed 42), keine illustrativen runden Zahlen.

**Szenario 1 – Energiekosten steigen 2024 deutlich.**
Ist: 2023 = −540.432 / 2024 = −726.365 / 2025 = −799.948.
Budget: 2023 = −540.000 / 2024 = −583.200 / 2025 = −612.360.
→ Ist übersteigt das Budget bis 2025 um **+30,6 %**.

**Szenario 2 – Marketingausgaben übersteigen das Budget während Kampagnen.**
Die monatlichen Ist-Werte 2024 (Konto 5700) springen im April (−60.879) und November (−74.852)
gegenüber einer Basis von ~−35.000 bis −43.000 in den übrigen Monaten – die Produkteinführung im
Frühjahr und die Jahresendkampagnen.

**Szenario 3 – Personalkosten steigen schrittweise.**
Ist: 2023 = −4.996.607 / 2024 = −5.361.550 / 2025 = −5.763.013 – ein stetiger Anstieg von ~7 %/6 %
pro Jahr durch Gehaltserhöhungen und Einstellungen, unternehmensweit über alle 8 Kostenstellen.

**Szenario 4 / 7 – Vertriebsumsatz wächst, aber Logistikkosten wachsen schneller; Logistik
dauerhaft über Budget.**
Ist: 2023 = −805.992 / 2024 = −919.263 / 2025 = −1.067.504.
Budget: 2023 = −810.000 / 2024 = −858.600 / 2025 = −901.530.
→ Die Abweichung gegenüber Budget weitet sich von ~0 % (2023) auf +7 % (2024) auf **+18 %** (2025)
aus, während der Umsatz im selben Zeitraum nur +6,7 %/+4,5 % gewachsen ist – die
Logistikkosteninflation (Fracht, Lagerhaltung) übersteigt klar das Geschäft, dem sie dient.

**Szenario 5 – Margendruck in einem Geschäftsbereich 2025.**
Deckungsbeitrag I (Umsatz − direkte Materialkosten) für die Produktlinie Maschinenkomponenten
(PROD-01 + PROD-02): 2023 = 4.908.113 / 2024 = 5.056.961 / **2025 = 4.656.645** – ein Rückgang,
obwohl der unternehmensweite Umsatz weiter wächst, weil sich die Rohstoffkosteninflation auf diese
Produktlinie konzentriert, während Automatisierungssysteme (die neuere Linie) weiter wächst.

**Szenario 6 – IT-Kosten steigen durch eine geplante Software-/Cloud-Investition.**
Ist Kostenstelle IT: 2023 = −1.151.009 / 2024 = −1.289.016 / 2025 = −1.416.794.
Budget Kostenstelle IT: 2023 = −1.143.000 / 2024 = −1.261.062 / 2025 = −1.347.680.
→ Das Ist läuft in beiden Jahren leicht vor einem bereits erhöhten Budget – die Investition war
geplant, aber die Umsetzung übertraf sie, und die höhere Run-Rate hielt länger an als budgetiert.

**Szenario 8 – Einkauf schlägt das Budget dauerhaft.**
Ist Einkauf: 2023 = −665.751 / 2024 = −706.632 / 2025 = −748.120.
Budget Einkauf: 2023 = −703.800 / 2024 = −738.720 / 2025 = −771.973.
→ Das Ist liegt in **allen drei Jahren** unter Budget – eine erfolgreiche
Beschaffungs-/Verhandlungsgeschichte, das positive Gegenstück zur Logistik-Überschreitung.

## 9. Was bewusst einfach gehalten ist (offenzulegende Annahmen, keine Mängel)

- Einzelne Rechtsgesellschaft, keine Mehr-Gesellschafts-Konsolidierung.
- Umsatz nur über die Kostenstelle Vertrieb gebucht, nicht nach produzierendem Geschäftsbereich
  aufgeteilt.
- Das Budget für 2023 hat keinen echten Vorjahres-Ist-Wert, aus dem es abgeleitet werden könnte
  (dokumentiert, nicht erfunden).
- Der Forecast ist ein einzelner Jahrgang (Hochrechnung zur Jahresmitte), keine vollständige
  quartalsweise rollierende Forecast-Historie – ausreichend für die Budget-/Forecast-/Ist-Analyse,
  ohne das Datenvolumen aufzublähen.
