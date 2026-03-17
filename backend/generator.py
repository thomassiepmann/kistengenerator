"""
Paradieschen Kistengenerator — Generator-Kernlogik

Ablauf (KORRIGIERTE Reihenfolge laut Chef):
1. Quelle laden (was ist diese Woche verfuegbar?)
2. Historischen Match suchen (HAUPTWEG — nicht Fallback!)
3. Besten Treffer verwenden + nicht-passende Artikel ersetzen
4. Aktuelle Preise einsetzen
5. Range-Feintuning wenn Preis nicht im Zielrahmen
6. Bei Misserfolg: Naechsten Treffer nehmen
7. Letzter Fallback: Statischer Masterplan
"""
from sqlalchemy.orm import Session
from models import (
    ArtikelStamm, Masterplan, MasterplanSlot, Tauschmuster,
    PreisPflege, GenerierteKisten, HistorischeSortimente,
    WochenQuelle, GelernteMasterplaene
)
from muster_lernen import (
    finde_besten_match, lade_wochenquelle_als_artikel,
    extrahiere_muster_aus_historie
)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def _lade_preis(db: Session, artikel_id: int) -> float:
    """Laedt den aktuellen Preis fuer einen Artikel. None wenn keiner da."""
    preis = db.query(PreisPflege).filter(
        PreisPflege.artikel_id == artikel_id
    ).order_by(PreisPflege.gueltig_ab.desc()).first()
    if preis:
        return preis.preis_pro_einheit
    return None


def _lade_tauschmuster(db: Session, artikel_id: int, groesse: str) -> dict:
    """Laedt das Tauschmuster (min/max/standard Menge) fuer einen Artikel."""
    tm = db.query(Tauschmuster).filter(
        Tauschmuster.artikel_id == artikel_id,
        Tauschmuster.groesse == groesse
    ).first()
    if tm:
        return {
            "min_menge": tm.min_menge,
            "max_menge": tm.max_menge,
            "standard_menge": tm.standard_menge or (tm.min_menge + tm.max_menge) / 2,
            "einheit": tm.einheit
        }
    return None


def _reduziere_mengen(positionen: list, zu_viel: float):
    """Reduziert Mengen bei teuersten kg-Artikeln (Stueck-Artikel bleiben fix)."""
    # Nur kg-Artikel die reduzierbar sind
    anpassbar = [p for p in positionen if not p["ist_stueck"] and p["menge"] > p["min_menge"]]
    # Nach Preis pro Einheit sortieren (teuerste zuerst)
    anpassbar.sort(key=lambda p: p["preis_einheit"], reverse=True)

    rest = zu_viel
    for p in anpassbar:
        if rest <= 0.01:
            break
        # Wie viel kann dieser Artikel maximal einsparen?
        reduzierbar = p["menge"] - p["min_menge"]
        schritt = 0.05  # 50g Schritte
        schritte_noetig = min(int(rest / (schritt * p["preis_einheit"])) + 1,
                              int(reduzierbar / schritt))
        if schritte_noetig > 0:
            reduktion = schritte_noetig * schritt
            reduktion = min(reduktion, reduzierbar)
            p["menge"] = round(p["menge"] - reduktion, 3)
            p["preis_position"] = round(p["menge"] * p["preis_einheit"], 2)
            rest -= reduktion * p["preis_einheit"]


def _erhoehe_mengen(positionen: list, zu_wenig: float):
    """Erhoeht Mengen bei guenstigsten kg-Artikeln (Stueck-Artikel bleiben fix)."""
    anpassbar = [p for p in positionen if not p["ist_stueck"] and p["menge"] < p["max_menge"]]
    # Nach Preis sortieren (guenstigste zuerst — mehr Menge fuer weniger Geld)
    anpassbar.sort(key=lambda p: p["preis_einheit"])

    rest = zu_wenig
    for p in anpassbar:
        if rest <= 0.01:
            break
        erhoehbar = p["max_menge"] - p["menge"]
        schritt = 0.05
        schritte_noetig = min(int(rest / (schritt * p["preis_einheit"])) + 1,
                              int(erhoehbar / schritt))
        if schritte_noetig > 0:
            erhoehung = schritte_noetig * schritt
            erhoehung = min(erhoehung, erhoehbar)
            p["menge"] = round(p["menge"] + erhoehung, 3)
            p["preis_position"] = round(p["menge"] * p["preis_einheit"], 2)
            rest -= erhoehung * p["preis_einheit"]


def _speichere_kiste(db: Session, masterplan, kw, jahr, ergebnis) -> GenerierteKisten:
    """Speichert die generierte Kiste in der Datenbank."""
    kiste = GenerierteKisten(
        masterplan_id=masterplan.id,
        kalenderwoche=kw,
        jahr=jahr,
        inhalt=ergebnis["inhalt"],
        gesamtpreis=ergebnis["gesamtpreis"],
        optimierung_versuche=ergebnis.get("optimierung_versuche", 0),
        match_score=ergebnis.get("match_score", 0.0),
        match_quelle=ergebnis.get("match_quelle", ""),
        methode=ergebnis.get("methode", ""),
        status="entwurf"
    )
    db.add(kiste)
    db.commit()
    db.refresh(kiste)
    return kiste


# ============================================================
# HAUPTFUNKTION
# ============================================================

def generiere_kiste(db: Session, sortiment_typ: str, groesse: str, kw: int, jahr: int) -> dict:
    """
    Hauptfunktion: Generiert eine vollstaendige Kiste.

    Args:
        sortiment_typ: z.B. "OG12"
        groesse: "S", "M" oder "L"
        kw: Kalenderwoche
        jahr: Jahr

    Returns:
        Dict mit allen Kisten-Informationen oder Fehlermeldung
    """
    # === SCHRITT 1: Masterplan und Quelle laden ===
    masterplan = db.query(Masterplan).filter(Masterplan.name == sortiment_typ).first()
    if not masterplan:
        return {"status": "fehler", "grund": f"Masterplan '{sortiment_typ}' nicht gefunden"}

    # Zielpreis aus KistenFestpreis-Tabelle laden
    from datetime import date
    heute = date.today().isoformat()
    festpreis_obj = db.query(KistenFestpreis).filter(
        KistenFestpreis.masterplan_id == masterplan.id,
        KistenFestpreis.groesse == groesse,
        KistenFestpreis.ist_aktiv == True,
        KistenFestpreis.gueltig_ab <= heute,
        (KistenFestpreis.gueltig_bis == None) |
        (KistenFestpreis.gueltig_bis >= heute)
    ).order_by(KistenFestpreis.gueltig_ab.desc()).first()

    if festpreis_obj:
        masterplan.zielpreis_min = festpreis_obj.festpreis * 0.97
        masterplan.zielpreis_max = festpreis_obj.festpreis * 1.03

    quelle_artikel = lade_wochenquelle_als_artikel(db, kw, jahr)
    if not quelle_artikel:
        return {"status": "fehler", "grund": f"Keine Wochenquelle fuer KW{kw}/{jahr} geplant"}

    # Sicherstellen dass Muster gelernt wurden
    muster_count = db.query(GelernteMasterplaene).count()
    if muster_count == 0:
        extrahiere_muster_aus_historie(db)

    # === SCHRITT 2: Historischen Match suchen (HAUPTWEG!) ===
    matches = finde_besten_match(db, quelle_artikel, sortiment_typ, top_n=5)

    # === SCHRITT 3-6: Treffer durchprobieren ===
    for match_nr, match in enumerate(matches):
        if match["match_score"] < 0.3:
            continue

        ergebnis = _versuche_kiste_aus_match(
            db, masterplan, groesse, kw, jahr, quelle_artikel, match
        )

        if ergebnis["status"] == "erfolg":
            ergebnis["match_nr"] = match_nr + 1
            ergebnis["methode"] = (
                f"Historischer Match ({match['historie_referenz']}) "
                f"+ Range-Feintuning, {ergebnis['optimierung_versuche']} Versuche"
            )
            kiste = _speichere_kiste(db, masterplan, kw, jahr, ergebnis)
            ergebnis["kiste_id"] = kiste.id
            return ergebnis

    # === SCHRITT 7: Fallback auf statischen Masterplan ===
    ergebnis = _versuche_kiste_statisch(
        db, masterplan, groesse, kw, jahr, quelle_artikel
    )

    if ergebnis["status"] == "erfolg":
        ergebnis["methode"] = "Statischer Masterplan + Range-Feintuning"
        kiste = _speichere_kiste(db, masterplan, kw, jahr, ergebnis)
        ergebnis["kiste_id"] = kiste.id
        return ergebnis

    return {
        "status": "manuell_erforderlich",
        "grund": "Kein Weg konnte den Zielpreis erreichen",
        "sortiment_typ": sortiment_typ,
        "zielpreis_min": masterplan.zielpreis_min,
        "zielpreis_max": masterplan.zielpreis_max,
        "matches_versucht": len(matches)
    }


# ============================================================
# KISTE AUS HISTORISCHEM MATCH
# ============================================================

def _versuche_kiste_aus_match(db, masterplan, groesse, kw, jahr, quelle_artikel, match):
    """Versucht aus einem historischen Match eine preisgerechte Kiste zu bauen."""
    positionen = []
    quelle_by_slot = {q["slot"]: q for q in quelle_artikel}
    mengen_by_id = {m["artikel_id"]: m for m in match["mengen_muster"]}

    for hist_pos in match["artikel_muster"]:
        slot = hist_pos["slot"]
        hist_artikel_id = hist_pos["artikel_id"]

        # Welchen Artikel verwenden?
        if slot in quelle_by_slot:
            akt = quelle_by_slot[slot]
            artikel_id = akt["artikel_id"]
            artikel_name = akt["artikel_name"]
        else:
            artikel_id = hist_artikel_id
            artikel_name = hist_pos["artikel_name"]

        # Menge vom historischen Muster
        hist_menge_info = mengen_by_id.get(hist_artikel_id, {})
        menge = hist_menge_info.get("menge", 0.5)

        artikel = db.query(ArtikelStamm).filter(ArtikelStamm.id == artikel_id).first()
        if not artikel:
            continue

        preis_info = _lade_preis(db, artikel_id)
        if preis_info is None:
            continue

        tm = _lade_tauschmuster(db, artikel_id, groesse)
        min_menge = tm["min_menge"] if tm else menge * 0.7
        max_menge = tm["max_menge"] if tm else menge * 1.3

        menge = max(min_menge, min(menge, max_menge))

        positionen.append({
            "slot": slot,
            "artikel_id": artikel_id,
            "name": artikel_name,
            "sid": artikel.sid,
            "menge": round(menge, 3),
            "einheit": artikel.einheit,
            "preis_einheit": preis_info,
            "preis_position": round(menge * preis_info, 2),
            "min_menge": min_menge,
            "max_menge": max_menge,
            "ist_stueck": artikel.einheit == "Stueck"
        })

    if not positionen:
        return {"status": "fehler", "grund": "Keine Positionen aufgebaut"}

    # Feintuning
    gesamtpreis = sum(p["preis_position"] for p in positionen)
    versuche = 0

    while versuche < 10:
        if masterplan.zielpreis_min <= gesamtpreis <= masterplan.zielpreis_max:
            break
        versuche += 1
        if gesamtpreis > masterplan.zielpreis_max:
            _reduziere_mengen(positionen, gesamtpreis - masterplan.zielpreis_max)
        elif gesamtpreis < masterplan.zielpreis_min:
            _erhoehe_mengen(positionen, masterplan.zielpreis_min - gesamtpreis)
        gesamtpreis = sum(p["preis_position"] for p in positionen)

    if not (masterplan.zielpreis_min <= gesamtpreis <= masterplan.zielpreis_max):
        return {"status": "preis_nicht_erreichbar", "gesamtpreis": gesamtpreis}

    inhalt = [{
        "slot": p["slot"], "artikel_id": p["artikel_id"], "name": p["name"],
        "sid": p["sid"], "menge": p["menge"], "einheit": p["einheit"],
        "preis_einheit": p["preis_einheit"], "preis_position": p["preis_position"],
        "min_menge": p["min_menge"], "max_menge": p["max_menge"]
    } for p in positionen]

    return {
        "status": "erfolg",
        "sortiment_typ": masterplan.name,
        "groesse": masterplan.groesse,
        "kw": kw, "jahr": jahr,
        "inhalt": inhalt,
        "gesamtpreis": round(gesamtpreis, 2),
        "zielpreis_min": masterplan.zielpreis_min,
        "zielpreis_max": masterplan.zielpreis_max,
        "match_score": match["match_score"],
        "match_quelle": match["historie_referenz"],
        "uebereinstimmungen": match["uebereinstimmungen_count"],
        "ersetzungen": match["ersetzungen_count"],
        "slot_count": match["slot_count"],
        "optimierung_versuche": versuche
    }


# ============================================================
# FALLBACK: STATISCHER MASTERPLAN
# ============================================================

def _versuche_kiste_statisch(db, masterplan, groesse, kw, jahr, quelle_artikel):
    """Fallback: Baut Kiste aus Masterplan-Slots + Quelle + Tauschmuster-Mittelwerte."""
    slots = db.query(MasterplanSlot).filter(
        MasterplanSlot.masterplan_id == masterplan.id
    ).order_by(MasterplanSlot.slot_nummer).all()

    quelle_by_slot = {q["slot"]: q for q in quelle_artikel}
    quelle_by_kat = {}
    for q in quelle_artikel:
        kat = q["kategorie"]
        if kat not in quelle_by_kat:
            quelle_by_kat[kat] = []
        quelle_by_kat[kat].append(q)

    positionen = []
    verwendete = set()

    for slot in slots:
        slot_bez = f"{slot.kategorie} {slot.slot_nummer}"
        artikel_info = quelle_by_slot.get(slot_bez)

        if not artikel_info and slot.kategorie in quelle_by_kat:
            for q in quelle_by_kat[slot.kategorie]:
                if q["artikel_id"] not in verwendete:
                    artikel_info = q
                    break

        if not artikel_info:
            continue

        artikel_id = artikel_info["artikel_id"]
        if artikel_id in verwendete:
            continue
        verwendete.add(artikel_id)

        artikel = db.query(ArtikelStamm).filter(ArtikelStamm.id == artikel_id).first()
        if not artikel:
            continue

        preis_info = _lade_preis(db, artikel_id)
        if preis_info is None:
            continue

        tm = _lade_tauschmuster(db, artikel_id, groesse)
        if tm:
            menge = tm["standard_menge"]
            min_menge = tm["min_menge"]
            max_menge = tm["max_menge"]
        else:
            menge = 1.0 if artikel.einheit == "Stueck" else 0.5
            min_menge = menge * 0.7
            max_menge = menge * 1.3

        positionen.append({
            "slot": slot_bez,
            "artikel_id": artikel_id,
            "name": artikel.name,
            "sid": artikel.sid,
            "menge": round(menge, 3),
            "einheit": artikel.einheit,
            "preis_einheit": preis_info,
            "preis_position": round(menge * preis_info, 2),
            "min_menge": min_menge,
            "max_menge": max_menge,
            "ist_stueck": artikel.einheit == "Stueck"
        })

    if not positionen:
        return {"status": "fehler", "grund": "Keine Positionen moeglich"}

    gesamtpreis = sum(p["preis_position"] for p in positionen)
    versuche = 0

    while versuche < 10:
        if masterplan.zielpreis_min <= gesamtpreis <= masterplan.zielpreis_max:
            break
        versuche += 1
        if gesamtpreis > masterplan.zielpreis_max:
            _reduziere_mengen(positionen, gesamtpreis - masterplan.zielpreis_max)
        elif gesamtpreis < masterplan.zielpreis_min:
            _erhoehe_mengen(positionen, masterplan.zielpreis_min - gesamtpreis)
        gesamtpreis = sum(p["preis_position"] for p in positionen)

    if not (masterplan.zielpreis_min <= gesamtpreis <= masterplan.zielpreis_max):
        return {"status": "preis_nicht_erreichbar", "gesamtpreis": gesamtpreis}

    inhalt = [{
        "slot": p["slot"], "artikel_id": p["artikel_id"], "name": p["name"],
        "sid": p["sid"], "menge": p["menge"], "einheit": p["einheit"],
        "preis_einheit": p["preis_einheit"], "preis_position": p["preis_position"],
        "min_menge": p["min_menge"], "max_menge": p["max_menge"]
    } for p in positionen]

    return {
        "status": "erfolg",
        "sortiment_typ": masterplan.name,
        "groesse": masterplan.groesse,
        "kw": kw, "jahr": jahr,
        "inhalt": inhalt,
        "gesamtpreis": round(gesamtpreis, 2),
        "zielpreis_min": masterplan.zielpreis_min,
        "zielpreis_max": masterplan.zielpreis_max,
        "match_score": 0.0,
        "match_quelle": "Statischer Masterplan",
        "uebereinstimmungen": 0,
        "ersetzungen": len(positionen),
        "slot_count": len(positionen),
        "optimierung_versuche": versuche
    }


# ============================================================
# KISTE FREIGEBEN
# ============================================================

def kiste_freigeben(db: Session, kiste_id: int) -> dict:
    """
    Gibt eine Kiste frei und speichert sie als neues historisches Sortiment.
    So lernt das System fuer die Zukunft!
    """
    kiste = db.query(GenerierteKisten).filter(GenerierteKisten.id == kiste_id).first()
    if not kiste:
        return {"status": "fehler", "grund": "Kiste nicht gefunden"}

    if kiste.status == "freigegeben":
        return {"status": "fehler", "grund": "Kiste bereits freigegeben"}

    # Status aendern
    kiste.status = "freigegeben"

    # Als historisches Sortiment speichern (LERNEFFEKT!)
    art_zuweisungen = []
    mengen_zuweisungen = []
    for pos in kiste.inhalt:
        art_zuweisungen.append({
            "slot": pos["slot"],
            "artikel_id": pos["artikel_id"],
            "artikel_name": pos["name"],
            "sid": pos["sid"]
        })
        mengen_zuweisungen.append({
            "artikel_id": pos["artikel_id"],
            "menge": pos["menge"],
            "einheit": pos["einheit"]
        })

    neues_hist = HistorischeSortimente(
        masterplan_id=kiste.masterplan_id,
        kalenderwoche=kiste.kalenderwoche,
        jahr=kiste.jahr,
        artikel_zuweisungen=art_zuweisungen,
        mengen_zuweisungen=mengen_zuweisungen,
        gesamtpreis=kiste.gesamtpreis
    )
    db.add(neues_hist)
    db.commit()

    return {
        "status": "freigegeben",
        "kiste_id": kiste.id,
        "historie_id": neues_hist.id,
        "nachricht": "Kiste freigegeben und in Historie gespeichert (Lerneffekt!)"
    }
