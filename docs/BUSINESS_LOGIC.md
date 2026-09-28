# Geschäftslogik & finanzielle Annahmen

Dieses Dokument erklärt, **warum die Zahlen so aussehen, wie sie aussehen** – die Annahmen,
Wachstumskurven und bewussten Szenarien, die in `generate_dataset.py` eingebaut sind. Alle unten
genannten Zahlen sind die tatsächlich berechnete Ausgabe des Generators (Seed = 42), übernommen aus
`data_validation_report.md`, keine handverlesenen Illustrationen. Das Geschäftsjahr 2026 wird von
`generate_2026.js` (Seed 2026) ergänzt; siehe §10.

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

## 6. Planlogik (Grundlage des Plan-Ist-Vergleichs)

Der Plan wird **zuerst** erzeugt, als glatte Planungsbasis: Basis 2023 × Wachstumsannahme des
Managements für das jeweilige Konto/Jahr, durch dieselbe Saisonkurve geführt, aber **ohne** das
Zufallsrauschen oder die Szenario-Schocks, die auf die Ist-Zahlen angewendet werden. Das spiegelt
wider, wie Jahrespläne tatsächlich aufgestellt werden – vor Jahresbeginn, auf Basis bekannter
Saisonalität und einer Wachstums-/Inflationsannahme, aber ohne Vorwissen über die konkreten
Überraschungen, die folgen. (Die Tabelle heißt technisch weiterhin `fact_budget`.)

Die Wachstumsannahmen im Plan sind bewusst **konservativer oder schlicht falsch**, wo immer ein
Szenario eine Abweichung erzeugen soll:

- Energie, Planwachstum: +8 % (2024), +5 % (2025) – das Ist kommt bei +35 %/+10 % an. Das
  Management hat das Ausmaß des Energiekostenanstiegs nicht eingeplant (Szenario 1).
- Marketing, Planwachstum: +4 %/+3 %, flach – kein kampagnenspezifischer Planaufschlag, weil die
  tatsächliche Kampagnen-Mehrausgabe genau das ist, was ein Controller kennzeichnen sollte
  (Szenario 2).
- Logistik, Planwachstum: +6 %/+5 % (nimmt an, dass die Kosten mit moderatem Umsatzwachstum
  skalieren) – das Ist kommt bei +14 %/+18 % an (Szenario 4/7).
- Umsatz, Planwachstum: Das Management plant für 2025 weiterhin +7 %/+5 % Wachstum – das Ist kommt
  bei nur +3 % an, d. h. die Marktabschwächung wurde zum Planungszeitpunkt nicht antizipiert.
- IT & Software, Planwachstum: +20 %/+10 % – die Cloud-/Software-Investition **ist** geplant (es
  ist ein geplantes Projekt), aber das Ist übersteigt sie trotzdem leicht, und die Run-Rate bleibt
  länger als geplant erhöht (Szenario 6).
- Alles Übrige (Miete, Versicherungen, Abschreibungen, Fremdleistungen, Reisekosten, Beratung,
  sonstiger betrieblicher Aufwand) erhält eine Planwachstumsrate nahe seinem Ist-Trend – nicht
  jede Position braucht eine dramatische Geschichte; der Großteil der GuV ist realistischerweise
  gut prognostiziert.

2023 hat keinen datensatzinternen Vorjahreswert, daher ist sein Plan einfach die Basis 2023 selbst
(d. h. modelliert, als hätte ein Ist-/Planzyklus 2022 außerhalb des Datensatzes existiert, was eine
übliche und offengelegte Vereinfachung für einen synthetischen Datensatz mit Einjahres-Start ist).

## 7. Forecast-Logik – Jahreshochrechnung (rollierender Forecast zur Jahresmitte)

Der Forecast stellt einen einzelnen rollierenden Forecast dar, erstellt zum Ende von Q2 jedes
Jahres – eine gängige deutsche Controlling-Praxis (Hochrechnung):

- **Januar–Juni**: Forecast = Ist (diese Monate sind bereits abgeschlossen, daher entspricht die
  „aktuellste Erwartung" schlicht dem, was tatsächlich passiert ist).
- **Juli–Dezember**: Forecast = Plan + 65 % × (Ist − Plan), plus kleines unabhängiges Rauschen
  (max. ±6 %). Der Forecast zur Jahresmitte erfasst also den Großteil, aber nicht die gesamte
  spätere Abweichung vom Plan – er ist weder eine Kopie des Plans noch eine Kopie des Ist, und er
  ist nicht zufällig: Er ist mechanisch aus der realen Lücke zwischen Plan und Ist abgeleitet,
  abgeschwächt, um unvollkommene (aber richtungssichere) Voraussicht darzustellen.

Das erzeugt einen wirklich brauchbaren Ganzjahres-Vergleich des Betriebsergebnisses:

| Jahr | Plan | Forecast | Ist |
|---|---|---|---|
| 2023 | 2.070.000 | 2.192.311 | 2.152.376 |
| 2024 | 2.352.420 | 2.126.647 | 1.945.394 |
| 2025 | 2.445.968 | 1.480.260 | 1.294.247 |
| 2026 | 2.722.099 | −107.051 | offenes Jahr (Jan–Jun: 277.532) |

Man beachte, wie der Forecast die **Richtung** der Unterschreitungen 2024 und 2025 gegenüber dem
Plan korrekt signalisiert, ihr volles Ausmaß aber weiterhin unterschätzt – genau die Art von
„wir haben es kommen sehen, aber nicht, wie schlimm es wird"-Geschichte, die eine
Forecast-Genauigkeits-Folie in einem realen Management-Bericht motiviert.

## 8. Die 8 eingebauten Controlling-Szenarien

Alle Zahlen sind die tatsächliche Generator-Ausgabe (Seed 42), keine illustrativen runden Zahlen.

**Szenario 1 – Energiekosten steigen 2024 deutlich.**
Ist: 2023 = −540.432 / 2024 = −726.365 / 2025 = −799.948.
Plan: 2023 = −540.000 / 2024 = −583.200 / 2025 = −612.360.
→ Das Ist übersteigt den Plan bis 2025 um **+30,6 %**.

**Szenario 2 – Marketingausgaben übersteigen den Plan während Kampagnen.**
Die monatlichen Ist-Werte 2024 (Konto 5700) springen im April (−60.879) und November (−74.852)
gegenüber einer Basis von ~−35.000 bis −43.000 in den übrigen Monaten – die Produkteinführung im
Frühjahr und die Jahresendkampagnen.

**Szenario 3 – Personalkosten steigen schrittweise.**
Ist: 2023 = −4.996.607 / 2024 = −5.361.550 / 2025 = −5.763.013 – ein stetiger Anstieg von ~7 %/6 %
pro Jahr durch Gehaltserhöhungen und Einstellungen, unternehmensweit über alle 8 Kostenstellen.

**Szenario 4 / 7 – Umsatz wächst, aber Logistikkosten wachsen schneller; Logistik dauerhaft über
Plan.**
Ist: 2023 = −805.992 / 2024 = −919.263 / 2025 = −1.067.504.
Plan: 2023 = −810.000 / 2024 = −858.600 / 2025 = −901.530.
→ Die Abweichung zum Plan weitet sich von ~0 % (2023) auf +7 % (2024) auf **+18 %** (2025) aus,
während der Umsatz im selben Zeitraum nur +6,7 %/+4,5 % gewachsen ist – die
Logistikkosteninflation (Fracht, Lagerhaltung) übersteigt klar das Geschäft, dem sie dient.

**Szenario 5 – Margendruck in einem Geschäftsbereich 2025.**
Deckungsbeitrag I (Umsatz − direkte Materialkosten) für die Produktlinie Maschinenkomponenten
(PROD-01 + PROD-02): 2023 = 4.908.113 / 2024 = 5.056.961 / **2025 = 4.656.645** – ein Rückgang,
obwohl der unternehmensweite Umsatz weiter wächst, weil sich die Rohstoffkosteninflation auf diese
Produktlinie konzentriert, während Automatisierungssysteme (die neuere Linie) weiter wächst.

**Szenario 6 – IT-Kosten steigen durch eine geplante Software-/Cloud-Investition.**
Ist Kostenstelle IT: 2023 = −1.151.009 / 2024 = −1.289.016 / 2025 = −1.416.794.
Plan Kostenstelle IT: 2023 = −1.143.000 / 2024 = −1.261.062 / 2025 = −1.347.680.
→ Das Ist läuft in beiden Jahren leicht vor einem bereits erhöhten Plan – die Investition war
geplant, aber die Umsetzung übertraf sie, und die höhere Run-Rate hielt länger an als geplant.

**Szenario 8 – Einkauf schlägt den Plan dauerhaft.**
Ist Einkauf: 2023 = −665.751 / 2024 = −706.632 / 2025 = −748.120.
Plan Einkauf: 2023 = −703.800 / 2024 = −738.720 / 2025 = −771.973.
→ Das Ist liegt in **allen drei Jahren** unter Plan – eine erfolgreiche
Beschaffungs-/Verhandlungsgeschichte, das positive Gegenstück zur Logistik-Überschreitung.

## 9. Was bewusst einfach gehalten ist (offenzulegende Annahmen, keine Mängel)

- Einzelne Rechtsgesellschaft, keine Mehr-Gesellschafts-Konsolidierung.
- Umsatz nur über die Kostenstelle Vertrieb gebucht, nicht nach produzierendem Geschäftsbereich
  aufgeteilt.
- Der Plan für 2023 hat keinen echten Vorjahres-Ist-Wert, aus dem er abgeleitet werden könnte
  (dokumentiert, nicht erfunden).
- Der Forecast ist ein einzelner Jahrgang (Hochrechnung zur Jahresmitte), keine vollständige
  quartalsweise rollierende Forecast-Historie – ausreichend für die Plan-/Forecast-/Ist-Analyse,
  ohne das Datenvolumen aufzublähen.
- Das Geschäftsjahr 2026 ist ein halb abgeschlossenes Jahr. Jeder Ganzjahresvergleich mit 2025
  (VJ, Veränderung zum Vorjahr) oder mit dem Ganzjahresplan vergleicht sechs Monate mit zwölf;
  2026 daher nur für Plan-vs.-Forecast-Sichten verwenden oder Januar–Juni mit Januar–Juni
  vergleichen.

## 10. Geschäftsjahr 2026 – das offene Jahr (`generate_2026.js`)

Der Datensatz steht auf dem **30. Juni 2026**: Januar–Juni sind abgeschlossen, und das Management
hat gerade seine Hochrechnung zur Jahresmitte erstellt. `generate_2026.js` ergänzt die CSV-Dateien
um 2026 mit eigenem Seed (2026), sodass sich keine Zeile von 2023–2025 ändert.

**Trend.** 2026 wiederholt jede Annahme von 2025: dieselben Plan- und Ist-Wachstumsraten je Konto,
dieselben Produktanpassungen (Maschinenkomponenten −3 %, Automatisierungssysteme +10 %, anhaltender
Materialkostendruck bei Maschinenkomponenten), Kampagnenmonate, Einkaufseinsparungen und
Saisonalität. Die Kosten wachsen daher weiter schneller als der Umsatz (Logistik +18 %, IT +15 %,
Energie +10 % gegenüber +3 % Umsatz).

**Was es für 2026 gibt:**

| Tabelle | Abdeckung 2026 |
|---|---|
| fact_budget | Ganzes Jahr, einschließlich der geplanten Produkteinführung |
| fact_actual | nur Januar–Juni |
| fact_forecast | Jan–Jun = Ist; Jul–Dez = Plan + 65 % × (Trend-Ist − Plan), Rauschen ±6 %, plus beide Ereignisse zu 100 % |
| fact_forecast_events | Die zwei Ereignisse, Aug–Dez |
| fact_tax / fact_capex / fact_working_capital | Januar–Juni |

Um den Forecast für das zweite Halbjahr abzuleiten, simuliert das Skript, wie sich das zweite
Halbjahr „tatsächlich" entwickelt – genauso wie `generate_dataset.py` für die Vorjahre –, schreibt
diese Ist-Werte aber nie.

**Ereignis 1 – neue Produktlinie, August (geplant).** PROD-10 „Smart Sensor Module SSM-1"
(Automatisierungssysteme). Der Umsatz steigt von August bis Dezember stufenweise auf 40 Tsd. /
80 Tsd. / 120 Tsd. / 160 Tsd. / 200 Tsd. (600.000), direktes Material 45 % des Umsatzes
(−270.000), Einführungsmarketing 100 Tsd. im August und 50 Tsd. im September (−150.000).
EBITDA-Nettoeffekt **+180.000**. Die Einführung war Teil des Plans und wird planmäßig
prognostiziert; sie erklärt daher nichts von der Lücke zwischen Forecast und Plan.

**Ereignis 2 – Verlust des größten Kunden, Oktober (nicht geplant).** CUST-013 Kraftwerk
Mechatronik GmbH kaufte 2025 für 5.158.132, das sind 25,6 % des Umsatzes. Die Kündigung kam im
Frühjahr 2026, nachdem der Plan erstellt war; der Plan enthält den Kunden also noch. Ab Oktober
nimmt der Forecast dessen Anteil an jedem Umsatzkonto heraus (−1.444.637), ebenso das nicht mehr
benötigte Rohmaterial (+585.295) und seinen Anteil an der Logistik (+82.457). Fixkosten bleiben,
da sie nicht innerhalb eines Quartals abgebaut werden können. EBITDA-Nettoeffekt **−776.885**,
vollständig eine Lücke zwischen Forecast und Plan.

**Ergebnis (EUR):**

| | Plan 2026 | Ist Jan–Jun | Forecast 2026 |
|---|---|---|---|
| Umsatz | 21.736.893 | 10.282.905 | 19.728.870 |
| Betriebsergebnis (EBIT) | 2.722.099 | 277.532 (Plan Jan–Jun: 1.260.457) | **−107.051** |

AlpenTech rutscht im Forecast 2026 in einen operativen Verlust: Der anhaltende Kostentrend zehrt
die Marge auf, und der Kundenverlust drückt das Ergebnis unter null.

**Steuern.** 29,825 % des monatlichen EBIT (15,825 % Körperschaftsteuer inkl.
Solidaritätszuschlag, 14 % Gewerbesteuer), wie 2023–2025. Januar und Mai 2026 sind Verlustmonate
und tragen null Steuern, keine Erstattung. Summe H1: −98.395.

**Investitionen und Working Capital.** Jeder Monat 2026 = derselbe Monat 2025 × Veränderung dieser
Reihe von 2024 auf 2025, mit kleinem Rauschen (Capex ±12 %, Bestände ±4 %).

**Nach der Erzeugung durchgeführte Prüfungen:** in Git nur hinzugefügte Zeilen (keine Zeile
2023–2025 geändert); Forecast 2026 Jan–Jun entspricht Ist 2026 je Kostenstelle × Konto (maximale
Differenz 0,00); Ist-Werte nur in den Monaten 1–6; keine doppelten Transaktions-IDs; keine
Ist-Werte für PROD-10; CUST-013 hat weiterhin Umsatz im ersten Halbjahr.
