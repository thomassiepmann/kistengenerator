# 🚀 Deployment-Anleitung: Paradieschen Kistengenerator

## Server-Informationen
- **IP:** 89.167.83.224
- **Benutzer:** root
- **App-URL:** http://89.167.83.224

## Automatisches Deployment

### Schritt 1: SSH-Schlüssel einrichten (empfohlen)

Für sicheres Deployment ohne Passwort-Eingabe:

```bash
# SSH-Schlüssel generieren (falls noch nicht vorhanden)
ssh-keygen -t rsa -b 4096

# Schlüssel auf Server kopieren
ssh-copy-id root@89.167.83.224
# Passwort eingeben: jkMfMNV4tM9enJjHxWTc
```

### Schritt 2: Deployment ausführen

```bash
cd /home/user/kistengenerator
./deploy.sh
```

Das Script führt automatisch aus:
1. ✅ Frontend bauen (`npm run build`)
2. ✅ Dateien auf Server kopieren
3. ✅ Node.js 20, Python 3, nginx installieren
4. ✅ Backend einrichten (venv, requirements, seed_data)
5. ✅ Systemd Service erstellen
6. ✅ Nginx konfigurieren
7. ✅ Services starten

**Dauer:** ca. 5-10 Minuten

---

## Manuelles Deployment (falls Script fehlschlägt)

### 1. Frontend bauen

```bash
cd /home/user/kistengenerator/frontend
npm run build
```

### 2. Dateien auf Server kopieren

```bash
cd /home/user/kistengenerator
scp -r backend root@89.167.83.224:/var/www/kistengenerator/
scp -r frontend/dist root@89.167.83.224:/var/www/kistengenerator/frontend/
```

### 3. Auf Server einloggen

```bash
ssh root@89.167.83.224
# Passwort: jkMfMNV4tM9enJjHxWTc
```

### 4. System aktualisieren

```bash
apt update && apt upgrade -y
```

### 5. Node.js 20 installieren

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

### 6. Python, nginx, git installieren

```bash
apt install -y python3 python3-pip python3-venv nginx git
```

### 7. Backend einrichten

```bash
cd /var/www/kistengenerator/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
```

### 8. Systemd Service erstellen

```bash
cat > /etc/systemd/system/kistengenerator.service << 'EOF'
[Unit]
Description=Paradieschen Kistengenerator Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/kistengenerator/backend
Environment="PATH=/var/www/kistengenerator/backend/venv/bin"
ExecStart=/var/www/kistengenerator/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kistengenerator
systemctl start kistengenerator
```

### 9. Nginx konfigurieren

```bash
cat > /etc/nginx/sites-available/kistengenerator << 'EOF'
server {
    listen 80;
    server_name 89.167.83.224;

    location / {
        root /var/www/kistengenerator/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/kistengenerator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

---

## Nach dem Deployment

### App testen

Öffnen Sie im Browser:
```
http://89.167.83.224
```

### Backend-Status prüfen

```bash
ssh root@89.167.83.224 'systemctl status kistengenerator'
```

### Logs anzeigen

```bash
# Backend-Logs live
ssh root@89.167.83.224 'journalctl -u kistengenerator -f'

# Nginx-Logs
ssh root@89.167.83.224 'tail -f /var/log/nginx/access.log'
ssh root@89.167.83.224 'tail -f /var/log/nginx/error.log'
```

### Service neu starten

```bash
# Backend neu starten
ssh root@89.167.83.224 'systemctl restart kistengenerator'

# Nginx neu starten
ssh root@89.167.83.224 'systemctl restart nginx'
```

---

## Updates deployen

Wenn Sie Änderungen am Code gemacht haben:

```bash
cd /home/user/kistengenerator
./deploy.sh
```

Das Script überschreibt die Dateien auf dem Server und startet die Services neu.

---

## Troubleshooting

### Backend startet nicht

```bash
ssh root@89.167.83.224
journalctl -u kistengenerator -n 50
```

### Nginx-Fehler

```bash
ssh root@89.167.83.224
nginx -t
tail -f /var/log/nginx/error.log
```

### Port 8001 bereits belegt

```bash
ssh root@89.167.83.224
lsof -i :8001
# Prozess beenden oder anderen Port verwenden
```

### Datenbank zurücksetzen

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
rm kistengenerator.db
source venv/bin/activate
python seed_data.py
systemctl restart kistengenerator
```

---

## Sicherheitshinweise

⚠️ **WICHTIG:**

1. **Firewall einrichten:**
   ```bash
   ssh root@89.167.83.224
   apt install -y ufw
   ufw allow 22
   ufw allow 80
   ufw allow 443
   ufw enable
   ```

2. **SSL/HTTPS einrichten (empfohlen):**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d ihre-domain.de
   ```

3. **Root-Login deaktivieren:**
   - Erstellen Sie einen normalen Benutzer
   - Deaktivieren Sie Root-SSH-Login

4. **Passwort ändern:**
   ```bash
   ssh root@89.167.83.224
   passwd
   ```

---

## Architektur

```
Internet
   ↓
Nginx (Port 80)
   ├─→ Frontend (statische Dateien)
   └─→ /api/* → Backend (Port 8001)
              ↓
          FastAPI + SQLite
```

---

## Support

Bei Problemen:
1. Logs prüfen (siehe oben)
2. Services neu starten
3. Server neu starten: `ssh root@89.167.83.224 'reboot'`
