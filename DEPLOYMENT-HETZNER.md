# Hetzner Server Deployment - Quick Reference

## Server-Details
- **IP**: 89.167.83.224
- **User**: root
- **Passwort**: tq7qWdqusRPb
- **OS**: Ubuntu 24.04
- **Python**: 3.12
- **Node**: v20
- **nginx**: 1.24

## Port-Konfiguration
- **Port 80**: SEO-Tool (NICHT ÄNDERN!)
- **Port 8080**: Kistengenerator Frontend
- **Port 8001**: Kistengenerator Backend (intern)

## Zugriff
- **Frontend**: http://89.167.83.224:8080
- **Backend API**: http://89.167.83.224:8080/api/

## Deployment ausführen

```bash
cd /home/user/kistengenerator
bash deploy-simple.sh
# Passwort eingeben: tq7qWdqusRPb
```

## Server-Verwaltung

### Backend-Service

```bash
# Status prüfen
ssh root@89.167.83.224
systemctl status kistengenerator

# Logs anzeigen
journalctl -u kistengenerator -f

# Service neu starten
systemctl restart kistengenerator

# Service stoppen
systemctl stop kistengenerator

# Service starten
systemctl start kistengenerator
```

### Frontend neu bauen

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/frontend
npm run build
```

### nginx

```bash
# nginx testen
nginx -t

# nginx neu laden
systemctl reload nginx

# nginx neu starten
systemctl restart nginx

# nginx Status
systemctl status nginx
```

## Verzeichnisstruktur auf Server

```
/var/www/kistengenerator/
├── backend/
│   ├── venv/              # Python Virtual Environment
│   ├── main.py            # FastAPI Backend
│   ├── generator.py       # Generator-Logik
│   ├── models.py          # Datenbank-Modelle
│   ├── kistengenerator.db # SQLite Datenbank
│   └── ...
├── frontend/
│   ├── dist/              # Gebautes Frontend (nginx root)
│   ├── src/               # Source Code
│   └── ...
└── ...
```

## Konfigurationsdateien

### systemd Service
```
/etc/systemd/system/kistengenerator.service
```

### nginx Config
```
/etc/nginx/sites-available/kistengenerator
/etc/nginx/sites-enabled/kistengenerator -> ../sites-available/kistengenerator
```

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
journalctl -u kistengenerator -n 50

# Manuell starten zum Testen
cd /var/www/kistengenerator/backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8001
```

### Frontend zeigt 404

```bash
# nginx Config prüfen
nginx -t

# nginx Logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Port 8080 nicht erreichbar

```bash
# Firewall prüfen
ufw status
# oder
iptables -L -n | grep 8080

# Port öffnen
ufw allow 8080/tcp
# oder
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### Datenbank zurücksetzen

```bash
cd /var/www/kistengenerator/backend
source venv/bin/activate
rm kistengenerator.db
python seed_data.py
systemctl restart kistengenerator
```

## Update/Neu-Deployment

```bash
# Lokal: Code packen
cd /home/user/kistengenerator
tar -czf /tmp/kistengenerator.tar.gz --exclude='node_modules' --exclude='__pycache__' --exclude='.git' --exclude='venv' --exclude='*.pyc' --exclude='dist' .

# Deployment ausführen
bash deploy-simple.sh
```

## Backup

### Datenbank sichern

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
cp kistengenerator.db kistengenerator.db.backup-$(date +%Y%m%d-%H%M%S)
```

### Datenbank herunterladen

```bash
scp root@89.167.83.224:/var/www/kistengenerator/backend/kistengenerator.db ./backup/
```

## Monitoring

### Ressourcen prüfen

```bash
ssh root@89.167.83.224

# CPU & RAM
htop

# Disk Space
df -h

# Prozesse
ps aux | grep kistengenerator
ps aux | grep nginx
```

### Backend Health Check

```bash
curl http://127.0.0.1:8001/api/status
```

### Frontend Health Check

```bash
curl -I http://127.0.0.1:8080
```

## Wichtige Hinweise

⚠️ **SEO-Tool auf Port 80 NICHT anfassen!**
⚠️ **Immer Backups vor Updates erstellen**
⚠️ **nginx -t vor nginx reload ausführen**
⚠️ **Logs regelmäßig prüfen**

## Support-Kontakte

Bei Problemen:
1. Logs prüfen (`journalctl -u kistengenerator -f`)
2. nginx Logs prüfen (`/var/log/nginx/error.log`)
3. Backend manuell testen
4. Firewall-Regeln prüfen

## Nützliche Befehle

```bash
# Kompletter Status-Check
ssh root@89.167.83.224 << 'EOF'
echo "=== Backend Service ==="
systemctl status kistengenerator --no-pager
echo ""
echo "=== nginx Status ==="
systemctl status nginx --no-pager
echo ""
echo "=== Backend Health ==="
curl -s http://127.0.0.1:8001/api/status | jq
echo ""
echo "=== Frontend Health ==="
curl -I http://127.0.0.1:8080 2>&1 | head -1
echo ""
echo "=== Disk Space ==="
df -h /var/www
echo ""
echo "=== Memory ==="
free -h
EOF
```
