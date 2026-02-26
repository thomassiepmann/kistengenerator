# Für Kurt: Benötigte Daten für den Kistengenerator

## 📋 Übersicht

Der Kistengenerator ist **vollständig funktionsfähig** und enthält bereits Beispieldaten. Um mit echten Daten zu arbeiten, benötigen wir folgende Informationen:

---

## 1️⃣ ARTIKEL-STAMMDATEN

### Was wird benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **SID** | Artikel-Nummer (eindeutig) | 13, 241, 22 |
| **Name** | Artikel-Bezeichnung | Zucchini, Paprika gelb, Fenchel |
| **Kategorie** | Produktgruppe | Gemuese, Obst, Salat |
| **Einheit** | Kilogramm oder Stück | Kilogramm, Stueck |
| **Status** | Aktiv/Inaktiv | aktiv |

### ✅ Wie einpflegen:

**Option 1: Excel/CSV-Import** (empfohlen)
1. In der App: "Artikel verwalten" → "Importieren"
2. Excel-Vorlage herunterladen
3. Daten eintragen
4. Hochladen

**Option 2: PC-Gärtner Synchronisation**
- Automatischer Import aus PC-Gärtner Artikelmanager
- Dashboard → "PC-Gärtner Integration" → "Artikel synchronisieren"

**Option 3: Manuell**
- In der App: "Artikel verwalten" → "Neuer Artikel"
- Einzeln anlegen

---

## 2️⃣ PREISE

### Was wird benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Artikel-SID** | Referenz zum Artikel | 13 |
| **Preis pro Einheit** | Aktueller Preis | 2.89 € |
| **Gültig ab** | Ab wann gilt der Preis | 2026-02-26 |
| **Gültig bis** | Bis wann (optional) | 2026-03-31 |

### ✅ Wie einpflegen:

**Option 1: Excel/CSV-Import** (empfohlen)
1. "Preise pflegen" → "Importieren"
2. Vorlage herunterladen
3. Preise eintragen
4. Hochladen

**Option 2: PC-Gärtner Synchronisation**
- Automatischer Import aus PC-Gärtner
- Dashboard → "Preise synchronisieren"

**Option 3: Manuell**
- "Preise pflegen" → Artikel auswählen → Preis eingeben

### 💡 Saisonale Preise:
- Einfach neuen Preis mit neuem "Gültig ab" Datum anlegen
- System nutzt automatisch den aktuell gültigen Preis
- Alte Preise bleiben in Historie

---

## 3️⃣ TAUSCHMUSTER (Gewichtsangaben)

### Was wird benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Artikel-SID** | Referenz zum Artikel | 13 |
| **Größe** | Kistengröße | S, M, L |
| **Min. Menge** | Mindestmenge | 0.55 kg |
| **Max. Menge** | Maximalmenge | 0.75 kg |
| **Standard Menge** | Standardmenge | 0.65 kg |
| **Einheit** | Kilogramm oder Stück | Kilogramm |

### ✅ Wie einpflegen:

**Aktuell:** Bereits 69 Tauschmuster in der Datenbank!

**Für neue Artikel:**
1. Excel-Import vorbereitet
2. Vorlage: "Tauschmuster" herunterladen
3. Mengen-Ranges eintragen
4. Hochladen

### 💡 Beispiel:
- Zucchini Größe S: 550-750g (Standard: 650g)
- Paprika Größe S: 200-300g (Standard: 250g)

---

## 4️⃣ HISTORISCHE SORTIMENTE

### Was wird benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Kalenderwoche** | KW des Sortiments | 8 |
| **Jahr** | Jahr | 2025 |
| **Masterplan** | Sortimentstyp | OG12, RE12 |
| **Artikel-Liste** | Welche Artikel waren drin | Zucchini, Paprika, ... |
| **Mengen** | Wie viel von jedem | 0.65 kg, 0.25 kg, ... |

### ✅ Wie einpflegen:

**Option 1: Excel-Import**
1. "Historie" → "Importieren"
2. Vorlage herunterladen
3. Vergangene Sortimente eintragen
4. Hochladen

**Option 2: Automatisch**
- Jede freigegebene Kiste wird automatisch zur Historie!
- Generator lernt daraus für zukünftige Sortimente

### 💡 Warum wichtig:
- Generator lernt aus Vergangenheit
- Findet beste Matches für neue Wochen
- Je mehr Historie, desto besser die Vorschläge

---

## 5️⃣ WOCHENPLANUNG (Verfügbarkeit)

### Was wird benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Kalenderwoche** | Für welche Woche | 9 |
| **Jahr** | Jahr | 2026 |
| **Slot** | Position in Kiste | Gemuese 1, Obst 2 |
| **Artikel-SID** | Welcher Artikel | 13 |

### ✅ Wie einpflegen:

**Option 1: In der App** (empfohlen)
1. "Wochenplanung" → Woche auswählen
2. Für jeden Slot Artikel zuweisen
3. Speichern

**Option 2: Excel-Import**
1. "Wochenplanung" → "Importieren"
2. Vorlage ausfüllen
3. Hochladen

**Option 3: Vorwoche kopieren**
- "Von Vorwoche kopieren" Button
- Anpassen was sich ändert

### 💡 Saisonale Produkte:
- Einfach in der jeweiligen Woche verfügbar machen
- Nicht verfügbare Artikel weglassen
- Generator passt sich automatisch an

---

## 6️⃣ MASTERPLAENE (Sortimentstypen)

### Was bereits vorhanden ist:

✅ **OG12** - Obst & Gemüse 12 Slots (Größe S)
✅ **RE12** - Regional 12 Slots (Größe S)
✅ **OOG12** - Ohne Obst Gemüse 12 Slots (Größe S)

### Falls neue Sortimentstypen benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Name** | Sortimentstyp | OG15, BIO20 |
| **Größe** | S, M oder L | M |
| **Slot-Anzahl** | Wie viele Positionen | 15 |
| **Zielpreis Min** | Mindestpreis | 12.00 € |
| **Zielpreis Max** | Maximalpreis | 16.00 € |

---

## 📊 ZUSAMMENFASSUNG: Was ist bereits vorhanden?

### ✅ Bereits in der App:

- **57 Artikel** (Gemüse, Obst, Salat)
- **69 Tauschmuster** (Min/Max-Mengen)
- **3 Masterplaene** (OG12, RE12, OOG12)
- **Beispiel-Preise** für alle Artikel
- **Beispiel-Historie** zum Testen

### 🔄 Was muss aktualisiert werden:

1. **Aktuelle Preise** - Ihre echten Preise einpflegen
2. **Wochenplanung** - Verfügbarkeit für kommende Wochen
3. **Historische Sortimente** - Vergangene Kisten (optional, aber empfohlen)
4. **Neue Artikel** - Falls Sie mehr als die 57 Beispiel-Artikel haben

---

## 🚀 EMPFOHLENER START-WORKFLOW

### Phase 1: Daten prüfen (Tag 1)
1. App öffnen: http://89.167.83.224:8080
2. "Artikel verwalten" → Beispiel-Artikel ansehen
3. Prüfen: Passen die Artikel zu Ihrem Sortiment?

### Phase 2: Preise aktualisieren (Tag 1-2)
1. "Preise pflegen" → Excel-Vorlage herunterladen
2. Ihre aktuellen Preise eintragen
3. Importieren

### Phase 3: Erste Wochenplanung (Tag 2)
1. "Wochenplanung" → Aktuelle Woche auswählen
2. Verfügbare Artikel zuweisen
3. Speichern

### Phase 4: Erste Kiste generieren (Tag 2)
1. "Generator" → Sortimentstyp wählen (z.B. OG12)
2. Woche auswählen
3. "Generieren" klicken
4. Ergebnis prüfen und ggf. anpassen

### Phase 5: Historie aufbauen (laufend)
1. Generierte Kisten freigeben
2. System lernt automatisch
3. Zukünftige Vorschläge werden besser

---

## 📁 IMPORT-VORLAGEN

Alle Vorlagen können in der App heruntergeladen werden:

1. **Artikel-Vorlage**: "Artikel verwalten" → "Vorlage herunterladen"
2. **Preis-Vorlage**: "Preise pflegen" → "Vorlage herunterladen"
3. **Wochenquelle-Vorlage**: "Wochenplanung" → "Vorlage herunterladen"
4. **Historie-Vorlage**: "Historie" → "Vorlage herunterladen"

---

## 🔄 PC-GÄRTNER INTEGRATION

Falls Sie PC-Gärtner nutzen:

### Automatischer Import möglich für:
- ✅ Artikel-Stammdaten
- ✅ Aktuelle Preise
- ✅ Kundendaten (zukünftig)

### Automatischer Export möglich für:
- ✅ Generierte Sortimente
- ✅ Kommissionierlisten

### Konfiguration:
- Dashboard → "PC-Gärtner Integration"
- Status prüfen
- Synchronisation starten

---

## ❓ HÄUFIGE FRAGEN

**Q: Muss ich alle Daten manuell eingeben?**
A: Nein! Excel-Import oder PC-Gärtner Sync möglich.

**Q: Kann ich mit den Beispieldaten testen?**
A: Ja! Die App ist sofort einsatzbereit zum Testen.

**Q: Wie pflege ich saisonale Produkte ein?**
A: Einfach in der Wochenplanung verfügbar machen, wenn Saison ist.

**Q: Was passiert mit alten Preisen?**
A: Bleiben in der Historie, System nutzt automatisch aktuellen Preis.

**Q: Wie viele historische Sortimente brauche ich?**
A: Minimum: 0 (funktioniert auch ohne)
Empfohlen: 10-20 für gute Vorschläge
Optimal: 50+ für beste Ergebnisse

---

## 📞 SUPPORT

Bei Fragen:
1. Dokumentation lesen: `PROJEKT-DOKUMENTATION.md`
2. PC-Gärtner Integration: `PCGAERTNER-INTEGRATION.md`
3. Deployment: `DEPLOYMENT-HETZNER.md`

---

## ✅ CHECKLISTE FÜR KURT

- [ ] App aufrufen und testen
- [ ] Beispiel-Artikel prüfen
- [ ] Aktuelle Preise vorbereiten (Excel)
- [ ] Preise importieren
- [ ] Erste Wochenplanung erstellen
- [ ] Erste Kiste generieren
- [ ] Ergebnis prüfen
- [ ] Bei Erfolg: Historische Daten importieren
- [ ] PC-Gärtner Integration konfigurieren (optional)

**Die App ist produktionsbereit! Alle Funktionen sind implementiert und getestet.** 🎉
