# 🌱 Wochenquelle - Die Quelle für den Masterplan

## 💡 Das Konzept verstehen

### Masterplan = Bauplan (WAS)
Der Masterplan definiert **WAS** in die Kiste soll:
- 3 Sorten Gemüse
- 1 Rohkost
- 3 Sorten Obst
- 1 Salat

### Wochenquelle = Verfügbarkeit (WOMIT)
Die Wochenquelle definiert **WOMIT** die Kiste gefüllt wird:
- **Welche** Artikel sind diese Woche verfügbar?
- **Welche** Zucchini-Sorte?
- **Welche** Äpfel?
- **Welche** Salate?

---

## 🎯 BEISPIEL: Vom Masterplan zur fertigen Kiste

### Schritt 1: Masterplan OG12

**Bauplan sagt:**
```
Slot 1: Gemüse
Slot 2: Gemüse  
Slot 3: Gemüse
Slot 4: Rohkost
Slot 5: Obst
Slot 6: Obst
Slot 7: Obst
Slot 8: Salat
```

**Aber WELCHE Artikel?** → Das sagt die Wochenquelle!

---

### Schritt 2: Wochenquelle KW 9/2026

**Verfügbare Artikel diese Woche:**

**Gemüse:**
- Zucchini (SID 13)
- Kürbis (SID 14)
- Brokkoli (SID 15)
- Blumenkohl (SID 16)
- Fenchel (SID 22)

**Rohkost:**
- Paprika gelb (SID 241)
- Gurke (SID 242)
- Tomate (SID 243)

**Obst:**
- Äpfel Elstar (SID 101)
- Birnen (SID 102)
- Bananen (SID 103)
- Orangen (SID 104)

**Salat:**
- Kopfsalat (SID 201)
- Rucola (SID 202)

---

### Schritt 3: Generator kombiniert beides

**Generator nimmt:**
1. **Masterplan:** "Ich brauche 3x Gemüse, 1x Rohkost, 3x Obst, 1x Salat"
2. **Wochenquelle:** "Diese Artikel sind verfügbar"
3. **Preise:** "Das kosten die Artikel"
4. **Tauschmuster:** "So viel darf ich nehmen"
5. **Historie:** "Das hat früher gut funktioniert"

**Generator erstellt:**
```
Slot 1: Zucchini 650g (Gemüse)
Slot 2: Brokkoli 500g (Gemüse)
Slot 3: Fenchel 400g (Gemüse)
Slot 4: Paprika gelb 250g (Rohkost)
Slot 5: Äpfel Elstar 800g (Obst)
Slot 6: Birnen 600g (Obst)
Slot 7: Bananen 500g (Obst)
Slot 8: Kopfsalat 1 Stück (Salat)

Gesamtpreis: 14.50€ ✅ (im Rahmen 12-16€)
```

---

## 📅 WOCHENQUELLE ERSTELLEN

### Methode 1: In der App (EMPFOHLEN)

**Schritt 1: Wochenplanung öffnen**
1. App → Menü → **"Wochenplanung"**
2. Woche auswählen (z.B. KW 9/2026)

**Schritt 2: Artikel zuweisen**

Für jeden Slot einen oder mehrere Artikel zuweisen:

```
Gemüse 1: Zucchini, Kürbis
Gemüse 2: Brokkoli, Blumenkohl
Gemüse 3: Fenchel, Sellerie
Rohkost 1: Paprika, Gurke, Tomate
Obst 1: Äpfel Elstar, Äpfel Jonagold
Obst 2: Birnen, Orangen
Obst 3: Bananen, Kiwi
Salat 1: Kopfsalat, Rucola, Feldsalat
```

**Schritt 3: Speichern**
- Button **"Speichern"** klicken
- Wochenquelle ist fertig! ✅

---

### Methode 2: Von Vorwoche kopieren

**Wenn sich wenig ändert:**

1. Wochenplanung öffnen
2. Neue Woche auswählen (z.B. KW 10)
3. Button **"Von Vorwoche kopieren"**
4. Anpassen was sich ändert:
   - Erdbeeren raus (keine Saison mehr)
   - Spargel rein (Saison beginnt)
5. Speichern

**Spart Zeit!** ⏱️

---

### Methode 3: Excel-Import

**Für viele Wochen auf einmal:**

**Schritt 1: Vorlage herunterladen**
1. Wochenplanung → "Vorlage herunterladen"

**Schritt 2: Excel ausfüllen**

| KW | Jahr | Slot | Artikel-SID |
|----|------|------|-------------|
| 9 | 2026 | Gemuese 1 | 13 |
| 9 | 2026 | Gemuese 1 | 14 |
| 9 | 2026 | Gemuese 2 | 15 |
| 9 | 2026 | Rohkost 1 | 241 |
| 9 | 2026 | Obst 1 | 101 |
| ... | ... | ... | ... |

**Schritt 3: Importieren**
1. "Importieren" klicken
2. Excel-Datei auswählen
3. Fertig! ✅

---

## 🔄 SAISONALE PLANUNG

### Beispiel: Jahresplanung

**Frühling (März-Mai):**
```
Gemüse: Spargel, Radieschen, Kohlrabi
Obst: Erdbeeren, Rhabarber
Salat: Rucola, Feldsalat
```

**Sommer (Juni-August):**
```
Gemüse: Tomaten, Gurken, Zucchini, Paprika
Obst: Kirschen, Pfirsiche, Aprikosen
Salat: Kopfsalat, Eisbergsalat
```

**Herbst (September-November):**
```
Gemüse: Kürbis, Kohl, Rote Beete
Obst: Äpfel, Birnen, Trauben
Salat: Endivien, Radicchio
```

**Winter (Dezember-Februar):**
```
Gemüse: Kohl, Wurzelgemüse, Lauch
Obst: Äpfel (Lager), Orangen, Mandarinen
Salat: Feldsalat, Chicorée
```

### Wie umsetzen?

**Option 1: Wöchentlich anpassen**
- Jede Woche neue Wochenquelle
- Saisonale Artikel rein/raus

**Option 2: Monatlich planen**
- Alle 4 Wochen auf einmal
- Excel-Import nutzen

**Option 3: Mit Claude**
```
"Erstelle Wochenquellen für März 2026 (KW 9-13)
mit folgenden saisonalen Artikeln:
- Spargel, Radieschen, Erdbeeren, ..."
```

---

## 🎨 FLEXIBILITÄT IN DER WOCHENQUELLE

### Mehrere Artikel pro Slot

**Warum?**
- Generator kann optimal auswählen
- Bessere Preisoptimierung
- Mehr Abwechslung

**Beispiel:**
```
Obst 1: Äpfel Elstar, Äpfel Jonagold, Äpfel Boskoop
```

Generator wählt:
- Günstigsten Apfel
- Oder besten Match aus Historie
- Oder für beste Gesamtpreis-Optimierung

---

### Ein Artikel pro Slot

**Warum?**
- Feste Vorgabe
- Keine Auswahl nötig
- Schneller

**Beispiel:**
```
Salat 1: Kopfsalat (nur dieser!)
```

Generator nimmt:
- Immer Kopfsalat
- Keine Alternative

---

## 💡 BEST PRACTICES

### ✅ DO's:

**1. Mehrere Optionen pro Slot**
```
Gemüse 1: Zucchini, Kürbis, Brokkoli
→ Generator kann optimal wählen
```

**2. Saisonale Artikel**
```
Frühling: Spargel verfügbar machen
Winter: Spargel rausnehmen
```

**3. Vorwoche kopieren**
```
Spart Zeit bei kleinen Änderungen
```

**4. Regelmäßig aktualisieren**
```
Wöchentlich oder alle 2 Wochen
```

---

### ❌ DON'Ts:

**1. Zu wenig Optionen**
```
Gemüse 1: Nur Zucchini
→ Wenn Zucchini zu teuer, keine Alternative!
```

**2. Veraltete Wochenquellen**
```
Erdbeeren im Winter verfügbar lassen
→ Unrealistisch!
```

**3. Ohne Wochenquelle generieren**
```
Generator braucht Wochenquelle!
→ Fehler!
```

---

## 🔍 WOCHENQUELLE PRÜFEN

### In der App:

1. Menü → "Wochenplanung"
2. Woche auswählen
3. Alle Slots ansehen
4. Prüfen: Sind alle Kategorien abgedeckt?

### Checkliste:

- [ ] Genug Gemüse-Optionen?
- [ ] Rohkost verfügbar?
- [ ] Obst-Auswahl vorhanden?
- [ ] Salate verfügbar?
- [ ] Saisonale Artikel aktuell?
- [ ] Preise für alle Artikel vorhanden?

---

## 🚀 WORKFLOW: Von Masterplan zu Kiste

### Schritt-für-Schritt:

**1. Masterplan erstellen** (einmalig)
```
OG12: 3 Gemüse, 1 Rohkost, 3 Obst, 1 Salat
```

**2. Wochenquelle erstellen** (wöchentlich)
```
KW 9: Zucchini, Brokkoli, Äpfel, Kopfsalat, ...
```

**3. Generator starten**
```
App → Generator → OG12 → KW 9 → Generieren
```

**4. Ergebnis prüfen**
```
Artikel-Liste ansehen
Preis prüfen (12-16€?)
Mengen prüfen
```

**5. Anpassen (optional)**
```
Artikel tauschen
Mengen ändern
```

**6. Freigeben**
```
Button "Freigeben"
→ Wird zur Historie
→ System lernt!
```

**7. Nächste Woche**
```
Wochenquelle aktualisieren
Wieder generieren
```

---

## 📊 ZUSAMMENHANG VISUALISIERT

```
MASTERPLAN (Bauplan)
    ↓
    "Ich brauche: 3 Gemüse, 1 Rohkost, 3 Obst, 1 Salat"
    ↓
WOCHENQUELLE (Verfügbarkeit)
    ↓
    "Verfügbar: Zucchini, Brokkoli, Äpfel, Paprika, ..."
    ↓
PREISE (Kosten)
    ↓
    "Zucchini 2.89€, Brokkoli 3.49€, ..."
    ↓
TAUSCHMUSTER (Mengen)
    ↓
    "Zucchini 550-750g, Brokkoli 400-600g, ..."
    ↓
HISTORIE (Erfahrung)
    ↓
    "Letzte Woche: Zucchini + Brokkoli = gut!"
    ↓
GENERATOR (Kombination)
    ↓
    Optimiert: Preis, Menge, Erfahrung
    ↓
FERTIGE KISTE
    ↓
    "Zucchini 650g, Brokkoli 500g, Äpfel 800g, ..."
    Gesamtpreis: 14.50€ ✅
```

---

## ❓ HÄUFIGE FRAGEN

**Q: Muss ich jede Woche eine neue Wochenquelle erstellen?**
A: Nein! "Von Vorwoche kopieren" und nur Änderungen machen.

**Q: Kann ich mehrere Artikel pro Slot zuweisen?**
A: Ja! Sogar empfohlen für bessere Optimierung.

**Q: Was passiert wenn ein Artikel nicht verfügbar ist?**
A: Einfach aus Wochenquelle entfernen. Generator nimmt Alternative.

**Q: Kann ich Wochenquellen im Voraus planen?**
A: Ja! Excel-Import für mehrere Wochen auf einmal.

**Q: Wie weit im Voraus planen?**
A: Empfohlen: 2-4 Wochen im Voraus.

---

## 🎯 QUICK-REFERENZ

### Wochenquelle in 3 Schritten:

**1. Woche auswählen**
```
App → Wochenplanung → KW 9/2026
```

**2. Artikel zuweisen**
```
Für jeden Slot: Verfügbare Artikel auswählen
```

**3. Speichern**
```
Button "Speichern" → Fertig!
```

### Zeit:
- **Erste Woche:** 15-20 Minuten
- **Folgewochen:** 5-10 Minuten (kopieren + anpassen)
- **Mit Excel:** 30 Minuten für 4 Wochen

---

## ✅ CHECKLISTE

- [ ] Masterplan vorhanden
- [ ] Woche ausgewählt
- [ ] Alle Slots mit Artikeln gefüllt
- [ ] Saisonale Artikel berücksichtigt
- [ ] Preise für alle Artikel vorhanden
- [ ] Gespeichert
- [ ] Mit Generator getestet

**Fertig! Die Wochenquelle erweckt Ihren Masterplan zum Leben!** 🌱

---

## 🎉 ZUSAMMENFASSUNG

### Masterplan + Wochenquelle = Fertige Kiste

**Masterplan sagt:**
- WAS in die Kiste soll (Struktur)
- WIE VIELE Positionen (Slots)
- WELCHER Preis-Rahmen (Zielpreis)

**Wochenquelle sagt:**
- WOMIT gefüllt wird (Artikel)
- WAS verfügbar ist (Saison)
- WELCHE Optionen (Auswahl)

**Generator kombiniert:**
- Masterplan-Vorgaben
- Wochenquelle-Verfügbarkeit
- Preise
- Mengen
- Historie

**Ergebnis:**
- Optimale Kiste
- Im Preis-Rahmen
- Mit verfügbaren Artikeln
- Basierend auf Erfahrung

---

**Die Wochenquelle ist der Schlüssel zum Erfolg!** 🔑
