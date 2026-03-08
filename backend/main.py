from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="Bio-Kisten Generator")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

OBST = ["Äpfel","Birnen","Bananen","Orangen","Trauben","Kiwi","Mango","Heidelbeeren","Erdbeeren","Zitronen"]
GEMUESE = ["Karotten","Tomaten","Gurken","Paprika","Brokkoli","Spinat","Zucchini","Aubergine","Salat","Radieschen"]

KISTEN = {
    "klein": {"preis": 15.90, "obst": 3, "gemuese": 3},
    "mittel": {"preis": 24.90, "obst": 4, "gemuese": 4},
    "gross": {"preis": 34.90, "obst": 5, "gemuese": 5}
}

@app.get("/")
def status():
    return {"status": "online", "service": "Bio-Kisten Generator"}

@app.post("/api/generate")
def generate(size: str = "mittel"):
    k = KISTEN.get(size, KISTEN["mittel"])
    return
