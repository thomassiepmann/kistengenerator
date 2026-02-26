#!/bin/bash
# Einfaches Deployment-Script für Hetzner Server
# Führen Sie dieses Script aus: bash deploy-simple.sh

set -e

SERVER="root@89.167.83.224"

echo "🚀 Deploying Kistengenerator to Hetzner Server..."
echo ""

# 1. Code auf Server kopieren
echo "📦 Step 1: Copying code to server..."
echo "Password: tq7qWdqusRPb"
scp /tmp/kistengenerator.tar.gz $SERVER:/tmp/

echo ""
echo "✅ Code copied!"
echo ""

# 2. Server-Setup
echo "🔧 Step 2: Running setup on server..."
echo "Password: tq7qWdqusRPb"
echo ""

ssh $SERVER 'bash -s' << 'ENDSSH'
set -e

echo "📁 Creating directory..."
mkdir -p /var/www/kistengenerator
cd /var/www/kistengenerator

echo "📦 Extracting code..."
tar -xzf /tmp/kistengenerator.tar.gz
rm /tmp/kistengenerator.tar.gz

echo "🐍 Setting up Python backend..."
cd /var/www/kistengenerator/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null

echo "💾 Initializing database..."
python seed_data.py

echo "⚙️  Creating systemd service..."
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

echo "📦 Building frontend..."
cd /var/www/kistengenerator/frontend
npm install > /dev/null 2>&1
npm run build

echo "🌐 Configuring nginx..."
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

ln -sf /etc/nginx/sites-available/kistengenerator /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo "🔥 Opening firewall port 8080..."
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp 2>/dev/null || true
elif command -v iptables &> /dev/null; then
    iptables -A INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null || true
fi

echo ""
echo "🧪 Testing deployment..."
sleep 3

if curl -s http://127.0.0.1:8001/api/status > /dev/null; then
    echo "✅ Backend is running on port 8001"
else
    echo "⚠️  Backend might still be starting..."
fi

if curl -s http://127.0.0.1:8080 > /dev/null; then
    echo "✅ Frontend is running on port 8080"
else
    echo "⚠️  Frontend might still be starting..."
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Access your Kistengenerator at:"
echo "   http://89.167.83.224:8080"
echo ""
echo "🔍 Check backend status:"
echo "   systemctl status kistengenerator"
echo ""
echo "📋 View logs:"
echo "   journalctl -u kistengenerator -f"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ENDSSH

echo ""
echo "✅ Deployment script completed!"
echo ""
