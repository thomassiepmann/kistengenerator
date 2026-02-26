# 🔧 Troubleshooting - Fehler beheben

## ❌ "Fehler beim Generieren aller Sortimente"

### Mögliche Ursachen & Lösungen:

---

## 1️⃣ KEINE WOCHENQUELLE VORHANDEN

### Problem:
```
Generator kann keine Kiste erstellen, weil keine Artikel 
für die gewählte Woche verfügbar sind.
```

### Lösung:
```
1. Menü → "Wochenplanung"
2. Woche auswählen (z.B. KW 9/2026)
3. Für jeden Slot Artikel zuweisen
4. "Speichern" klicken
5. Zurück zum Generator
6. Erneut versuchen
```

---

## 2️⃣ KEINE PREISE VORHANDEN

### Problem:
```
Artikel sind verfügbar, aber haben keine Preise.
Generator kann Gesamtpreis nicht berechnen.
```

### Lösung:
```
1. Menü → "Preise pflegen"
2. Für alle verfügbaren Artikel Preise eintragen
3. "Gültig ab" Datum setzen (heute oder früher)
4. Speichern
5. Zurück zum Generator
6. Erneut versuchen
```

### Schnellcheck:
```bash
# Auf Server prüfen:
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
sqlite3 kistengenerator.db

SELECT COUNT(*) FROM preis WHERE gueltig_bis IS NULL OR gueltig_bis >= date('now');
-- Sollte > 0 sein

.quit
```

---

## 3️⃣ KEINE TAUSCHMUSTER

### Problem:
```
Artikel haben keine Mengen-Definitionen (Tauschmuster).
Generator weiß nicht, wie viel er nehmen soll.
```

### Lösung:
```
1. Prüfen ob Tauschmuster vorhanden:
   - Sollten bereits 69 Tauschmuster in DB sein
   
2. Falls nicht:
   - Mit Claude: "Erstelle Tauschmuster für alle Artikel"
   - Oder: seed_data.py erneut ausführen
```

### Schnellcheck:
```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
sqlite3 kistengenerator.db

SELECT COUNT(*) FROM tauschmuster;
-- Sollte > 0 sein (idealerweise 69)

.quit
```

---

## 4️⃣ BACKEND NICHT ERREICHBAR

### Problem:
```
Frontend kann nicht mit Backend kommunizieren.
API-Anfragen schlagen fehl.
```

### Lösung:
```
1. Backend-Status prüfen:
ssh root@89.167.83.224
systemctl status kistengenerator

2. Falls nicht läuft:
systemctl start kistengenerator

3. Logs prüfen:
journalctl -u kistengenerator -n 50

4. Falls Fehler:
systemctl restart kistengenerator
```

---

## 5️⃣ DATENBANK-FEHLER

### Problem:
```
Datenbank ist korrupt oder fehlt.
```

### Lösung:
```
1. Datenbank prüfen:
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
ls -lh kistengenerator.db

2. Falls Datei fehlt oder 0 Bytes:
python seed_data.py

3. Backend neu starten:
systemctl restart kistengenerator
```

---

## 6️⃣ ZIELPREIS NICHT ERREICHBAR

### Problem:
```
Generator kann mit verfügbaren Artikeln den 
Zielpreis nicht erreichen (zu teuer oder zu günstig).
```

### Lösung:
```
Option 1: Mehr Artikel verfügbar machen
- Wochenplanung → Mehr Optionen hinzufügen

Option 2: Zielpreis anpassen
- Masterplan → Zielpreis-Rahmen erweitern

Option 3: Preise prüfen
- Sind die Preise realistisch?
- Zu hohe Preise → Generator kann Ziel nicht erreichen
```

---

## 7️⃣ BROWSER-CACHE

### Problem:
```
Alte Version der App im Browser-Cache.
```

### Lösung:
```
1. Browser-Cache leeren:
   - Chrome: Strg+Shift+Delete
   - Firefox: Strg+Shift+Delete
   
2. Seite neu laden:
   - Strg+F5 (Hard Reload)
   
3. Oder:
   - Inkognito-Modus testen
```

---

## 🔍 DETAILLIERTE FEHLERSUCHE

### Schritt 1: Browser-Konsole öffnen

```
1. F12 drücken (Developer Tools)
2. Tab "Console" auswählen
3. "Generieren" klicken
4. Fehlermeldungen lesen
```

### Häufige Fehlermeldungen:

**"Network Error"**
```
→ Backend nicht erreichbar
→ Lösung: Backend-Status prüfen (siehe oben)
```

**"404 Not Found"**
```
→ API-Endpoint existiert nicht
→ Lösung: Backend neu starten
```

**"500 Internal Server Error"**
```
→ Backend-Fehler
→ Lösung: Logs prüfen (journalctl)
```

**"No matching articles found"**
```
→ Keine passenden Artikel in Wochenquelle
→ Lösung: Mehr Artikel verfügbar machen
```

**"Price target not achievable"**
```
→ Zielpreis nicht erreichbar
→ Lösung: Zielpreis anpassen oder mehr Artikel
```

---

### Schritt 2: Backend-Logs prüfen

```bash
ssh root@89.167.83.224
journalctl -u kistengenerator -f
```

**Dann im Browser "Generieren" klicken und Logs beobachten.**

Häufige Log-Meldungen:

```
ERROR: No wochenquelle found for KW 9/2026
→ Wochenplanung fehlt

ERROR: No prices found for article 13
→ Preise fehlen

ERROR: No tauschmuster found for article 13, size S
→ Tauschmuster fehlen

ERROR: Database connection failed
→ Datenbank-Problem
```

---

### Schritt 3: Datenbank direkt prüfen

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
sqlite3 kistengenerator.db

-- Wochenquelle prüfen
SELECT COUNT(*) FROM wochenquelle WHERE kalenderwoche = 9 AND jahr = 2026;

-- Preise prüfen
SELECT COUNT(*) FROM preis WHERE gueltig_bis IS NULL OR gueltig_bis >= date('now');

-- Tauschmuster prüfen
SELECT COUNT(*) FROM tauschmuster;

-- Artikel prüfen
SELECT COUNT(*) FROM artikel WHERE status = 'aktiv';

.quit
```

---

## 🚀 SCHNELL-FIX

### Wenn nichts hilft:

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend

# 1. Datenbank neu initialisieren
source venv/bin/activate
python seed_data.py

# 2. Backend neu starten
systemctl restart kistengenerator

# 3. Status prüfen
systemctl status kistengenerator

# 4. Im Browser:
# - Cache leeren (Strg+Shift+Delete)
# - Seite neu laden (Strg+F5)
# - Erneut versuchen
```

---

## 📞 SUPPORT-CHECKLISTE

Wenn Sie Hilfe brauchen, sammeln Sie diese Informationen:

```
□ Fehlermeldung (exakter Wortlaut)
□ Browser-Konsole (F12 → Console → Screenshot)
□ Backend-Logs (journalctl -u kistengenerator -n 50)
□ Welche Woche? (z.B. KW 9/2026)
□ Welcher Masterplan? (z.B. OG12)
□ Wochenquelle vorhanden? (Ja/Nein)
□ Preise vorhanden? (Ja/Nein)
```

---

## ✅ PRÄVENTIV-CHECKLISTE

### Vor dem Generieren prüfen:

```
□ Wochenplanung für gewählte Woche erstellt?
□ Alle Slots mit Artikeln gefüllt?
□ Preise für alle Artikel vorhanden?
□ Preise aktuell (gültig ab <= heute)?
□ Tauschmuster vorhanden?
□ Backend läuft? (systemctl status)
□ Masterplan aktiv?
```

---

## 🎯 TYPISCHE SZENARIEN

### Szenario 1: Erste Nutzung

```
Problem: "Fehler beim Generieren"

Ursache: Keine Wochenquelle

Lösung:
1. Wochenplanung → KW 9/2026
2. Artikel zuweisen
3. Speichern
4. Erneut generieren ✅
```

### Szenario 2: Nach Preis-Änderung

```
Problem: "Zielpreis nicht erreichbar"

Ursache: Neue Preise zu hoch

Lösung:
1. Zielpreis anpassen (z.B. 14-18€ statt 12-16€)
2. Oder: Günstigere Artikel verfügbar machen
3. Erneut generieren ✅
```

### Szenario 3: Nach Server-Neustart

```
Problem: "Backend nicht erreichbar"

Ursache: Service nicht gestartet

Lösung:
systemctl start kistengenerator ✅
```

---

## 💡 TIPPS

### Tipp 1: Immer mit Beispieldaten testen
```
Die App enthält Beispieldaten.
Testen Sie erst damit, bevor Sie eigene Daten nutzen.
```

### Tipp 2: Logs sind Ihr Freund
```
journalctl -u kistengenerator -f
→ Zeigt genau was schief läuft
```

### Tipp 3: Browser-Konsole nutzen
```
F12 → Console
→ Zeigt Frontend-Fehler
```

### Tipp 4: Schritt für Schritt
```
1. Erst Artikel
2. Dann Preise
3. Dann Wochenplanung
4. Dann Generieren
→ Nicht alles auf einmal!
```

---

**Bei Problemen: Ruhe bewahren, Checkliste durchgehen, Logs prüfen!** 🔧
