# 📋 QUICK START HANDOUT - Kistengenerator

## 🚀 In 5 Minuten loslegen

---

## 1️⃣ ARTIKEL HOCHLADEN

### Schritt 1: Vorlage herunterladen
1. App öffnen: http://89.167.83.224:8080
2. Menü → **"Artikel verwalten"**
3. Button **"Vorlage herunterladen"** klicken
4. Excel-Datei wird heruntergeladen

### Schritt 2: Artikel eintragen
Öffnen Sie die Excel-Datei und tragen Sie ein:

| SID | Name | Kategorie | Einheit | Status |
|-----|------|-----------|---------|--------|
| 13 | Zucchini | Gemuese | Kilogramm | aktiv |
| 241 | Paprika gelb | Gemuese | Kilogramm | aktiv |
| 22 | Fenchel | Gemuese | Kilogramm | aktiv |

**Kategorien:** Gemuese, Obst, Salat, Kraeuter
**Einheit:** Kilogramm oder Stueck

### Schritt 3: Hochladen
1. Zurück zu "Artikel verwalten"
2. Button **"Importieren"** klicken
3. Excel-Datei auswählen
4. **Fertig!** ✅

---

## 2️⃣ PREISE HOCHLADEN

### Schritt 1: Vorlage herunterladen
1. Menü → **"Preise pflegen"**
2. Button **"Vorlage herunterladen"**

### Schritt 2: Preise eintragen
| Artikel-SID | Preis | Gültig ab |
|-------------|-------|-----------|
| 13 | 2.89 | 2026-02-26 |
| 241 | 3.49 | 2026-02-26 |
| 22 | 2.99 | 2026-02-26 |

### Schritt 3: Hochladen
1. "Preise pflegen" → **"Importieren"**
2. Excel-Datei auswählen
3. **Fertig!** ✅

**💡 Tipp:** Für saisonale Preise einfach neuen Preis mit neuem Datum anlegen!

---

## 3️⃣ GEWICHTE/STÜCKZAHLEN EINPFLEGEN

### Was sind Tauschmuster?
Definieren Min/Max-Mengen pro Artikel und Kistengröße.

**Beispiel:**
- Zucchini Größe S: 550-750g (Standard: 650g)
- Zucchini Größe M: 800-1200g (Standard: 1000g)

### Schritt 1: Vorlage herunterladen
1. Menü → **"Einstellungen"** (oder direkt in Datenbank)
2. Vorlage "Tauschmuster" herunterladen

### Schritt 2: Mengen eintragen
| Artikel-SID | Größe | Min | Max | Standard | Einheit |
|-------------|-------|-----|-----|----------|---------|
| 13 | S | 0.55 | 0.75 | 0.65 | Kilogramm |
| 13 | M | 0.80 | 1.20 | 1.00 | Kilogramm |
| 241 | S | 0.20 | 0.30 | 0.25 | Kilogramm |

**Größen:** S, M, L
**Einheit:** Kilogramm oder Stueck

### Schritt 3: Hochladen
1. Importieren
2. **Fertig!** ✅

**💡 Bereits vorhanden:** 69 Tauschmuster für Beispiel-Artikel!

---

## 4️⃣ MASTERPLAENE GENERIEREN

### Was ist ein Masterplan?
Ein Sortimentstyp mit festen Eigenschaften:
- Name (z.B. "OG12")
- Anzahl Slots (z.B. 12)
- Zielpreis-Rahmen (z.B. 12-16€)
- Größe (S, M, L)

### Bereits vorhanden:
✅ **OG12** - Obst & Gemüse 12 Slots
✅ **RE12** - Regional 12 Slots
✅ **OOG12** - Ohne Obst Gemüse 12 Slots

### Neuen Masterplan erstellen:

**Option 1: Mit Claude/Cline (empfohlen)**

Sagen Sie einfach:
```
"Erstelle einen neuen Masterplan 'SALAT10' mit:
- 10 Slots nur für Salate
- Größe S
- Zielpreis 8-12€"
```

Claude/Cline macht alles automatisch! ✅

**Option 2: Manuell in Datenbank**

SSH auf Server:
```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
sqlite3 kistengenerator.db

INSERT INTO masterplan (name, groesse, slot_anzahl, zielpreis_min, zielpreis_max, ist_aktiv)
VALUES ('SALAT10', 'S', 10, 8.00, 12.00, 1);
```

---

## 5️⃣ ERSTE KISTE GENERIEREN

### Schritt 1: Wochenplanung
1. Menü → **"Wochenplanung"**
2. Woche auswählen (z.B. KW 9/2026)
3. Für jeden Slot einen Artikel zuweisen
4. **"Speichern"**

**💡 Tipp:** Button "Von Vorwoche kopieren" nutzen!

### Schritt 2: Kiste generieren
1. Menü → **"Generator"**
2. Sortimentstyp wählen (z.B. OG12)
3. Woche wählen (z.B. KW 9/2026)
4. Button **"Generieren"** klicken
5. **Fertig!** ✅

### Schritt 3: Ergebnis prüfen
- Artikel-Liste ansehen
- Mengen prüfen
- Gesamtpreis prüfen
- Bei Bedarf manuell anpassen

### Schritt 4: Freigeben
- Button **"Freigeben"** klicken
- Kiste wird zur Historie
- System lernt daraus! 🎓

---

## 📊 ZUSAMMENFASSUNG

### Reihenfolge für den Start:

1. **Artikel hochladen** (5 Min)
   - Vorlage → Ausfüllen → Importieren

2. **Preise hochladen** (5 Min)
   - Vorlage → Ausfüllen → Importieren

3. **Gewichte eintragen** (10 Min)
   - Vorlage → Ausfüllen → Importieren
   - ODER: Beispiel-Gewichte nutzen

4. **Wochenplanung** (10 Min)
   - Verfügbare Artikel zuweisen

5. **Erste Kiste generieren** (2 Min)
   - Generator → Generieren → Prüfen

**Gesamt: ~30 Minuten** ⏱️

---

## 💡 WICHTIGE TIPPS

### ✅ DO's:
- Vorlage herunterladen BEVOR Sie Daten eintragen
- Artikel-SID muss eindeutig sein
- Preise mit Datum versehen
- Generierte Kisten freigeben (System lernt!)

### ❌ DON'Ts:
- Keine Sonderzeichen in SID
- Nicht ohne Wochenplanung generieren
- Nicht ohne Preise generieren

---

## 🔄 EXCEL-VORLAGEN ÜBERSICHT

| Vorlage | Wo herunterladen | Wofür |
|---------|------------------|-------|
| **Artikel** | Artikel verwalten | Neue Artikel anlegen |
| **Preise** | Preise pflegen | Preise einpflegen |
| **Tauschmuster** | Einstellungen | Gewichte/Mengen |
| **Wochenquelle** | Wochenplanung | Verfügbarkeit |
| **Historie** | Historie | Vergangene Kisten |

---

## 🆘 HÄUFIGE FEHLER

### "Keine Artikel gefunden"
→ Artikel hochladen vergessen

### "Keine Preise vorhanden"
→ Preise hochladen vergessen

### "Keine Wochenquelle"
→ Wochenplanung erstellen

### "Preis nicht im Zielrahmen"
→ Preise zu hoch/niedrig oder Tauschmuster anpassen

---

## 📞 HILFE

### Bei Fragen:

**Option 1: Dokumentation**
- `FÜR-KURT-DATENANFORDERUNG.md` - Detaillierte Anleitung
- `FÜR-KURT-ANPASSUNGEN.md` - Anpassungen mit Claude
- `PROJEKT-DOKUMENTATION.md` - Vollständige Doku

**Option 2: Claude fragen**
```
"Wie lade ich Artikel hoch?"
"Wie erstelle ich einen Masterplan?"
"Wie ändere ich Gewichte?"
```

**Option 3: Cline nutzen**
- VS Code öffnen
- Cline Extension
- Beschreiben was Sie wollen

---

## ✅ CHECKLISTE

- [ ] App aufgerufen (http://89.167.83.224:8080)
- [ ] Artikel-Vorlage heruntergeladen
- [ ] Artikel eingetragen und hochgeladen
- [ ] Preis-Vorlage heruntergeladen
- [ ] Preise eingetragen und hochgeladen
- [ ] Tauschmuster geprüft (oder Beispiele nutzen)
- [ ] Erste Wochenplanung erstellt
- [ ] Erste Kiste generiert
- [ ] Ergebnis geprüft
- [ ] Kiste freigegeben

**Geschafft! Sie können jetzt Kisten generieren!** 🎉

---

## 🚀 NÄCHSTE SCHRITTE

Nach dem ersten Erfolg:

1. **Mehr Artikel** hinzufügen
2. **Historische Kisten** importieren (bessere Vorschläge!)
3. **Eigene Masterplaene** erstellen
4. **PC-Gärtner** Integration einrichten
5. **Design** anpassen (mit Claude)

---

**Viel Erfolg mit dem Kistengenerator!** 🥬🍎🥕
