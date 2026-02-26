"""
Paradieschen Kistengenerator — Seed-Daten
Erstellt die Datenbank mit echten Paradieschen-Artikeln,
Masterplaenen, Tauschmustern und 20 historischen Sortimenten.
"""
from database import engine, SessionLocal, Base
from models import (
    ArtikelStamm, Masterplan, MasterplanSlot, Tauschmuster,
    WochenQuelle, PreisPflege, HistorischeSortimente
)


def seed():
    """Hauptfunktion: Loescht alte Daten und fuellt alles neu."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # ============================================================
    # ARTIKEL-STAMM — Echte Paradieschen-Artikel mit SIDs
    # ============================================================
    artikel_daten = [
        # Gemuese
        ("13", "Zucchini", "Gemuese", "Kilogramm"),
        ("241", "Paprika gelb", "Gemuese", "Kilogramm"),
        ("22", "Fenchel", "Gemuese", "Kilogramm"),
        ("84", "Dicke Bohnen", "Gemuese", "Kilogramm"),
        ("23", "Gurke", "Gemuese", "Stueck"),
        ("43", "Mangold", "Gemuese", "Kilogramm"),
        ("20", "Rote Bete", "Gemuese", "Kilogramm"),
        ("32", "Lauch", "Gemuese", "Stueck"),
        ("11m", "Moehren", "Gemuese", "Kilogramm"),
        ("200", "Pastinaken", "Gemuese", "Kilogramm"),
        ("89", "Gruenkohl", "Gemuese", "Kilogramm"),
        ("3011", "Blumenkohl gross", "Gemuese", "Stueck"),
        ("304", "Blumenkohl klein", "Gemuese", "Stueck"),
        ("38", "Rosenkohl", "Gemuese", "Kilogramm"),
        ("382", "Rosenkohl klein", "Gemuese", "Kilogramm"),
        ("412", "Sellerie", "Gemuese", "Kilogramm"),
        ("42", "Staudensellerie", "Gemuese", "Stueck"),
        ("18", "Radieschen", "Gemuese", "Stueck"),
        ("209", "Rettich", "Gemuese", "Stueck"),
        ("44", "Wirsing", "Gemuese", "Kilogramm"),
        ("45", "Rotkohl", "Gemuese", "Kilogramm"),
        ("46", "Weisskohl", "Gemuese", "Kilogramm"),
        ("47", "Kohlrabi", "Gemuese", "Stueck"),
        ("48", "Brokkoli", "Gemuese", "Kilogramm"),
        ("49", "Porree", "Gemuese", "Stueck"),
        ("50", "Kartoffeln", "Gemuese", "Kilogramm"),
        # Rohkost
        ("197", "Kresse", "Rohkost", "Stueck"),
        ("24", "Paprika gruen", "Rohkost", "Kilogramm"),
        ("17041", "Sprossen Alfalfa", "Rohkost", "Stueck"),
        ("216", "Sprossen Mungobohne", "Rohkost", "Stueck"),
        ("18r", "Radieschen (Rohkost)", "Rohkost", "Stueck"),
        # Salat
        ("51", "Kopfsalat", "Salat", "Stueck"),
        ("52", "Eisbergsalat", "Salat", "Stueck"),
        ("53", "Feldsalat", "Salat", "Kilogramm"),
        ("54", "Rucola", "Salat", "Kilogramm"),
        ("55", "Batavia", "Salat", "Stueck"),
        ("56", "Eichblattsalat", "Salat", "Stueck"),
        ("57", "Romana", "Salat", "Stueck"),
        # Kraeuter
        ("201", "Petersilie glatt", "Kraeuter", "Stueck"),
        ("202", "Petersilie kraus", "Kraeuter", "Stueck"),
        ("203", "Petersilienwurzel", "Kraeuter", "Kilogramm"),
        # Obst
        ("60", "Aepfel", "Obst", "Kilogramm"),
        ("66", "Birnen", "Obst", "Kilogramm"),
        ("861", "Bananen", "Obst", "Kilogramm"),
        ("1991", "Orangen", "Obst", "Kilogramm"),
        ("65", "Trauben", "Obst", "Kilogramm"),
        ("87", "Kiwi", "Obst", "Kilogramm"),
        ("88", "Mandarinen", "Obst", "Kilogramm"),
        ("90", "Zitronen", "Obst", "Stueck"),
        ("91", "Mango", "Obst", "Stueck"),
        ("92", "Ananas", "Obst", "Stueck"),
    ]

    artikel_map = {}  # sid -> ArtikelStamm Objekt
    for sid, name, kategorie, einheit in artikel_daten:
        artikel = ArtikelStamm(sid=sid, name=name, kategorie=kategorie, einheit=einheit)
        db.add(artikel)
        db.flush()
        artikel_map[sid] = artikel

    print(f"  ✅ {len(artikel_map)} Artikel erstellt")

    # ============================================================
    # MASTERPLAENE — Die Kistentypen des Paradieschens
    # ============================================================
    # Masterplaene mit Zielpreis ±10% Toleranz
    # Format: (name, beschreibung, groesse, zielpreis)
    # min = zielpreis * 0.9, max = zielpreis * 1.1
    masterplaene_basis = [
        ("OG12", "Obst & Gemuese 12 - Standard", "S", 12.00),
        ("OG12-G", "Obst & Gemuese 12 - nur Gemuese", "S", 12.00),
        ("OG12-O", "Obst & Gemuese 12 - nur Obst", "S", 12.00),
        ("OG15", "Obst & Gemuese 15 - Mittel", "M", 15.00),
        ("OG18", "Obst & Gemuese 18 - Gross", "M", 18.00),
        ("OG18-G", "Obst & Gemuese 18 - nur Gemuese gross", "M", 18.00),
        ("OG21", "Obst & Gemuese 21 - Familien", "L", 21.00),
        ("OG21-G", "Obst & Gemuese 21 - Familien Gemuese", "L", 21.00),
    ]
    
    masterplaene = []
    for name, beschr, groesse, zielpreis in masterplaene_basis:
        preis_min = round(zielpreis * 0.9, 2)  # -10%
        preis_max = round(zielpreis * 1.1, 2)  # +10%
        masterplaene.append((name, beschr, groesse, preis_min, preis_max))

    mp_map = {}  # name -> Masterplan Objekt
    for name, beschr, groesse, pmin, pmax in masterplaene:
        mp = Masterplan(
            name=name, beschreibung=beschr, groesse=groesse,
            zielpreis_min=pmin, zielpreis_max=pmax
        )
        db.add(mp)
        db.flush()
        mp_map[name] = mp

    print(f"  ✅ {len(mp_map)} Masterplaene erstellt")

    # ============================================================
    # MASTERPLAN-SLOTS — Was in welcher Kiste drin sein muss
    # ============================================================
    # OG12: 3x Gemuese, 1x Rohkost, 1x Salat, 3x Obst = 8 Slots
    og12_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Rohkost", 1, True),
        ("Salat", 1, True),
        ("Obst", 1, True), ("Obst", 2, True), ("Obst", 3, True),
    ]
    for kat, nr, pflicht in og12_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG12"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG12-G: 5x Gemuese, 1x Rohkost, 1x Salat, 1x Kraeuter = 8 Slots
    og12g_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Gemuese", 4, True), ("Gemuese", 5, True),
        ("Rohkost", 1, True),
        ("Salat", 1, True),
        ("Kraeuter", 1, False),
    ]
    for kat, nr, pflicht in og12g_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG12-G"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG12-O: 5x Obst = 5 Slots (reine Obstkiste)
    og12o_slots = [
        ("Obst", 1, True), ("Obst", 2, True), ("Obst", 3, True),
        ("Obst", 4, True), ("Obst", 5, True),
    ]
    for kat, nr, pflicht in og12o_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG12-O"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG15: 4x Gemuese, 1x Rohkost, 1x Salat, 4x Obst = 10 Slots
    og15_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True), ("Gemuese", 4, True),
        ("Rohkost", 1, True),
        ("Salat", 1, True),
        ("Obst", 1, True), ("Obst", 2, True), ("Obst", 3, True), ("Obst", 4, True),
    ]
    for kat, nr, pflicht in og15_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG15"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG18: 5x Gemuese, 1x Rohkost, 1x Salat, 1x Kraeuter, 4x Obst = 12 Slots
    og18_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Gemuese", 4, True), ("Gemuese", 5, True),
        ("Rohkost", 1, True),
        ("Salat", 1, True),
        ("Kraeuter", 1, False),
        ("Obst", 1, True), ("Obst", 2, True), ("Obst", 3, True), ("Obst", 4, True),
    ]
    for kat, nr, pflicht in og18_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG18"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG18-G: 8x Gemuese, 1x Rohkost, 1x Salat, 1x Kraeuter = 11 Slots
    og18g_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Gemuese", 4, True), ("Gemuese", 5, True), ("Gemuese", 6, True),
        ("Gemuese", 7, True), ("Gemuese", 8, True),
        ("Rohkost", 1, True),
        ("Salat", 1, True),
        ("Kraeuter", 1, False),
    ]
    for kat, nr, pflicht in og18g_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG18-G"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG21: 6x Gemuese, 2x Rohkost, 1x Salat, 1x Kraeuter, 5x Obst = 15 Slots
    og21_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Gemuese", 4, True), ("Gemuese", 5, True), ("Gemuese", 6, True),
        ("Rohkost", 1, True), ("Rohkost", 2, True),
        ("Salat", 1, True),
        ("Kraeuter", 1, False),
        ("Obst", 1, True), ("Obst", 2, True), ("Obst", 3, True),
        ("Obst", 4, True), ("Obst", 5, True),
    ]
    for kat, nr, pflicht in og21_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG21"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    # OG21-G: 10x Gemuese, 2x Rohkost, 1x Salat, 1x Kraeuter = 14 Slots
    og21g_slots = [
        ("Gemuese", 1, True), ("Gemuese", 2, True), ("Gemuese", 3, True),
        ("Gemuese", 4, True), ("Gemuese", 5, True), ("Gemuese", 6, True),
        ("Gemuese", 7, True), ("Gemuese", 8, True), ("Gemuese", 9, True),
        ("Gemuese", 10, True),
        ("Rohkost", 1, True), ("Rohkost", 2, True),
        ("Salat", 1, True),
        ("Kraeuter", 1, False),
    ]
    for kat, nr, pflicht in og21g_slots:
        db.add(MasterplanSlot(masterplan_id=mp_map["OG21-G"].id, kategorie=kat, slot_nummer=nr, ist_pflicht=pflicht))

    db.flush()
    print(f"  ✅ Masterplan-Slots erstellt")

    # ============================================================
    # TAUSCHMUSTER — Mengen-Ranges pro Artikel und Groesse
    # ============================================================
    # Format: (sid, groesse, sortimentsart, min, max, standard, einheit)
    tauschmuster_daten = [
        # Gemuese - Groesse S, Sortiment OG
        ("13", "S", "OG", 0.55, 0.75, 0.65, "Kilogramm"),    # Zucchini
        ("241", "S", "OG", 0.20, 0.30, 0.25, "Kilogramm"),   # Paprika gelb
        ("22", "S", "OG", 0.60, 0.80, 0.70, "Kilogramm"),    # Fenchel
        ("84", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Dicke Bohnen
        ("23", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Gurke
        ("43", "S", "OG", 0.30, 0.50, 0.40, "Kilogramm"),    # Mangold
        ("20", "S", "OG", 0.50, 0.70, 0.60, "Kilogramm"),    # Rote Bete
        ("32", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Lauch
        ("11m", "S", "OG", 0.70, 1.00, 0.85, "Kilogramm"),   # Moehren
        ("200", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),   # Pastinaken
        ("89", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Gruenkohl
        ("3011", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),        # Blumenkohl gross
        ("304", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),         # Blumenkohl klein
        ("38", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Rosenkohl
        ("412", "S", "OG", 0.50, 0.80, 0.65, "Kilogramm"),   # Sellerie
        ("42", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Staudensellerie
        ("18", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Radieschen
        ("209", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),         # Rettich
        ("44", "S", "OG", 0.50, 0.80, 0.65, "Kilogramm"),    # Wirsing
        ("45", "S", "OG", 0.50, 0.80, 0.65, "Kilogramm"),    # Rotkohl
        ("46", "S", "OG", 0.50, 0.80, 0.65, "Kilogramm"),    # Weisskohl
        ("47", "S", "OG", 1.0, 2.0, 1.0, "Stueck"),          # Kohlrabi
        ("48", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Brokkoli
        ("49", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Porree
        ("50", "S", "OG", 1.00, 1.50, 1.25, "Kilogramm"),    # Kartoffeln
        # Rohkost - Groesse S
        ("197", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),         # Kresse
        ("24", "S", "OG", 0.20, 0.30, 0.25, "Kilogramm"),    # Paprika gruen
        ("17041", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),       # Sprossen Alfalfa
        ("216", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),         # Sprossen Mungobohne
        ("18r", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),         # Radieschen Rohkost
        # Salat - Groesse S
        ("51", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Kopfsalat
        ("52", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Eisbergsalat
        ("53", "S", "OG", 0.10, 0.15, 0.125, "Kilogramm"),   # Feldsalat
        ("54", "S", "OG", 0.10, 0.15, 0.125, "Kilogramm"),   # Rucola
        ("55", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Batavia
        ("56", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Eichblattsalat
        ("57", "S", "OG", 1.0, 1.0, 1.0, "Stueck"),          # Romana
        # Obst - Groesse S
        ("60", "S", "OG", 0.80, 1.20, 1.00, "Kilogramm"),    # Aepfel
        ("66", "S", "OG", 0.50, 0.80, 0.65, "Kilogramm"),    # Birnen
        ("861", "S", "OG", 0.70, 1.00, 0.85, "Kilogramm"),   # Bananen
        ("1991", "S", "OG", 0.80, 1.20, 1.00, "Kilogramm"),  # Orangen
        ("65", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Trauben
        ("87", "S", "OG", 0.40, 0.60, 0.50, "Kilogramm"),    # Kiwi
        ("88", "S", "OG", 0.60, 1.00, 0.80, "Kilogramm"),    # Mandarinen
        ("90", "S", "OG", 1.0, 2.0, 1.0, "Stueck"),          # Zitronen
        # Groesse M — hoehere Mengen
        ("13", "M", "OG", 0.75, 1.00, 0.85, "Kilogramm"),    # Zucchini
        ("241", "M", "OG", 0.30, 0.45, 0.35, "Kilogramm"),   # Paprika gelb
        ("22", "M", "OG", 0.80, 1.10, 0.95, "Kilogramm"),    # Fenchel
        ("11m", "M", "OG", 1.00, 1.50, 1.25, "Kilogramm"),   # Moehren
        ("60", "M", "OG", 1.20, 1.80, 1.50, "Kilogramm"),    # Aepfel
        ("66", "M", "OG", 0.80, 1.20, 1.00, "Kilogramm"),    # Birnen
        ("861", "M", "OG", 1.00, 1.50, 1.25, "Kilogramm"),   # Bananen
        # Groesse L — noch hoehere Mengen
        ("13", "L", "OG", 1.00, 1.50, 1.25, "Kilogramm"),    # Zucchini
        ("241", "L", "OG", 0.45, 0.65, 0.55, "Kilogramm"),   # Paprika gelb
        ("11m", "L", "OG", 1.50, 2.00, 1.75, "Kilogramm"),   # Moehren
        ("60", "L", "OG", 1.80, 2.50, 2.15, "Kilogramm"),    # Aepfel
        ("861", "L", "OG", 1.50, 2.00, 1.75, "Kilogramm"),   # Bananen
    ]

    for sid, groesse, sort_art, min_m, max_m, std_m, einheit in tauschmuster_daten:
        if sid in artikel_map:
            db.add(Tauschmuster(
                artikel_id=artikel_map[sid].id, groesse=groesse,
                sortimentsart=sort_art, min_menge=min_m, max_menge=max_m,
                standard_menge=std_m, einheit=einheit
            ))

    db.flush()
    print(f"  ✅ {len(tauschmuster_daten)} Tauschmuster erstellt")

    # ============================================================
    # PREISE — Gueltig fuer KW24-26/2025 (Testpreise)
    # ============================================================
    preise_daten = {
        # Gemuese (EUR pro kg bzw. pro Stueck)
        "13": 2.90, "241": 4.50, "22": 3.20, "84": 4.80,
        "23": 0.90, "43": 3.50, "20": 2.40, "32": 1.20,
        "11m": 1.80, "200": 3.80, "89": 3.00, "3011": 2.50,
        "304": 1.80, "38": 5.50, "382": 4.80, "412": 2.60,
        "42": 1.90, "18": 1.20, "209": 1.50, "44": 1.80,
        "45": 1.60, "46": 1.40, "47": 1.30, "48": 4.20,
        "49": 1.50, "50": 1.50,
        # Rohkost
        "197": 1.10, "24": 3.80, "17041": 1.80, "216": 1.60,
        "18r": 1.20,
        # Salat
        "51": 1.20, "52": 1.10, "53": 12.00, "54": 10.00,
        "55": 1.30, "56": 1.20, "57": 1.40,
        # Kraeuter
        "201": 0.80, "202": 0.80, "203": 4.50,
        # Obst
        "60": 3.00, "66": 3.80, "861": 2.50, "1991": 2.20,
        "65": 5.50, "87": 4.00, "88": 3.20, "90": 0.50,
        "91": 2.50, "92": 2.80,
    }

    for sid, preis in preise_daten.items():
        if sid in artikel_map:
            db.add(PreisPflege(
                artikel_id=artikel_map[sid].id,
                preis_pro_einheit=preis,
                gueltig_ab="2025-06-01",
                gueltig_bis="2025-07-31"
            ))

    db.flush()
    print(f"  ✅ {len(preise_daten)} Preise erstellt")

    # ============================================================
    # WOCHEN-QUELLE — KW26/2025 als aktuelle Planungswoche
    # ============================================================
    quelle_kw26 = [
        ("Gemuese 1", "13"),     # Zucchini
        ("Gemuese 2", "241"),    # Paprika gelb
        ("Gemuese 3", "22"),     # Fenchel
        ("Rohkost 1", "18r"),    # Radieschen
        ("Salat 1", "51"),       # Kopfsalat
        ("Obst 1", "60"),        # Aepfel
        ("Obst 2", "66"),        # Birnen
        ("Obst 3", "861"),       # Bananen
    ]

    for slot, sid in quelle_kw26:
        if sid in artikel_map:
            db.add(WochenQuelle(
                kalenderwoche=26, jahr=2025,
                slot_bezeichnung=slot,
                artikel_id=artikel_map[sid].id
            ))

    db.flush()
    print(f"  ✅ Wochenquelle KW26/2025 erstellt")

    # ============================================================
    # HISTORISCHE SORTIMENTE — 20 vergangene Kisten zum Lernen
    # ============================================================
    historische_kisten = [
        # KW1-KW10/2024: Winter-Kisten (OG12)
        {
            "mp": "OG12", "kw": 1, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "11m", "menge": 0.85},
                {"slot": "Gemuese 2", "sid": "20", "menge": 0.60},
                {"slot": "Gemuese 3", "sid": "200", "menge": 0.50},
                {"slot": "Rohkost 1", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "53", "menge": 0.125},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "1991", "menge": 1.00},
                {"slot": "Obst 3", "sid": "87", "menge": 0.50},
            ],
            "preis": 13.42
        },
        {
            "mp": "OG12", "kw": 3, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "50", "menge": 1.25},
                {"slot": "Gemuese 2", "sid": "45", "menge": 0.65},
                {"slot": "Gemuese 3", "sid": "32", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "24", "menge": 0.25},
                {"slot": "Salat 1", "sid": "53", "menge": 0.125},
                {"slot": "Obst 1", "sid": "60", "menge": 1.10},
                {"slot": "Obst 2", "sid": "66", "menge": 0.70},
                {"slot": "Obst 3", "sid": "88", "menge": 0.80},
            ],
            "preis": 12.85
        },
        {
            "mp": "OG12", "kw": 5, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "11m", "menge": 0.90},
                {"slot": "Gemuese 2", "sid": "412", "menge": 0.65},
                {"slot": "Gemuese 3", "sid": "44", "menge": 0.60},
                {"slot": "Rohkost 1", "sid": "17041", "menge": 1.0},
                {"slot": "Salat 1", "sid": "52", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 0.90},
                {"slot": "Obst 2", "sid": "1991", "menge": 1.10},
                {"slot": "Obst 3", "sid": "861", "menge": 0.85},
            ],
            "preis": 13.10
        },
        {
            "mp": "OG12", "kw": 8, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "50", "menge": 1.30},
                {"slot": "Gemuese 2", "sid": "89", "menge": 0.50},
                {"slot": "Gemuese 3", "sid": "49", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "216", "menge": 1.0},
                {"slot": "Salat 1", "sid": "57", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "87", "menge": 0.45},
                {"slot": "Obst 3", "sid": "861", "menge": 0.90},
            ],
            "preis": 12.60
        },
        {
            "mp": "OG12", "kw": 10, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "11m", "menge": 0.80},
                {"slot": "Gemuese 2", "sid": "32", "menge": 1.0},
                {"slot": "Gemuese 3", "sid": "46", "menge": 0.70},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "55", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "66", "menge": 0.60},
                {"slot": "Obst 3", "sid": "1991", "menge": 0.90},
            ],
            "preis": 12.95
        },
        # KW12-KW16: Fruehling (OG12)
        {
            "mp": "OG12", "kw": 12, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "47", "menge": 1.0},
                {"slot": "Gemuese 2", "sid": "11m", "menge": 0.85},
                {"slot": "Gemuese 3", "sid": "18", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "861", "menge": 0.85},
                {"slot": "Obst 3", "sid": "88", "menge": 0.70},
            ],
            "preis": 12.50
        },
        {
            "mp": "OG12", "kw": 14, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.60},
                {"slot": "Gemuese 2", "sid": "47", "menge": 1.0},
                {"slot": "Gemuese 3", "sid": "18", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 0.90},
                {"slot": "Obst 2", "sid": "66", "menge": 0.65},
                {"slot": "Obst 3", "sid": "861", "menge": 0.80},
            ],
            "preis": 12.20
        },
        {
            "mp": "OG12", "kw": 16, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.65},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.25},
                {"slot": "Gemuese 3", "sid": "48", "menge": 0.45},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "56", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "66", "menge": 0.55},
                {"slot": "Obst 3", "sid": "861", "menge": 0.90},
            ],
            "preis": 13.75
        },
        # KW18-KW24: Sommer (OG12) — WICHTIG fuer Match!
        {
            "mp": "OG12", "kw": 18, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.70},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.25},
                {"slot": "Gemuese 3", "sid": "22", "menge": 0.70},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 0.95},
                {"slot": "Obst 2", "sid": "66", "menge": 0.60},
                {"slot": "Obst 3", "sid": "861", "menge": 0.85},
            ],
            "preis": 14.10
        },
        {
            "mp": "OG12", "kw": 20, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.65},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.25},
                {"slot": "Gemuese 3", "sid": "43", "menge": 0.40},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "66", "menge": 0.65},
                {"slot": "Obst 3", "sid": "1991", "menge": 0.90},
            ],
            "preis": 13.80
        },
        {
            "mp": "OG12", "kw": 22, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.65},
                {"slot": "Gemuese 2", "sid": "22", "menge": 0.70},
                {"slot": "Gemuese 3", "sid": "84", "menge": 0.50},
                {"slot": "Rohkost 1", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "52", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 0.90},
                {"slot": "Obst 2", "sid": "861", "menge": 0.90},
                {"slot": "Obst 3", "sid": "65", "menge": 0.45},
            ],
            "preis": 14.55
        },
        {
            "mp": "OG12", "kw": 24, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.70},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.30},
                {"slot": "Gemuese 3", "sid": "22", "menge": 0.65},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "66", "menge": 0.70},
                {"slot": "Obst 3", "sid": "861", "menge": 0.90},
            ],
            "preis": 14.39
        },
        # Einige OG15 Kisten
        {
            "mp": "OG15", "kw": 4, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "11m", "menge": 1.00},
                {"slot": "Gemuese 2", "sid": "50", "menge": 1.50},
                {"slot": "Gemuese 3", "sid": "20", "menge": 0.70},
                {"slot": "Gemuese 4", "sid": "32", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "24", "menge": 0.25},
                {"slot": "Salat 1", "sid": "53", "menge": 0.125},
                {"slot": "Obst 1", "sid": "60", "menge": 1.20},
                {"slot": "Obst 2", "sid": "1991", "menge": 1.20},
                {"slot": "Obst 3", "sid": "87", "menge": 0.50},
                {"slot": "Obst 4", "sid": "861", "menge": 1.00},
            ],
            "preis": 18.30
        },
        {
            "mp": "OG15", "kw": 20, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.85},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.35},
                {"slot": "Gemuese 3", "sid": "22", "menge": 0.90},
                {"slot": "Gemuese 4", "sid": "23", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.30},
                {"slot": "Obst 2", "sid": "66", "menge": 0.90},
                {"slot": "Obst 3", "sid": "861", "menge": 1.10},
                {"slot": "Obst 4", "sid": "65", "menge": 0.50},
            ],
            "preis": 19.20
        },
        # OG18 Kisten
        {
            "mp": "OG18", "kw": 6, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "50", "menge": 1.50},
                {"slot": "Gemuese 2", "sid": "11m", "menge": 1.20},
                {"slot": "Gemuese 3", "sid": "44", "menge": 0.80},
                {"slot": "Gemuese 4", "sid": "20", "menge": 0.70},
                {"slot": "Gemuese 5", "sid": "32", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "53", "menge": 0.15},
                {"slot": "Kraeuter 1", "sid": "201", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.50},
                {"slot": "Obst 2", "sid": "1991", "menge": 1.30},
                {"slot": "Obst 3", "sid": "87", "menge": 0.60},
                {"slot": "Obst 4", "sid": "861", "menge": 1.20},
            ],
            "preis": 22.50
        },
        {
            "mp": "OG18", "kw": 18, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.90},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.40},
                {"slot": "Gemuese 3", "sid": "22", "menge": 0.85},
                {"slot": "Gemuese 4", "sid": "23", "menge": 1.0},
                {"slot": "Gemuese 5", "sid": "43", "menge": 0.45},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Kraeuter 1", "sid": "202", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.40},
                {"slot": "Obst 2", "sid": "66", "menge": 1.00},
                {"slot": "Obst 3", "sid": "861", "menge": 1.30},
                {"slot": "Obst 4", "sid": "65", "menge": 0.55},
            ],
            "preis": 23.10
        },
        # OG21 Familien-Kisten
        {
            "mp": "OG21", "kw": 10, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "50", "menge": 2.00},
                {"slot": "Gemuese 2", "sid": "11m", "menge": 1.50},
                {"slot": "Gemuese 3", "sid": "20", "menge": 0.80},
                {"slot": "Gemuese 4", "sid": "44", "menge": 0.70},
                {"slot": "Gemuese 5", "sid": "32", "menge": 1.0},
                {"slot": "Gemuese 6", "sid": "412", "menge": 0.70},
                {"slot": "Rohkost 1", "sid": "24", "menge": 0.30},
                {"slot": "Rohkost 2", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "53", "menge": 0.15},
                {"slot": "Kraeuter 1", "sid": "201", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 2.00},
                {"slot": "Obst 2", "sid": "1991", "menge": 1.50},
                {"slot": "Obst 3", "sid": "87", "menge": 0.60},
                {"slot": "Obst 4", "sid": "861", "menge": 1.50},
                {"slot": "Obst 5", "sid": "66", "menge": 1.00},
            ],
            "preis": 27.80
        },
        {
            "mp": "OG21", "kw": 20, "jahr": 2024,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 1.20},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.50},
                {"slot": "Gemuese 3", "sid": "22", "menge": 1.00},
                {"slot": "Gemuese 4", "sid": "23", "menge": 1.0},
                {"slot": "Gemuese 5", "sid": "43", "menge": 0.50},
                {"slot": "Gemuese 6", "sid": "18", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Rohkost 2", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Kraeuter 1", "sid": "202", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 2.00},
                {"slot": "Obst 2", "sid": "66", "menge": 1.20},
                {"slot": "Obst 3", "sid": "861", "menge": 1.50},
                {"slot": "Obst 4", "sid": "65", "menge": 0.60},
                {"slot": "Obst 5", "sid": "88", "menge": 1.00},
            ],
            "preis": 28.50
        },
        # Noch zwei Sommer-OG12 (2023) fuer mehr Lernbasis
        {
            "mp": "OG12", "kw": 25, "jahr": 2023,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.70},
                {"slot": "Gemuese 2", "sid": "241", "menge": 0.25},
                {"slot": "Gemuese 3", "sid": "22", "menge": 0.75},
                {"slot": "Rohkost 1", "sid": "18r", "menge": 1.0},
                {"slot": "Salat 1", "sid": "51", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 0.95},
                {"slot": "Obst 2", "sid": "66", "menge": 0.60},
                {"slot": "Obst 3", "sid": "861", "menge": 0.85},
            ],
            "preis": 13.90
        },
        {
            "mp": "OG12", "kw": 26, "jahr": 2023,
            "artikel": [
                {"slot": "Gemuese 1", "sid": "13", "menge": 0.65},
                {"slot": "Gemuese 2", "sid": "22", "menge": 0.70},
                {"slot": "Gemuese 3", "sid": "23", "menge": 1.0},
                {"slot": "Rohkost 1", "sid": "197", "menge": 1.0},
                {"slot": "Salat 1", "sid": "55", "menge": 1.0},
                {"slot": "Obst 1", "sid": "60", "menge": 1.00},
                {"slot": "Obst 2", "sid": "861", "menge": 0.90},
                {"slot": "Obst 3", "sid": "65", "menge": 0.50},
            ],
            "preis": 14.20
        },
    ]

    for kiste in historische_kisten:
        # Artikel-Zuweisungen aufbauen
        art_zuweisungen = []
        mengen_zuweisungen = []
        for pos in kiste["artikel"]:
            sid = pos["sid"]
            if sid in artikel_map:
                art = artikel_map[sid]
                art_zuweisungen.append({
                    "slot": pos["slot"],
                    "artikel_id": art.id,
                    "artikel_name": art.name,
                    "sid": sid
                })
                mengen_zuweisungen.append({
                    "artikel_id": art.id,
                    "menge": pos["menge"],
                    "einheit": art.einheit
                })

        db.add(HistorischeSortimente(
            masterplan_id=mp_map[kiste["mp"]].id,
            kalenderwoche=kiste["kw"],
            jahr=kiste["jahr"],
            artikel_zuweisungen=art_zuweisungen,
            mengen_zuweisungen=mengen_zuweisungen,
            gesamtpreis=kiste["preis"]
        ))

    db.flush()
    print(f"  ✅ {len(historische_kisten)} historische Sortimente erstellt")

    # ============================================================
    # COMMIT
    # ============================================================
    db.commit()
    db.close()

    print("\n🎉 Seed-Daten komplett!")
    print(f"  📦 {len(artikel_map)} Artikel")
    print(f"  📋 {len(mp_map)} Masterplaene (OG12, OG15, OG18, OG21 + Varianten)")
    print(f"  📊 {len(tauschmuster_daten)} Tauschmuster")
    print(f"  💰 {len(preise_daten)} Preise")
    print(f"  📅 1 Wochenquelle (KW26/2025)")
    print(f"  📜 {len(historische_kisten)} Historische Sortimente")


if __name__ == "__main__":
    seed()
