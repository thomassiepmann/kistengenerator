# 📦 Paradieschen Kistengenerator - Projektübersicht

> **Automatisierte Sortimentsgenerierung für Bio-Obst & Gemüse-Kisten**  
> Version 1.0.0 | Stand: 25.02.2026

---

## 📁 Projektstruktur

```
kistengenerator/
├── backend/                          # FastAPI Backend
│   ├── main.py                       # API-Endpunkte (FastAPI App)
│   ├── models.py                     # SQLAlchemy Datenmodelle
│   ├── schemas.py                    # Pydantic Request/Response Schemas
│   ├── database.py                   # Datenbank-Konfiguration (SQLite)
│   ├── generator.py                  # Kernlogik: Kistengenerierung
│   ├── muster_lernen.py              # KI-Logik: Mustererkennung
│   ├── seed_data.py                  # Testdaten-Generator
│   ├── requirements.txt              # Python Dependencies
│   ├── kistengenerator.db            # SQLite Datenbank
│   └── tests/                        # Unit & Integration Tests
│
├── frontend/                         # React Frontend (Vite)
│   ├── src/
│   │   ├── App.jsx                   # Haupt-Komponente
│   │   ├── main.jsx                  # React Entry Point
│   │   └── assets/
│   ├── package.json
│   └── vite.config.js
│
└── PROJEKT-UEBERSICHT.md            # Diese Datei
```

---

## 🎯 KERNLOGIK: Wie der Kistengenerator funktioniert

### Masterplan-Konzept

Ein **Masterplan** ist ein Kistentyp mit definierten **Slots**.

**Kistentypen:**
- `OG12` = Obst & Gemüse für ~12 EUR (8 Slots)
- `OG15` = Obst & Gemüse für ~15 EUR (10 Slots)
- `OG18` = Obst & Gemüse für ~18 EUR (12 Slots)
- `OG21` = Familien-Kiste für ~21 EUR (15 Slots)
- Varianten: `OG-G` (Gemüse-lastig), `OG-O` (Obst-lastig)

### Slot-System

**Slot-Kategorien:**
- **Gemüse**: Zucchini, Lauch, Fenchel, Kartoffeln
- **Rohkost**: Gurke, Paprika, Möhren, Radieschen
- **Salat**: Kopfsalat, Feldsalat, Rucola
- **Obst**: Äpfel, Birnen, Bananen, Orangen
- **Kräuter**: Petersilie (optional)

**Beispiel OG12:**
```
✓ Gemüse 1, 2, 3
✓ Rohkost 1
✓ Salat 1
✓ Obst 1, 2, 3
= 8 Slots gesamt
```

### Artikel-Eigenschaften

- **SID** (Artikelnummer): z.B. `13`, `241`, `84`
- **Name**: z.B. "Zucchini", "Paprika gelb"
- **Kategorie**: Gemüse, Rohkost, Salat, Obst, Kräuter
- **Einheit**: Kilogramm oder Stück
- **Menge**: z.B. 0,65 kg, 1 Stück
- **Preis**: z.B. 2,90 EUR/kg

### Wochenquelle (Verfügbarkeit)

Jede Woche: Liste verfügbarer Artikel pro Slot

```
KW 26/2025:
  Gemüse 1  → Zucchini (SID 13)
  Gemüse 2  → Paprika gelb (SID 241)
  Gemüse 3  → Fenchel (SID 22)
  Rohkost 1 → Radieschen (SID 18r)
  Salat 1   → Kopfsalat (SID 51)
  Obst 1    → Äpfel (SID 60)
  Obst 2    → Birnen (SID 66)
  Obst 3    → Bananen (SID 861)
```

### Generator-Workflow

```
1. QUELLE LADEN
   → Welche Artikel sind verfügbar?

2. HISTORISCHEN MATCH SUCHEN (KI)
   → Beste vergangene Kiste finden
   → Match-Score: 0.0 - 1.0

3. SLOTS BEFÜLLEN
   → Artikel aus Match übernehmen
   → Fehlende ersetzen (gleiche Kategorie)

4. PREISE EINSETZEN
   → Aktuelle Preise laden
   → Gesamtpreis berechnen

5. FEINTUNING
   → Mengen anpassen für Zielpreis
   → Teuer → reduzieren
   → Günstig → erhöhen

6. FALLBACK
   → Bei Misserfolg: Nächster Match
   → Letzter Fallback: Statischer Plan
```

---

## 🔌 API-Endpunkte

### Status
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/` | App-Info |
| GET | `/api/status` | Statistiken |

### Artikel
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/artikel` | Alle Artikel |
| GET | `/api/artikel/{id}` | Artikel-Details |

### Masterplaene
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/masterplan` | Alle Masterplaene |
| GET | `/api/masterplan/{id}` | Details mit Slots |

### Preise
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/preise` | Alle Preise |
| POST | `/api/preise` | Preis anlegen |
| PUT | `/api/preise/{id}` | Preis ändern |

### Wochenquelle
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/quelle/{kw}/{jahr}` | Verfügbarkeit abrufen |
| POST | `/api/quelle/{kw}/{jahr}` | Verfügbarkeit setzen |

### Generator (Hauptfunktion)
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| POST | `/api/kiste/generieren` | **Kiste generieren** |
| GET | `/api/kiste/{id}` | Kiste abrufen |
| PUT | `/api/kiste/{id}/freigeben` | Freigeben → Historie |
| GET | `/api/kisten` | Alle Kisten |

### Historie & Muster
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/historie` | Historische Sortimente |
| POST | `/api/muster/lernen` | Muster extrahieren |
| POST | `/api/muster/match` | Match finden (Debug) |

---

## 🗄️ Datenbank-Modelle

### ArtikelStamm
Alle verfügbaren Artikel

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| sid | String | Paradieschen-ID (z.B. "13") |
| name | String | Artikelname |
| kategorie | String | Gemuese, Obst, Rohkost, Salat, Kraeuter |
| einheit | String | Kilogramm oder Stueck |
| status | String | aktiv, saisonende, inaktiv |

### Masterplan
Kistentypen mit Zielpreis

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| name | String | z.B. "OG12", "OG15" |
| beschreibung | String | Beschreibung |
| groesse | String | S, M, L |
| zielpreis_min | Float | Min. Preis (EUR) |
| zielpreis_max | Float | Max. Preis (EUR) |
| ist_aktiv | Boolean | Aktiv/Inaktiv |

### MasterplanSlot
Slots eines Masterplans

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| masterplan_id | Integer | FK → Masterplan |
| kategorie | String | Gemuese, Obst, etc. |
| slot_nummer | Integer | 1, 2, 3... |
| ist_pflicht | Boolean | Pflicht oder optional |

### Tauschmuster
Mengen-Ranges pro Artikel

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| artikel_id | Integer | FK → ArtikelStamm |
| groesse | String | S, M, L |
| sortimentsart | String | OG, RE, OOG |
| min_menge | Float | Min. Menge |
| max_menge | Float | Max. Menge |
| standard_menge | Float | Empfohlener Wert |
| einheit | String | Kilogramm/Stueck |

### PreisPflege
Wöchentliche Preise

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| artikel_id | Integer | FK → ArtikelStamm |
| preis_pro_einheit | Float | EUR pro kg/Stück |
| gueltig_ab | String | ISO-Datum |
| gueltig_bis | String | NULL = unbefristet |

### WochenQuelle
Verfügbarkeit pro KW

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| kalenderwoche | Integer | 1-53 |
| jahr | Integer | Jahr |
| slot_bezeichnung | String | z.B. "Gemuese 1" |
| artikel_id | Integer | FK → ArtikelStamm |

### HistorischeSortimente
Vergangene Kisten (Lernbasis)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| masterplan_id | Integer | FK → Masterplan |
| kalenderwoche | Integer | KW |
| jahr | Integer | Jahr |
| artikel_zuweisungen | JSON | Slot → Artikel |
| mengen_zuweisungen | JSON | Artikel → Menge |
| gesamtpreis | Float | Gesamtpreis |

### GelernteMasterplaene
Extrahierte Muster (KI)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| basis_masterplan_id | Integer | FK → Masterplan |
| quell_historie_id | Integer | FK → Historie |
| artikel_muster | JSON | Kategorie-Muster |
| mengen_muster | JSON | Mengen-Verteilung |
| haeufigkeit | Integer | Häufigkeit |
| durchschnittspreis | Float | Ø Preis |

### GenerierteKisten
Vom Generator erstellte Kisten

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | Integer | Primary Key |
| masterplan_id | Integer | FK → Masterplan |
| kalenderwoche | Integer | KW |
| jahr | Integer | Jahr |
| inhalt | JSON | Komplette Kiste |
| gesamtpreis | Float | Gesamtpreis |
| optimierung_versuche | Integer | Anzahl Iterationen |
| match_score | Float | 0.0 - 1.0 |
| match_quelle | String | z.B. "KW20/2024" |
| methode | String | Verwendete Methode |
| status | String | entwurf, freigegeben, verworfen |

---

## 🎨 Frontend-Komponenten

### Aktueller Stand
**Standard Vite + React Template** (noch nicht angepasst)

### Geplante Komponenten
- **Generator-View**: Kiste erstellen
- **Artikel-Verwaltung**: Artikel anzeigen/filtern
- **Wochenquelle-Editor**: Verfügbarkeit setzen
- **Kisten-Übersicht**: Entwürfe/Freigaben
- **Historie-Browser**: Vergangene Sortimente
- **Dashboard**: Statistiken

---

## 📊 Status & Implementierung

### ✅ Vollständig implementiert

- **Backend-Architektur**: FastAPI + SQLAlchemy
- **Datenmodelle**: 9 Tabellen mit Relationen
- **API-Endpunkte**: 20+ REST-Endpunkte
- **Generator-Kernlogik**: Kompletter Workflow
- **Muster-Lernen**: KI-Mustererkennung
- **Seed-Daten**: 50+ Artikel, 8 Masterplaene, 20 Historie-Einträge
- **Preis-Optimierung**: Automatisches Feintuning
- **Tests**: Unit & Integration Tests

### 🚧 Fehlt noch / In Arbeit

- **Frontend-UI**: Noch Standard-Template
- **Frontend-Backend-Integration**: Keine API-Calls
- **Benutzer-Auth**: Nicht implementiert
- **Erweiterte Validierung**: Mehr Business-Logic
- **Reporting**: PDF-Export, Druckansichten
- **Deployment**: Docker, CI/CD

### 🎯 Nächste Schritte

1. Frontend-Komponenten entwickeln
2. API-Integration (Axios/Fetch)
3. UI/UX Design
4. Batch-Generierung
5. Deployment-Setup

---

## 🛠️ Technologie-Stack

**Backend:**
- FastAPI 0.115.6
- SQLAlchemy 2.0.36
- Pydantic 2.10.3
- SQLite

**Frontend:**
- React 19.2.0
- Vite 7.3.1
- JavaScript (ES6+)

---

## 🚀 Schnellstart

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python main.py
```
→ API: `http://localhost:8000`  
→ Docs: `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
→ Frontend: `http://localhost:5173`
