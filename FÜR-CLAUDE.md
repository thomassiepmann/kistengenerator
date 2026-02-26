# Für Claude: Was soll auf den Hetzner Server?

## 🥬 Paradieschen Kistengenerator

**Eine vollständige Web-Anwendung für Bio-Gemüse-Kisten-Sortimente**

### Was ist das?

Ein intelligenter Generator für Bio-Obst & Gemüse-Kisten, der automatisch optimierte Sortimente erstellt basierend auf:
- Verfügbarkeit (Wochenquelle)
- Historischen Daten (lernt aus der Vergangenheit)
- Preisen und Zielpreis-Rahmen
- Tauschmuster (Min/Max-Mengen pro Artikel)

### Technologie-Stack

**Backend:**
- Python 3.12
- FastAPI (REST API)
- SQLite Datenbank
- uvicorn Server
- Port: 8001 (intern)

**Frontend:**
- React (Vite)
- Responsive Design
- Mobile/Tablet-optimiert
- Port: 8080 (öffentlich)

**Server:**
- nginx als Reverse Proxy
- systemd Service für Backend
- Ubuntu 24.04

### Deployment-Ziel

**Server:** 89.167.83.224 (Hetzner)
- **Port 80**: SEO-Tool (NICHT ANFASSEN!)
- **Port 8080**: Kistengenerator Frontend (NEU)
- **Port 8001**: Kistengenerator Backend (intern, NEU)

### Was muss deployed werden?

1. **Backend** (`/var/www/kistengenerator/backend/`)
   - Python Virtual Environment
   - FastAPI App
   - SQLite Datenbank mit Seed-Daten
   - systemd Service

2. **Frontend** (`/var/www/kistengenerator/frontend/`)
   - React App (gebaut mit `npm run build`)
   - Statische Dateien in `dist/`
   - Served von nginx

3. **nginx Config**
   - Neue Site auf Port 8080
   - Proxy zu Backend Port 8001
   - Statische Dateien aus `frontend/dist/`

4. **Firewall**
   - Port 8080 öffnen (ufw oder iptables)

### Dateien die hochgeladen werden

Das tar.gz Archiv enthält:
- `backend/` - Python FastAPI Backend
  - `main.py` - API Endpoints
  - `generator.py` - Generator-Logik
  - `models.py` - Datenbank-Modelle
  - `seed_data.py` - Initialdaten
  - `requirements.txt` - Python Dependencies
  - etc.

- `frontend/` - React Frontend
  - `src/` - Source Code
  - `package.json` - npm Dependencies
  - `vite.config.js` - Build Config
  - etc.

### Wichtig!

- **NICHT** das SEO-Tool auf Port 80 anfassen!
- **NICHT** bestehende nginx Configs ändern!
- **NUR** neue Config für Port 8080 erstellen!

### Erwartetes Ergebnis

Nach dem Deployment:
- http://89.167.83.224:8080 → Kistengenerator Frontend
- http://89.167.83.224:8080/api/status → Backend API
- http://89.167.83.224 → SEO-Tool (unverändert)

### Deployment-Schritte

1. Code entpacken nach `/var/www/kistengenerator/`
2. Python venv erstellen und Dependencies installieren
3. Datenbank initialisieren (`python seed_data.py`)
4. systemd Service erstellen und starten
5. Frontend bauen (`npm install && npm run build`)
6. nginx Config erstellen (Port 8080)
7. nginx neu laden
8. Firewall Port 8080 öffnen

### Credentials

- **Server**: root@89.167.83.224
- **Passwort**: tq7qWdqusRPb

### Hilfreiche Befehle nach Deployment

```bash
# Backend Status
systemctl status kistengenerator

# Backend Logs
journalctl -u kistengenerator -f

# nginx testen
nginx -t

# nginx neu laden
systemctl reload nginx
```

Das ist alles! 🚀
