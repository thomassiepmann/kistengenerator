#!/bin/bash
set -e

SERVER="89.167.83.224"
USER="root"
PASSWORD="tq7qWdqusRPb"
REMOTE_DIR="/var/www/kistengenerator"

echo "🚀 Deploying Kistengenerator to Hetzner Server..."

# 1. Code auf Server kopieren
echo "📦 Step 1: Copying code to server..."
sshpass -p "$PASSWORD" scp /tmp/kistengenerator.tar.gz $USER@$SERVER:/tmp/

# 2. Server-Setup ausführen
echo "🔧 Step 2: Setting up on server..."
sshpass -p "$PASSWORD" ssh $USER@$SERVER << 'ENDSSH'
set -e

# Verzeichnis erstellen
mkdir -p /var/www/kistengenerator
cd /var/www/kistengenerator

# Code entpacken
tar -xzf /tmp/kistengenerator.tar.gz
rm /tmp/kistengenerator.tar.gz

echo "✅ Code extracted"

# Backend einrichten
cd /var/www/kistengenerator/backend

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# Datenbank initialisieren
python seed_data.py

echo "✅ Database initialized"

# systemd Service erstellen
cat > /etc/systemd/system/kistengenerator.service << 'EOF'
[Unit]
Description=Kistengenerator Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/kistengenerator/backend
Environment="PATH=/var/www/kistengenerator/backend/venv/bin"
ExecStart=/var/www/kistengenerator/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kistengenerator
systemctl start kistengenerator

echo "✅ Backend service started"

# Frontend bauen
cd /var/www/kistengenerator/frontend

npm install
npm run build

echo "✅ Frontend built"

# nginx Config erstellen
cat > /etc/nginx/sites-available/kistengenerator << 'EOF'
server {
    listen 8080;
    server_name _;

    root /var/www/kistengenerator/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# nginx aktivieren
ln -sf /etc/nginx/sites-available/kistengenerator /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo "✅ nginx configured"

# Firewall Port 8080 öffnen
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp
    echo "✅ Firewall (ufw) configured"
elif command -v iptables &> /dev/null; then
    iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    echo "✅ Firewall (iptables) configured"
fi

# Status prüfen
echo ""
echo "🧪 Testing deployment..."
sleep 2

# Backend testen
if curl -s http://127.0.0.1:8001/api/status > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend test failed"
fi

# Frontend testen
if curl -s http://127.0.0.1:8080 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend test failed"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📍 Access your app at:"
echo "   http://89.167.83.224:8080"
echo ""
echo "🔍 Check status:"
echo "   systemctl status kistengenerator"
echo "   journalctl -u kistengenerator -f"
echo ""

ENDSSH

echo "✅ Deployment finished!"
