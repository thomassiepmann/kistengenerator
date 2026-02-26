"""
Paradieschen Kistengenerator — Datenmodell
Alle Tabellen fuer den vollstaendigen Generator-Workflow.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base


class ArtikelStamm(Base):
    """Alle Artikel mit Paradieschen-SID, Kategorie und Einheit."""
    __tablename__ = "artikel_stamm"

    id = Column(Integer, primary_key=True, index=True)
    sid = Column(String, unique=True, nullable=False)          # Paradieschen-ID z.B. "13"
    name = Column(String, nullable=False)                       # z.B. "Zucchini"
    kategorie = Column(String, nullable=False)                  # Gemuese, Obst, Rohkost, Salat, Kraeuter
    einheit = Column(String, default="Kilogramm")               # Kilogramm oder Stueck
    status = Column(String, default="aktiv")                    # aktiv, saisonende, inaktiv

    # Beziehungen
    preise = relationship("PreisPflege", back_populates="artikel")
    tauschmuster = relationship("Tauschmuster", back_populates="artikel")
    quell_eintraege = relationship("WochenQuelle", back_populates="artikel")


class Masterplan(Base):
    """Kistentypen mit Zielpreis-Rahmen. z.B. OG12, OG15, OG18."""
    __tablename__ = "masterplan"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)          # z.B. "OG12"
    beschreibung = Column(String, default="")
    groesse = Column(String, nullable=False)                    # S, M, L
    zielpreis_min = Column(Float, nullable=False)               # z.B. 10.00
    zielpreis_max = Column(Float, nullable=False)               # z.B. 15.00
    ist_aktiv = Column(Boolean, default=True)

    # Beziehungen
    slots = relationship("MasterplanSlot", back_populates="masterplan", order_by="MasterplanSlot.slot_nummer")
    historische_sortimente = relationship("HistorischeSortimente", back_populates="masterplan")
    generierte_kisten = relationship("GenerierteKisten", back_populates="masterplan")


class MasterplanSlot(Base):
    """Einzelne Slots eines Masterplans. z.B. OG12 hat 8 Slots."""
    __tablename__ = "masterplan_slot"

    id = Column(Integer, primary_key=True, index=True)
    masterplan_id = Column(Integer, ForeignKey("masterplan.id"), nullable=False)
    kategorie = Column(String, nullable=False)                  # Gemuese, Obst, Rohkost, Salat
    slot_nummer = Column(Integer, nullable=False)               # 1, 2, 3...
    ist_pflicht = Column(Boolean, default=True)

    masterplan = relationship("Masterplan", back_populates="slots")


class Tauschmuster(Base):
    """Mengen-Ranges pro Artikel, Groesse und Sortimentsart."""
    __tablename__ = "tauschmuster"

    id = Column(Integer, primary_key=True, index=True)
    artikel_id = Column(Integer, ForeignKey("artikel_stamm.id"), nullable=False)
    groesse = Column(String, nullable=False)                    # S, M, L
    sortimentsart = Column(String, default="OG")                # OG, RE, OOG
    min_menge = Column(Float, nullable=False)                   # z.B. 0.55 (kg) oder 1 (Stueck)
    max_menge = Column(Float, nullable=False)                   # z.B. 0.75 (kg) oder 1 (Stueck)
    standard_menge = Column(Float, nullable=True)               # Empfohlener Mittelwert
    einheit = Column(String, default="Kilogramm")

    artikel = relationship("ArtikelStamm", back_populates="tauschmuster")


class WochenQuelle(Base):
    """Welche Artikel sind in einer bestimmten KW verfuegbar?"""
    __tablename__ = "wochen_quelle"

    id = Column(Integer, primary_key=True, index=True)
    kalenderwoche = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    slot_bezeichnung = Column(String, nullable=False)           # z.B. "Gemuese 1"
    artikel_id = Column(Integer, ForeignKey("artikel_stamm.id"), nullable=False)

    artikel = relationship("ArtikelStamm", back_populates="quell_eintraege")


class PreisPflege(Base):
    """Woechentliche Preise pro Artikel."""
    __tablename__ = "preis_pflege"

    id = Column(Integer, primary_key=True, index=True)
    artikel_id = Column(Integer, ForeignKey("artikel_stamm.id"), nullable=False)
    preis_pro_einheit = Column(Float, nullable=False)           # EUR pro kg oder pro Stueck
    gueltig_ab = Column(String, nullable=False)                 # ISO-Datum "2025-06-01"
    gueltig_bis = Column(String, nullable=True)                 # NULL = unbefristet

    artikel = relationship("ArtikelStamm", back_populates="preise")


class KistenFestpreis(Base):
    """Festpreise fuer ganze Kisten (Masterplan + Groesse)."""
    __tablename__ = "kisten_festpreis"

    id = Column(Integer, primary_key=True, index=True)
    masterplan_id = Column(Integer, ForeignKey("masterplan.id"), nullable=False)
    groesse = Column(String, nullable=False)                    # S, M, L
    festpreis = Column(Float, nullable=False)                   # EUR z.B. 14.50
    gueltig_ab = Column(String, nullable=False)                 # ISO-Datum "2026-03-01"
    gueltig_bis = Column(String, nullable=True)                 # NULL = unbefristet
    ist_aktiv = Column(Boolean, default=True)

    masterplan = relationship("Masterplan")


class HistorischeSortimente(Base):
    """Vergangene Kisten-Zusammenstellungen — die Lern-Basis!"""
    __tablename__ = "historische_sortimente"

    id = Column(Integer, primary_key=True, index=True)
    masterplan_id = Column(Integer, ForeignKey("masterplan.id"), nullable=False)
    kalenderwoche = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    # JSON: [{"slot": "Gemuese 1", "artikel_id": 13, "artikel_name": "Zucchini"}, ...]
    artikel_zuweisungen = Column(JSON, nullable=False)
    # JSON: [{"artikel_id": 13, "menge": 0.65, "einheit": "Kilogramm"}, ...]
    mengen_zuweisungen = Column(JSON, nullable=False)
    gesamtpreis = Column(Float, nullable=False)

    masterplan = relationship("Masterplan", back_populates="historische_sortimente")


class GelernteMasterplaene(Base):
    """Aus der Historie extrahierte Muster."""
    __tablename__ = "gelernte_masterplaene"

    id = Column(Integer, primary_key=True, index=True)
    basis_masterplan_id = Column(Integer, ForeignKey("masterplan.id"), nullable=False)
    quell_historie_id = Column(Integer, ForeignKey("historische_sortimente.id"), nullable=True)
    artikel_muster = Column(JSON, nullable=False)               # Kategorie-Muster der Slots
    mengen_muster = Column(JSON, nullable=False)                # Mengen-Verteilung
    haeufigkeit = Column(Integer, default=1)                    # Wie oft kam dieses Muster vor
    durchschnittspreis = Column(Float, default=0.0)

    masterplan = relationship("Masterplan")
    quell_historie = relationship("HistorischeSortimente")


class GenerierteKisten(Base):
    """Vom Generator erstellte Kisten mit Status-Workflow."""
    __tablename__ = "generierte_kisten"

    id = Column(Integer, primary_key=True, index=True)
    masterplan_id = Column(Integer, ForeignKey("masterplan.id"), nullable=False)
    kalenderwoche = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    # JSON: [{"slot": "Gemuese 1", "artikel_id": 13, "name": "Zucchini",
    #          "menge": 0.65, "einheit": "Kilogramm", "preis_einheit": 2.90,
    #          "preis_position": 1.89}, ...]
    inhalt = Column(JSON, nullable=False)
    gesamtpreis = Column(Float, nullable=False)
    optimierung_versuche = Column(Integer, default=0)
    match_score = Column(Float, default=0.0)                    # 0.0 - 1.0
    match_quelle = Column(String, nullable=True)                # z.B. "KW20/2024"
    methode = Column(String, default="")                        # z.B. "Historischer Match + Feintuning"
    status = Column(String, default="entwurf")                  # entwurf, freigegeben, verworfen

    masterplan = relationship("Masterplan", back_populates="generierte_kisten")
