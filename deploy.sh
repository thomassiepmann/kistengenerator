#!/bin/bash
# Paradieschen Kistengenerator - Deployment Script für Hetzner Server
# Server: 89.167.83.224

set -e  # Bei Fehler abbrechen

SERVER_IP="89.167.83.224"
SERVER_USER="root"
APP_DIR="/var/www/kistengenerator"

echo "🚀 Paradieschen Kistengenerator - Deployment"
echo "=============================================="
echo ""

# 1. Frontend bauen
echo "📦 1. Frontend wird gebaut..."
cd frontend
npm run build
cd ..
echo "✅ Frontend gebaut!"
echo ""

# 2. Dateien auf Server kopieren
echo "📤 2. Dateien werden auf Server kopiert..."
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${APP_DIR}"
scp -r backend ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/
scp -r frontend/dist ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/frontend/
scp -r frontend/package.json ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/frontend/
echo "✅ Dateien kopiert!"
echo ""

# 3. Server-Setup ausführen
echo "⚙️  3. Server wird konfiguriert..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'

# System aktualisieren
apt update
apt upgrade -y

# Node.js 20 installieren
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Python 3, pip, nginx, git installieren
apt install -y python3 python3-pip python3-venv nginx git

# Backend einrichten
cd /var/www/kistengenerator/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py

# Systemd Service für Backend erstellen
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

# Service aktivieren und starten
systemctl daemon-reload
systemctl enable kistengenerator
systemctl start kistengenerator

# Nginx konfigurieren
cat > /etc/nginx/sites-available/kistengenerator << 'EOF'
server {
    listen 80;
    server_name 89.167.83.224;

    # Frontend (statische Dateien)
    location / {
        root /var/www/kistengenerator/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
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

# Nginx Site aktivieren
ln -sf /etc/nginx/sites-available/kistengenerator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx testen und neustarten
nginx -t
systemctl restart nginx

echo "✅ Server-Konfiguration abgeschlossen!"

ENDSSH

echo ""
echo "🎉 DEPLOYMENT ERFOLGREICH!"
echo "=========================="
echo ""
echo "Die App ist jetzt erreichbar unter:"
echo "👉 http://89.167.83.224"
echo ""
echo "Backend-Status prüfen:"
echo "  ssh root@89.167.83.224 'systemctl status kistengenerator'"
echo ""
echo "Logs anzeigen:"
echo "  ssh root@89.167.83.224 'journalctl -u kistengenerator -f'"
echo ""
