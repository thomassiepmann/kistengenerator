"""
Kistengenerator — Backend-Test
Wenn das hier funktioniert, ist die Umgebung korrekt.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Kistengenerator API",
    description="Dynamischer Sortiments- und Kistengenerator",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def startseite():
    return {"nachricht": "Kistengenerator API laeuft!"}

@app.get("/api/status")
def status():
    return {
        "status": "online",
        "version": "0.1.0",
        "python": "3.13.7",
        "phase": "Setup abgeschlossen - bereit fuer Phase 1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
