"""
Paradieschen Kistengenerator — Import-Handler
Verarbeitet Excel/CSV-Uploads und externe Datenbank-Synchronisation.
"""
import pandas as pd
import openpyxl
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from models import (
    ArtikelStamm, Masterplan, MasterplanSlot, Tauschmuster,
    PreisPflege, WochenQuelle, HistorischeSortimente
)


def import_artikel_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert Artikel aus Excel-Datei.
    Erwartete Spalten: SID, Name, Kategorie, Einheit, Status (optional)
    """
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        # Spalten validieren
        required_cols = ['SID', 'Name', 'Kategorie', 'Einheit']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "status": "fehler",
                "grund": f"Fehlende Spalten: {', '.join(missing)}"
            }
        
        imported = 0
        updated = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                sid = str(row['SID']).strip()
                name = str(row['Name']).strip()
                kategorie = str(row['Kategorie']).strip()
                einheit = str(row['Einheit']).strip()
                status = str(row.get('Status', 'aktiv')).strip()
                
                # Prüfen ob Artikel existiert
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                
                if artikel:
                    # Update
                    artikel.name = name
                    artikel.kategorie = kategorie
                    artikel.einheit = einheit
                    artikel.status = status
                    updated += 1
                else:
                    # Neu anlegen
                    artikel = ArtikelStamm(
                        sid=sid, name=name, kategorie=kategorie,
                        einheit=einheit, status=status
                    )
                    db.add(artikel)
                    imported += 1
                    
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "importiert": imported,
            "aktualisiert": updated,
            "fehler": errors,
            "gesamt": imported + updated
        }
        
    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_historie_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert historische Sortimente aus Excel.
    Erwartete Spalten: KW, Jahr, Kistentyp, Slot, Artikel_SID, Menge, Preis (optional)
    """
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        required_cols = ['KW', 'Jahr', 'Kistentyp', 'Slot', 'Artikel_SID', 'Menge']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "status": "fehler",
                "grund": f"Fehlende Spalten: {', '.join(missing)}"
            }
        
        # Nach KW, Jahr, Kistentyp gruppieren
        grouped = df.groupby(['KW', 'Jahr', 'Kistentyp'])
        
        imported = 0
        errors = []
        
        for (kw, jahr, kistentyp), group in grouped:
            try:
                # Masterplan finden
                masterplan = db.query(Masterplan).filter(Masterplan.name == kistentyp).first()
                if not masterplan:
                    errors.append(f"Masterplan '{kistentyp}' nicht gefunden")
                    continue
                
                # Artikel-Zuweisungen und Mengen sammeln
                artikel_zuweisungen = []
                mengen_zuweisungen = []
                gesamtpreis = 0.0
                
                for _, row in group.iterrows():
                    sid = str(row['Artikel_SID']).strip()
                    slot = str(row['Slot']).strip()
                    menge = float(row['Menge'])
                    
                    # Artikel finden
                    artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                    if not artikel:
                        errors.append(f"Artikel SID '{sid}' nicht gefunden")
                        continue
                    
                    artikel_zuweisungen.append({
                        "slot": slot,
                        "artikel_id": artikel.id,
                        "artikel_name": artikel.name,
                        "sid": sid
                    })
                    
                    mengen_zuweisungen.append({
                        "artikel_id": artikel.id,
                        "menge": menge,
                        "einheit": artikel.einheit
                    })
                    
                    # Preis berechnen (wenn vorhanden)
                    if 'Preis' in row and pd.notna(row['Preis']):
                        gesamtpreis += float(row['Preis'])
                    else:
                        # Preis aus PreisPflege holen
                        preis = db.query(PreisPflege).filter(
                            PreisPflege.artikel_id == artikel.id
                        ).order_by(PreisPflege.gueltig_ab.desc()).first()
                        if preis:
                            gesamtpreis += menge * preis.preis_pro_einheit
                
                # Historisches Sortiment anlegen
                hist = HistorischeSortimente(
                    masterplan_id=masterplan.id,
                    kalenderwoche=int(kw),
                    jahr=int(jahr),
                    artikel_zuweisungen=artikel_zuweisungen,
                    mengen_zuweisungen=mengen_zuweisungen,
                    gesamtpreis=round(gesamtpreis, 2)
                )
                db.add(hist)
                imported += 1
                
            except Exception as e:
                errors.append(f"KW{kw}/{jahr} {kistentyp}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "importiert": imported,
            "fehler": errors
        }
        
    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_preise_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert Preise aus Excel.
    Erwartete Spalten: Artikel_SID, Preis, Gueltig_ab, Gueltig_bis (optional)
    """
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        required_cols = ['Artikel_SID', 'Preis', 'Gueltig_ab']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "status": "fehler",
                "grund": f"Fehlende Spalten: {', '.join(missing)}"
            }
        
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                sid = str(row['Artikel_SID']).strip()
                preis = float(row['Preis'])
                gueltig_ab = str(row['Gueltig_ab'])
                gueltig_bis = str(row.get('Gueltig_bis', '')) if pd.notna(row.get('Gueltig_bis')) else None
                
                # Artikel finden
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                if not artikel:
                    errors.append(f"Zeile {idx + 2}: Artikel SID '{sid}' nicht gefunden")
                    continue
                
                # Preis anlegen
                preis_obj = PreisPflege(
                    artikel_id=artikel.id,
                    preis_pro_einheit=preis,
                    gueltig_ab=gueltig_ab,
                    gueltig_bis=gueltig_bis
                )
                db.add(preis_obj)
                imported += 1
                
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "importiert": imported,
            "fehler": errors
        }
        
    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_wochenquelle_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert Wochenquelle aus Excel.
    Erwartete Spalten: KW, Jahr, Slot, Artikel_SID
    """
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        required_cols = ['KW', 'Jahr', 'Slot', 'Artikel_SID']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "status": "fehler",
                "grund": f"Fehlende Spalten: {', '.join(missing)}"
            }
        
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                kw = int(row['KW'])
                jahr = int(row['Jahr'])
                slot = str(row['Slot']).strip()
                sid = str(row['Artikel_SID']).strip()
                
                # Artikel finden
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                if not artikel:
                    errors.append(f"Zeile {idx + 2}: Artikel SID '{sid}' nicht gefunden")
                    continue
                
                # Prüfen ob bereits vorhanden
                existing = db.query(WochenQuelle).filter(
                    WochenQuelle.kalenderwoche == kw,
                    WochenQuelle.jahr == jahr,
                    WochenQuelle.slot_bezeichnung == slot
                ).first()
                
                if existing:
                    existing.artikel_id = artikel.id
                else:
                    wq = WochenQuelle(
                        kalenderwoche=kw,
                        jahr=jahr,
                        slot_bezeichnung=slot,
                        artikel_id=artikel.id
                    )
                    db.add(wq)
                    imported += 1
                
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "importiert": imported,
            "fehler": errors
        }
        
    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_masterplan_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert Masterplan-Matrix aus Excel.
    Erwartete Struktur: Erste Spalte = Kistentyp, weitere Spalten = Slots mit 'x' Markierung
    """
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        if df.shape[1] < 2:
            return {
                "status": "fehler",
                "grund": "Excel muss mindestens 2 Spalten haben (Kistentyp + Slots)"
            }
        
        imported_mp = 0
        imported_slots = 0
        errors = []
        
        kistentyp_col = df.columns[0]
        slot_cols = df.columns[1:]
        
        for idx, row in df.iterrows():
            try:
                kistentyp = str(row[kistentyp_col]).strip()
                if not kistentyp or kistentyp.lower() == 'nan':
                    continue
                
                # Masterplan anlegen/finden
                mp = db.query(Masterplan).filter(Masterplan.name == kistentyp).first()
                if not mp:
                    # Defaults setzen
                    mp = Masterplan(
                        name=kistentyp,
                        beschreibung=f"Importiert aus Excel",
                        groesse="M",
                        zielpreis_min=10.0,
                        zielpreis_max=20.0,
                        ist_aktiv=True
                    )
                    db.add(mp)
                    db.flush()
                    imported_mp += 1
                
                # Alte Slots löschen
                db.query(MasterplanSlot).filter(MasterplanSlot.masterplan_id == mp.id).delete()
                
                # Neue Slots anlegen
                slot_nr = 1
                for slot_name in slot_cols:
                    if pd.notna(row[slot_name]) and str(row[slot_name]).strip().lower() in ['x', '1', 'ja', 'yes']:
                        # Kategorie aus Slot-Name extrahieren (z.B. "Gemüse 1" -> "Gemüse")
                        kategorie = slot_name.rsplit(' ', 1)[0] if ' ' in slot_name else slot_name
                        
                        slot = MasterplanSlot(
                            masterplan_id=mp.id,
                            kategorie=kategorie,
                            slot_nummer=slot_nr,
                            ist_pflicht=True
                        )
                        db.add(slot)
                        imported_slots += 1
                        slot_nr += 1
                
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "masterplaene": imported_mp,
            "slots": imported_slots,
            "fehler": errors
        }
        
    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def create_excel_template(template_type: str) -> bytes:
    """
    Erstellt Excel-Vorlagen für verschiedene Import-Typen.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    
    if template_type == "artikel":
        ws.title = "Artikel"
        ws.append(["SID", "Name", "Kategorie", "Einheit", "Status"])
        ws.append(["13", "Zucchini", "Gemuese", "Kilogramm", "aktiv"])
        ws.append(["241", "Paprika gelb", "Gemuese", "Kilogramm", "aktiv"])
        
    elif template_type == "historie":
        ws.title = "Historie"
        ws.append(["KW", "Jahr", "Kistentyp", "Slot", "Artikel_SID", "Menge", "Preis"])
        ws.append([26, 2025, "OG12", "Gemuese 1", "13", 0.65, 1.89])
        ws.append([26, 2025, "OG12", "Gemuese 2", "241", 0.25, 1.13])
        
    elif template_type == "preise":
        ws.title = "Preise"
        ws.append(["Artikel_SID", "Preis", "Gueltig_ab", "Gueltig_bis"])
        ws.append(["13", 2.90, "2025-06-01", "2025-07-31"])
        ws.append(["241", 4.50, "2025-06-01", ""])
        
    elif template_type == "wochenquelle":
        ws.title = "Wochenquelle"
        ws.append(["KW", "Jahr", "Slot", "Artikel_SID"])
        ws.append([26, 2025, "Gemuese 1", "13"])
        ws.append([26, 2025, "Gemuese 2", "241"])
        
    elif template_type == "masterplan":
        ws.title = "Masterplan"
        ws.append(["Kistentyp", "Gemuese 1", "Gemuese 2", "Gemuese 3", "Rohkost 1", "Salat 1", "Obst 1", "Obst 2", "Obst 3"])
        ws.append(["OG12", "x", "x", "x", "x", "x", "x", "x", "x"])
        ws.append(["OG15", "x", "x", "x", "x", "x", "x", "x", "x"])
    
    # In BytesIO speichern
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
