#!/bin/bash

# Alles stoppen
kill $(lsof -t -i:8001) 2>/dev/null
kill $(lsof -t -i:5173) 2>/dev/null

# Backend starten
cd ~/kistengenerator/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &

sleep 3

if curl -s http://localhost:8001/api/status | grep -q "online"; then
    echo "✅ Backend läuft auf Port 8001"
else
    echo "❌ Backend FEHLER!"
    exit 1
fi

# Frontend starten
cd ~/kistengenerator/frontend
npm run dev &

sleep 3
echo "✅ Frontend läuft auf Port 5173"
echo "=== ALLES LÄUFT ==="
