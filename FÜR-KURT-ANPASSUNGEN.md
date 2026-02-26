# Für Kurt: App nach Ihren Wünschen anpassen

## 🎨 Übersicht: Wie flexibel ist die App?

**SEHR FLEXIBEL!** Sie können fast alles anpassen - mit oder ohne Programmierkenntnisse.

---

## 🔧 ANPASSUNGEN OHNE PROGRAMMIERUNG

### 1️⃣ PREISE ÄNDERN

**Wo:** In der App unter "Preise pflegen"

**Was können Sie ändern:**
- ✅ Alle Preise jederzeit
- ✅ Saisonale Preise (mit Gültigkeitsdatum)
- ✅ Preise für verschiedene Zeiträume
- ✅ Historische Preise bleiben erhalten

**Wie:**
1. "Preise pflegen" öffnen
2. Artikel auswählen
3. Neuen Preis eingeben
4. "Gültig ab" Datum setzen
5. Speichern

**Oder per Excel:**
1. Vorlage herunterladen
2. Alle Preise in Excel eintragen
3. Importieren → Fertig!

---

### 2️⃣ GEWICHTE/MENGEN ÄNDERN (Tauschmuster)

**Wo:** Datenbank oder Excel-Import

**Was können Sie ändern:**
- ✅ Min/Max-Mengen pro Artikel
- ✅ Standard-Mengen
- ✅ Verschiedene Mengen für S/M/L Kisten
- ✅ Stück vs. Kilogramm

**Beispiel:**
```
Zucchini Größe S: 550-750g (Standard: 650g)
Zucchini Größe M: 800-1200g (Standard: 1000g)
Zucchini Größe L: 1300-1800g (Standard: 1500g)
```

**Wie anpassen:**
1. Excel-Vorlage "Tauschmuster" herunterladen
2. Ihre Wunsch-Mengen eintragen
3. Importieren

---

### 3️⃣ ARTIKEL HINZUFÜGEN/ÄNDERN

**Wo:** "Artikel verwalten"

**Was können Sie ändern:**
- ✅ Neue Artikel hinzufügen
- ✅ Artikel-Namen ändern
- ✅ Kategorien ändern (Gemüse, Obst, Salat, etc.)
- ✅ Artikel deaktivieren (ohne zu löschen)
- ✅ Einheit ändern (kg ↔ Stück)

**Wie:**
- **Einzeln:** "Neuer Artikel" Button
- **Massenimport:** Excel-Vorlage nutzen

---

### 4️⃣ MASTERPLAENE ANPASSEN

**Wo:** Datenbank (mit Hilfe von Claude/Cline)

**Was können Sie ändern:**
- ✅ Anzahl der Slots (z.B. 15 statt 12)
- ✅ Zielpreis-Rahmen (z.B. 10-14€ statt 12-16€)
- ✅ Sortimentstypen (z.B. "BIO20", "REGIONAL15")
- ✅ Größen (S, M, L, XL)

**Beispiel neue Masterplaene:**
```
OG15 - Obst & Gemüse 15 Slots, Größe M, 15-20€
BIO20 - Bio Premium 20 Slots, Größe L, 20-25€
MINI8 - Mini-Kiste 8 Slots, Größe S, 8-12€
```

**Wie anpassen:**
→ Siehe Abschnitt "Mit Claude/Cline arbeiten"

---

### 5️⃣ SORTIMENTSGROSSEN ÄNDERN

**Aktuell:** S, M, L

**Können Sie ändern zu:**
- ✅ XS, S, M, L, XL
- ✅ Klein, Mittel, Groß
- ✅ 1-Person, 2-Personen, Familie
- ✅ Beliebige Namen

**Wie:**
→ Mit Claude/Cline (siehe unten)

---

### 6️⃣ SORTIMENTSARTEN ÄNDERN

**Aktuell:** OG12, RE12, OOG12

**Können Sie ändern zu:**
- ✅ Beliebige Namen
- ✅ Beliebige Slot-Anzahl
- ✅ Verschiedene Kategorien-Verteilungen
- ✅ Spezial-Sortimente (z.B. nur Salat, nur Obst)

**Beispiele:**
```
SALAT10 - Salat-Kiste 10 Slots
OBST8 - Obst-Kiste 8 Slots
PREMIUM15 - Premium-Mix 15 Slots
REGIONAL20 - Regional 20 Slots
VEGAN12 - Vegan 12 Slots
```

---

## 🤖 ANPASSUNGEN MIT KI-HILFE (Claude/Cline)

### Was ist Claude/Cline?

**Claude:** KI-Assistent (wie ich!)
**Cline:** VS Code Extension für Code-Änderungen

**Sie können:**
- ✅ In natürlicher Sprache sagen was Sie wollen
- ✅ Keine Programmierkenntnisse nötig
- ✅ Claude/Cline macht die Änderungen
- ✅ Sie prüfen und bestätigen

---

### 🎯 BEISPIEL-PROMPTS FÜR CLAUDE/CLINE

#### Neue Sortimentsgröße hinzufügen:

```
"Füge eine neue Sortimentsgröße 'XL' hinzu für 
Familien-Kisten mit 18 Slots und Zielpreis 22-28€"
```

**Claude/Cline wird:**
1. Datenbank-Modell anpassen
2. Neue Tauschmuster für XL erstellen
3. Frontend anpassen (Dropdown-Menü)
4. Alles testen

---

#### Neuen Masterplan erstellen:

```
"Erstelle einen neuen Masterplan 'SALAT10' mit:
- 10 Slots nur für Salate
- Größe S
- Zielpreis 8-12€
- Slots: 5x Blattsalat, 3x Gemüse, 2x Kräuter"
```

**Claude/Cline wird:**
1. Masterplan in Datenbank anlegen
2. Slots definieren
3. Im Frontend verfügbar machen

---

#### Tauschmuster anpassen:

```
"Ändere alle Zucchini-Mengen:
- Größe S: 400-600g (Standard 500g)
- Größe M: 700-900g (Standard 800g)
- Größe L: 1000-1400g (Standard 1200g)"
```

**Claude/Cline wird:**
1. Datenbank aktualisieren
2. Änderungen testen
3. Bestätigung geben

---

#### Neue Kategorie hinzufügen:

```
"Füge eine neue Artikel-Kategorie 'Kräuter' hinzu
und erstelle 5 Kräuter-Artikel:
- Basilikum, Petersilie, Schnittlauch, Dill, Koriander
- Alle als 'Bund' (Stück)"
```

**Claude/Cline wird:**
1. Kategorie anlegen
2. Artikel erstellen
3. Preise vorschlagen
4. Tauschmuster erstellen

---

#### Design anpassen:

```
"Ändere die Hauptfarbe der App von Grün zu Blau
und das Logo zu unserem Firmenlogo"
```

**Claude/Cline wird:**
1. CSS-Farben anpassen
2. Logo austauschen
3. Alle Seiten aktualisieren

---

#### Neue Funktion hinzufügen:

```
"Füge einen 'Favoriten'-Button hinzu, damit ich
häufig genutzte Sortimente markieren kann"
```

**Claude/Cline wird:**
1. Datenbank erweitern
2. Button im Frontend hinzufügen
3. Favoriten-Filter erstellen
4. Alles implementieren

---

## 💬 WIE MIT CLAUDE/CLINE ARBEITEN?

### Option 1: Mit Claude (Chat)

**Schritt 1:** Öffnen Sie Claude (wie diesen Chat)

**Schritt 2:** Beschreiben Sie Ihre Wünsche:
```
"Ich möchte im Kistengenerator folgendes ändern:
[Ihre Beschreibung]"
```

**Schritt 3:** Claude gibt Ihnen:
- Code-Änderungen
- Schritt-für-Schritt Anleitung
- SQL-Befehle für Datenbank
- Erklärungen

**Schritt 4:** Sie führen die Änderungen aus (oder lassen Claude helfen)

---

### Option 2: Mit Cline (VS Code Extension)

**Schritt 1:** VS Code öffnen mit Projekt

**Schritt 2:** Cline Extension aktivieren

**Schritt 3:** Prompt eingeben:
```
"Ändere den Masterplan OG12 zu 15 Slots"
```

**Schritt 4:** Cline:
- Analysiert Code
- Macht Änderungen
- Zeigt Vorschau
- Wartet auf Bestätigung

**Schritt 5:** Sie prüfen und bestätigen

**Schritt 6:** Fertig!

---

## 🛠️ BEISPIEL-WORKFLOWS

### Workflow 1: Neue Kistengröße "Familie" hinzufügen

**Prompt an Claude/Cline:**
```
"Füge eine neue Kistengröße 'Familie' hinzu:
- 20 Slots
- Zielpreis 25-32€
- Größere Mengen als L
- Neue Tauschmuster für alle Artikel"
```

**Claude/Cline macht:**
1. ✅ Datenbank: Neue Größe "Familie"
2. ✅ Tauschmuster: Mengen für "Familie"
3. ✅ Frontend: Dropdown erweitern
4. ✅ Generator: Logik anpassen
5. ✅ Testen

**Dauer:** 10-15 Minuten

---

### Workflow 2: Saisonale Sortimente

**Prompt:**
```
"Erstelle 4 saisonale Masterplaene:
- FRÜHLING12 (März-Mai): Spargel, Erdbeeren, etc.
- SOMMER12 (Juni-Aug): Tomaten, Gurken, etc.
- HERBST12 (Sep-Nov): Kürbis, Äpfel, etc.
- WINTER12 (Dez-Feb): Kohl, Wurzelgemüse, etc.

Jeder mit passenden Slots für die Saison"
```

**Claude/Cline macht:**
1. ✅ 4 neue Masterplaene
2. ✅ Saisonale Slot-Definitionen
3. ✅ Im Frontend verfügbar
4. ✅ Dokumentation

**Dauer:** 20-30 Minuten

---

### Workflow 3: Preisanpassung für Inflation

**Prompt:**
```
"Erhöhe alle Preise um 5% ab 01.03.2026
und behalte die alten Preise in der Historie"
```

**Claude/Cline macht:**
1. ✅ Alle aktuellen Preise laden
2. ✅ +5% rechnen
3. ✅ Neue Preise mit Datum 01.03.2026 anlegen
4. ✅ Alte Preise bleiben erhalten

**Dauer:** 5 Minuten

---

## 📝 PROMPT-VORLAGEN FÜR KURT

### Vorlage 1: Masterplan ändern
```
"Ändere den Masterplan [NAME]:
- Neue Slot-Anzahl: [ZAHL]
- Neuer Zielpreis: [MIN]-[MAX]€
- Neue Slot-Verteilung: [BESCHREIBUNG]"
```

### Vorlage 2: Artikel-Kategorie
```
"Füge neue Artikel-Kategorie '[NAME]' hinzu
mit folgenden Artikeln:
- [Artikel 1]
- [Artikel 2]
- [Artikel 3]"
```

### Vorlage 3: Mengen anpassen
```
"Ändere Tauschmuster für [ARTIKEL]:
- Größe S: [MIN]-[MAX]g
- Größe M: [MIN]-[MAX]g
- Größe L: [MIN]-[MAX]g"
```

### Vorlage 4: Design ändern
```
"Ändere das Design:
- Hauptfarbe: [FARBE]
- Logo: [BESCHREIBUNG]
- Schriftart: [NAME]"
```

### Vorlage 5: Neue Funktion
```
"Füge folgende Funktion hinzu:
[BESCHREIBUNG WAS DIE FUNKTION TUN SOLL]"
```

---

## 🎓 LERNKURVE

### Ohne Programmierkenntnisse:

**Woche 1:** Daten einpflegen (Preise, Artikel)
**Woche 2:** Erste Anpassungen mit Claude
**Woche 3:** Eigene Masterplaene erstellen
**Woche 4:** Komplexe Änderungen selbst promten

### Mit Programmierkenntnissen:

**Tag 1:** Code verstehen
**Tag 2:** Erste Änderungen selbst machen
**Tag 3:** Neue Features entwickeln

---

## 🚀 EMPFEHLUNG FÜR KURT

### Phase 1: Kennenlernen (Woche 1)
1. App mit Beispieldaten testen
2. Alle Funktionen ausprobieren
3. Notizen machen: "Was möchte ich ändern?"

### Phase 2: Erste Anpassungen (Woche 2)
1. Eigene Preise einpflegen
2. Eigene Artikel hinzufügen
3. Erste Kisten generieren

### Phase 3: Mit Claude experimentieren (Woche 3)
1. Kleine Änderung mit Claude testen
2. Z.B. "Ändere Zielpreis von OG12"
3. Ergebnis prüfen
4. Lernen wie es funktioniert

### Phase 4: Eigene Anpassungen (Woche 4+)
1. Eigene Masterplaene erstellen
2. Sortimentsgrößen anpassen
3. Design personalisieren
4. Neue Funktionen hinzufügen

---

## 💡 TIPPS FÜR ERFOLGREICHE PROMPTS

### ✅ Gute Prompts:

**Spezifisch:**
```
"Ändere den Zielpreis von OG12 auf 13-17€"
```

**Mit Kontext:**
```
"Ich habe 3 Kistengr

ößen (S/M/L). 
Füge eine vierte Größe 'XL' für Großfamilien hinzu 
mit 20 Slots und Zielpreis 25-30€"
```

**Mit Beispielen:**
```
"Erstelle einen Masterplan wie OG12, aber nur mit Obst.
Name: OBST10, 10 Slots, Zielpreis 10-14€"
```

### ❌ Vermeiden:

**Zu vage:**
```
"Mach die App besser"
```

**Zu komplex auf einmal:**
```
"Ändere alles: Design, Preise, Masterplaene, 
füge 50 neue Funktionen hinzu..."
```

**Ohne Kontext:**
```
"Ändere das"
```

---

## 🔧 TECHNISCHE DETAILS (Optional)

### Wo sind die Daten?

**Datenbank:** `/var/www/kistengenerator/backend/kistengenerator.db`
- SQLite Datenbank
- Kann mit jedem SQLite-Tool geöffnet werden
- Backup vor Änderungen empfohlen!

**Code:**
- Backend: `/var/www/kistengenerator/backend/`
- Frontend: `/var/www/kistengenerator/frontend/`

### Wichtige Dateien:

**Backend:**
- `models.py` - Datenbank-Struktur
- `generator.py` - Generator-Logik
- `seed_data.py` - Beispieldaten

**Frontend:**
- `src/pages/` - Alle Seiten
- `src/styles/colors.css` - Farben
- `src/services/api.js` - API-Calls

---

## 📞 SUPPORT

### Bei Fragen zu Anpassungen:

**Option 1:** Fragen Sie Claude
```
"Wie kann ich [ÄNDERUNG] machen?"
```

**Option 2:** Nutzen Sie Cline
```
Beschreiben Sie die Änderung → Cline macht es
```

**Option 3:** Dokumentation lesen
- `PROJEKT-DOKUMENTATION.md`
- `GENERATOR_IMPROVEMENTS.md`

---

## ✅ ZUSAMMENFASSUNG

### Was Kurt OHNE Programmierung ändern kann:
- ✅ Alle Preise
- ✅ Alle Artikel
- ✅ Alle Mengen (via Excel)
- ✅ Wochenplanung
- ✅ Saisonale Verfügbarkeit

### Was Kurt MIT Claude/Cline ändern kann:
- ✅ Masterplaene
- ✅ Sortimentsgrößen
- ✅ Sortimentsarten
- ✅ Design
- ✅ Neue Funktionen
- ✅ Alles andere!

### Wie flexibel ist die App?
**SEHR FLEXIBEL!** Fast alles kann angepasst werden.

### Wie schwer ist es?
**EINFACH!** Mit Claude/Cline in natürlicher Sprache beschreiben → Fertig!

---

**Die App ist Ihr Baukasten - bauen Sie was Sie brauchen!** 🎨🔧

