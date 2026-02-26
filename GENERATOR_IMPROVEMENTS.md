# Generator-Verbesserungen - Implementierungsplan

## Status: Das Masterplan-Modell hat bereits zielpreis_min und zielpreis_max!

Die aktuelle Implementierung verwendet bereits einen Preisrahmen:
- `zielpreis_min` = Untergrenze
- `zielpreis_max` = Obergrenze

## Anpassungen die gemacht werden:

### 1. ✅ Zielpreis ist bereits vorhanden
Das Modell hat `zielpreis_min` und `zielpreis_max` - perfekt!

### 2. ✅ Toleranz ±10% ist bereits implementiert
Der Generator nutzt bereits den Rahmen zwischen min und max.
Wir können die Seed-Daten so anpassen, dass:
- zielpreis_min = zielpreis * 0.9 (90%)
- zielpreis_max = zielpreis * 1.1 (110%)

### 3. 🔧 Frontend Generator-Seite MUSS verbessert werden
Aktuelle Probleme:
- Zu einfach
- Keine Matching-Score-Anzeige
- Keine CSV-Export
- Keine "Alle generieren"-Funktion

### 4. 🔧 CSV-Export fehlt komplett

### 5. 🔧 "Alle Sortimente generieren" fehlt

### 6. 🔧 Verfügbarkeits-Check fehlt
Aktuell: Artikel werden global aus Wochenquelle genommen
Neu: Artikel müssen pro Masterplan markiert sein

## Implementierungsschritte:

1. ✅ Seed-Daten anpassen (Zielpreise mit ±10%)
2. ✅ Generator-Seite komplett neu (mit allen Features)
3. ✅ CSV-Export-Funktion
4. ✅ "Alle generieren"-Endpoint im Backend
5. ✅ Verfügbarkeits-Check in WochenQuelle-Modell

## Neue Zielpreise (mit ±10% Toleranz):

```python
OG12-S: 12.00€ → min: 10.80€, max: 13.20€
OG12-M: 15.00€ → min: 13.50€, max: 16.50€
OG15-S: 15.00€ → min: 13.50€, max: 16.50€
OG15-M: 18.00€ → min: 16.20€, max: 19.80€
OG18-S: 18.00€ → min: 16.20€, max: 19.80€
OG18-M: 21.00€ → min: 18.90€, max: 23.10€
OG21-S: 21.00€ → min: 18.90€, max: 23.10€
OG21-M: 24.00€ → min: 21.60€, max: 26.40€
```

## Zeitaufwand:
- Seed-Daten: 5 Min
- Generator-Seite: 30 Min
- CSV-Export: 10 Min
- Alle-generieren: 15 Min
- Verfügbarkeits-Check: 20 Min

**Gesamt: ca. 80 Minuten**

Soll ich mit der Implementierung beginnen?
