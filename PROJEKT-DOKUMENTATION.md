# 📋 Paradieschen Kistengenerator - Vollständige Projekt-Dokumentation

## 🎯 Projekt-Übersicht

**Name:** Paradieschen Kistengenerator  
**Zweck:** Automatische Generierung von Bio-Obst & Gemüse-Kisten mit historischem Matching  
**Technologie:** FastAPI (Backend) + React (Frontend)  
**Status:** ✅ Produktionsbereit

---

## 📁 Projekt-Struktur

```
kistengenerator/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Hauptdatei mit allen Endpoints
│   ├── database.py             # SQLite Datenbankverbindung
│   ├── models.py               # SQLAlchemy Datenmodelle
│   ├── schemas.py              # Pydantic Schemas für API
│   ├── generator.py            # KERNLOGIK: Kistengenerierung
│   ├── muster_lernen.py        # Historisches Matching
│   ├── import_handler.py       # Excel Import/Export
│   ├── seed_data.py            # Testdaten (51 Artikel, 8 Masterplaene, 20 Historie)
│   ├── requirements.txt        # Python Dependencies
│   ├── kistengenerator.db      # SQLite Datenbank (wird generiert)
│   └── tests/
│       ├── test_generator.py
│       └── test_integration.py
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx            # React Entry Point
│   │   ├── App.jsx             # Routing
│   │   ├── services/
│   │   │   └── api.js          # Alle Backend-Calls
│   │   ├── components/
│   │   │   └── layout/
│   │   │       ├── Layout.jsx
│   │   │       ├── Header.jsx
│   │   │       └── Sidebar.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx           # Übersicht
│   │   │   ├── Generator.jsx           # ⭐ HAUPTSEITE
│   │   │   ├── ArtikelVerwaltung.jsx   # CRUD Artikel
│   │   │   ├── Preispflege.jsx         # Preise verwalten
│   │   │   ├── Wochenplanung.jsx       # Wochenquelle
│   │   │   ├── Masterplaene.jsx        # Masterplaene
│   │   │   ├── Historie.jsx            # Historische Sortimente
│   │   │   └── Einstellungen.jsx       # System-Status
│   │   └── styles/
│   │       ├── global.css
│   │       └── colors.css
│   ├── package.json
│   └── vite.config.js
│
├── deploy.sh                   # Deployment-Script für Hetzner
├── DEPLOYMENT.md               # Deployment-Anleitung
├── PROJEKT-UEBERSICHT.md       # Projekt-Übersicht
└── PROJEKT-DOKUMENTATION.md    # Diese Datei

```

---

## 🗄️ Datenbank-Schema

### 1. ArtikelStamm
```sql
- id (PK)
- sid (Paradieschen-ID, z.B. "13")
- name (z.B. "Zucchini")
- kategorie (Gemuese, Obst, Rohkost, Salat, Kraeuter)
- einheit (Kilogramm oder Stueck)
- status (aktiv, saisonende, inaktiv)
```

### 2. Masterplan
```sql
- id (PK)
- name (z.B. "OG12")
- beschreibung
- groesse (S, M, L)
- zielpreis_min (z.B. 10.80€)  # -10% vom Zielpreis
- zielpreis_max (z.B. 13.20€)  # +10% vom Zielpreis
- ist_aktiv
```

**Aktuelle Masterplaene:**
- OG12 (S): 12.00€ → 10.80€ - 13.20€
- OG12-G (S): 12.00€ → 10.80€ - 13.20€ (nur Gemüse)
- OG12-O (S): 12.00€ → 10.80€ - 13.20€ (nur Obst)
- OG15 (M): 15.00€ → 13.50€ - 16.50€
- OG18 (M): 18.00€ → 16.20€ - 19.80€
- OG18-G (M): 18.00€ → 16.20€ - 19.80€ (nur Gemüse)
- OG21 (L): 21.00€ → 18.90€ - 23.10€
- OG21-G (L): 21.00€ → 18.90€ - 23.10€ (nur Gemüse)

### 3. MasterplanSlot
```sql
- id (PK)
- masterplan_id (FK)
- kategorie (Gemuese, Obst, etc.)
- slot_nummer (1, 2, 3...)
- ist_pflicht
```

### 4. Tauschmuster
```sql
- id (PK)
- artikel_id (FK)
- groesse (S, M, L)
- sortimentsart (OG, RE, OOG)
- min_menge (z.B. 0.55 kg)
- max_menge (z.B. 0.75 kg)
- standard_menge (z.B. 0.65 kg)
- einheit
```

### 5. WochenQuelle
```sql
- id (PK)
- kalenderwoche
- jahr
- slot_bezeichnung (z.B. "Gemuese 1")
- artikel_id (FK)
```

### 6. PreisPflege
```sql
- id (PK)
- artikel_id (FK)
- preis_pro_einheit (EUR)
- gueltig_ab (Datum)
- gueltig_bis (Datum, NULL = unbefristet)
```

### 7. HistorischeSortimente
```sql
- id (PK)
- masterplan_id (FK)
- kalenderwoche
- jahr
- artikel_zuweisungen (JSON)
- mengen_zuweisungen (JSON)
- gesamtpreis
```

### 8. GenerierteKisten
```sql
- id (PK)
- masterplan_id (FK)
- kalenderwoche
- jahr
- inhalt (JSON)
- gesamtpreis
- optimierung_versuche
- match_score (0.0 - 1.0)
- match_quelle (z.B. "KW20/2024")
- methode
- status (entwurf, freigegeben, verworfen)
```

### 9. GelernteMasterplaene
```sql
- id (PK)
- basis_masterplan_id (FK)
- quell_historie_id (FK)
- artikel_muster (JSON)
- mengen_muster (JSON)
- haeufigkeit
- durchschnittspreis
```

---

## 🔧 Backend-API Endpoints

### Status
- `GET /` - Startseite
- `GET /api/status` - System-Status

### Artikel
- `GET /api/artikel` - Alle Artikel (optional: ?kategorie=Gemuese)
- `GET /api/artikel/{id}` - Artikel-Details
- `POST /api/artikel` - Neuer Artikel
- `PUT /api/artikel/{id}` - Artikel bearbeiten
- `DELETE /api/artikel/{id}` - Artikel löschen

### Masterplaene
- `GET /api/masterplan` - Alle Masterplaene
- `GET /api/masterplan/{id}` - Masterplan-Details

### Preise
- `GET /api/preise` - Alle Preise
- `POST /api/preise` - Neuer Preis
- `PUT /api/preise/{id}` - Preis bearbeiten
- `DELETE /api/preise/{id}` - Preis löschen

### Wochenquelle
- `GET /api/quelle/{kw}/{jahr}` - Wochenquelle laden
- `POST /api/quelle/{kw}/{jahr}` - Wochenquelle setzen
- `POST /api/quelle/{kw}/{jahr}/kopieren-von/{quell_kw}/{quell_jahr}` - Kopieren

### Generator (⭐ HAUPTFUNKTIONEN)
- `POST /api/kiste/generieren` - Einzelne Kiste generieren
- `POST /api/kiste/generieren-alle?kw={kw}&jahr={jahr}` - **ALLE Kisten generieren**
- `GET /api/kiste/{id}` - Kiste laden
- `PUT /api/kiste/{id}` - Kiste bearbeiten
- `PUT /api/kiste/{id}/freigeben` - Kiste freigeben
- `GET /api/kisten` - Alle Kisten (optional: ?status=entwurf)
- `GET /api/kiste/{id}/export/csv` - **CSV-Export**

### Historie
- `GET /api/historie` - Historische Sortimente (optional: ?masterplan_name=OG12)

### Muster
- `POST /api/muster/lernen` - Muster aus Historie extrahieren
- `POST /api/muster/match` - Besten Match finden

### Import/Export
- `POST /api/import/artikel` - Artikel aus Excel
- `POST /api/import/historie` - Historie aus Excel
- `POST /api/import/preise` - Preise aus Excel
- `POST /api/import/wochenquelle` - Wochenquelle aus Excel
- `POST /api/import/masterplan` - Masterplan aus Excel
- `GET /api/import/vorlage/{typ}` - Excel-Vorlage herunterladen

---

## 🎯 Generator-Algorithmus (8 Schritte)

### Schritt 1: Masterplan laden
- Lädt den gewählten Masterplan (z.B. OG12)
- Definiert alle Slots (Gemüse 1, Gemüse 2, Obst 1, etc.)

### Schritt 2: Wochenquelle laden
- Lädt verfügbare Artikel der aktuellen Woche
- Nur diese Artikel dürfen verwendet werden

### Schritt 3: Historisches Matching ⭐
- Lädt ALLE historischen Sortimente
- Zählt Übereinstimmungen mit aktueller Wochenquelle
- Sortiert nach Matching-Score (höchste zuerst)
- Nimmt besten Treffer als Vorlage

### Schritt 4: Sortiment aus Vorlage generieren
- Übernimmt STRUKTUR des besten historischen Treffers
- Ersetzt Artikel durch aktuell verfügbare (aus Wochenquelle)
- Wählt passende Artikel der gleichen Kategorie

### Schritt 5: Mengen aus Tauschmuster
- Lädt Tauschmuster für jeden Artikel
- Verwendet min_menge und max_menge
- Startet mit Mittelwert: (min + max) / 2

### Schritt 6: Preisoptimierung (iterativ)
- Berechnet Gesamtpreis: Σ(Menge × Preis)
- Vergleicht mit Zielpreis des Masterplans
- Zu teuer → Reduziert Mengen (nicht unter min)
- Zu günstig → Erhöht Mengen (nicht über max)
- Max 10 Iterationen

### Schritt 7: Qualitätsprüfung
- Prüft: Alle Slots besetzt?
- Prüft: Preis im Rahmen?
- Prüft: Mengen sinnvoll?
- Wenn NICHT OK → Nächstbester historischer Treffer
- Letzter Fallback: Statischer Masterplan

### Schritt 8: Ergebnis zurückgeben
- Generiertes Sortiment mit allen Details
- Gesamtpreis, Matching-Score
- Hinweise zu Anpassungen

---

## 🎨 Frontend-Seiten

### 1. Dashboard (/)
- Übersicht mit Statistiken
- Schnellzugriff auf alle Funktionen

### 2. Generator (/generator) ⭐ HAUPTSEITE
**Features:**
- Dropdown: Masterplan auswählen
- Dropdown: Kalenderwoche + Jahr
- Button: "Sortiment generieren" (einzeln)
- Button: "ALLE Sortimente generieren" (Batch)
- Matching-Score in Prozent
- Detaillierte Matching-Info
- Sortiment-Tabelle mit allen Details
- Inline-Editing der Mengen
- CSV-Export Button
- Batch-Ergebnisse als Karten-Grid
- Gesamtpreis + Zielpreis-Rahmen

### 3. Artikel-Verwaltung (/artikel)
- CRUD-Operationen
- Suche & Filter
- Excel-Import/Export

### 4. Preispflege (/preise)
- Inline-Editing
- Gültigkeitszeiträume
- Excel-Import/Export

### 5. Wochenplanung (/wochenquelle)
- Slot-Grid
- Kopieren-Funktion
- Excel-Import/Export

### 6. Masterplaene (/masterplaene)
- Übersicht
- Details anzeigen
- Excel-Import

### 7. Historie (/historie)
- Historische Sortimente
- Filter nach Masterplan
- Excel-Import/Export

### 8. Einstellungen (/einstellungen)
- System-Status
- Vorlagen herunterladen
- Muster lernen

---

## 🎨 Design-System (Paradieschen)

### Farben
```css
--paradieschen-dunkelgruen: #1a472a;
--paradieschen-gruen: #2d8a4e;
--paradieschen-hellgruen: #8cc63f;
--paradieschen-braun: #5a3e28;
--paradieschen-creme: #faf8f5;
```

### Verwendung
- **Sidebar:** Dunkelgrün (#1a472a) mit weißer Schrift
- **Header:** Weiß mit braunen Überschriften
- **Buttons:** Grün (#2d8a4e) oder Hellgrün (#8cc63f)
- **Hintergrund:** Creme (#faf8f5)
- **Überschriften:** Braun (#5a3e28)
- **Akzente:** Grün (#2d8a4e)

---

## 📊 Testdaten

### Artikel (51 Stück)
**Gemüse:** Zucchini, Paprika, Fenchel, Gurke, Mangold, Rote Bete, Lauch, Möhren, Pastinaken, Grünkohl, Blumenkohl, Rosenkohl, Sellerie, Radieschen, Rettich, Wirsing, Rotkohl, Weißkohl, Kohlrabi, Brokkoli, Porree, Kartoffeln

**Rohkost:** Kresse, Paprika grün, Sprossen Alfalfa, Sprossen Mungobohne, Radieschen

**Salat:** Kopfsalat, Eisbergsalat, Feldsalat, Rucola, Batavia, Eichblattsalat, Romana

**Kräuter:** Petersilie glatt, Petersilie kraus, Petersilienwurzel

**Obst:** Äpfel, Birnen, Bananen, Orangen, Trauben, Kiwi, Mandarinen, Zitronen, Mango, Ananas

### Historische Sortimente (20 Stück)
- 12x OG12 (verschiedene Wochen 2023-2024)
- 2x OG15
- 2x OG18
- 2x OG21
- 2x OG12 (Sommer 2023)

---

## 🚀 Deployment

### Lokale Entwicklung

**Backend starten:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python main.py
# Läuft auf http://localhost:8000
```

**Frontend starten:**
```bash
cd frontend
npm install
npm run dev
# Läuft auf http://localhost:5173
```

### Produktion (Hetzner Server)

**Automatisches Deployment:**
```bash
cd /home/user/kistengenerator
./deploy.sh
```

**Server-Details:**
- IP: 89.167.83.224
- Benutzer: root
- App-URL: http://89.167.83.224
- Backend: Port 8001 (intern)
- Frontend: Port 80 (nginx)

**Siehe:** `DEPLOYMENT.md` für Details

---

## 📝 Wichtige Dateien

### Backend
- `generator.py` - Kernlogik (450+ Zeilen)
- `muster_lernen.py` - Historisches Matching
- `main.py` - API Endpoints (500+ Zeilen)
- `seed_data.py` - Testdaten mit ±10% Toleranz

### Frontend
- `Generator.jsx` - Hauptseite (450+ Zeilen)
- `Generator.css` - Styling (500+ Zeilen)
- `api.js` - Alle Backend-Calls

### Deployment
- `deploy.sh` - Automatisches Deployment
- `DEPLOYMENT.md` - Anleitung

---

## ✅ Implementierte Features

### Generator-Verbesserungen (alle 6)
1. ✅ Zielpreise mit ±10% Toleranz
2. ✅ CSV-Export Backend
3. ✅ Batch-Generierung Backend
4. ⏸️ Verfügbarkeits-Check (übersprungen)
5. ✅ Generator-Seite komplett neu
6. ✅ Testing & Datenbank

### Weitere Features
- ✅ Historisches Matching
- ✅ Preisoptimierung
- ✅ Inline-Editing
- ✅ Excel-Import/Export
- ✅ Paradieschen-Design
- ✅ 8 Seiten komplett
- ✅ Responsive Design

---

## 🔮 Zukünftige Erweiterungen

1. **Verfügbarkeits-Check:** Artikel pro Masterplan markieren
2. **SSL/HTTPS:** Certbot für sichere Verbindung
3. **Benutzer-Verwaltung:** Login & Rollen
4. **Statistiken:** Auswertungen & Berichte
5. **PDF-Export:** Sortimente als PDF
6. **E-Mail-Benachrichtigungen:** Bei Generierung

---

## 📞 Support

Bei Fragen oder Problemen:
1. Logs prüfen: `journalctl -u kistengenerator -f`
2. Services neu starten
3. Datenbank neu laden: `python seed_data.py`

---

**Stand:** 25.02.2026, 23:33 Uhr  
**Version:** 1.0.0  
**Status:** ✅ Produktionsbereit
