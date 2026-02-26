"""
Paradieschen Kistengenerator — FastAPI Backend
Alle API-Endpunkte fuer den vollstaendigen Generator-Workflow.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from io import BytesIO

from database import engine, get_db, Base
from models import (
    ArtikelStamm, Masterplan, MasterplanSlot, PreisPflege,
    WochenQuelle, HistorischeSortimente, GenerierteKisten, KistenFestpreis
)
from schemas import (
    ArtikelOut, ArtikelCreate, ArtikelUpdate,
    MasterplanOut, MasterplanKurzOut,
    PreisOut, PreisCreate, PreisUpdate,
    KistenFestpreisOut, KistenFestpreisCreate, KistenFestpreisUpdate,
    WochenQuelleOut, WochenQuelleCreate,
    GeneratorRequest, GeneratorResponse, GenerierteKisteOut,
    HistorieOut, KisteUpdate
)

# Tabellen erstellen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Paradieschen Kistengenerator API",
    description="Automatisierte Sortimentsgenerierung fuer Bio-Obst & Gemuese-Kisten",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== STATUS ====================

@app.get("/")
def startseite():
    return {
        "app": "Paradieschen Kistengenerator",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/status")
def status(db: Session = Depends(get_db)):
    return {
        "status": "online",
        "artikel": db.query(ArtikelStamm).count(),
        "masterplaene": db.query(Masterplan).count(),
        "historische_kisten": db.query(HistorischeSortimente).count(),
        "generierte_kisten": db.query(GenerierteKisten).count(),
        "preise": db.query(PreisPflege).count(),
    }


# ==================== ARTIKEL ====================

@app.get("/api/artikel", response_model=list[ArtikelOut])
def get_artikel(kategorie: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ArtikelStamm)
    if kategorie:
        query = query.filter(ArtikelStamm.kategorie == kategorie)
    return query.order_by(ArtikelStamm.name).all()


@app.get("/api/artikel/{artikel_id}", response_model=ArtikelOut)
def get_artikel_detail(artikel_id: int, db: Session = Depends(get_db)):
    artikel = db.query(ArtikelStamm).filter(ArtikelStamm.id == artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    return artikel


@app.post("/api/artikel", response_model=ArtikelOut)
def create_artikel(data: ArtikelCreate, db: Session = Depends(get_db)):
    """Neuen Artikel anlegen."""
    # Prüfen ob SID bereits existiert
    existing = db.query(ArtikelStamm).filter(ArtikelStamm.sid == data.sid).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Artikel mit SID '{data.sid}' existiert bereits")
    
    artikel = ArtikelStamm(**data.model_dump())
    db.add(artikel)
    db.commit()
    db.refresh(artikel)
    return artikel


@app.put("/api/artikel/{artikel_id}", response_model=ArtikelOut)
def update_artikel(artikel_id: int, data: ArtikelUpdate, db: Session = Depends(get_db)):
    """Artikel bearbeiten."""
    artikel = db.query(ArtikelStamm).filter(ArtikelStamm.id == artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artikel, key, value)
    
    db.commit()
    db.refresh(artikel)
    return artikel


@app.delete("/api/artikel/{artikel_id}")
def delete_artikel(artikel_id: int, db: Session = Depends(get_db)):
    """Artikel löschen."""
    artikel = db.query(ArtikelStamm).filter(ArtikelStamm.id == artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    db.delete(artikel)
    db.commit()
    return {"status": "erfolg", "message": f"Artikel '{artikel.name}' gelöscht"}


# ==================== MASTERPLAENE ====================

@app.get("/api/masterplan", response_model=list[MasterplanKurzOut])
def get_masterplaene(db: Session = Depends(get_db)):
    return db.query(Masterplan).filter(Masterplan.ist_aktiv == True).all()


@app.get("/api/masterplan/{masterplan_id}", response_model=MasterplanOut)
def get_masterplan_detail(masterplan_id: int, db: Session = Depends(get_db)):
    mp = db.query(Masterplan).filter(Masterplan.id == masterplan_id).first()
    if not mp:
        raise HTTPException(status_code=404, detail="Masterplan nicht gefunden")
    return mp


# ==================== PREISE ====================

@app.get("/api/preise", response_model=list[PreisOut])
def get_preise(db: Session = Depends(get_db)):
    return db.query(PreisPflege).all()


@app.post("/api/preise", response_model=PreisOut)
def create_preis(data: PreisCreate, db: Session = Depends(get_db)):
    preis = PreisPflege(**data.model_dump())
    db.add(preis)
    db.commit()
    db.refresh(preis)
    return preis


@app.put("/api/preise/{preis_id}", response_model=PreisOut)
def update_preis(preis_id: int, data: PreisUpdate, db: Session = Depends(get_db)):
    preis = db.query(PreisPflege).filter(PreisPflege.id == preis_id).first()
    if not preis:
        raise HTTPException(status_code=404, detail="Preis nicht gefunden")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preis, key, value)
    db.commit()
    db.refresh(preis)
    return preis


@app.delete("/api/preise/{preis_id}")
def delete_preis(preis_id: int, db: Session = Depends(get_db)):
    """Preis löschen."""
    preis = db.query(PreisPflege).filter(PreisPflege.id == preis_id).first()
    if not preis:
        raise HTTPException(status_code=404, detail="Preis nicht gefunden")
    
    db.delete(preis)
    db.commit()
    return {"status": "erfolg", "message": "Preis gelöscht"}


# ==================== KISTENPREISE ====================

@app.get("/api/kistenpreise", response_model=list[KistenFestpreisOut])
def get_kistenpreise(db: Session = Depends(get_db)):
    """Alle Kistenpreise abrufen."""
    return db.query(KistenFestpreis).all()


@app.post("/api/kistenpreise", response_model=KistenFestpreisOut)
def create_kistenpreis(
    preis: KistenFestpreisCreate,
    db: Session = Depends(get_db)
):
    """Neuen Kistenpreis erstellen."""
    db_preis = KistenFestpreis(**preis.model_dump())
    db.add(db_preis)
    db.commit()
    db.refresh(db_preis)
    return db_preis


@app.put("/api/kistenpreise/{preis_id}", response_model=KistenFestpreisOut)
def update_kistenpreis(
    preis_id: int,
    preis: KistenFestpreisUpdate,
    db: Session = Depends(get_db)
):
    """Kistenpreis aktualisieren."""
    db_preis = db.query(KistenFestpreis).filter(
        KistenFestpreis.id == preis_id
    ).first()
    
    if not db_preis:
        raise HTTPException(status_code=404, detail="Kistenpreis nicht gefunden")
    
    for key, value in preis.model_dump(exclude_unset=True).items():
        setattr(db_preis, key, value)
    
    db.commit()
    db.refresh(db_preis)
    return db_preis


@app.delete("/api/kistenpreise/{preis_id}")
def delete_kistenpreis(preis_id: int, db: Session = Depends(get_db)):
    """Kistenpreis löschen."""
    db_preis = db.query(KistenFestpreis).filter(
        KistenFestpreis.id == preis_id
    ).first()
    
    if not db_preis:
        raise HTTPException(status_code=404, detail="Kistenpreis nicht gefunden")
    
    db.delete(db_preis)
    db.commit()
    return {"status": "deleted"}


@app.get("/api/kistenpreise/masterplan/{masterplan_id}/{groesse}")
def get_aktiver_kistenpreis(
    masterplan_id: int,
    groesse: str,
    db: Session = Depends(get_db)
):
    """Aktuell gültigen Festpreis für Masterplan + Größe abrufen."""
    from datetime import date
    heute = date.today().isoformat()
    
    preis = db.query(KistenFestpreis).filter(
        KistenFestpreis.masterplan_id == masterplan_id,
        KistenFestpreis.groesse == groesse,
        KistenFestpreis.ist_aktiv == True,
        KistenFestpreis.gueltig_ab <= heute,
        (KistenFestpreis.gueltig_bis == None) | 
        (KistenFestpreis.gueltig_bis >= heute)
    ).first()
    
    if preis:
        return {"festpreis": preis.festpreis, "id": preis.id}
    return {"festpreis": None}


# ==================== WOCHENQUELLE ====================

@app.get("/api/quelle/{kw}/{jahr}", response_model=list[WochenQuelleOut])
def get_quelle(kw: int, jahr: int, db: Session = Depends(get_db)):
    return db.query(WochenQuelle).filter(
        WochenQuelle.kalenderwoche == kw,
        WochenQuelle.jahr == jahr
    ).all()


@app.post("/api/quelle/{kw}/{jahr}", response_model=list[WochenQuelleOut])
def set_quelle(kw: int, jahr: int, eintraege: list[WochenQuelleCreate], db: Session = Depends(get_db)):
    # Alte Eintraege loeschen
    db.query(WochenQuelle).filter(
        WochenQuelle.kalenderwoche == kw,
        WochenQuelle.jahr == jahr
    ).delete()
    # Neue einfuegen
    neue = []
    for e in eintraege:
        wq = WochenQuelle(
            kalenderwoche=kw, jahr=jahr,
            slot_bezeichnung=e.slot_bezeichnung,
            artikel_id=e.artikel_id
        )
        db.add(wq)
        neue.append(wq)
    db.commit()
    for n in neue:
        db.refresh(n)
    return neue


@app.post("/api/quelle/{kw}/{jahr}/kopieren-von/{quell_kw}/{quell_jahr}", response_model=list[WochenQuelleOut])
def kopiere_quelle(kw: int, jahr: int, quell_kw: int, quell_jahr: int, db: Session = Depends(get_db)):
    """Kopiert Wochenquelle von einer anderen Woche."""
    # Quell-Einträge laden
    quell_eintraege = db.query(WochenQuelle).filter(
        WochenQuelle.kalenderwoche == quell_kw,
        WochenQuelle.jahr == quell_jahr
    ).all()
    
    if not quell_eintraege:
        raise HTTPException(status_code=404, detail=f"Keine Quelle für KW{quell_kw}/{quell_jahr} gefunden")
    
    # Alte Einträge der Ziel-Woche löschen
    db.query(WochenQuelle).filter(
        WochenQuelle.kalenderwoche == kw,
        WochenQuelle.jahr == jahr
    ).delete()
    
    # Neue Einträge erstellen
    neue = []
    for quelle in quell_eintraege:
        wq = WochenQuelle(
            kalenderwoche=kw,
            jahr=jahr,
            slot_bezeichnung=quelle.slot_bezeichnung,
            artikel_id=quelle.artikel_id
        )
        db.add(wq)
        neue.append(wq)
    
    db.commit()
    for n in neue:
        db.refresh(n)
    
    return neue


# ==================== GENERATOR ====================

@app.post("/api/kiste/generieren", response_model=GeneratorResponse)
def generate_kiste(request: GeneratorRequest, db: Session = Depends(get_db)):
    """Generiert eine Kiste — die Hauptfunktion!"""
    from generator import generiere_kiste
    ergebnis = generiere_kiste(db, request.typ, request.groesse, request.kw, request.jahr)
    return ergebnis


@app.get("/api/kiste/{kiste_id}", response_model=GenerierteKisteOut)
def get_kiste(kiste_id: int, db: Session = Depends(get_db)):
    kiste = db.query(GenerierteKisten).filter(GenerierteKisten.id == kiste_id).first()
    if not kiste:
        raise HTTPException(status_code=404, detail="Kiste nicht gefunden")
    return kiste


@app.put("/api/kiste/{kiste_id}", response_model=GenerierteKisteOut)
def update_kiste(kiste_id: int, data: KisteUpdate, db: Session = Depends(get_db)):
    """Manuell bearbeitete Kiste speichern (editierbare Slots!)."""
    kiste = db.query(GenerierteKisten).filter(GenerierteKisten.id == kiste_id).first()
    if not kiste:
        raise HTTPException(status_code=404, detail="Kiste nicht gefunden")
    
    # Inhalt und Gesamtpreis aktualisieren
    kiste.inhalt = data.inhalt
    kiste.gesamtpreis = data.gesamtpreis
    kiste.methode = kiste.methode + " (manuell bearbeitet)" if kiste.methode else "Manuell bearbeitet"
    
    db.commit()
    db.refresh(kiste)
    return kiste


@app.put("/api/kiste/{kiste_id}/freigeben")
def freigeben(kiste_id: int, db: Session = Depends(get_db)):
    """Gibt eine Kiste frei und speichert sie als historisches Sortiment."""
    from generator import kiste_freigeben
    return kiste_freigeben(db, kiste_id)


@app.get("/api/kisten", response_model=list[GenerierteKisteOut])
def get_alle_kisten(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(GenerierteKisten)
    if status:
        query = query.filter(GenerierteKisten.status == status)
    return query.order_by(GenerierteKisten.id.desc()).all()


@app.get("/api/kiste/{kiste_id}/export/csv")
def export_kiste_csv(kiste_id: int, db: Session = Depends(get_db)):
    """Exportiert eine Kiste als CSV-Datei."""
    kiste = db.query(GenerierteKisten).filter(GenerierteKisten.id == kiste_id).first()
    if not kiste:
        raise HTTPException(status_code=404, detail="Kiste nicht gefunden")
    
    # CSV-Inhalt erstellen
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Header
    writer.writerow(['Slot', 'Artikel', 'SID', 'Menge', 'Einheit', 'Einzelpreis', 'Positionspreis'])
    
    # Daten
    for pos in kiste.inhalt:
        writer.writerow([
            pos.get('slot', ''),
            pos.get('name', ''),
            pos.get('sid', ''),
            pos.get('menge', 0),
            pos.get('einheit', ''),
            f"{pos.get('preis_einheit', 0):.2f}",
            f"{pos.get('preis_position', 0):.2f}"
        ])
    
    # Gesamtpreis
    writer.writerow([])
    writer.writerow(['', '', '', '', '', 'GESAMT:', f"{kiste.gesamtpreis:.2f}"])
    
    # CSV als Response
    csv_content = output.getvalue()
    output.close()
    
    masterplan = db.query(Masterplan).filter(Masterplan.id == kiste.masterplan_id).first()
    filename = f"Kiste_{masterplan.name if masterplan else 'Export'}_KW{kiste.kalenderwoche}_{kiste.jahr}.csv"
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/kiste/generieren-alle")
def generate_alle_kisten(kw: int, jahr: int, db: Session = Depends(get_db)):
    """Generiert ALLE Masterplaene auf einmal für eine Woche — HAUPTANWENDUNGSFALL!"""
    from generator import generiere_kiste
    
    # Alle aktiven Masterplaene laden
    masterplaene = db.query(Masterplan).filter(Masterplan.ist_aktiv == True).all()
    
    if not masterplaene:
        raise HTTPException(status_code=404, detail="Keine aktiven Masterplaene gefunden")
    
    ergebnisse = []
    fehler = []
    
    for mp in masterplaene:
        try:
            ergebnis = generiere_kiste(db, mp.name, mp.groesse, kw, jahr)
            ergebnisse.append({
                "masterplan": mp.name,
                "status": ergebnis.get("status"),
                "kiste_id": ergebnis.get("kiste_id"),
                "gesamtpreis": ergebnis.get("gesamtpreis"),
                "match_score": ergebnis.get("match_score", 0),
                "methode": ergebnis.get("methode", "")
            })
        except Exception as e:
            fehler.append({
                "masterplan": mp.name,
                "fehler": str(e)
            })
    
    return {
        "status": "abgeschlossen",
        "kw": kw,
        "jahr": jahr,
        "generiert": len(ergebnisse),
        "fehler": len(fehler),
        "ergebnisse": ergebnisse,
        "fehler_details": fehler
    }


# ==================== HISTORIE ====================

@app.get("/api/historie", response_model=list[HistorieOut])
def get_historie(
    masterplan_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(HistorischeSortimente)
    if masterplan_name:
        mp = db.query(Masterplan).filter(Masterplan.name == masterplan_name).first()
        if mp:
            query = query.filter(HistorischeSortimente.masterplan_id == mp.id)
    return query.order_by(HistorischeSortimente.jahr.desc(), HistorischeSortimente.kalenderwoche.desc()).all()


# ==================== MUSTER ====================

@app.post("/api/muster/lernen")
def muster_lernen(db: Session = Depends(get_db)):
    """Extrahiert Muster aus allen historischen Sortimenten."""
    from muster_lernen import extrahiere_muster_aus_historie
    return extrahiere_muster_aus_historie(db)


@app.post("/api/muster/match")
def muster_match(request: GeneratorRequest, db: Session = Depends(get_db)):
    """Findet den besten historischen Match fuer eine Wochenquelle."""
    from muster_lernen import finde_besten_match, lade_wochenquelle_als_artikel
    quelle = lade_wochenquelle_als_artikel(db, request.kw, request.jahr)
    if not quelle:
        raise HTTPException(status_code=404, detail=f"Keine Quelle fuer KW{request.kw}/{request.jahr}")
    matches = finde_besten_match(db, quelle, request.typ, top_n=5)
    return {"matches": matches, "quelle_artikel": len(quelle)}


# ==================== IMPORT ====================

@app.post("/api/import/artikel")
async def import_artikel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importiert Artikel aus Excel-Datei."""
    from import_handler import import_artikel_from_excel
    content = await file.read()
    result = import_artikel_from_excel(db, content)
    return result


@app.post("/api/import/historie")
async def import_historie(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importiert historische Sortimente aus Excel-Datei."""
    from import_handler import import_historie_from_excel
    content = await file.read()
    result = import_historie_from_excel(db, content)
    return result


@app.post("/api/import/preise")
async def import_preise(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importiert Preise aus Excel-Datei."""
    from import_handler import import_preise_from_excel
    content = await file.read()
    result = import_preise_from_excel(db, content)
    return result


@app.post("/api/import/wochenquelle")
async def import_wochenquelle(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importiert Wochenquelle aus Excel-Datei."""
    from import_handler import import_wochenquelle_from_excel
    content = await file.read()
    result = import_wochenquelle_from_excel(db, content)
    return result


@app.post("/api/import/masterplan")
async def import_masterplan(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importiert Masterplan-Matrix aus Excel-Datei."""
    from import_handler import import_masterplan_from_excel
    content = await file.read()
    result = import_masterplan_from_excel(db, content)
    return result


@app.get("/api/import/vorlage/{typ}")
def download_vorlage(typ: str):
    """Lädt Excel-Vorlage für Import herunter."""
    from import_handler import create_excel_template
    
    valid_types = ["artikel", "historie", "preise", "wochenquelle", "masterplan"]
    if typ not in valid_types:
        raise HTTPException(status_code=400, detail=f"Ungültiger Typ. Erlaubt: {', '.join(valid_types)}")
    
    content = create_excel_template(typ)
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Vorlage_{typ}.xlsx"}
    )


# ==================== PC-GÄRTNER INTEGRATION ====================

@app.get("/api/integration/status")
def get_integration_status():
    """Gibt den Status der PC-Gärtner Integration zurück."""
    from pcgaertner_integration import pcgaertner_api
    
    if pcgaertner_api:
        return pcgaertner_api.get_integration_status()
    else:
        return {
            "konfiguriert": False,
            "nachricht": "PC-Gärtner Integration nicht initialisiert",
            "hinweis": "Nutzen Sie CSV-Import/Export als Alternative"
        }


@app.post("/api/integration/test")
def test_integration():
    """Testet die Verbindung zu PC-Gärtner."""
    from pcgaertner_integration import pcgaertner_api
    
    if not pcgaertner_api:
        raise HTTPException(status_code=503, detail="Integration nicht konfiguriert")
    
    return pcgaertner_api.test_connection()


@app.post("/api/integration/sync-artikel")
def sync_artikel_from_pcgaertner(db: Session = Depends(get_db)):
    """
    Synchronisiert Artikel aus PC-Gärtner Artikelmanager.
    
    Importiert:
    - Artikel-SID
    - Artikel-Name
    - Kategorie
    - Einheit
    """
    from pcgaertner_integration import pcgaertner_api
    
    if not pcgaertner_api:
        raise HTTPException(
            status_code=503,
            detail="PC-Gärtner Integration nicht konfiguriert. Nutzen Sie /api/import/artikel für CSV-Import."
        )
    
    result = pcgaertner_api.sync_artikel_from_pcgaertner(db)
    return result


@app.post("/api/integration/sync-preise")
def sync_preise_from_pcgaertner(db: Session = Depends(get_db)):
    """
    Synchronisiert Preise aus PC-Gärtner.
    
    Importiert:
    - Artikel-SID
    - Preis pro Einheit
    - Gültigkeitsdatum
    """
    from pcgaertner_integration import pcgaertner_api
    
    if not pcgaertner_api:
        raise HTTPException(
            status_code=503,
            detail="PC-Gärtner Integration nicht konfiguriert. Nutzen Sie /api/import/preise für CSV-Import."
        )
    
    result = pcgaertner_api.sync_preise_from_pcgaertner(db)
    return result


@app.post("/api/integration/export-sortiment/{kiste_id}")
def export_sortiment_to_pcgaertner(kiste_id: int, db: Session = Depends(get_db)):
    """
    Exportiert ein generiertes Sortiment an PC-Gärtner.
    
    Args:
        kiste_id: ID der generierten Kiste
    """
    from pcgaertner_integration import pcgaertner_api
    
    if not pcgaertner_api:
        # Fallback: CSV-Export
        return {
            "status": "info",
            "nachricht": "PC-Gärtner Integration nicht konfiguriert",
            "alternative": f"Nutzen Sie /api/kiste/{kiste_id}/export/csv für CSV-Export"
        }
    
    result = pcgaertner_api.export_sortiment_to_pcgaertner(db, kiste_id)
    return result


# ==================== START ====================

if __name__ == "__main__":
    import uvicorn
    
    # PC-Gärtner Integration initialisieren (optional)
    # Kann über Umgebungsvariablen konfiguriert werden
    import os
    from pcgaertner_integration import init_pcgaertner_integration
    
    pcgaertner_url = os.getenv("PCGAERTNER_API_URL")
    pcgaertner_key = os.getenv("PCGAERTNER_API_KEY")
    
    if pcgaertner_url:
        init_pcgaertner_integration(base_url=pcgaertner_url, api_key=pcgaertner_key)
        print(f"✅ PC-Gärtner Integration initialisiert: {pcgaertner_url}")
    else:
        print("ℹ️  PC-Gärtner Integration nicht konfiguriert (nutzen Sie CSV-Import/Export)")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
