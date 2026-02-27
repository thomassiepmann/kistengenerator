# 📦 KISTENGENERATOR - AKTUELLER STAND DER APP

**Datum:** 27.02.2026, 10:02 Uhr  
**Zusammenfassung für Claude**

---

## 🎯 WAS IST DER KISTENGENERATOR?

Eine vollständige Web-Anwendung zur **automatisierten Generierung von Bio-Obst & Gemüse-Kisten** für das Paradieschen.

### Kernfunktion
Der Generator erstellt optimierte Sortimente basierend auf:
- ✅ **Verfügbarkeit** (Wochenquelle - welche Artikel sind diese Woche da?)
- ✅ **Historischen Daten** (KI lernt aus vergangenen Kisten)
- ✅ **Preisen** (aktuelle Preise + Zielpreis-Rahmen)
- ✅ **Tauschmuster** (Min/Max-Mengen pro Artikel)

### Kistentypen
- **OG12** = Obst & Gemüse für ~12 EUR (8 Slots)
- **OG15** = Obst & Gemüse für ~15 EUR (10 Slots)
- **OG18** = Obst & Gemüse für ~18 EUR (12 Slots)
- **OG21** = Familien-Kiste für ~21 EUR (15 Slots)
- Varianten: OG-G (Gemüse-lastig), OG-O (Obst-lastig)

---

## 📁 PROJEKTSTRUKTUR

```
kistengenerator/
├── backend/                          # FastAPI Backend (Python)
│   ├── main.py                       # 🔴 API-Endpunkte (35+ Endpoints)
│   ├── models.py                     # 🔴 10 Datenbank-Modelle (SQLAlchemy)
│   ├── schemas.py                    # 🔴 Pydantic Request/Response Schemas
│   ├── database.py                   # SQLite Konfiguration
│   ├── generator.py                  # 🔴 KERNLOGIK: Kistengenerierung
│   ├── muster_lernen.py              # 🔴 KI-Logik: Mustererkennung
│   ├── import_handler.py             # Excel-Import/Export
│   ├── pcgaertner_integration.py     # PC-Gärtner Integration (optional)
│   ├── seed_data.py                  # Testdaten-Generator
│   ├── requirements.txt              # Python Dependencies
│   └── kistengenerator.db            # SQLite Datenbank (wird erstellt)
│
├── frontend/                         # React Frontend (Vite)
│   ├── src/
│   │   ├── App.jsx                   # 🔴 Haupt-App mit Routing
│   │   ├── main.jsx                  # React Entry Point
│   │   ├── components/
│   │   │   └── layout/
│   │   │       ├── Layout.jsx        # 🔴 Haupt-Layout mit Sidebar
│   │   │       ├── Sidebar.jsx       # Navigation
│   │   │       └── Header.jsx        # Top-Bar
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx         # 🔴 Übersicht & Statistiken
│   │   │   ├── Generator.jsx         # 🔴 Kisten generieren
│   │   │   ├── ArtikelVerwaltung.jsx # 🔴 Artikel CRUD
│   │   │   ├── Wochenplanung.jsx     # 🔴 Verfügbarkeit setzen
│   │   │   ├── Preispflege.jsx       # 🔴 Preise verwalten
│   │   │   ├── Masterplaene.jsx      # 🔴 Kistentypen anzeigen
│   │   │   ├── Historie.jsx          # 🔴 Vergangene Sortimente
│   │   │   └── Einstellungen.jsx     # App-Info
│   │   ├── services/
│   │   │   └── api.js                # 🔴 API-Client (Axios)
│   │   └── styles/
│   │       ├── colors.css            # Farbschema
│   │       └── global.css            # Globale Styles
│   ├── package.json
│   └── vite.config.js
│
└── Dokumentation/                    # 15+ Markdown-Dateien
    ├── PROJEKT-UEBERSICHT.md         # 🔴 Vollständige Übersicht
    ├── APP-REVIEW.md                 # 🔴 Detaillierte Code-Analyse
    ├── FÜR-CLAUDE.md                 # Deployment-Info
    ├── GENERATOR-FUNKTIONSWEISE.md   # Wie der Generator arbeitet
    ├── KISTENPREISE-IMPLEMENTATION.md # Festpreis-Feature
    ├── DEPLOYMENT-HETZNER.md         # Deployment-Anleitung
    └── ... (weitere Docs)
```

---

## 🗄️ DATENBANK-MODELLE (10 Tabellen)

### 1. **ArtikelStamm** - Alle verfügbaren Artikel
- `id`, `sid` (Paradieschen-ID), `name`, `kategorie`, `einheit`, `status`
- Beispiel: SID="13", Name="Zucchini", Kategorie="Gemuese"

### 2. **Masterplan** - Kistentypen
- `id`, `name` (z.B. "OG12"), `groesse` (S/M/L), `zielpreis_min`, `zielpreis_max`
- Definiert welche Kisten es gibt

### 3. **MasterplanSlot** - Slots eines Masterplans
- `masterplan_id`, `kategorie`, `slot_nummer`, `ist_pflicht`
- Beispiel: OG12 hat 3x Gemüse, 1x Rohkost, 1x Salat, 3x Obst

### 4. **Tauschmuster** - Mengen-Ranges
- `artikel_id`, `groesse`, `min_menge`, `max_menge`, `standard_menge`
- Beispiel: Zucchini in M-Kiste: 0.5-0.8 kg, Standard 0.65 kg

### 5. **PreisPflege** - Wöchentliche Preise
- `artikel_id`, `preis_pro_einheit`, `gueltig_ab`, `gueltig_bis`
- Beispiel: Zucchini = 2.90 EUR/kg ab 24.02.2026

### 6. **KistenFestpreis** - Festpreise für Kisten
- `masterplan_id`, `groesse`, `festpreis`, `gueltig_ab`, `gueltig_bis`
- Beispiel: OG12-M = exakt 12.00 EUR (statt Range 11-13 EUR)

### 7. **WochenQuelle** - Verfügbarkeit pro KW
- `kalenderwoche`, `jahr`, `slot_bezeichnung`, `artikel_id`
- Beispiel: KW26/2025, Gemüse 1 → Zucchini (SID 13)

### 8. **HistorischeSortimente** - Vergangene Kisten
- `masterplan_id`, `kw`, `jahr`, `artikel_zuweisungen` (JSON), `mengen_zuweisungen` (JSON)
- Lernbasis für KI

### 9. **GelernteMasterplaene** - Extrahierte Muster
- `basis_masterplan_id`, `artikel_muster` (JSON), `mengen_muster` (JSON), `haeufigkeit`
- KI-generierte Muster aus Historie

### 10. **GenerierteKisten** - Vom Generator erstellte Kisten
- `masterplan_id`, `kw`, `jahr`, `inhalt` (JSON), `gesamtpreis`, `match_score`, `status`
- Status: entwurf, freigegeben, verworfen

---

## 🔌 BACKEND API (35+ Endpunkte)

### Status & Info
- `GET /` - App-Info
- `GET /api/status` - Statistiken (Anzahl Artikel, Preise, etc.)

### Artikel-Verwaltung
- `GET /api/artikel` - Alle Artikel (optional: ?kategorie=Gemuese)
- `GET /api/artikel/{id}` - Artikel-Details
- `POST /api/artikel` - Artikel anlegen
- `PUT /api/artikel/{id}` - Artikel ändern
- `DELETE /api/artikel/{id}` - Artikel löschen

### Masterplaene
- `GET /api/masterplan` - Alle Masterplaene
- `GET /api/masterplan/{id}` - Details mit Slots

### Preis-Verwaltung
- `GET /api/preise` - Alle Preise
- `POST /api/preise` - Preis anlegen
- `PUT /api/preise/{id}` - Preis ändern
- `DELETE /api/preise/{id}` - Preis löschen

### Kistenpreis-Verwaltung (NEU!)
- `GET /api/kistenpreise` - Alle Festpreise
- `POST /api/kistenpreise` - Festpreis anlegen
- `PUT /api/kistenpreise/{id}` - Festpreis ändern
- `DELETE /api/kistenpreise/{id}` - Festpreis löschen
- `GET /api/kistenpreise/aktiv` - Aktiven Festpreis abrufen

### Wochenquelle (Verfügbarkeit)
- `GET /api/quelle/{kw}/{jahr}` - Verfügbarkeit abrufen
- `POST /api/quelle/{kw}/{jahr}` - Verfügbarkeit setzen
- `POST /api/quelle/{kw}/{jahr}/kopieren` - Von anderer KW kopieren

### 🔴 GENERATOR (HAUPTFUNKTION)
- `POST /api/kiste/generieren` - **Kiste generieren**
- `GET /api/kiste/{id}` - Kiste abrufen
- `PUT /api/kiste/{id}` - Kiste manuell bearbeiten
- `PUT /api/kiste/{id}/freigeben` - Freigeben → Historie
- `GET /api/kisten` - Alle Kisten (optional: ?status=entwurf)
- `GET /api/kiste/{id}/export/csv` - Als CSV exportieren
- `POST /api/kisten/batch` - Alle Kisten für KW generieren

### Historie & Muster
- `GET /api/historie` - Historische Sortimente
- `POST /api/muster/lernen` - Muster aus Historie extrahieren
- `POST /api/muster/match` - Match finden (Debug)

### Import/Export
- `POST /api/import/artikel` - Excel-Import
- `POST /api/import/historie` - Excel-Import
- `POST /api/import/preise` - Excel-Import
- `POST /api/import/wochenquelle` - Excel-Import
- `POST /api/import/masterplan` - Excel-Import
- `GET /api/vorlagen/{typ}` - Excel-Vorlage downloaden

### PC-Gärtner Integration (optional)
- `GET /api/integration/status` - Status prüfen
- `POST /api/integration/test` - Verbindung testen
- `POST /api/integration/sync/artikel` - Artikel synchronisieren
- `POST /api/integration/sync/preise` - Preise synchronisieren
- `POST /api/integration/export/{kiste_id}` - Sortiment exportieren

---

## 🧠 GENERATOR-WORKFLOW (KERNLOGIK)

```
1. QUELLE LADEN
   → Welche Artikel sind verfügbar? (WochenQuelle)
   → Beispiel: KW26/2025 → Zucchini, Paprika, Fenchel, ...

2. HISTORISCHEN MATCH SUCHEN (KI)
   → Finde beste vergangene Kiste mit ähnlicher Verfügbarkeit
   → Match-Score: 0.0 - 1.0 (1.0 = perfekt)
   → Beispiel: KW20/2024 hatte ähnliche Artikel → Score 0.85

3. SLOTS BEFÜLLEN
   → Übernehme Artikel aus Match
   → Fehlende Slots: Ersetze mit ähnlichem Artikel (gleiche Kategorie)
   → Beispiel: Match hatte Zucchini → übernehmen
              Match hatte Brokkoli (nicht verfügbar) → ersetze mit Fenchel

4. PREISE EINSETZEN
   → Lade aktuelle Preise (PreisPflege)
   → Berechne Gesamtpreis
   → Beispiel: Zucchini 0.65kg × 2.90€/kg = 1.89€

5. FEINTUNING (Preis-Optimierung)
   → Prüfe ob Gesamtpreis im Zielpreis-Rahmen
   → Zu teuer? → Mengen reduzieren
   → Zu günstig? → Mengen erhöhen
   → Beispiel: Zielpreis 12.00€, aktuell 13.50€ → reduziere Mengen

6. FALLBACK
   → Bei Misserfolg: Nächster Match
   → Letzter Fallback: Statischer Plan (vordefiniert)

7. SPEICHERN
   → Kiste als "entwurf" speichern
   → Benutzer kann manuell anpassen
   → Freigabe → wird zu HistorischeSortimente
```

---

## 🎨 FRONTEND-KOMPONENTEN

### Layout
- **Layout.jsx** - Haupt-Layout mit Sidebar + Content-Bereich
- **Sidebar.jsx** - Navigation (Dashboard, Generator, Artikel, etc.)
- **Header.jsx** - Top-Bar mit Titel

### Seiten (Pages)

#### 1. **Dashboard.jsx** ⚠️ PROBLEM!
- Zeigt Statistiken (Anzahl Artikel, Preise, Kisten)
- PC-Gärtner Integration Status
- **🚨 KRITISCH:** Hardcoded `localhost:8001` URLs!
  - Zeile 35, 47, 58: `fetch('http://localhost:8001/...')`
  - **Funktioniert NICHT auf Produktion!**
  - **Lösung:** Nutze `api.get()` aus `services/api.js`

#### 2. **Generator.jsx**
- Formular: Kistentyp, Größe, KW, Jahr auswählen
- Button "Kiste generieren"
- Zeigt Ergebnis: Artikel, Mengen, Preise, Gesamtpreis
- Kann manuell angepasst werden
- Freigabe-Button

#### 3. **ArtikelVerwaltung.jsx**
- Tabelle: Alle Artikel
- CRUD: Anlegen, Bearbeiten, Löschen
- Filter nach Kategorie
- **Fehlt:** Suchfunktion, Sortierung

#### 4. **Wochenplanung.jsx**
- Wochenquelle setzen (KW + Jahr)
- Für jeden Slot: Artikel aus Dropdown wählen
- Speichern-Button
- **Fehlt:** "Kopieren von letzter Woche" Button (Backend existiert!)

#### 5. **Preispflege.jsx**
- Tabelle: Alle Preise
- CRUD: Anlegen, Bearbeiten, Löschen
- Zeigt Artikel-Name, Preis, Gültig ab/bis
- **NEU:** Kistenpreis-Verwaltung (Festpreise)
- **Fehlt:** Suchfunktion, Sortierung

#### 6. **Masterplaene.jsx**
- Zeigt alle Masterplaene
- Details: Slots, Zielpreis-Range
- Nur Anzeige (kein CRUD)

#### 7. **Historie.jsx**
- Zeigt historische Sortimente
- Filter nach KW, Jahr, Masterplan
- Details: Artikel, Mengen, Preis
- **Fehlt:** Export-Funktion

#### 8. **Einstellungen.jsx**
- Nur "Über die App" Info
- **Fehlt:** Echte Einstellungen

### Services
- **api.js** - Axios-Client für API-Calls
  - Base URL: `/api` (relativ, funktioniert auf Produktion)
  - Alle API-Funktionen als Wrapper

---

## ✅ WAS FUNKTIONIERT (VOLLSTÄNDIG IMPLEMENTIERT)

### Backend
- ✅ **Datenbank-Modelle** - 10 Tabellen mit Relationen
- ✅ **API-Endpunkte** - 35+ REST-Endpunkte
- ✅ **Generator-Kernlogik** - Kompletter Workflow
- ✅ **KI-Mustererkennung** - Lernt aus Historie
- ✅ **Preis-Optimierung** - Automatisches Feintuning
- ✅ **Import/Export** - Excel-Import für alle Daten
- ✅ **Seed-Daten** - 50+ Artikel, 8 Masterplaene, 20 Historie-Einträge
- ✅ **Kistenpreis-Feature** - Festpreise für Kisten (NEU!)

### Frontend
- ✅ **Layout & Navigation** - Sidebar, Header, Routing
- ✅ **Artikel-Verwaltung** - CRUD funktioniert
- ✅ **Preis-Verwaltung** - CRUD funktioniert
- ✅ **Wochenplanung** - Verfügbarkeit setzen funktioniert
- ✅ **Generator** - Kisten generieren funktioniert
- ✅ **Historie** - Anzeige funktioniert
- ✅ **Dashboard** - Statistiken funktionieren (aber Hardcoded URLs!)

---

## 🚨 KRITISCHE PROBLEME (SOFORT BEHEBEN!)

### 1. **Dashboard: Hardcoded localhost URLs** ⚠️⚠️⚠️
**Datei:** `frontend/src/pages/Dashboard.jsx`  
**Zeilen:** 35, 47, 58  
**Problem:**
```javascript
const response = await fetch('http://localhost:8001/api/integration/status');
```
**Auswirkung:**
- Funktioniert NICHT auf Produktion (89.167.83.224)
- PC-Gärtner Integration komplett kaputt auf Live-Server

**Lösung:**
```javascript
import { api } from '../services/api';
const response = await api.get('/api/integration/status');
```

### 2. **Generator nutzt NICHT die neuen Kistenpreise!** ⚠️⚠️
**Datei:** `backend/generator.py`  
**Problem:**
- Kistenpreis-Feature wurde implementiert (KistenFestpreis-Tabelle)
- Generator prüft aber NICHT ob Festpreis existiert
- Nutzt immer nur Masterplan-Zielpreis-Range

**Fehlende Integration:**
```python
# FEHLT in generator.py:
from models import KistenFestpreis

def get_zielpreis(db, masterplan_id, groesse, kw, jahr):
    # Prüfe ob Festpreis existiert
    festpreis = db.query(KistenFestpreis).filter(...).first()
    if festpreis:
        return festpreis.festpreis  # EXAKTER Preis
    else:
        return masterplan.zielpreis_min, masterplan.zielpreis_max  # Range
```

**Auswirkung:**
- Neue Kistenpreis-Funktion ist NUTZLOS
- Generator ignoriert Festpreise komplett

### 3. **Keine Fehlerbehandlung bei leeren Daten** ⚠️
**Problem:** Was passiert wenn:
- 0 Artikel vorhanden?
- 0 Preise vorhanden?
- 0 Wochenquelle vorhanden?

**Aktuell:** App stürzt ab oder zeigt leere Seiten

**Lösung:** Empty-State-Handling überall

### 4. **Keine Validierung beim Import** ⚠️
**Datei:** `backend/import_handler.py`  
**Problem:**
- Fehlerhafte Excel-Dateien werden nicht abgefangen
- Keine Duplikat-Prüfung
- Keine Datenvalidierung

---

## ⚠️ WICHTIGE VERBESSERUNGEN (SOLLTE MAN MACHEN)

1. **Fehlende Suchfunktion** - Bei 100+ Artikeln unmöglich zu finden
2. **Keine Sortierung in Tabellen** - Keine Sortierung nach Name, Preis, Datum
3. **Keine Bestätigung bei Löschen** - Nur `confirm()` - unprofessionell
4. **Keine Bulk-Aktionen** - Mehrere Artikel auf einmal löschen
5. **Keine Export-Funktionen** - PDF, Excel, CSV fehlen
6. **Dashboard zeigt keine echten Daten** - Nur Anzahlen
7. **Keine Hilfe-Texte / Tooltips** - Benutzer weiß nicht was "Masterplan" ist
8. **Keine Undo-Funktion** - Artikel gelöscht → Weg!
9. **Keine Benachrichtigungen** - Nur `alert()` - unprofessionell
10. **Wochenplanung kopieren fehlt im Frontend** - Backend existiert bereits!

---

## 💾 DEPLOYMENT-STATUS

### Aktuell deployed auf:
**Server:** 89.167.83.224 (Hetzner)
- **Port 80:** SEO-Tool (NICHT ANFASSEN!)
- **Port 8080:** Kistengenerator Frontend
- **Port 8001:** Kistengenerator Backend (intern)

### Deployment-Methode:
- Backend: systemd Service (`kistengenerator.service`)
- Frontend: nginx (statische Dateien aus `dist/`)
- Datenbank: SQLite (`/var/www/kistengenerator/backend/kistengenerator.db`)

### Deployment-Befehle:
```bash
# Backend Status
systemctl status kistengenerator

# Backend Logs
journalctl -u kistengenerator -f

# Backend neu starten
systemctl restart kistengenerator

# Frontend neu bauen
cd /var/www/kistengenerator/frontend
npm run build
systemctl reload nginx
```

---

## 📊 TECHNOLOGIE-STACK

### Backend
- **Python 3.12**
- **FastAPI 0.115.6** - REST API Framework
- **SQLAlchemy 2.0.36** - ORM
- **Pydantic 2.10.3** - Validierung
- **SQLite** - Datenbank
- **uvicorn** - ASGI Server

### Frontend
- **React 19.2.0** - UI Framework
- **Vite 7.3.1** - Build Tool
- **React Router 7.1.1** - Routing
- **Axios 1.7.9** - HTTP Client
- **JavaScript (ES6+)** - Keine TypeScript

### Server
- **Ubuntu 24.04**
- **nginx** - Reverse Proxy
- **systemd** - Service Management
- **ufw** - Firewall

---

## 📝 WICHTIGE DATEIEN (WO IST WAS?)

### Backend-Kernlogik
- `backend/main.py` - **API-Endpunkte** (35+ Endpoints)
- `backend/generator.py` - **Generator-Kernlogik** (Kisten erstellen)
- `backend/muster_lernen.py` - **KI-Mustererkennung** (Match-Algorithmus)
- `backend/models.py` - **Datenbank-Modelle** (10 Tabellen)
- `backend/schemas.py` - **API-Schemas** (Request/Response)

### Frontend-Kernlogik
- `frontend/src/App.jsx` - **Haupt-App** (Routing)
- `frontend/src/services/api.js` - **API-Client** (alle API-Calls)
- `frontend/src/pages/Generator.jsx` - **Generator-UI**
- `frontend/src/pages/Dashboard.jsx` - **Dashboard** (⚠️ Hardcoded URLs!)

### Dokumentation
- `PROJEKT-UEBERSICHT.md` - **Vollständige Übersicht**
- `APP-REVIEW.md` - **Detaillierte Code-Analyse**
- `GENERATOR-FUNKTIONSWEISE.md` - **Wie der Generator arbeitet**
- `KISTENPREISE-IMPLEMENTATION.md` - **Festpreis-Feature**
- `DEPLOYMENT-HETZNER.md` - **Deployment-Anleitung**

---

## 🎯 NÄCHSTE SCHRITTE (PRIORISIERT)

### 🔴 KRITISCH (SOFORT)
1. **Dashboard URLs fixen** (10 Min)
2. **Generator Kistenpreis-Integration** (30 Min)
3. **Empty States** (1 Std)
4. **Import-Validierung** (2 Std)

### 🟡 WICHTIG (DIESE WOCHE)
5. **Suchfunktion** (1 Std)
6. **Sortierung** (2 Std)
7. **Toast-Notifications** (1 Std)
8. **Wochenplanung kopieren Button** (30 Min)

### 🟢 NICE-TO-HAVE (NÄCHSTER MONAT)
9. **Tooltips / Hilfe-Texte**
10. **Undo-Funktion**
11. **Bulk-Aktionen**
12. **Preis-Historie Grafik**

---

## 📞 SUPPORT & KONTAKT

**Entwickler:** Claude (AI Assistant)  
**Auftraggeber:** Paradieschen (Bio-Gemüse-Kisten)  
**Server:** 89.167.83.224 (Hetzner)  
**Zugang:** root@89.167.83.224 (Passwort: tq7qWdqusRPb)

---

## 🎓 FAZIT

**Die App ist funktional, aber nicht produktionsreif.**

**Stärken:**
- ✅ Gute Grundarchitektur
- ✅ Kernfunktionen vorhanden
- ✅ Sauberer Code
- ✅ Vollständige Dokumentation

**Schwächen:**
- ❌ Kritische Bugs (Hardcoded URLs, Kistenpreis-Integration fehlt)
- ❌ Fehlende Benutzerfreundlichkeit
- ❌ Keine Fehlerbehandlung
- ❌ Wichtige Features fehlen

**Gesamtnote: 3 (Befriedigend)**

**Empfehlung:**
1. Kritische Fixes (Woche 1)
2. Benutzerfreundlichkeit (Woche 2)
3. Features (Woche 3)

**Dann:** Produktionsreif! ✅

---

**Stand:** 27.02.2026, 10:02 Uhr  
**Letzte Änderung:** Kistenpreis-Feature implementiert (26.02.2026)  
**Nächster Review:** Nach Umsetzung der kritischen Fixes
