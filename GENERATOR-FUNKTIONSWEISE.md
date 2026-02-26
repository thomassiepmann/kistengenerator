# 🧠 Generator-Funktionsweise - Wie der intelligente Algorithmus arbeitet

## 📋 Übersicht: Die 5 Schritte zur perfekten Kiste

```
1. MASTERPLAN → Was soll rein? (Struktur)
2. WOCHENQUELLE → Womit füllen? (Verfügbarkeit)
3. TAUSCHMUSTER → Wie viel? (Mengen-Ranges)
4. PREISE → Was kostet es? (Optimierung)
5. HISTORIE → Was hat früher funktioniert? (Intelligenz)
```

---

## 🎯 SCHRITT 3: TAUSCHMUSTER - Die Mengen-Ranges

### Was sind Tauschmuster?

**Tauschmuster definieren flexible Mengen-Bereiche** für jeden Artikel in jeder Sortimentsgröße.

**Statt fixer Werte:**
```
❌ Zucchini: IMMER 650g
```

**Nutzen wir Ranges:**
```
✅ Zucchini Größe S: 550-750g (Standard: 650g)
✅ Zucchini Größe M: 800-1200g (Standard: 1000g)
✅ Zucchini Größe L: 1300-1800g (Standard: 1500g)
```

---

### Warum Ranges?

**Flexibilität für Preisoptimierung:**

**Beispiel:**
```
Zielpreis: 12-16€
Zucchini: 2.89€/kg
Range: 550-750g

Generator kann wählen:
- 550g = 1.59€ (wenn Budget knapp)
- 650g = 1.88€ (Standard)
- 750g = 2.17€ (wenn Budget übrig)
```

**Der Generator passt die Menge an, um den Zielpreis zu erreichen!**

---

### Tauschmuster-Beispiel

**Artikel: Zucchini (SID 13)**

| Größe | Min | Max | Standard | Einheit |
|-------|-----|-----|----------|---------|
| S | 550g | 750g | 650g | Kilogramm |
| M | 800g | 1200g | 1000g | Kilogramm |
| L | 1300g | 1800g | 1500g | Kilogramm |

**Artikel: Paprika gelb (SID 241)**

| Größe | Min | Max | Standard | Einheit |
|-------|-----|-----|----------|---------|
| S | 200g | 300g | 250g | Kilogramm |
| M | 300g | 450g | 375g | Kilogramm |
| L | 450g | 600g | 525g | Kilogramm |

**Artikel: Kopfsalat (SID 201)**

| Größe | Min | Max | Standard | Einheit |
|-------|-----|-----|----------|---------|
| S | 1 | 1 | 1 | Stueck |
| M | 1 | 2 | 1 | Stueck |
| L | 2 | 2 | 2 | Stueck |

---

## 🔄 SCHRITT 4: PREIS-OPTIMIERUNG

### Wie der Generator Mengen anpasst

**Gegeben:**
- Masterplan OG12: Zielpreis 12-16€
- Wochenquelle: Zucchini, Brokkoli, Äpfel verfügbar
- Tauschmuster: Ranges für alle Artikel
- Preise: Aktuell

**Generator-Logik:**

```
1. Starte mit Standard-Mengen
   Zucchini 650g × 2.89€ = 1.88€
   Brokkoli 500g × 3.49€ = 1.75€
   ...
   Gesamt: 15.20€ ✅ (im Rahmen!)

2. Falls zu teuer (z.B. 17.50€):
   → Reduziere Mengen (Min-Werte nutzen)
   Zucchini 550g statt 650g
   Brokkoli 400g statt 500g
   Gesamt: 14.80€ ✅

3. Falls zu günstig (z.B. 11.00€):
   → Erhöhe Mengen (Max-Werte nutzen)
   Zucchini 750g statt 650g
   Brokkoli 600g statt 500g
   Gesamt: 13.20€ ✅
```

---

## 🎓 SCHRITT 5: HISTORISCHES MATCHING - Die Intelligenz

### Das Problem ohne Historie:

**Generator ohne Erfahrung:**
```
Wochenquelle: 20 Artikel verfügbar
Masterplan: 12 Slots zu füllen

Mögliche Kombinationen: Millionen!
Welche ist die beste?
```

**Lösung: Aus der Vergangenheit lernen!**

---

### Wie funktioniert historisches Matching?

**Schritt 1: Historie aufbauen**

Jede freigegebene Kiste wird gespeichert:

```
KW 5/2025, OG12:
- Zucchini 650g
- Brokkoli 500g
- Fenchel 400g
- Paprika 250g
- Äpfel 800g
- Birnen 600g
- Bananen 500g
- Kopfsalat 1 Stück
Preis: 14.20€ ✅ ERFOLGREICH
```

---

**Schritt 2: Wochenquelle für neue Woche**

```
KW 9/2026:
Verfügbar: Zucchini, Brokkoli, Fenchel, Paprika, 
           Äpfel, Birnen, Bananen, Kopfsalat, 
           Kürbis, Gurken, Orangen
```

---

**Schritt 3: Matching-Suche**

Generator sucht in Historie nach **größter Übereinstimmung**:

```
Historisches Sortiment KW 5/2025:
✓ Zucchini - VERFÜGBAR
✓ Brokkoli - VERFÜGBAR
✓ Fenchel - VERFÜGBAR
✓ Paprika - VERFÜGBAR
✓ Äpfel - VERFÜGBAR
✓ Birnen - VERFÜGBAR
✓ Bananen - VERFÜGBAR
✓ Kopfsalat - VERFÜGBAR

Match: 8/8 = 100% ✅ PERFEKT!
```

---

**Schritt 4: Artikel übernehmen**

```
Generator nimmt historisches Sortiment als Basis:
- Zucchini 650g
- Brokkoli 500g
- Fenchel 400g
- Paprika 250g
- Äpfel 800g
- Birnen 600g
- Bananen 500g
- Kopfsalat 1 Stück
```

---

**Schritt 5: Mit aktuellen Preisen neu berechnen**

```
Alte Preise (KW 5/2025):
Zucchini 2.79€ × 0.65kg = 1.81€

Neue Preise (KW 9/2026):
Zucchini 2.89€ × 0.65kg = 1.88€

Generator passt Mengen an:
Zucchini 630g × 2.89€ = 1.82€ (leicht reduziert)

Neuer Gesamtpreis: 14.50€ ✅
```

---

### Fallback-Strategie

**Was wenn kein perfekter Match?**

**Beispiel:**
```
Wochenquelle KW 10:
Verfügbar: Zucchini, Kürbis, Äpfel, Orangen, Kopfsalat
NICHT verfügbar: Brokkoli, Fenchel, Paprika, Birnen, Bananen

Historisches Sortiment KW 5:
Match: 3/8 = 37.5% ❌ ZU WENIG
```

**Generator sucht nächstbesten Match:**

```
Suche 1: Match 8/8 = 100% → Nicht gefunden
Suche 2: Match 7/8 = 87.5% → Nicht gefunden
Suche 3: Match 6/8 = 75% → Gefunden! ✅

Historisches Sortiment KW 3/2025:
✓ Zucchini - VERFÜGBAR
✓ Kürbis - VERFÜGBAR
✗ Brokkoli - NICHT verfügbar → Ersatz: Blumenkohl
✓ Paprika - VERFÜGBAR
✓ Äpfel - VERFÜGBAR
✓ Orangen - VERFÜGBAR
✗ Birnen - NICHT verfügbar → Ersatz: Kiwi
✓ Kopfsalat - VERFÜGBAR

Match: 6/8 = 75% ✅ GUT GENUG!
```

---

### Ersatz-Logik

**Wenn Artikel nicht verfügbar:**

1. **Gleiche Kategorie suchen**
   ```
   Brokkoli (Gemüse) nicht verfügbar
   → Suche anderes Gemüse: Blumenkohl ✅
   ```

2. **Ähnlicher Preis**
   ```
   Brokkoli 3.49€/kg
   → Blumenkohl 3.29€/kg ✅ ÄHNLICH
   ```

3. **Ähnliche Menge**
   ```
   Brokkoli 400-600g
   → Blumenkohl 400-600g ✅ PASST
   ```

---

## 🔍 KOMPLETTES BEISPIEL

### Ausgangssituation:

**Masterplan OG12:**
- 3 Gemüse, 1 Rohkost, 3 Obst, 1 Salat
- Zielpreis: 12-16€
- Größe: S

**Wochenquelle KW 9/2026:**
- Gemüse: Zucchini, Kürbis, Brokkoli, Fenchel
- Rohkost: Paprika, Gurken, Tomaten
- Obst: Äpfel, Birnen, Bananen, Orangen
- Salat: Kopfsalat, Rucola

**Tauschmuster (Größe S):**
- Zucchini: 550-750g
- Brokkoli: 400-600g
- Paprika: 200-300g
- Äpfel: 700-900g
- etc.

**Preise:**
- Zucchini: 2.89€/kg
- Brokkoli: 3.49€/kg
- Paprika: 4.99€/kg
- Äpfel: 2.49€/kg
- etc.

---

### Generator-Ablauf:

**1. Historie durchsuchen**
```
Suche Sortimente mit:
- Masterplan: OG12
- Größe: S
- Hohe Übereinstimmung mit Wochenquelle

Gefunden: KW 5/2025
Match: 8/8 = 100% ✅
```

**2. Historisches Sortiment laden**
```
KW 5/2025:
- Zucchini 650g
- Brokkoli 500g
- Fenchel 400g
- Paprika 250g
- Äpfel 800g
- Birnen 600g
- Bananen 500g
- Kopfsalat 1 Stück
Damaliger Preis: 14.20€
```

**3. Mit aktuellen Preisen berechnen**
```
Zucchini 650g × 2.89€ = 1.88€
Brokkoli 500g × 3.49€ = 1.75€
Fenchel 400g × 2.99€ = 1.20€
Paprika 250g × 4.99€ = 1.25€
Äpfel 800g × 2.49€ = 1.99€
Birnen 600g × 2.79€ = 1.67€
Bananen 500g × 2.29€ = 1.15€
Kopfsalat 1 × 1.49€ = 1.49€

Gesamt: 14.38€ ✅ (im Rahmen 12-16€)
```

**4. Feintuning (optional)**
```
Preis ist gut, aber Generator optimiert noch:
- Äpfel von 800g auf 750g (günstiger)
- Brokkoli von 500g auf 550g (mehr Wert)

Neuer Preis: 14.25€ ✅ OPTIMAL!
```

**5. Ergebnis präsentieren**
```
FERTIGE KISTE OG12 - KW 9/2026:

Slot 1: Zucchini 650g - 1.88€
Slot 2: Brokkoli 550g - 1.92€
Slot 3: Fenchel 400g - 1.20€
Slot 4: Paprika gelb 250g - 1.25€
Slot 5: Äpfel Elstar 750g - 1.87€
Slot 6: Birnen 600g - 1.67€
Slot 7: Bananen 500g - 1.15€
Slot 8: Kopfsalat 1 Stück - 1.49€

GESAMTPREIS: 14.43€ ✅
Zielpreis: 12-16€ ✅
Match-Qualität: 100% ✅
```

---

## 💡 VORTEILE DES SYSTEMS

### 1. Intelligente Auswahl
```
Nicht zufällig, sondern basierend auf Erfahrung
→ Bewährte Kombinationen werden bevorzugt
```

### 2. Preis-Optimierung
```
Flexible Mengen innerhalb der Ranges
→ Zielpreis wird immer erreicht
```

### 3. Lerneffekt
```
Je mehr Kisten freigegeben werden
→ Desto besser werden die Vorschläge
```

### 4. Fallback-Sicherheit
```
Wenn kein perfekter Match
→ Nächstbester wird genommen
→ Immer ein Ergebnis!
```

### 5. Saisonalität
```
Historische Sortimente aus gleicher Saison
→ Passende Artikel-Kombinationen
```

---

## 📊 MATCHING-QUALITÄT

### Bewertung der Übereinstimmung:

| Match-Rate | Qualität | Aktion |
|------------|----------|--------|
| 90-100% | ⭐⭐⭐⭐⭐ Perfekt | Sofort nutzen |
| 75-89% | ⭐⭐⭐⭐ Sehr gut | Nutzen mit kleinen Anpassungen |
| 60-74% | ⭐⭐⭐ Gut | Nutzen, mehr Ersetzungen |
| 40-59% | ⭐⭐ Okay | Nutzen als Basis, viel anpassen |
| <40% | ⭐ Schwach | Neues Sortiment erstellen |

---

## 🔄 WORKFLOW VISUALISIERT

```
START
  ↓
[1] MASTERPLAN LADEN
  "OG12: 3 Gemüse, 1 Rohkost, 3 Obst, 1 Salat"
  ↓
[2] WOCHENQUELLE LADEN
  "Verfügbar: Zucchini, Brokkoli, Äpfel, ..."
  ↓
[3] HISTORIE DURCHSUCHEN
  "Suche ähnliche Sortimente..."
  ↓
[4] BESTEN MATCH FINDEN
  "KW 5/2025: 100% Match ✅"
  ↓
[5] ARTIKEL ÜBERNEHMEN
  "Zucchini, Brokkoli, Fenchel, ..."
  ↓
[6] TAUSCHMUSTER ANWENDEN
  "Zucchini 550-750g, Brokkoli 400-600g, ..."
  ↓
[7] AKTUELLE PREISE LADEN
  "Zucchini 2.89€, Brokkoli 3.49€, ..."
  ↓
[8] MENGEN OPTIMIEREN
  "Anpassen für Zielpreis 12-16€"
  ↓
[9] PREIS BERECHNEN
  "Gesamt: 14.43€ ✅"
  ↓
[10] ERGEBNIS PRÄSENTIEREN
  "Fertige Kiste mit 8 Artikeln"
  ↓
ENDE
```

---

## ✅ ZUSAMMENFASSUNG

### Die 5 Säulen des Generators:

**1. MASTERPLAN**
- Definiert Struktur
- Gibt Kategorien vor
- Setzt Zielpreis

**2. WOCHENQUELLE**
- Liefert verfügbare Artikel
- Begrenzt Auswahl
- Berücksichtigt Saison

**3. TAUSCHMUSTER**
- Flexible Mengen-Ranges
- Ermöglicht Optimierung
- Verschiedene Größen

**4. PREISE**
- Aktuelle Kosten
- Basis für Berechnung
- Optimierungs-Ziel

**5. HISTORIE**
- Bewährte Kombinationen
- Intelligente Auswahl
- Lerneffekt

### Ergebnis:
**Optimale Kiste mit minimalem Aufwand!** 🎯

---

**Der Generator wird mit jeder freigegebenen Kiste intelligenter!** 🧠
