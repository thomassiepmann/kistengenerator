# PC-Gärtner Integration

## Übersicht

Die PC-Gärtner Integration ermöglicht den automatischen Datenaustausch zwischen der PC-Gärtner Software (https://pcgaertner.de/) und dem Paradieschen Kistengenerator.

## Unterstützte Module

- **Artikelmanager**: https://pcgaertner.de/pc-gaertner-module/artikelmanager/
- **Kundenstamm**: https://pcgaertner.de/pc-gaertner-module/kundenstamm/

## Funktionen

### 1. Artikel-Synchronisation
Importiert Artikel aus dem PC-Gärtner Artikelmanager:
- Artikel-SID
- Artikel-Name
- Kategorie
- Einheit (kg/Stück)

### 2. Preis-Synchronisation
Importiert aktuelle Preise aus PC-Gärtner:
- Artikel-SID
- Preis pro Einheit
- Gültigkeitsdatum

### 3. Sortiment-Export
Exportiert generierte Sortimente an PC-Gärtner:
- Sortiment-Typ
- Kalenderwoche/Jahr
- Artikel-Positionen mit Mengen
- Gesamtpreis

## Konfiguration

### Option 1: REST API (empfohlen)

Wenn PC-Gärtner eine REST API bereitstellt:

```bash
# Umgebungsvariablen setzen
export PCGAERTNER_API_URL="https://ihre-pcgaertner-url.de/api"
export PCGAERTNER_API_KEY="ihr-api-schluessel"

# Backend starten
cd backend
python main.py
```

### Option 2: CSV Import/Export (Fallback)

Wenn keine API verfügbar ist, nutzen Sie den manuellen CSV-Import/Export:

1. **Artikel importieren**:
   - Gehen Sie zu "Artikel verwalten"
   - Klicken Sie auf "Importieren"
   - Laden Sie die CSV-Datei aus PC-Gärtner hoch

2. **Preise importieren**:
   - Gehen Sie zu "Preise pflegen"
   - Klicken Sie auf "Importieren"
   - Laden Sie die Preis-CSV aus PC-Gärtner hoch

3. **Sortimente exportieren**:
   - Generieren Sie eine Kiste
   - Klicken Sie auf "CSV exportieren"
   - Importieren Sie die CSV in PC-Gärtner

## API-Endpoints

### Status prüfen
```http
GET /api/integration/status
```

**Response:**
```json
{
  "konfiguriert": true,
  "api_verfuegbar": true,
  "letzte_sync": "2026-02-26T00:00:00",
  "sync_methode": "API"
}
```

### Verbindung testen
```http
POST /api/integration/test
```

### Artikel synchronisieren
```http
POST /api/integration/sync-artikel
```

**Response:**
```json
{
  "status": "erfolg",
  "neu": 15,
  "aktualisiert": 42,
  "fehler": 0,
  "timestamp": "2026-02-26T00:00:00"
}
```

### Preise synchronisieren
```http
POST /api/integration/sync-preise
```

**Response:**
```json
{
  "status": "erfolg",
  "neu": 57,
  "aktualisiert": 0,
  "fehler": 0,
  "timestamp": "2026-02-26T00:00:00"
}
```

### Sortiment exportieren
```http
POST /api/integration/export-sortiment/{kiste_id}
```

## Dashboard-Integration

Die Integration ist direkt im Dashboard verfügbar:

1. **Status-Anzeige**: Zeigt ob die Integration konfiguriert ist
2. **Sync-Buttons**: 
   - "Artikel synchronisieren"
   - "Preise synchronisieren"
3. **Letzte Synchronisation**: Zeitstempel der letzten Sync

## CSV-Format

### Artikel-Import (CSV)
```csv
SID;Name;Kategorie;Einheit
13;Zucchini;Gemuese;Kilogramm
241;Paprika gelb;Gemuese;Kilogramm
22;Fenchel;Gemuese;Kilogramm
```

### Preis-Import (CSV)
```csv
SID;Preis;Gueltig_ab
13;2.89;2026-02-26
241;3.49;2026-02-26
22;2.99;2026-02-26
```

### Sortiment-Export (CSV)
```csv
Slot;Artikel;SID;Menge;Einheit;Einzelpreis;Positionspreis
Gemuese 1;Zucchini;13;0.65;Kilogramm;2.89;1.88
Gemuese 2;Paprika gelb;241;0.25;Kilogramm;3.49;0.87
Gemuese 3;Fenchel;22;0.70;Kilogramm;2.99;2.09
```

## Implementierungs-Details

### Backend-Modul
- **Datei**: `backend/pcgaertner_integration.py`
- **Klasse**: `PCGaertnerAPI`
- **Methoden**:
  - `sync_artikel_from_pcgaertner()`
  - `sync_preise_from_pcgaertner()`
  - `export_sortiment_to_pcgaertner()`
  - `get_integration_status()`
  - `test_connection()`

### Frontend-Integration
- **Dashboard**: `frontend/src/pages/Dashboard.jsx`
- **Komponente**: PC-Gärtner Integration Card
- **Features**:
  - Status-Anzeige
  - Sync-Buttons
  - Fehlerbehandlung

## Fehlerbehandlung

### Keine API konfiguriert
```json
{
  "status": "info",
  "nachricht": "PC-Gärtner Integration nicht konfiguriert",
  "hinweis": "Nutzen Sie CSV-Import/Export als Alternative"
}
```

### API-Fehler
```json
{
  "status": "fehler",
  "fehler": "API-Fehler: Connection refused",
  "timestamp": "2026-02-26T00:00:00"
}
```

### Artikel nicht gefunden
```json
{
  "status": "erfolg",
  "neu": 10,
  "aktualisiert": 5,
  "fehler": 2,
  "fehler_details": [
    "Artikel 999 nicht gefunden",
    "Fehlende Daten: {'sid': null}"
  ]
}
```

## Sicherheit

- **API-Key**: Wird über Umgebungsvariable `PCGAERTNER_API_KEY` gesetzt
- **HTTPS**: Empfohlen für Produktionsumgebung
- **Authentifizierung**: Bearer Token im Authorization Header

## Erweiterungen

### Zukünftige Features
- [ ] Kunden-Synchronisation
- [ ] Bestellungen importieren
- [ ] Lieferscheine generieren
- [ ] Automatische Synchronisation (Cron-Job)
- [ ] Webhook-Support

## Support

Bei Fragen zur Integration:
1. Prüfen Sie die PC-Gärtner API-Dokumentation
2. Testen Sie die Verbindung mit `/api/integration/test`
3. Nutzen Sie CSV-Import/Export als Fallback

## Beispiel-Workflow

### Tägliche Synchronisation

```bash
# 1. Artikel synchronisieren
curl -X POST http://localhost:8001/api/integration/sync-artikel

# 2. Preise synchronisieren
curl -X POST http://localhost:8001/api/integration/sync-preise

# 3. Kisten generieren
curl -X POST http://localhost:8001/api/kiste/generieren-alle?kw=9&jahr=2026

# 4. Sortimente exportieren
curl -X POST http://localhost:8001/api/integration/export-sortiment/1
```

## Lizenz

Die Integration ist Teil des Paradieschen Kistengenerators und unterliegt derselben Lizenz.
