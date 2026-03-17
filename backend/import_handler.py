"""
Paradieschen Kistengenerator — Import-Handler
Verarbeitet Excel/CSV-Uploads nach Kurts Original-Excelformaten.
"""
import pandas as pd
import openpyxl
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from models import (
    ArtikelStamm, Masterplan, MasterplanSlot, Tauschmuster,
    PreisPflege, WochenQuelle, HistorischeSortimente, KistenFestpreis
)


def extract_kategorie_from_name(name: str) -> str:
    """
    Leitet Kategorie aus Artikelnamen ab.
    - Enthält "Salat" → Salat
    - Enthält Apfel/Birne/Obst/Beere/Zitrus → Obst
    - Sonst → Gemuese
    """
    ober_name = str(name).upper()
    if "SALAT" in ober_name:
        return "Salat"
    if any(keyword in ober_name for keyword in ["APFEL", "BIRNE", "OBST", "BEERE", "ZITRUS", "TRAUBE", "PFIRSICH", "NEKTARINE", "KIRSCH", "MELONE"]):
        return "Obst"
    return "Gemuese"


def derive_groesse_from_name(sortiment: str) -> str:
    """
    Leitet Kistengröße aus Sortimentsnamen ab.
    - "12" im Namen → S
    - "15" im Namen → M
    - "18" im Namen → L
    - "21" im Namen → XL
    """
    for num, size in [("21", "XL"), ("18", "L"), ("15", "M"), ("12", "S")]:
        if num in sortiment:
            return size
    return "M"  # Default


def get_default_preis_range(groesse: str) -> tuple:
    """
    Gibt Default-Zielpreise zurück wenn kein Festpreis existiert.
    """
    defaults = {
        'S': (12.0, 18.0),
        'M': (18.0, 28.0),
        'L': (25.0, 35.0),
        'XL': (30.0, 40.0)
    }
    return defaults.get(groesse, (15.0, 25.0))


def get_festpreis_range(db: Session, masterplan_id: int, groesse: str) -> tuple:
    """
    Holt Zielpreis-Range aus KistenFestpreis-Tabelle.
    Returns (zielpreis_min, zielpreis_max) or None wenn nicht gefunden.
    """
    from datetime import date
    heute = date.today().isoformat()

    festpreis = db.query(KistenFestpreis).filter(
        KistenFestpreis.masterplan_id == masterplan_id,
        KistenFestpreis.groesse == groesse,
        KistenFestpreis.ist_aktiv == True,
        KistenFestpreis.gueltig_ab <= heute,
        (KistenFestpreis.gueltig_bis == None) |
        (KistenFestpreis.gueltig_bis >= heute)
    ).first()

    if festpreis:
        return (festpreis.festpreis * 0.97, festpreis.festpreis * 1.03)
    return None


def normalisiere_kategorie(kat_raw: str) -> str:
    """
    Normalisiert Kategorienamen für Konsistenz.
    """
    konvertierung = {
        'Gemüse': 'Gemuese',
        'Gemüse MK': 'Gemuese',
        'Gemüse MK1': 'Gemuese',
        'Rohkost': 'Rohkost',
        'Rohkost MK1': 'Rohkost',
        'Salat': 'Salat',
        'Obst': 'Obst',
    }
    return konvertierung.get(kat_raw, kat_raw)


def import_masterplan_from_excel(db: Session, file_content: bytes) -> dict:
    """
    Importiert Masterplan-Matrix aus Kurts Excel-Format.

    Format:
    - Spalte 1: Sortiment (z.B. "OG12", "OG18-G", "RE15")
    - Ab Spalte 2: Slot-Namen als Header (z.B. "Gemüse 1", "Rohkost 2")
    - Zelle mit "x" = Slot aktiv, leer = nicht aktiv
    - KEINE Größe/Preis-Spalten!

    Größe wird aus Sortimentsnamen abgeleitet.
    Zielpreis kommt aus KistenFestpreis-Tabelle (nicht aus Excel).
    """
    try:
        df = pd.read_excel(BytesIO(file_content))

        if df.shape[1] < 2:
            return {
                "status": "fehler",
                "grund": "Excel muss mindestens 2 Spalten haben (Sortiment + Slots)"
            }

        imported_mp = 0
        imported_slots = 0
        updated_mp = 0
        errors = []

        # Spalte 1 = Sortiment, Rest = Slots
        sortiment_col = df.columns[0]
        slot_cols = df.columns[1:]

        for idx, row in df.iterrows():
            try:
                sortiment = str(row[sortiment_col]).strip()

                # Leere Zeilen und Header überspringen
                if not sortiment or sortiment.lower() == 'nan' or sortiment == 'Sortiment' or sortiment == 'Kistenname':
                    continue

                # Größe aus Sortimentsnamen ableiten
                groesse = derive_groesse_from_name(sortiment)

                # Masterplan finden oder anlegen
                mp = db.query(Masterplan).filter(Masterplan.name == sortiment).first()

                # Zielpreis-Range holen (aus Festpreistabelle oder Default)
                if mp and mp.masterplan_id:
                    preis_range = get_festpreis_range(db, mp.id, groesse)
                else:
                    # Für neue Masterplans: erstmal Default, wird nach Erstellung aktualisiert
                    preis_range = None

                if mp:
                    # Update bestehenden Masterplan
                    mp.groesse = groesse
                    mp.ist_aktiv = True
                    if preis_range:
                        mp.zielpreis_min = preis_range[0]
                        mp.zielpreis_max = preis_range[1]
                    updated_mp += 1
                else:
                    # Neu anlegen
                    zielpreis_min, zielpreis_max = preis_range if preis_range else get_default_preis_range(groesse)

                    mp = Masterplan(
                        name=sortiment,
                        beschreibung=f"{groesse}-Kiste (aus Excel importiert)",
                        groesse=groesse,
                        zielpreis_min=zielpreis_min,
                        zielpreis_max=zielpreis_max,
                        ist_aktiv=True
                    )
                    db.add(mp)
                    db.flush()  # ID zuweisen
                    imported_mp += 1

                # Zielpreis nach Erstellung neu holen (wenn Masterplan-ID existiert)
                if not preis_range and mp.id:
                    preis_range = get_festpreis_range(db, mp.id, groesse)
                    if preis_range:
                        mp.zielpreis_min = preis_range[0]
                        mp.zielpreis_max = preis_range[1]

                # Alte Slots löschen
                db.query(MasterplanSlot).filter(MasterplanSlot.masterplan_id == mp.id).delete()

                # Neue Slots aus den markierten Spalten anlegen
                slot_nr = 1
                for slot_name in slot_cols:
                    # Prüfen ob Slot markiert ("x", "X", "1", etc.)
                    marked = False
                    cell_val = row[slot_name]
                    if pd.notna(cell_val):
                        cell_str = str(cell_val).strip().lower()
                        if cell_str in ['x', '1', 'ja', 'yes', '✓']:
                            marked = True

                    if marked:
                        # Kategorie aus Slot-Name extrahieren
                        kat_raw = str(slot_name).strip()

                        # Nummer und Suffix entfernen
                        if ' ' in kat_raw:
                            kategorie = ' '.join(kat_raw.split()[:-1])  # Letztes Teil (Nummer) entfernen
                        else:
                            kategorie = kat_raw

                        kategorie = normalisiere_kategorie(kategorie)

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
            "neu_erstellt": imported_mp,
            "aktualisiert": updated_mp,
            "slots_gesamt": imported_slots,
            "fehler": errors
        }

    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_wochenquelle_from_excel(db: Session, file_content: bytes, kw: int, jahr: int) -> dict:
    """
    Importiert Wochenquelle aus Kurts Excel-Format.

    Format:
    - Spalte "Bezeichnung" = Slot-Name (z.B. "Gemüse 1", "Obst 1")
    - Spalte "Artikel" = SID (numerisch, kann leer sein)
    - Leere Zeilen werden ignoriert
    - KW und Jahr werden als Parameter übergeben (nicht in Excel enthalten)
    """
    try:
        df = pd.read_excel(BytesIO(file_content))

        # Spalten finden
        spalten = df.columns.tolist()
        bezeichnung_col = None
        artikel_col = None

        for col in spalten:
            col_sane = str(col).strip()
            if col_sane in ['Bezeichnung', 'Slot', 'Slot-Name']:
                bezeichnung_col = col
            elif col_sane in ['Artikel', 'SID', 'SID-Nr']:
                artikel_col = col

        if not bezeichnung_col or not artikel_col:
            return {
                "status": "fehler",
                "grund": "Excel muss Spalten 'Bezeichnung' und 'Artikel' enthalten"
            }

        imported = 0
        updated = 0
        errors = []

        # Alte Einträge für diese KW löschen
        db.query(WochenQuelle).filter(
            WochenQuelle.kalenderwoche == kw,
            WochenQuelle.jahr == jahr
        ).delete()

        for idx, row in df.iterrows():
            try:
                bezeichnung = str(row[bezeichnung_col]).strip()
                artikel_sid_val = row[artikel_col]

                # Leere Zeilen überspringen
                if not bezeichnung or bezeichnung.lower() == 'nan' or bezeichnung == 'Bezeichnung':
                    continue

                # Leere SID überspringen
                if pd.isna(artikel_sid_val) or artikel_sid_val == '':
                    continue

                # SID bereinigen
                sid = str(artikel_sid_val).strip()

                # Artikel in Datenbank finden
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                if not artikel:
                    errors.append(f"Zeile {idx + 2}: Artikel SID '{sid}' nicht gefunden")
                    continue

                # Wochenquelle eintragen
                wq = WochenQuelle(
                    kalenderwoche=kw,
                    jahr=jahr,
                    slot_bezeichnung=bezeichnung,
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
            "aktualisiert": updated,
            "kw": kw,
            "jahr": jahr,
            "fehler": errors
        }

    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


def import_tauschmuster_from_excel(db: Session, file_content: bytes, kw: int = None, jahr: int = None) -> dict:
    """
    Importiert Tauschmuster aus Kurts Excel-Format.

    Format:
    - Spalte D = SID (z.B. "11", "11m")
    - Spalte E = Artikelname (z.B. "DEUTSCHE Paprika gelb - kg")
    - Spalte F = Preis pro Einheit (z.B. 0.25, 0.8, 1)
    - Spalte G = Einheit ("Kilogramm" oder "Stück")

    Importiert GLEICHZEITIG:
    - ArtikelStamm (SID + Name + Einheit + Kategorie)
    - PreisPflege (aktueller Preis)

    Kategorie wird aus Artikelnamen abgeleitet.
    gueltig_ab = heutiges Datum
    """
    try:
        df = pd.read_excel(BytesIO(file_content))

        if df.shape[1] < 7:
            return {
                "status": "fehler",
                "grund": "Excel muss mindestens 7 Spalten haben (bis Spalte G)"
            }

        # Spalten D, E, F, G suchen
        spalten = df.columns.tolist()
        sid_col = None
        name_col = None
        preis_col = None
        einheit_col = None

        # Per Position (Index) suchen, da Spaltenüberschriften variieren können
        for i, col in enumerate(spalten):
            # Spalte D (Index 3)
            if i == 3:
                sid_col = col
            # Spalte E (Index 4)
            elif i == 4:
                name_col = col
            # Spalte F (Index 5)
            elif i == 5:
                preis_col = col
            # Spalte G (Index 6)
            elif i == 6:
                einheit_col = col

        if not all([sid_col, name_col, preis_col, einheit_col]):
            return {
                "status": "fehler",
                "grund": "Konnte Spalten D, E, F, G nicht identifizieren"
            }

        imported_artikel = 0
        updated_artikel = 0
        imported_preise = 0
        errors = []

        heute = datetime.now().strftime("%Y-%m-%d")

        for idx, row in df.iterrows():
            try:
                sid_val = row[sid_col]
                name_val = row[name_col]
                preis_val = row[preis_col]
                einheit_val = row[einheit_col]

                # Leere Zeilen überspringen
                if pd.isna(sid_val) or pd.isna(name_val):
                    continue

                # SID bereinigen
                sid = str(sid_val).strip()
                if sid.lower() == 'nan':
                    continue

                name = str(name_val).strip()
                if name.lower() == 'nan' or name == 'Artikelname':
                    continue

                # Einheit bereinigen
                einheit = str(einheit_val).strip() if pd.notna(einheit_val) else "Kilogramm"
                if einheit.lower() == 'nan' or not einheit:
                    einheit = "Kilogramm"

                # Einheit normalisieren
                if "st" in einheit.lower() and "kg" not in einheit.lower():
                    einheit = "Stueck"
                else:
                    einheit = "Kilogramm"

                # Preis bereinigen
                preis = None
                if pd.notna(preis_val):
                    try:
                        preis = float(preis_val)
                    except:
                        pass

                # Kategorie aus Artikelnamen ableiten
                kategorie = extract_kategorie_from_name(name)

                # Artikel anlegen oder aktualisieren
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()

                if artikel:
                    # Update
                    artikel.name = name
                    artikel.einheit = einheit
                    artikel.kategorie = kategorie
                    artikel.status = "aktiv"
                    updated_artikel += 1
                else:
                    # Neu
                    artikel = ArtikelStamm(
                        sid=sid,
                        name=name,
                        kategorie=kategorie,
                        einheit=einheit,
                        status="aktiv"
                    )
                    db.add(artikel)
                    imported_artikel += 1

                # Preis hinzufügen (wenn vorhanden)
                if preis is not None:
                    # Alten Preis deaktivieren (optional)
                    db.query(PreisPflege).filter(
                        PreisPflege.artikel_id == artikel.id,
                        PreisPflege.gueltig_bis == None
                    ).update({"gueltig_bis": heute})

                    neuer_preis = PreisPflege(
                        artikel_id=artikel.id,
                        preis_pro_einheit=preis,
                        gueltig_ab=heute,
                        gueltig_bis=None
                    )
                    db.add(neuer_preis)
                    imported_preise += 1

            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")

        db.commit()

        return {
            "status": "erfolg",
            "artikel_neu": imported_artikel,
            "artikel_aktualisiert": updated_artikel,
            "preise_importiert": imported_preise,
            "gesamt_artikel": imported_artikel + updated_artikel,
            "fehler": errors
        }

    except Exception as e:
        return {
            "status": "fehler",
            "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"
        }


# ==================== LEGACY IMPORT-FUNKTIONEN ====================
# Diese bleiben für Kompatibilität mit alten Tests

def import_artikel_from_excel(db: Session, file_content: bytes) -> dict:
    """Legacy: Importiert Artikel aus Excel (alte Struktur)."""
    # Alte Implementierung für Kompatibilität
    try:
        df = pd.read_excel(BytesIO(file_content))

        required_cols = ['SID', 'Name', 'Kategorie', 'Einheit']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {"status": "fehler", "grund": f"Fehlende Spalten: {', '.join(missing)}"}

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

                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()

                if artikel:
                    artikel.name = name
                    artikel.kategorie = kategorie
                    artikel.einheit = einheit
                    artikel.status = status
                    updated += 1
                else:
                    artikel = ArtikelStamm(
                        sid=sid, name=name, kategorie=kategorie,
                        einheit=einheit, status=status
                    )
                    db.add(artikel)
                    imported += 1

            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")

        db.commit()
        return {"status": "erfolg", "importiert": imported, "aktualisiert": updated, "fehler": errors}
    except Exception as e:
        return {"status": "fehler", "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"}

def import_historie_from_excel(db: Session, file_content: bytes) -> dict:
    """Legacy: Importiert historische Sortimente."""
    from datetime import datetime
    try:
        df = pd.read_excel(BytesIO(file_content))
        required_cols = ['KW', 'Jahr', 'Kistentyp', 'Slot', 'Artikel_SID', 'Menge']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {"status": "fehler", "grund": f"Fehlende Spalten: {', '.join(missing)}"}

        imported = 0
        errors = []
        grouped = df.groupby(['KW', 'Jahr', 'Kistentyp'])

        for (kw, jahr, kistentyp), group in grouped:
            try:
                masterplan = db.query(Masterplan).filter(Masterplan.name == kistentyp).first()
                if not masterplan:
                    errors.append(f"Masterplan '{kistentyp}' nicht gefunden")
                    continue

                artikel_zuweisungen = []
                mengen_zuweisungen = []
                gesamtpreis = 0.0

                for _, row in group.iterrows():
                    sid = str(row['Artikel_SID']).strip()
                    slot = str(row['Slot']).strip()
                    menge = float(row['Menge'])

                    artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                    if not artikel:
                        errors.append(f"Artikel SID '{sid}' nicht gefunden")
                        continue

                    artikel_zuweisungen.append({
                        "slot": slot, "artikel_id": artikel.id,
                        "artikel_name": artikel.name, "sid": sid
                    })
                    mengen_zuweisungen.append({
                        "artikel_id": artikel.id, "menge": menge, "einheit": artikel.einheit
                    })

                    if 'Preis' in row and pd.notna(row['Preis']):
                        gesamtpreis += float(row['Preis'])
                    else:
                        preis = db.query(PreisPflege).filter(
                            PreisPflege.artikel_id == artikel.id
                        ).order_by(PreisPflege.gueltig_ab.desc()).first()
                        if preis:
                            gesamtpreis += menge * preis.preis_pro_einheit

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
        return {"status": "erfolg", "importiert": imported, "fehler": errors}

    except Exception as e:
        return {"status": "fehler", "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"}


def import_preise_from_excel(db: Session, file_content: bytes) -> dict:
    """Legacy: Importiert Preise aus Excel."""
    try:
        df = pd.read_excel(BytesIO(file_content))

        required_cols = ['Artikel_SID', 'Preis', 'Gueltig_ab']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {"status": "fehler", "grund": f"Fehlende Spalten: {', '.join(missing)}"}

        imported = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                sid = str(row['Artikel_SID']).strip()
                preis = float(row['Preis'])
                gueltig_ab = str(row['Gueltig_ab'])
                gueltig_bis = str(row.get('Gueltig_bis', '')) if pd.notna(row.get('Gueltig_bis')) else None

                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                if not artikel:
                    errors.append(f"Zeile {idx + 2}: Artikel SID '{sid}' nicht gefunden")
                    continue

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
        return {"status": "erfolg", "importiert": imported, "fehler": errors}
    except Exception as e:
        return {"status": "fehler", "grund": f"Excel-Verarbeitung fehlgeschlagen: {str(e)}"}

def create_excel_template(template_type: str) -> bytes:
    """Erstellt Excel-Vorlagen."""
    wb = openpyxl.Workbook()
    ws = wb.active

    if template_type == "artikel":
        ws.title = "Artikel"
        ws.append(["SID", "Name", "Kategorie", "Einheit", "Status"])
        ws.append(["13", "Zucchini", "Gemuese", "Kilogramm", "aktiv"])

    elif template_type == "historie":
        ws.title = "Historie"
        ws.append(["KW", "Jahr", "Kistentyp", "Slot", "Artikel_SID", "Menge", "Preis"])
        ws.append([26, 2025, "OG12", "Gemuese 1", "13", 0.65, 1.89])

    elif template_type == "preise":
        ws.title = "Preise"
        ws.append(["Artikel_SID", "Preis", "Gueltig_ab", "Gueltig_bis"])
        ws.append(["13", 2.90, "2025-06-01", "2025-07-31"])

    elif template_type == "wochenquelle":
        ws.title = "Wochenquelle"
        ws.append(["Bezeichnung", "Artikel"])
        ws.append(["Gemuese 1", "13"])
        ws.append(["Gemuese 2", "241"])

    elif template_type == "masterplan":
        ws.title = "Masterplan"
        ws.append(["Sortiment", "Gemuese 1", "Gemuese 2", "Rohkost 1", "Salat 1", "Obst 1"])
        ws.append(["OG12", "x", "x", "x", "x", "x"])
        ws.append(["OG15", "x", "x", "x", "x", "x"])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
