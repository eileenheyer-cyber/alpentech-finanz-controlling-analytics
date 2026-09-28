# AlpenTech Controlling — Entscheidungsprotokoll

Dokumentiert, *warum* Modell und Bericht so aufgebaut sind, wie sie sind — die fachliche Begründung hinter Measure-Definitionen, Abgrenzungsentscheidungen und der Lesart der Zahlen. Gleicher Zweck wie das NordHome-Protokoll. Formatierung, Farben und Layout sind hier bewusst **nicht** enthalten.

Die vollständige Measure-Referenz mit DAX steht in `alpentech_controlling/MEASURES.md`. Diese Datei hält die **Entscheidungen** fest, nicht den Code.

---

## Projektrahmen

### Zielgruppe

**Controller / FP&A-Analyst.** Ein Arbeitswerkzeug für den regelmäßigen Einsatz, keine Management-Zusammenfassung. Dichte ist gewollt — Abweichungstabellen, Drill-down nach Kostenstelle, Detail auf Kontoebene. Seite 1 ist die Ausnahme: Sie heißt *Management Cockpit* und bleibt bewusst auf höherer Flughöhe.

### Sprache

**Durchgehend Englisch** in Modell und Bericht — Measure-Namen, Anzeigeordner, Visual-Titel, Seitenüberschriften. Siehe die Sprachentscheidung unten. Die Modellkultur bleibt `de-DE` (nur Zahlen- und Datumsformat). Die Dokumentation ist seit dem 28.09.2026 auf Deutsch.

### Seiten

1. Management Cockpit — How is the business performing?
2. P&L Analysis — What is driving profitability?
3. Budget & Variance — Where are we deviating from plan?
4. Forecast — Where will we land in 2026?
5. Scenario Analysis — What happens if assumptions change?

Die frühere Seite 6, *Cost Center Controlling*, wurde entfernt; die Abweichung nach Kostenstelle steht auf Seite 3 (Budget & Variance).

---

## Entscheidungen

### Sprache von gemischt Deutsch/Englisch auf durchgehend Englisch umgestellt

**Entscheidung (09.09.2026):** Jeder Measure-Name, Anzeigeordner, Visual-Titel und jede Seitenüberschrift ist Englisch. Die frühere Konvention — englische Struktur mit deutschen Controlling-Fachbegriffen — wurde aufgegeben.

**Warum:** Die gemischte Konvention stiftete mehr Verwirrung als Präzision. Der Leser musste beide Vokabulare kennen, und die deutschen Begriffe wurden nicht einheitlich verwendet. Einheitlichkeit in einer Sprache schlägt Präzision, die auf zwei Sprachen verteilt ist. Dass Stakeholder die englischen Begriffe nicht kennen, ist kein Grund, die Mischung beizubehalten.

**Was sich geändert hat:** 34 von 36 Measures umbenannt (`EBIT` und `EBITDA` waren bereits universell), 3 What-if-Parametertabellen, alle 7 Anzeigeordner, 30 Visual-Titel, 6 Seitenüberschriften sowie die DAX-Variablennamen in den Measure-Ausdrücken.

**Merkenswerter Hinweis zur Umsetzung.** Eine Umbenennung über TOM schreibt das DAX der Measures, die darauf verweisen, **nicht** um — `Operating Result = [Revenue] - [Total Cost]` wäre stillschweigend kaputtgegangen. Die Umbenennung erfolgte deshalb als TMDL-Texttransformation, die Deklarationen und `[Klammer]`-Verweise im selben Durchlauf umbenannte, und wurde anschließend durch Neuladen des Modells und Abgleich aller 122 Feldverweise des Berichts geprüft. Die Klammern machen das sicher: `[Actual]` kann nicht versehentlich `[Actual PY]` treffen.

Der Bericht wurde **direkt angepasst** statt neu erzeugt, weil er bis dahin in Desktop von Hand bearbeitet worden war und eine Neuerzeugung diese Arbeit verworfen hätte.

**Zielkonflikt:** `MEASURES.md`, dieses Protokoll und alle externen Notizen mit den alten Namen sind veraltet, sofern sie nicht aktualisiert werden. Beide Dokumente wurden im selben Durchgang aktualisiert. `BUSINESS_LOGIC.md` und `DATA_DICTIONARY.md` blieben unverändert — sie beschreiben den *Datensatz*, der weiterhin deutsche Fachkonzepte verwendet, und das ist richtig.

---

### Bruttoergebnis (Gross Profit) — definiert als Umsatz abzüglich der Kosten der Kostenstelle Produktion — ABGELÖST am 14.09.2026, siehe „COGS als direkte Produktionskosten ohne Abschreibungen" unten

**Entscheidung:** `Gross Profit` = Umsatz − alles, was auf die Kostenstelle **Produktion** gebucht ist. Das umfasst Rohstoffe plus den der Produktion zugeordneten Anteil an Personal (35 %), Energie (70 %), Fremdleistungen (55 %) und Abschreibungen (65 %) — also die vollen Herstellkosten.

**Warum diese und nicht die Alternativen.** Der Kontenplan hat kein COGS-Kennzeichen; das Bruttoergebnis musste also erst *definiert* werden, bevor es gemessen werden konnte. Drei Kandidaten wurden an den Daten durchgerechnet:

| Definition | 2023 | 2024 | 2025 | Marge 2025 |
|---|---|---|---|---|
| A — Umsatz − Rohstoffe | 11.776.086 | 12.473.045 | 12.657.554 | 62,8 % |
| **B — Umsatz − Kostenstelle Produktion** | **8.813.500** | **9.200.466** | **9.108.821** | **45,2 %** |
| C — Umsatz − alle variablen Kosten | 9.278.964 | 9.767.397 | 9.754.306 | 48,4 % |

- **A wurde verworfen**, weil das bereits der `Contribution Margin I` (Deckungsbeitrag I) ist. Er zieht nur das direkte Material ab und ignoriert Fertigungslöhne, Energie und Abschreibungen — ein Deckungsbeitrag, kein Bruttoergebnis.
- **C wurde verworfen**, weil `cost_behavior = "Variable"` auch Marketing, Reisekosten und Beratung erfasst. Das sind Betriebsaufwendungen, keine Umsatzkosten. C ist ein Deckungsbeitrag nach Teilkostenrechnung.
- **B ist das echte Bruttoergebnis** — Umsatz abzüglich der vollen Herstellkosten, also das, was COGS in einem Fertigungsbetrieb bedeutet.

B erzählt auch die schärfste Geschichte: Die Bruttomarge sinkt von **48,8 % → 47,7 % → 45,2 %**, und 2025 *sinkt das Bruttoergebnis absolut* (9.200.466 → 9.108.821), während der Umsatz um 4,5 % wächst. Die DB-I-Sicht übersieht das vollständig, weil die Erosion bei Energie und Fertigungslöhnen liegt, nicht beim Material.

**Zielkonflikte:**
- **Nur auf Unternehmensebene.** Das Measure braucht `REMOVEFILTERS ( dim_cost_center )`, weil der Umsatz im Vertrieb und die Herstellkosten in der Produktion liegen. Es ignoriert daher jeden Kostenstellen- oder Geschäftsbereichs-Slicer. Bei diesem Modell unvermeidlich.
- **Ohne Logistik.** Ob Vertriebslogistik in die Umsatzkosten gehört, ist eine echte Bilanzierungsentscheidung; sie auszuschließen ist die üblichere Konvention. Neu prüfen, falls eine vollständige Umsatzkostendefinition gewünscht wird.

---

### Vorzeichenkonvention bleibt vorzeichenbehaftet — Umkehr nur für die Anzeige

**Entscheidung:** Umsatz bleibt in der Quelle positiv, Aufwand negativ (`BUSINESS_LOGIC.md` §3). Vorzeichenumkehr für die Lesbarkeit erfolgt innerhalb von Measures (`Total Cost`, `Depreciation`), nie in Power Query.

**Warum:** `Actual − Budget` liest sich dann für Umsatz und Kosten in dieselbe Richtung — negativ ist immer ungünstig. Eine einzige Regel für bedingte Formatierung deckt den ganzen Bericht ab, ohne Fallunterscheidung nach Kontotyp. Würden Aufwendungen schon in der Quelle positiv gedreht, müsste jedes Abweichungs-Measure eine Vorzeichenkorrektur enthalten, und irgendwann würde jemand eine vergessen.

---

### `ABS()` in jedem Abweichungsnenner

**Entscheidung:** `Variance %`, `Actual YoY %`, `Forecast Error H2 %` und `Forecast vs Budget %` teilen alle durch `ABS()` der Basis.

**Warum:** Ohne `ABS` wird eine negative Abweichung geteilt durch einen negativen Plan positiv dargestellt. Energie 2025: Plan −612.360, Ist −799.948. Einfache Division ergibt **+30,6 %** — eine Überschreitung, die als günstig erscheint. Mit `ABS` lautet sie **−30,6 %**. Das ist der wahrscheinlichste stille Fehler in einem Modell mit Vorzeichenkonvention.

---

### Kennzahlen-Measures verwenden `REMOVEFILTERS ( dim_account )`

**Entscheidung:** `Material Cost Ratio`, `Personnel Cost Ratio`, `Contribution Margin I`, `EBITDA Margin %` und `Gross Profit` neutralisieren die Kontendimension, bevor sie ihre eigenen Filter setzen.

**Warum:** Zähler und Nenner liegen auf *verschiedenen* Konten. Ein `CALCULATE`-Filter ersetzt nur den Filter auf seiner eigenen Spalte — Filter auf anderen Spalten bleiben bestehen und werden kombiniert. Auf einer Zeile „Material Costs" erbt ein auf `account_type = "Revenue"` gefilterter Nenner also `account_category = "Material Costs"`; beides widerspricht sich, und die Kennzahl ist genau dort leer, wo sie gebraucht wird.

**Zielkonflikt:** Diese Measures ignorieren Konto-Slicer absichtlich. Das ist gewollt, muss aber dokumentiert sein, sonst sieht es wie ein Fehler aus.

---

### Kostenquoten bleiben auf Unternehmensebene, *ohne* `REMOVEFILTERS ( dim_cost_center )`

**Entscheidung:** Die Quoten entfernen nur Kontofilter.

**Warum:** Das zusätzliche Entfernen der Kostenstelle würde sie einen Geschäftsbereichs-Slicer stillschweigend ignorieren lassen — man tauscht eine Verwirrung gegen eine andere. Stattdessen ist die Einschränkung dokumentiert, und diese Measures stehen auf Seiten ohne Kostenstellen-Slicer.

---

### Forecast-Genauigkeit auf Juli–Dezember beschränkt

**Entscheidung:** `Forecast Error H2` / `Forecast Error H2 %` filtern über `KEEPFILTERS` auf `month >= 7`.

**Warum:** Der Forecast für Januar–Juni *entspricht* konstruktionsbedingt dem Ist (`BUSINESS_LOGIC.md` §7) — geprüft, die Differenz ist genau 0. Der absolute Fehler bleibt davon unberührt, der *prozentuale* aber nicht: 2024 ergibt sich mit Ganzjahresnenner −8,5 %, mit Nenner nur für H2 **−18,9 %**. Der H2-Wert ist der ehrliche.

`KEEPFILTERS` statt eines einfachen Filters, damit sich die Einschränkung mit der Zeitauswahl des Nutzers *schneidet*, statt sie zu überschreiben — wer auf Q3 filtert, bekommt Juli–September, nicht stillschweigend Juli–Dezember.

---

### Seite Working Capital gestrichen — ABGELÖST am 11.09.2026, siehe „Bilanzerweiterung" unten

**Entscheidung:** Die ursprünglich geplante 7-seitige Struktur verlor „Working Capital — where is cash tied up?". Sechs Seiten wurden ausgeliefert.

**Warum:** Der Datensatz ist reine GuV. 16 Konten, 3 Umsatz- und 13 Aufwandskonten, keinerlei Bilanzkonten und in keiner Quelldokumentation eine Erwähnung von Forderungen, Verbindlichkeiten, Vorräten oder Liquidität. DSO, DPO, DIO und der Cash Conversion Cycle lassen sich nicht ableiten. Alles auf dieser Seite wäre erfunden gewesen.

**Folge:** „Cash Flow" und „Cash-flow trend" wurden aus demselben Grund aus der KPI-Liste von Seite 1 entfernt. Der einzige vertretbare Näherungswert ist das EBITDA vor Working-Capital-Veränderungen — und das ist wörtlich der EBITDA-KPI, der bereits auf der Seite steht. Ihn unter einer zweiten Bezeichnung doppelt zu zeigen, würde eher irreführen als informieren.

---

### `EBIT` als Alias von `Operating Result` angelegt

**Entscheidung:** `EBIT = [Operating Result]`, als eigenes benanntes Measure beibehalten.

**Warum:** Ohne Zins- und Steuerkonten im Modell *ist* das Betriebsergebnis das EBIT. Der Alias existiert, damit das Cockpit die englische Bezeichnung verwenden kann, die das Publikum erwartet. Als Alias dokumentiert, damit niemand eine eigenständige Berechnung vermutet.

**Dazu:** Der Jahresüberschuss war zu diesem Zeitpunkt **nicht** berechenbar — die GuV endete beim EBIT. (Mit `fact_tax` seit dem 11.09.2026 überholt, siehe „Bilanzerweiterung" und „Brücke vom Umsatz zum Jahresüberschuss".)

---

### Sortierung von `account_category` aus `account_id` abgeleitet, nicht aus sich selbst

**Entscheidung:** `account_category_sort` ist eine ausgeblendete berechnete Spalte, gebildet mit `SWITCH ( TRUE (), ... )` über `account_id`.

**Warum:** Die naheliegende Variante — `SWITCH` über `account_category` — lehnt Power BI mit einer zirkulären Abhängigkeit ab, weil eine Spalte nicht nach einer berechneten Spalte sortiert werden kann, die sie selbst liest. Die Kontonummern kodieren die GuV-Struktur bereits (<5000 Umsatz, 5000 Material, 5500 Personal, 6100 Abschreibungen, 6200 Sonstige, Rest Betriebsaufwand), die Sortierung ergibt sich also sauber daraus. 1:1 über alle 16 Konten geprüft.

**Wirkung:** Die GuV liest sich jetzt von oben nach unten — Revenue, Material Costs, Personnel Costs, Operating Expenses, Depreciation, Other Costs — statt alphabetisch mit dem Umsatz ganz unten. Das behebt gleichzeitig die Zeilenreihenfolge in der monatlichen GuV-Matrix, den Abweichungsbalken, dem Kostenstrukturdiagramm und dem GuV-Wasserfall.

---

### Measures liefern Euro, nicht TEUR

**Entscheidung:** Keine Skalierung innerhalb der Measures.

**Warum:** Die Skalierung gehört in die Einstellung *Anzeigeeinheiten* des Visuals, damit ein Modell sowohl eine TEUR-Matrix als auch einen Drillthrough in vollen Euro bedienen kann, ohne einen zweiten Satz Measures.

---

### Umsatz nach *Produktkategorie*, nicht nach Geschäftsbereich

**Entscheidung:** Das Visual „Revenue by business unit" auf Seite 1 wurde stattdessen gegen `dim_product[product_category]` gebaut.

**Warum:** Alle 8.971 Umsatzzeilen buchen auf die Kostenstelle 4000 (Vertrieb), also Geschäftsbereich 20. Ein Umsatz-nach-Geschäftsbereich-Diagramm zeigt einen Balken und fünf leere Plätze. Das ist eine dokumentierte Vereinfachung (`BUSINESS_LOGIC.md` §9), kein Datenfehler. Die Produktkategorie trägt die echte Produktlinien-Geschichte, einschließlich des Margenrückgangs bei Maschinenkomponenten.

---

### Bilanzerweiterung — löst „Seite Working Capital gestrichen" ab

**Entscheidung (11.09.2026):** Der Datensatz wurde über die reine GuV hinaus um drei neue Fakt-Tabellen erweitert — `fact_working_capital` (Forderungen, Verbindlichkeiten, Vorräte zum Monatsende), `fact_capex` (monatliche Investitionen nach Anlagenkategorie) und `fact_tax` (monatliche Ertragsteuern). Das kehrt die frühere Entscheidung um, Working Capital mangels Daten zu streichen.

**Warum:** Die ursprüngliche Einschränkung war real — ein reiner GuV-Kontenplan kann weder eine Bilanz noch einen Cashflow liefern. Statt das Cockpit die Frage offen lassen zu lassen, ob aus dem Gewinn auch Liquidität wurde, wurden die Bilanzpositionen aus Ist-Umsatz und Ist-Kosten mit angenommenen Zahlungszielen und Lagerreichweiten abgeleitet. Damit sind sie synthetisch, aber in sich konsistent mit der GuV, aus der sie stammen.

**Lesart:** Die *Trends* als real behandeln, die *absoluten Niveaus* als illustrativ. Die Richtung von DSO, DIO und Net Working Capital folgt echten Umsatz- und Kostenbewegungen. Die Euro-Niveaus hängen von den angenommenen Zahlungszielen ab.

**Einschränkung, die bis ins Cockpit reicht:** Alles, was auf dem Working Capital aufbaut, ist für 2023 leer, weil es keinen Eröffnungsbestand gibt, gegen den man eine Differenz bilden könnte. Eine Liquiditäts- oder Working-Capital-Karte bleibt leer, wenn 2023 gewählt ist. Das ist korrektes Verhalten, kein Fehler — die Alternative wäre, einen unbekannten Eröffnungsbestand als null zu behandeln.

**Ebenfalls nur auf Unternehmensebene:** Keine der drei Tabellen hat einen Schlüssel für Gesellschaft, Kostenstelle, Produkt oder Kunde. Karten darauf wiederholen bei jedem solchen Slicer den Gesamtwert, statt aufzuteilen.

---

### Brücke vom Umsatz zum Jahresüberschuss — Steuern als eigener Schritt, Jahresüberschuss als Endsumme

**Entscheidung (12.09.2026):** Die Brücke im Cockpit läuft Umsatz → Materialkosten → Personalkosten → Betriebsaufwand → Sonstige Kosten → Abschreibungen → Steuern → **Jahresüberschuss**, wobei der Jahresüberschuss als eigene Endposition gezeigt wird statt nur implizit.

**Warum:** Eine Brücke, die beim Betriebsergebnis endet, beantwortet eine engere Frage als die, die das Cockpit stellt. Der Leser will sehen, was nach Steuern übrig bleibt, und die sieben Schritte summieren sich exakt zum Jahresüberschuss — die Kette schließt ohne Ausgleichsposten. Zwei nützliche Zwischenstände ergeben sich nebenbei: Nach den Sonstigen Kosten ist die laufende Summe das EBITDA, nach den Abschreibungen das EBIT.

**Warum Steuern einen eigenen Schritt brauchen:** `fact_tax` liegt bewusst außerhalb von `fact_actual`, damit Actual, Operating Result, EBIT und alle Abweichungs-Measures unverändert bleiben. Dadurch liegt die Steuer außerhalb der Kontenhierarchie, weshalb die Brücke über eine eigene Schrittliste statt über `account_category` gesteuert wird.

**Nur auf Unternehmensebene.** Die Schritte Steuern und Jahresüberschuss haben keine Kostenstellen-, Produkt- oder Kundengranularität. Unter einem solchen Slicer ist die Brücke falsch, nicht nur unvollständig. Diese Slicer von der Seite fernhalten oder das Visual auf eine Brücke vom Umsatz zum EBIT beschränken, wo es sicher ist.

---

### Es gibt keinen geplanten Jahresüberschuss — und keine Planlinie dafür

**Entscheidung (12.09.2026):** Der Jahresüberschuss wird mit dem Vorjahr und mit einem abgeleiteten Zielwert verglichen, nie mit dem Plan.

**Warum:** Der Plan umfasst nur GuV-Konten, und `fact_tax` hat kein Plan-Gegenstück. Ein geplanter Jahresüberschuss existiert in diesem Modell daher nicht. Einen durch Anwendung eines Steuersatzes auf den Plan zu erfinden, ist als *Zielwert* legitim (siehe den Eintrag zu Zielwerten unten), darf aber nicht als Plan dargestellt werden, weil ihn niemand geplant hat.

**Wo sich das zeigt:** Die Planlinie im Trenddiagramm verschwindet, wenn im KPI-Auswähler Net Income gewählt ist. Das ist richtig, und der Diagrammtitel lässt den Zusatz „vs. Plan" entsprechend weg, statt eine Linie zu versprechen, die es nicht gibt.

---

### Richtungskonvention im Working Capital — Forderungen und Vorräte ungünstig bei Anstieg, Verbindlichkeiten günstig

**Entscheidung (12.09.2026):** Die günstige Richtung wird je Measure festgelegt und nicht von der GuV-Konvention übernommen.

| Measure | Anstieg bedeutet | Lesart |
|---|---|---|
| Forderungen | Kunden zahlen langsamer | ungünstig |
| DSO | Kunden zahlen langsamer | ungünstig |
| Vorräte / DIO | Lager dreht langsamer | ungünstig |
| Net Working Capital | mehr Liquidität im operativen Geschäft gebunden | ungünstig |
| Verbindlichkeiten / DPO | Unternehmen zahlt Lieferanten später | **günstig** |
| Cash Conversion Cycle | längere Lücke zwischen Zahlen und Kassieren | ungünstig |

**Warum:** Die GuV-Konvention — Umsatz positiv, Aufwand negativ, eine positive Veränderung ist also immer gut — lässt sich nicht auf Bilanzpositionen übertragen. Verbindlichkeiten laufen genau umgekehrt: Lieferanten später zu bezahlen, hält Liquidität im Unternehmen. Die Working-Capital-Familie als einen Block zu behandeln, würde eine sich verbessernde Liquiditätslage als Verschlechterung ausweisen.

**Folge für den Leser:** Eine Aufwärtsbewegung auf einer Working-Capital-Karte ist nicht von selbst gut oder schlecht. Jede Karte nennt ihre eigene Richtung.

---

### Working-Capital-Wachstum wird am Umsatzwachstum gemessen, nie isoliert

**Entscheidung (13.09.2026):** Steigendes Net Working Capital gilt nur dann als Warnsignal, wenn es schneller wächst als der Umsatz. Die Diagnosegröße ist das Net Working Capital in Prozent des Umsatzes.

**Warum:** Working-Capital-Wachstum ist unbedenklich, wenn es echte Expansion finanziert — wer mehr verkauft, trägt zwangsläufig mehr Forderungen und mehr Bestand, und jeder Euro arbeitet. Es ist ein Warnsignal, wenn dasselbe Geschäft mehr Liquidität bindet als früher, also bei langsameren Zahlungseingängen, langsamerem Lagerumschlag oder beidem. Der Anteil am Umsatz trennt die beiden Fälle; die Wachstumsrate allein kann das nicht.

**Befund 2023–2025:** Es ist der ungünstige Fall.

| Jahr | Umsatzwachstum | NWC-Wachstum | NWC in % vom Umsatz |
|---|---|---|---|
| 2023 | | | 11,4 % |
| 2024 | +6,7 % | +18,8 % | 12,6 % |
| 2025 | +4,5 % | +19,7 % | 14,5 % |

Der Umsatz wuchs über die zwei Jahre um 11,6 %, das Working Capital um 42 %. Rund drei Cent mehr von jedem Umsatz-Euro sind jetzt im operativen Geschäft gebunden. DSO und DIO bestätigen das unabhängig: Kunden zahlen zehn Tage später als 2023, und der Bestand liegt acht Tage länger.

---

### Zielwerte für die drei Cockpit-KPIs

**Entscheidung (13.09.2026):** Jeder der drei Cockpit-KPIs bekommt eine andere Art von Zielwert, weil jeder eine andere Art von Frage stellt.

**1. Jahresüberschuss — ein abgeleiteter Zielwert, als solcher gekennzeichnet.**

Geplantes Betriebsergebnis mal eins minus effektiver Steuersatz. Der effektive Satz ist konstruktionsbedingt in allen drei Jahren konstant 29,825 %.

| Jahr | Plan | Abgeleiteter Zielwert | Ist | Erreicht |
|---|---|---|---|---|
| 2023 | 2.070.000 | 1.452.623 | 1.510.430 | 104 % |
| 2024 | 2.352.420 | 1.650.811 | 1.365.180 | 83 % |
| 2025 | 2.445.968 | 1.716.458 | 908.238 | 53 % |

Der Zielwert 2025 beträgt 1,72 Mio. Er muss auf der Karte als *abgeleitet* gekennzeichnet sein, weil er Arithmetik auf dem Plan ist und keine geplante Zahl — siehe den Eintrag „kein geplanter Jahresüberschuss" oben.

*Alternative in Reserve:* eine Untergrenze von 7 % Nettomarge. Die Marge lag bei 8,4 %, 7,1 %, 4,5 %. Ein Quotenziel übersteht Umsatzschwankungen; ein absolutes Euro-Ziel nicht.

**2. Cash Conversion Rate — 75 %, ausdrücklich nicht 100 %.**

Ein Ziel von 100 % ist in diesem Modell strukturell unerreichbar. Der operative Cashflow beginnt beim Jahresüberschuss, die Identität reduziert sich also auf EBITDA minus Steuern minus Working-Capital-Veränderung. Selbst ohne Working-Capital-Belastung liegt die Obergrenze bei eins minus Steuern durch EBITDA:

| Jahr | Obergrenze ohne Belastung | Ist |
|---|---|---|
| 2023 | 76,7 % | leer |
| 2024 | 77,5 % | 62,6 % |
| 2025 | 80,8 % | 56,9 % |

75 % liegt knapp unter der Obergrenze und erlaubt eine Working-Capital-Belastung von rund 6 % des EBITDA. Anspruchsvoll, aber erreichbar. Ein Ziel von 100 % würde einen dauerhaft roten KPI erzeugen und den Leser lehren, ihn zu ignorieren.

**3. Ist vs. Plan — Ziel null, mit Toleranzband.**

Eine Abweichung hat kein sinnvolles Ziel außer null. Die Karte braucht ein Band, keinen Zielwert:

| Band | Abweichung % | Lesart |
|---|---|---|
| Grün | innerhalb ±5 % | im Plan |
| Gelb | ±5 % bis ±10 % | beobachten |
| Rot | über ±10 % | handeln |

Für 2025 sind das ±122.298 bei einem Plan von 2.445.968. Das Ist liegt bei −47,1 %, tief im Handlungsband.

**Warum Bänder statt eines einzelnen Schwellenwerts:** Eine binäre Kennzeichnung „im Plan / nicht im Plan" lässt dem Controller keinen Platz für eine Abweichung, die real, aber noch nicht handlungsrelevant ist. Drei Bänder trennen Rauschen von einem Beobachtungspunkt und von etwas, das eine Entscheidung braucht.

---

### COGS als direkte Produktionskosten ohne Abschreibungen — löst die Definition des Bruttoergebnisses ab

**Entscheidung (14.09.2026):** **COGS = direkte Produktionskosten ohne Abschreibungen** — jeder Aufwand, der auf die Kostenstelle Produktion gebucht ist, außer Konto 6100 Abschreibungen. Die Definition lebt in einem einzigen Measure, `COGS`. `Gross Profit`, `Gross Margin %` und die COGS-Zeile der GuV-Staffelmatrix lesen alle daraus.

**Warum sich das geändert hat.** Seite 2 bekam eine GuV-Staffel: Umsatz → COGS → Bruttoergebnis → Betriebsaufwand → EBITDA → Abschreibungen → EBIT → Steuern & Zinsen → Jahresüberschuss. Eine Staffel funktioniert nur, wenn jeder Schritt aufgeht, und Bruttoergebnis minus Betriebsaufwand muss exakt beim EBITDA landen. Unter der früheren Definition lagen die Abschreibungen der Produktion (65 % aller Abschreibungen) in den COGS, also oberhalb des EBITDA, der Rest darunter. Die Staffel konnte nicht aufgehen.

Drei Definitionen wurden für 2025 durchgerechnet:

| Definition | COGS | Bruttoergebnis | Marge |
|---|---|---|---|
| Nur Rohstoffe | 7.502.175 | 12.657.554 | 62,8 % |
| Kostenstelle Produktion inkl. Abschreibungen (bisher) | 11.050.908 | 9.108.821 | 45,2 % |
| **Kostenstelle Produktion ohne Abschreibungen (vereinbart)** | **10.587.605** | **9.572.123** | **47,5 %** |

- **Nur Rohstoffe wurde verworfen** — das ist der `Contribution Margin I`. Er ignoriert Fertigungslöhne und Energie.
- **Produktion inklusive Abschreibungen wurde verworfen** — die Abschreibungen verteilen sich dabei auf beide Seiten des EBITDA, die Staffel geht nicht auf.
- **Produktion ohne Abschreibungen wurde vereinbart** — die vollen zahlungswirksamen Herstellkosten bleiben in den COGS, und alle Abschreibungen stehen in einer Zeile.

**Was sich bewegt hat:** Das Bruttoergebnis steigt um die Abschreibungen der Produktion — +388.356 · +412.968 · +463.303. Die Bruttomarge lautet jetzt **50,9 % → 49,9 % → 47,5 %** statt 48,8 % → 47,7 % → 45,2 %. **Der Befund bleibt gleich:** Die Marge sinkt weiter, um 3,5 Pp. statt 3,6 Pp., und 2025 sinkt das Bruttoergebnis weiterhin absolut (9.613.434 → 9.572.123), während der Umsatz um 4,5 % wächst.

**Zielkonflikte:**
- **Zwei Filterverhalten.** `COGS` respektiert Konto- und Kostenstellen-Slicer und lässt sich daher nach Konto aufgliedern. `Gross Profit` entfernt sie und bleibt auf Unternehmensebene, weil der Umsatz im Vertrieb und die COGS in der Produktion liegen.
- **Ohne Logistik** — unverändert gegenüber der früheren Definition.
- **Keine Bestandsveränderung.** `fact_working_capital[inventory_balance]` wurde aus dem Materialverbrauch abgeleitet; Konto 5000 erfasst also bereits das verbrauchte Material. Den Bestandsaufbau von den COGS abzuziehen, würde ihn doppelt zählen und den Jahresüberschuss 2025 ohne geschäftlichen Grund um 213.324 erhöhen. Die Vorräte sind stattdessen über den Cashflow-Teil der Matrix mit der GuV verbunden, als gebundene Liquidität.

---

### GuV-Staffelmatrix — eigener Measure-Satz auf einer entkoppelten Layouttabelle

**Entscheidung (14.09.2026):** Die Matrix *P&L structure with prior year* auf Seite 2 läuft auf einer entkoppelten Tabelle `PnL_Layout` (16 Zeilen, vom Umsatz bis zum Free Cashflow) und einer eigenen Measure-Familie im Ordner `15 P&L Matrix`: `P&L Actual`, `P&L Actual Q1`–`Q4`, `P&L Actual PY`, `P&L Actual YoY %`. Sie verwendet **nicht** `Actual`.

**Warum eine Layouttabelle.** Die gewünschte Struktur — Umsatz → COGS → Bruttoergebnis → Betriebsaufwand → EBITDA → EBIT → Steuern & Zinsen → Jahresüberschuss — enthält Zeilen, die keine Konten sind. Bruttoergebnis, EBITDA und EBIT sind Zwischensummen; die Steuern liegen in `fact_tax`. Eine Matrix nach `account_category` kann keine davon zeigen. Die Layouttabelle liefert die Zeilen, und `P&L Actual` löst jede über `SWITCH` auf. Gleiches Muster wie die Brücke vom Umsatz zum Jahresüberschuss.

**Warum nicht `Actual`.** `Actual` ist eine einfache Summe und kann eine entkoppelte Zeile nicht sehen; auf jeder `Line`-Zeile liefert es daher Umsatz minus alle Kosten — das EBIT. Genau das passierte: Der erste Versuch zeigte 291.347 auf allen 16 Zeilen. `P&L Actual` existiert, weil es die Zeile liest. **Regel:** Zeilen aus `PnL_Layout` → `P&L Actual…`; alles andere → `Actual`. Die beiden stimmen nur in der EBIT-Zeile überein.

**Warum eine Zeile Abschreibungen ergänzt wurde.** Ohne sie findet der Schritt vom EBITDA zum EBIT (716 Tsd. im Jahr 2025) nirgends sichtbar statt.

**Warum ein Cashflow unter dem Jahresüberschuss.** Die Vorräte mussten mit der GuV verbunden werden. In die COGS können sie nicht (siehe den COGS-Eintrag oben), also werden sie dort verbunden, wo sie tatsächlich wirken — bei der Liquidität. Die Zeilen 10–16 folgen der indirekten Methode: Jahresüberschuss + Abschreibungen − Δ Vorräte − Δ Forderungen + Δ Verbindlichkeiten = Operativer Cashflow, − Investitionen = Free Cashflow. Sie stimmen mit den bestehenden Measures `Operating Cash Flow` und `Free Cash Flow` überein. Der Befund: Aus 2,0 Mio. EBITDA wurden 2025 391 Tsd. Free Cashflow, 59 % weniger, und Q1 2025 war in einem profitablen Quartal cash-negativ.

**Drill-down-Gruppierung.** Der Betriebsaufwand klappt nach `dim_account[pnl_group]` auf, einer Anzeigespalte, die `account_name` entspricht, außer dass **Miete, Reisekosten, Versicherungen und Sonstiger betrieblicher Aufwand (5400, 5800, 5900, 6200) als Other Operating Expenses zusammengefasst sind** — 846.620 im Jahr 2025. Eine eigene Spalte statt umbenannter Konten, damit alle anderen Seiten ihre Kontensicht behalten. Über `account_id` verschlüsselt, damit ein umbenanntes Konto nicht herausfallen kann.

**Aufteilung in zwei Tabellen (14.09.2026).** Die eine 16-zeilige Matrix wurde zu zwei übereinanderliegenden Matrizen, *Income Statement* (Zeilen 1–9) und *Cash Flow* (Zeilen 9–16), weil Gewinn und Liquidität unterschiedliche Fragen beantworten und eine lange Tabelle die Cashflow-Zeilen untergehen ließ. Keine neuen Measures: Ein Filter auf Visual-Ebene auf `PnL_Layout[Line Order]` teilt dieselben `P&L Actual…`-Spalten. **Der Jahresüberschuss steht in beiden** — er schließt die GuV und eröffnet den Cashflow, sodass der Cashflow mit einer Zahl beginnt, die der Leser gerade gesehen hat. Beide Tabellen haben identische Spalten und Formatierung; nur die GuV behält den `pnl_group`-Drill-down.

**Zielkonflikte:**
- **Zwei Measure-Familien, die sich ähneln.** Die älteren `14 Quarters`-Measures (`Actual Q1`–`Q4`, auf `Actual` aufgebaut) luden zur falschen Wahl ein; sie wurden am 14.09.2026 gelöscht, nachdem feststand, dass kein Visual und kein Measure sie verwendete. Es bleibt nur die `P&L Actual…`-Familie. Die Matrix hatte ihre Wertfelder zunächst in *Actual Q1 … Actual YoY %* umbenannt, was es schlimmer machte — die Überschriften lasen sich wie die `Actual`-Familie. Diese Umbenennungen wurden am 14.09.2026 entfernt; die Überschriften zeigen jetzt die echten `P&L Actual…`-Namen.
- **Namenskonflikt.** *Other Operating Expenses* bedeutet überall sonst nur Konto 6200 (232.819), in dieser Matrix aber vier Konten (846.620).
- **Die Gesamtsumme ist absichtlich leer** — eine Staffel aufzusummieren zählt jede Zwischensumme doppelt.
- **Unterhalb des EBIT nur auf Unternehmensebene**, geerbt von `fact_tax`, `fact_working_capital` und `fact_capex`.
- **Cashflow-Zeilen für 2023 leer** — kein Eröffnungsbestand, dieselbe Regel wie bei den Liquiditätskarten im Cockpit.

---

### „Plan" statt „Budget" in allem, was der Leser sieht

**Entscheidung (17.09.2026):** Sichtbare Beschriftungen verwenden die Begriffe **Actual / Plan / Forecast / PY** — „Actual vs Plan", „Forecast vs Plan", „Variance to Plan %".

**Warum:** „Budget" klingt nach einer Ausgabenobergrenze und liest sich bei Umsatz oder EBIT seltsam. „Plan" entspricht der Praxis im deutschen Mittelstand (Plan / Ist / Vorjahr) und den bestehenden Measures `Revenue Plan` / `EBITDA Plan`.

**Zielkonflikt:** Measure-Namen (`Budget`, `Forecast vs Budget`, …) bleiben unverändert, weil Umbenennungen außerhalb von Desktop die Bindung der Visuals zerstören können. Der Seitenreiter heißt weiterhin „Budget & Variance".

---

### Das Geschäftsjahr 2026 ist ein halb abgeschlossenes Jahr, Stand 30. Juni 2026

**Entscheidung:** Januar–Juni 2026 sind Ist; Juli–Dezember ist die Hochrechnung zur Jahresmitte (`BUSINESS_LOGIC.md` §10).

**Regel für Leser:** 2026 nur als **Plan vs. Forecast** vergleichen oder **Januar–Juni mit Januar–Juni**. Ein Ganzjahresvergleich mit 2025 oder mit dem Ganzjahresplan stellt sechs Ist-Monate plus sechs Forecast-Monate zwölf Ist-Monaten gegenüber.

---

### Nur der Kundenverlust erklärt die Lücke zum Plan

**Entscheidung:** Die zwei Ereignisse 2026 werden unterschiedlich behandelt.

| Ereignis | Wirkung auf das Betriebsergebnis | Im Plan? | Erklärt die Lücke? |
|---|---|---|---|
| Markteinführung SSM-1, ab August | +180.000 | ja, planmäßig prognostiziert | nein |
| Verlust von Kraftwerk Mechatronik, ab Oktober | −776.885 | nein — die Kündigung kam nach der Planerstellung | ja, vollständig |

**Folge:** Rund ein Drittel der Lücke von 2,83 Mio. zum Plan ist der Kundenverlust; die anderen zwei Drittel sind der Kostentrend (die Kosten wachsen seit drei Jahren schneller als der Umsatz). Kraftwerk stand für 25,6 % des Umsatzes 2025 — das eigentliche Problem ist also die Kundenkonzentration.

---

### Der Working-Capital-Forecast für H2 verwendet die Zahlungsziele aus H1 2026

**Entscheidung:** Die Bestände Juli–Dezember übernehmen die Zahlungsziele aus **H1 2026** — DSO 58, DIO 65, DPO 36 —, nicht die von 2025.

**Warum:** Die Zahlungsziele von 2025 hätten allein durch die Annahme rund 675 Tsd. Working Capital freigesetzt und den Cash-Forecast besser aussehen lassen, als das Geschäft es hergibt.

---

### Steuern werden monatlich abgegrenzt, ohne Erstattung in Verlustmonaten

**Entscheidung:** 29,825 % (Körperschaftsteuer 15,825 % + Gewerbesteuer 14 %) nur auf profitable Monate, wie 2023–2025. Verlustmonate tragen null Steuern, keine Erstattung.

**Folge:** Das Geschäftsjahr 2026 bucht **119.843** Steuern trotz eines operativen Verlusts von −107.051; der Jahresüberschuss liegt daher bei −226.894. In Szenarien wird ein Upside stärker besteuert, als ein pauschaler Jahressteuersatz vermuten lässt, weil er Verlustmonate in profitable Monate verwandelt.

---

### Der Forecast wird als das optimistische Ende der Bandbreite gelesen

**Entscheidung:** Der Forecast 2026 von −107.051 wird als das bessere Ende der Bandbreite dargestellt, nicht als deren Mitte.

**Warum:** Die Hochrechnung zur Jahresmitte war in jedem der letzten drei Jahre zu optimistisch — +39.935 (2023), +181.253 (2024), +186.013 (2025). Das ist systematisch: Die Methode überträgt nur 65 % der Planabweichung in den Forecast.

---

### Die Szenarioanalyse verändert den Forecast, und nur die offenen Monate

**Entscheidung (28.09.2026):** Jedes Szenario setzt auf dem **Forecast 2026** auf (Free Cashflow −490.049), nie auf dem Ist, und verändert nur die Monate nach dem letzten Ist-Datum (Juli–Dezember).

**Warum:** Januar–Juni sind abgeschlossen; sie zu verändern, würde die Vergangenheit umschreiben. Der Stichtag wird aus den Daten gelesen und verschiebt sich von selbst, sobald die Ist-Werte für Juli vorliegen.

**Korrektheitstest:** Base muss den veröffentlichten Forecast exakt reproduzieren — −490.049 Free Cashflow, −226.894 Jahresüberschuss. Tut es das nicht, wird ein Treiber doppelt gezählt.

---

### Drei feste Szenarien, keine freien Schieberegler

**Entscheidung (28.09.2026):** Die Szenarien sind **Base, Downside und Upside**, jeweils mit Werten, die in den Daten verankert sind. Das frühere Szenario Custom mit vier freien Schiebereglern wurde entfernt.

| | Umsatz | Betriebskosten | Vorräte | Investitionen |
|---|---|---|---|---|
| Base | 0 | 0 | 0 | 0 |
| Downside | −5 % — etwa ein weiterer Kunde von der Größe von Kraftwerk Mechatronik | +3 % — die Hälfte des bereits im Forecast enthaltenen Kostenwachstums | +10 % — Lageraufbau bei sinkendem Absatz, wie schon 2026 | 0 |
| Upside | +2 % — Umsatz zurück auf dem Niveau von 2025 | −2 % — kehrt einen Teil des Kostenaufbaus um | −15 % — ein Working-Capital-Programm | −20 % — verschiebt 157 Tsd. Investitionen |

**Warum:** Benannte Szenarien mit verankerten Werten lassen sich vor dem Management begründen. Freie Schieberegler erzeugen Kombinationen, die niemand geplant hat, und machten die Seite schwerer lesbar. Die älteren Schieberegler für Energie / Umsatz / Personal, die das Ist statt des Forecasts veränderten, wurden aus demselben Grund entfernt.

**Ergebnis, Free Cashflow 2026:** Base −490.049 · Downside −1.034.000 · Upside −8.278.

---

### Wie jeder Szenariotreiber die Liquidität erreicht

**Entscheidung (28.09.2026):**

- **Umsatz wirkt mit dem Deckungsbeitrag, nicht eins zu eins.** Nur Rohstoffe (5000) und Logistik (5200) bewegen sich mit dem Volumen; Energie, Personal und der Rest gelten innerhalb des Jahres als fix. 2026: 1 − (7.713.312 + 1.145.790) / 19.728.870 = **55,1 %**. Energie ebenfalls als variabel zu behandeln, ergäbe 50,8 %.
- **Betriebskosten** wirken auf Personal, Betriebsaufwand und Sonstige Kosten (−11.377.595 für das Jahr, die Hälfte davon in den offenen Monaten). Ausgenommen sind das Material, das sich bereits mit dem Umsatz bewegt, und die Abschreibungen, die den Investitionen folgen.
- **Vorräte** verändern den Endbestand (1.349.689) vollständig ab dem Stichtag — ein Zielbestand, kein monatliches Programm. Forderungen und Verbindlichkeiten werden nicht verändert: DSO ist kein Treiber, und etwas anderes vorzugeben, würde die Annahme verstecken.
- **Investitionen** verändern nur den noch nicht ausgegebenen Teil — 422.883 von 787.262 für das Jahr. Die Abschreibungen werden nicht angepasst: Innerhalb eines Jahres ist der Effekt unwesentlich.

**Folge:** Der Liquiditätseffekt jedes Szenarios teilt sich exakt in Ergebnis nach Steuern, Working Capital und Investitionen, ohne Ausgleichsposten.

---

## Offene Punkte

| # | Punkt | Status |
|---|---|---|
| 1 | Bedingte Formatierung in den Abweichungsmatrizen (Seiten 3, 4) | nicht umgesetzt |
| 2 | Schlüsselspalten der Fakt-Tabellen noch sichtbar — insbesondere `fact_actual[business_unit_id]` | nicht umgesetzt |
| 3 | Monatsdiagramme verwenden `month_short` und fassen drei Jahre zu 12 Punkten zusammen, sofern kein Jahr gewählt ist | noch offen |
| 4 | Monatliche GuV-Matrix von Hand von Seite 1 entfernt; noch nicht auf Seite 2 neu platziert | von der Nutzerin erledigt |
| 5 | Kostenlinie im kumulierten Diagramm | von der Nutzerin erledigt |
| 6 | What-if-Slicer werden als Bereichsschieberegler dargestellt | hinfällig seit 28.09.2026 — Schieberegler entfernt, siehe „Drei feste Szenarien, keine freien Schieberegler" |
| 7 | Ziel-Measures + Ampelbänder für die drei Cockpit-KPIs (Jahresüberschuss, Cash Conversion Rate, Ist vs. Plan) | vereinbart, nicht gebaut |
| 8 | Net Working Capital in % vom Umsatz — die ehrliche Wachstumsdiagnose — noch nicht im Cockpit | nicht gebaut |
| 9 | Zeilen-Zwischensummen der GuV-Matrix waren aus, eine aufgeklappte Zeile zeigte daher keinen Wert — EBITDA und EBIT waren leer, der Betriebsaufwand verlor seine Summe. Zwischensummen einschalten und die Gesamtsumme je Zeilenebene ausblenden | teilweise erledigt am 14.09.2026 — Zwischensummen an, aufgeklappte Zeilen behalten ihre Werte; leere Gesamtzeile noch sichtbar, je Zeilenebene ausblenden |
| 10 | Nicht verwendete `14 Quarters`-Measures (`Actual Q1`–`Q4`, `Actual Q1 YoY %`–`Q4 YoY %`) — löschen oder ausblenden | erledigt am 14.09.2026 — alle 8 gelöscht, nachdem feststand, dass kein Visual und kein Measure sie verwendete |
| 11 | Spaltenüberschriften der GuV-Matrix sind Anzeigenamen (*Actual Q1 … Actual YoY %*), die sich wie die `Actual`-Familie lesen — die echten `P&L Actual…`-Namen zeigen | erledigt am 14.09.2026 — Umbenennungen entfernt, Überschriften zeigen `P&L Actual Q1 … P&L Actual YoY %` |
| 12 | Seite P&L: Balkendiagramm mit dem Titel „Contribution Margin I by product line" zeigt tatsächlich Total Cost nach Kostenstelle | offen |
