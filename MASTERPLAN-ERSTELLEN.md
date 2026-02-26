# 🎯 Masterplan erstellen - Schritt für Schritt

## Was ist ein Masterplan?

Ein Masterplan definiert die **Struktur** eines Sortiments:
- Wie viele Slots (Positionen)
- Welche Kategorien in welchen Slots
- Zielpreis-Rahmen
- Kistengröße (S, M, L)

---

## 📋 BEISPIEL: OG12 Masterplan

### Struktur:
- **Name:** OG12 (Obst & Gemüse 12 Slots)
- **Größe:** S
- **Zielpreis:** 12-16€
- **Slots:** 12

### Slot-Verteilung:
```
Slot 1:  Gemüse
Slot 2:  Gemüse
Slot 3:  Gemüse
Slot 4:  Rohkost (z.B. Paprika, Gurke, Tomate)
Slot 5:  Obst
Slot 6:  Obst
Slot 7:  Obst
Slot 8:  Salat
Slot 9:  Gemüse (flexibel)
Slot 10: Gemüse (flexibel)
Slot 11: Obst (flexibel)
Slot 12: Gemüse (flexibel)
```

---

## 🔧 MASTERPLAN ERSTELLEN - 3 METHODEN

### Methode 1: Mit Claude/Cline (EMPFOHLEN)

**Einfach beschreiben was Sie wollen:**

```
"Erstelle einen neuen Masterplan 'OG12_NEU' mit:
- 12 Slots
- Größe S
- Zielpreis 12-16€
- Slot-Verteilung:
  * Slot 1-3: Gemüse (fest)
  * Slot 4: Rohkost (fest)
  * Slot 5-7: Obst (fest)
  * Slot 8: Salat (fest)
  * Slot 9-12: Flexibel (Gemüse oder Obst)"
```

**Claude/Cline macht:**
1. Masterplan in Datenbank anlegen
2. Alle 12 Slots mit Kategorien definieren
3. Im Frontend verfügbar machen
4. Fertig! ✅

---

### Methode 2: SQL-Befehle (Manuell)

**Schritt 1: Auf Server einloggen**
```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
sqlite3 kistengenerator.db
```

**Schritt 2: Masterplan anlegen**
```sql
INSERT INTO masterplan (
    name, 
    groesse, 
    slot_anzahl, 
    zielpreis_min, 
    zielpreis_max, 
    ist_aktiv
) VALUES (
    'OG12_NEU',  -- Name
    'S',         -- Größe
    12,          -- Anzahl Slots
    12.00,       -- Min-Preis
    16.00,       -- Max-Preis
    1            -- Aktiv (1=ja, 0=nein)
);
```

**Schritt 3: Masterplan-ID ermitteln**
```sql
SELECT id FROM masterplan WHERE name = 'OG12_NEU';
-- Angenommen die ID ist 4
```

**Schritt 4: Slots definieren**
```sql
-- Slot 1: Gemüse
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 1, 'Gemuese', 1);

-- Slot 2: Gemüse
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 2, 'Gemuese', 1);

-- Slot 3: Gemüse
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 3, 'Gemuese', 1);

-- Slot 4: Rohkost
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 4, 'Rohkost', 1);

-- Slot 5: Obst
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 5, 'Obst', 1);

-- Slot 6: Obst
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 6, 'Obst', 1);

-- Slot 7: Obst
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 7, 'Obst', 1);

-- Slot 8: Salat
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 8, 'Salat', 1);

-- Slot 9-12: Flexibel (NULL = beliebige Kategorie)
INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 9, NULL, 0);

INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 10, NULL, 0);

INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 11, NULL, 0);

INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
VALUES (4, 12, NULL, 0);
```

**Schritt 5: Prüfen**
```sql
SELECT * FROM masterplan WHERE name = 'OG12_NEU';
SELECT * FROM masterplan_slot WHERE masterplan_id = 4 ORDER BY slot_nummer;
```

**Schritt 6: Beenden**
```sql
.quit
```

**Schritt 7: Backend neu starten**
```bash
systemctl restart kistengenerator
```

---

### Methode 3: Python-Script

**Datei erstellen:** `create_masterplan.py`

```python
import sqlite3

# Verbindung zur Datenbank
conn = sqlite3.connect('kistengenerator.db')
cursor = conn.cursor()

# Masterplan anlegen
cursor.execute("""
    INSERT INTO masterplan (name, groesse, slot_anzahl, zielpreis_min, zielpreis_max, ist_aktiv)
    VALUES (?, ?, ?, ?, ?, ?)
""", ('OG12_NEU', 'S', 12, 12.00, 16.00, 1))

masterplan_id = cursor.lastrowid

# Slots definieren
slots = [
    (1, 'Gemuese', 1),   # Slot 1: Gemüse (Pflicht)
    (2, 'Gemuese', 1),   # Slot 2: Gemüse (Pflicht)
    (3, 'Gemuese', 1),   # Slot 3: Gemüse (Pflicht)
    (4, 'Rohkost', 1),   # Slot 4: Rohkost (Pflicht)
    (5, 'Obst', 1),      # Slot 5: Obst (Pflicht)
    (6, 'Obst', 1),      # Slot 6: Obst (Pflicht)
    (7, 'Obst', 1),      # Slot 7: Obst (Pflicht)
    (8, 'Salat', 1),     # Slot 8: Salat (Pflicht)
    (9, None, 0),        # Slot 9: Flexibel
    (10, None, 0),       # Slot 10: Flexibel
    (11, None, 0),       # Slot 11: Flexibel
    (12, None, 0),       # Slot 12: Flexibel
]

for slot_nr, kategorie, pflicht in slots:
    cursor.execute("""
        INSERT INTO masterplan_slot (masterplan_id, slot_nummer, kategorie, ist_pflicht)
        VALUES (?, ?, ?, ?)
    """, (masterplan_id, slot_nr, kategorie, pflicht))

conn.commit()
conn.close()

print(f"✅ Masterplan 'OG12_NEU' erstellt mit ID {masterplan_id}")
```

**Ausführen:**
```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
source venv/bin/activate
python create_masterplan.py
systemctl restart kistengenerator
```

---

## 🎨 WEITERE BEISPIELE

### Beispiel 1: SALAT10 (Salat-Kiste)

```
Name: SALAT10
Größe: S
Zielpreis: 8-12€
Slots: 10

Slot 1-5:  Salat (verschiedene Sorten)
Slot 6-8:  Gemüse (Rohkost)
Slot 9-10: Kräuter
```

**Claude-Prompt:**
```
"Erstelle Masterplan 'SALAT10':
- 10 Slots, Größe S, Zielpreis 8-12€
- Slot 1-5: Salat (Pflicht)
- Slot 6-8: Gemüse/Rohkost (Pflicht)
- Slot 9-10: Kräuter (Pflicht)"
```

---

### Beispiel 2: PREMIUM15 (Premium-Kiste)

```
Name: PREMIUM15
Größe: M
Zielpreis: 18-24€
Slots: 15

Slot 1-5:  Gemüse (Premium)
Slot 6-8:  Rohkost
Slot 9-12: Obst (Premium)
Slot 13:   Salat
Slot 14:   Kräuter
Slot 15:   Spezialität
```

**Claude-Prompt:**
```
"Erstelle Masterplan 'PREMIUM15':
- 15 Slots, Größe M, Zielpreis 18-24€
- Slot 1-5: Gemüse
- Slot 6-8: Rohkost
- Slot 9-12: Obst
- Slot 13: Salat
- Slot 14: Kräuter
- Slot 15: Flexibel"
```

---

### Beispiel 3: REGIONAL12 (Regional)

```
Name: REGIONAL12
Größe: S
Zielpreis: 13-17€
Slots: 12

Slot 1-4:  Gemüse (regional)
Slot 5-6:  Rohkost (regional)
Slot 7-9:  Obst (regional)
Slot 10:   Salat (regional)
Slot 11-12: Flexibel
```

---

## 📊 KATEGORIEN ÜBERSICHT

### Verfügbare Kategorien:

| Kategorie | Beispiel-Artikel |
|-----------|------------------|
| **Gemuese** | Zucchini, Kürbis, Brokkoli |
| **Rohkost** | Paprika, Gurke, Tomate, Radieschen |
| **Obst** | Äpfel, Birnen, Bananen |
| **Salat** | Kopfsalat, Rucola, Feldsalat |
| **Kraeuter** | Basilikum, Petersilie, Schnittlauch |

### Neue Kategorie hinzufügen:

**Mit Claude:**
```
"Füge neue Kategorie 'Exotisch' hinzu für:
- Mango, Papaya, Ananas, Avocado"
```

---

## 🔍 MASTERPLAN PRÜFEN

### In der Datenbank:

```sql
-- Alle Masterplaene anzeigen
SELECT * FROM masterplan;

-- Slots eines Masterplans anzeigen
SELECT 
    slot_nummer, 
    kategorie, 
    ist_pflicht 
FROM masterplan_slot 
WHERE masterplan_id = 4 
ORDER BY slot_nummer;
```

### In der App:

1. Menü → "Masterplaene"
2. Masterplan auswählen
3. Slots ansehen

---

## 💡 TIPPS & TRICKS

### Tipp 1: Pflicht vs. Flexibel

**Pflicht-Slots (ist_pflicht = 1):**
- MUSS diese Kategorie enthalten
- Generator sucht nur in dieser Kategorie

**Flexible Slots (ist_pflicht = 0, kategorie = NULL):**
- Kann beliebige Kategorie sein
- Generator wählt optimal aus

### Tipp 2: Slot-Reihenfolge

Die Slot-Nummer bestimmt die Reihenfolge in der Kiste:
- Slot 1 = Erste Position
- Slot 12 = Letzte Position

### Tipp 3: Mehrere Größen

Erstellen Sie denselben Masterplan für verschiedene Größen:
```
OG12_S - Größe S, 12 Slots, 12-16€
OG15_M - Größe M, 15 Slots, 16-22€
OG18_L - Größe L, 18 Slots, 22-28€
```

### Tipp 4: Saisonale Masterplaene

```
FRUEHLING12 - Spargel, Erdbeeren, etc.
SOMMER12 - Tomaten, Gurken, etc.
HERBST12 - Kürbis, Äpfel, etc.
WINTER12 - Kohl, Wurzelgemüse, etc.
```

---

## 🚀 SCHNELL-ANLEITUNG

### Für Kurt: Neuen Masterplan in 5 Minuten

**Schritt 1:** Struktur überlegen
```
Name: ?
Größe: S/M/L
Slots: ?
Zielpreis: ?-?€
Kategorien: ?
```

**Schritt 2:** Claude fragen
```
"Erstelle Masterplan '[NAME]' mit:
- [ANZAHL] Slots
- Größe [S/M/L]
- Zielpreis [MIN]-[MAX]€
- Slot-Verteilung:
  * Slot X-Y: [KATEGORIE]
  * Slot Z: [KATEGORIE]
  * etc."
```

**Schritt 3:** Prüfen
- In App → "Masterplaene"
- Neuen Masterplan sehen
- Testen mit Generator

**Schritt 4:** Anpassen
- Falls nötig mit Claude nachbessern
- Zielpreis anpassen
- Slots ändern

---

## ❓ HÄUFIGE FRAGEN

**Q: Kann ich Slots nachträglich ändern?**
A: Ja! Mit Claude oder SQL UPDATE-Befehl.

**Q: Kann ich einen Masterplan kopieren?**
A: Ja! Mit Claude: "Kopiere OG12 zu OG12_NEU und ändere..."

**Q: Wie viele Masterplaene kann ich haben?**
A: Unbegrenzt!

**Q: Kann ich Masterplaene löschen?**
A: Ja, aber besser deaktivieren (ist_aktiv = 0)

**Q: Was ist der Unterschied zwischen Gemüse und Rohkost?**
A: 
- **Gemüse:** Alles Gemüse (auch zum Kochen)
- **Rohkost:** Nur roh essbar (Paprika, Gurke, Tomate, etc.)

---

## 📞 HILFE

### Bei Problemen:

**Option 1: Claude fragen**
```
"Ich möchte einen Masterplan erstellen mit..."
```

**Option 2: Dokumentation**
- Diese Datei: `MASTERPLAN-ERSTELLEN.md`
- Projekt-Doku: `PROJEKT-DOKUMENTATION.md`

**Option 3: Beispiele ansehen**
```sql
-- Bestehende Masterplaene ansehen
SELECT * FROM masterplan;
SELECT * FROM masterplan_slot WHERE masterplan_id = 1;
```

---

## ✅ CHECKLISTE

- [ ] Struktur überlegt (Name, Größe, Slots, Preis)
- [ ] Kategorien festgelegt (Gemüse, Obst, Salat, etc.)
- [ ] Masterplan erstellt (mit Claude oder SQL)
- [ ] In App geprüft
- [ ] Mit Generator getestet
- [ ] Bei Bedarf angepasst

**Fertig! Ihr individueller Masterplan ist einsatzbereit!** 🎉

---

## 🎯 ZUSAMMENFASSUNG

### Masterplan = Bauplan für Sortiment

**Definiert:**
- ✅ Anzahl Positionen (Slots)
- ✅ Welche Kategorien wo
- ✅ Pflicht vs. Flexibel
- ✅ Zielpreis-Rahmen
- ✅ Kistengröße

**Erstellen:**
- 🥇 **Am einfachsten:** Mit Claude beschreiben
- 🥈 **Alternativ:** SQL-Befehle
- 🥉 **Für Profis:** Python-Script

**Dauer:** 5-10 Minuten pro Masterplan

**Flexibilität:** Unbegrenzt anpassbar!

---

**Viel Erfolg beim Erstellen Ihrer individuellen Masterplaene!** 🎨
