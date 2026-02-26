"""
Paradieschen Kistengenerator — Muster-Lernen
Extrahiert Muster aus historischen Sortimenten und findet
den besten Match fuer eine aktuelle Wochenquelle.

Das ist die KERNINTELLIGENZ des Systems:
"Wir lassen aus den bereits in der Vergangenheit geplanten
 Sortimenten Masterplaene generieren." — Chef-E-Mail
"""
from sqlalchemy.orm import Session
from models import (
    HistorischeSortimente, GelernteMasterplaene, Masterplan,
    WochenQuelle, ArtikelStamm
)


def extrahiere_muster_aus_historie(db: Session) -> dict:
    """
    Laedt alle historischen Sortimente und extrahiert daraus
    wiederverwendbare Muster (gelernte Masterplaene).

    Rueckgabe: {"extrahiert": int, "muster_gesamt": int}
    """
    # Alte gelernte Muster loeschen
    db.query(GelernteMasterplaene).delete()
    db.flush()

    historien = db.query(HistorischeSortimente).all()

    if not historien:
        return {"extrahiert": 0, "muster_gesamt": 0}

    # Fuer jedes historische Sortiment ein Muster extrahieren
    muster_zaehler = 0
    for hist in historien:
        # Kategorie-Muster extrahieren: Welche Kategorie in welchem Slot?
        artikel_muster = []
        for zuw in hist.artikel_zuweisungen:
            artikel = db.query(ArtikelStamm).filter(
                ArtikelStamm.id == zuw["artikel_id"]
            ).first()
            if artikel:
                artikel_muster.append({
                    "slot": zuw["slot"],
                    "kategorie": artikel.kategorie,
                    "artikel_name": artikel.name,
                    "artikel_id": artikel.id,
                    "sid": zuw.get("sid", artikel.sid)
                })

        # Mengen-Muster: Relative Verteilung zum Gesamtpreis
        mengen_muster = []
        for mzuw in hist.mengen_zuweisungen:
            mengen_muster.append({
                "artikel_id": mzuw["artikel_id"],
                "menge": mzuw["menge"],
                "einheit": mzuw["einheit"],
                "anteil_am_preis": round(mzuw["menge"] / max(hist.gesamtpreis, 0.01), 4)
            })

        gelernter_mp = GelernteMasterplaene(
            basis_masterplan_id=hist.masterplan_id,
            quell_historie_id=hist.id,
            artikel_muster=artikel_muster,
            mengen_muster=mengen_muster,
            haeufigkeit=1,
            durchschnittspreis=hist.gesamtpreis
        )
        db.add(gelernter_mp)
        muster_zaehler += 1

    db.commit()

    return {
        "extrahiert": muster_zaehler,
        "muster_gesamt": muster_zaehler
    }


def finde_besten_match(
    db: Session,
    aktuelle_quelle_artikel: list[dict],
    sortiment_typ: str,
    top_n: int = 5
) -> list[dict]:
    """
    Vergleicht die aktuelle Wochenquelle mit allen gelernten Masterplaenen
    und findet die besten Uebereinstimmungen.

    Args:
        aktuelle_quelle_artikel: Liste von Dicts mit
            {"slot": "Gemuese 1", "artikel_id": 13, "artikel_name": "Zucchini", "sid": "13"}
        sortiment_typ: z.B. "OG12"
        top_n: Anzahl der besten Treffer (default 5)

    Returns:
        Liste der Top-Matches, jeweils mit:
        - match_score (0.0 - 1.0)
        - uebereinstimmungen (welche Slots matchen)
        - ersetzungen (welche Slots ersetzt werden muessen)
        - historie_referenz (KW/Jahr)
        - gelernter_masterplan (das Objekt)
        - mengen_muster (die Mengenverteilung)
    """
    # Masterplan finden
    masterplan = db.query(Masterplan).filter(Masterplan.name == sortiment_typ).first()
    if not masterplan:
        return []

    # Alle gelernten Muster fuer diesen Masterplan-Typ laden
    gelernte = db.query(GelernteMasterplaene).filter(
        GelernteMasterplaene.basis_masterplan_id == masterplan.id
    ).all()

    if not gelernte:
        return []

    # Aktuelle Artikel als schnelles Lookup: slot -> artikel_id
    aktuelle_by_slot = {}
    aktuelle_artikel_ids = set()
    for qa in aktuelle_quelle_artikel:
        aktuelle_by_slot[qa["slot"]] = qa
        aktuelle_artikel_ids.add(qa["artikel_id"])

    matches = []

    for gmp in gelernte:
        # Historische Referenz laden
        hist = gmp.quell_historie
        if not hist:
            continue

        uebereinstimmungen = []
        ersetzungen = []
        slot_count = len(gmp.artikel_muster)

        for hist_pos in gmp.artikel_muster:
            slot = hist_pos["slot"]
            hist_artikel_id = hist_pos["artikel_id"]

            if slot in aktuelle_by_slot:
                akt = aktuelle_by_slot[slot]
                if akt["artikel_id"] == hist_artikel_id:
                    # Exakter Match: Gleicher Artikel im gleichen Slot
                    uebereinstimmungen.append({
                        "slot": slot,
                        "artikel_name": hist_pos["artikel_name"],
                        "typ": "exakt"
                    })
                elif hist_pos["kategorie"] == _get_kategorie_from_slot(slot):
                    # Kategorie-Match: Anderer Artikel, aber richtige Kategorie
                    ersetzungen.append({
                        "slot": slot,
                        "historisch": hist_pos["artikel_name"],
                        "aktuell": akt.get("artikel_name", "?"),
                        "typ": "kategorie_match"
                    })
                else:
                    ersetzungen.append({
                        "slot": slot,
                        "historisch": hist_pos["artikel_name"],
                        "aktuell": akt.get("artikel_name", "?"),
                        "typ": "ersetzung"
                    })
            else:
                # Slot nicht in aktueller Quelle — pruefen ob Artikel
                # trotzdem in der Quelle vorkommt (anderer Slot)
                if hist_artikel_id in aktuelle_artikel_ids:
                    uebereinstimmungen.append({
                        "slot": slot,
                        "artikel_name": hist_pos["artikel_name"],
                        "typ": "artikel_vorhanden"
                    })
                else:
                    ersetzungen.append({
                        "slot": slot,
                        "historisch": hist_pos["artikel_name"],
                        "aktuell": None,
                        "typ": "fehlt"
                    })

        # Match-Score berechnen
        if slot_count > 0:
            # Exakte Matches zaehlen voll, Kategorie-Matches halb
            score_punkte = 0
            for u in uebereinstimmungen:
                if u["typ"] == "exakt":
                    score_punkte += 1.0
                elif u["typ"] == "artikel_vorhanden":
                    score_punkte += 0.8
            for e in ersetzungen:
                if e["typ"] == "kategorie_match":
                    score_punkte += 0.3

            match_score = round(score_punkte / slot_count, 3)
        else:
            match_score = 0.0

        matches.append({
            "match_score": match_score,
            "uebereinstimmungen": uebereinstimmungen,
            "uebereinstimmungen_count": len(uebereinstimmungen),
            "ersetzungen": ersetzungen,
            "ersetzungen_count": len(ersetzungen),
            "slot_count": slot_count,
            "historie_referenz": f"KW{hist.kalenderwoche}/{hist.jahr}",
            "historie_id": hist.id,
            "gelernter_mp_id": gmp.id,
            "mengen_muster": gmp.mengen_muster,
            "artikel_muster": gmp.artikel_muster,
            "historischer_preis": gmp.durchschnittspreis
        })

    # Nach Score sortieren (beste zuerst)
    matches.sort(key=lambda m: m["match_score"], reverse=True)

    return matches[:top_n]


def lade_wochenquelle_als_artikel(db: Session, kw: int, jahr: int) -> list[dict]:
    """
    Hilfsfunktion: Laedt die Wochenquelle und gibt sie als
    Liste von Dicts zurueck (passend fuer finde_besten_match).
    """
    quellen = db.query(WochenQuelle).filter(
        WochenQuelle.kalenderwoche == kw,
        WochenQuelle.jahr == jahr
    ).all()

    result = []
    for q in quellen:
        artikel = db.query(ArtikelStamm).filter(
            ArtikelStamm.id == q.artikel_id
        ).first()
        if artikel:
            result.append({
                "slot": q.slot_bezeichnung,
                "artikel_id": artikel.id,
                "artikel_name": artikel.name,
                "sid": artikel.sid,
                "kategorie": artikel.kategorie
            })

    return result


def _get_kategorie_from_slot(slot_bezeichnung: str) -> str:
    """Extrahiert die Kategorie aus einer Slot-Bezeichnung."""
    # "Gemuese 1" -> "Gemuese", "Rohkost 1" -> "Rohkost"
    parts = slot_bezeichnung.rsplit(" ", 1)
    return parts[0] if parts else slot_bezeichnung
