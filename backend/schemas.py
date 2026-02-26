"""
Paradieschen Kistengenerator — Pydantic Schemas
Request/Response Modelle fuer die API.
"""
from pydantic import BaseModel
from typing import Optional


# ============================================================
# ARTIKEL
# ============================================================

class ArtikelOut(BaseModel):
    id: int
    sid: str
    name: str
    kategorie: str
    einheit: str
    status: str
    model_config = {"from_attributes": True}


class ArtikelCreate(BaseModel):
    sid: str
    name: str
    kategorie: str
    einheit: str
    status: str = "aktiv"


class ArtikelUpdate(BaseModel):
    sid: Optional[str] = None
    name: Optional[str] = None
    kategorie: Optional[str] = None
    einheit: Optional[str] = None
    status: Optional[str] = None


# ============================================================
# MASTERPLAN
# ============================================================

class MasterplanSlotOut(BaseModel):
    id: int
    kategorie: str
    slot_nummer: int
    ist_pflicht: bool
    model_config = {"from_attributes": True}


class MasterplanOut(BaseModel):
    id: int
    name: str
    beschreibung: str
    groesse: str
    zielpreis_min: float
    zielpreis_max: float
    ist_aktiv: bool
    slots: list[MasterplanSlotOut] = []
    model_config = {"from_attributes": True}


class MasterplanKurzOut(BaseModel):
    id: int
    name: str
    groesse: str
    zielpreis_min: float
    zielpreis_max: float
    ist_aktiv: bool
    model_config = {"from_attributes": True}


# ============================================================
# PREISE
# ============================================================

class PreisOut(BaseModel):
    id: int
    artikel_id: int
    preis_pro_einheit: float
    gueltig_ab: str
    gueltig_bis: Optional[str] = None
    model_config = {"from_attributes": True}


class PreisCreate(BaseModel):
    artikel_id: int
    preis_pro_einheit: float
    gueltig_ab: str
    gueltig_bis: Optional[str] = None


class PreisUpdate(BaseModel):
    preis_pro_einheit: Optional[float] = None
    gueltig_bis: Optional[str] = None


# ============================================================
# KISTENPREISE (FESTPREISE)
# ============================================================

class KistenFestpreisOut(BaseModel):
    id: int
    masterplan_id: int
    groesse: str
    festpreis: float
    gueltig_ab: str
    gueltig_bis: Optional[str] = None
    ist_aktiv: bool
    model_config = {"from_attributes": True}


class KistenFestpreisCreate(BaseModel):
    masterplan_id: int
    groesse: str
    festpreis: float
    gueltig_ab: str
    gueltig_bis: Optional[str] = None
    ist_aktiv: bool = True


class KistenFestpreisUpdate(BaseModel):
    festpreis: Optional[float] = None
    gueltig_bis: Optional[str] = None
    ist_aktiv: Optional[bool] = None


# ============================================================
# WOCHENQUELLE
# ============================================================

class WochenQuelleOut(BaseModel):
    id: int
    kalenderwoche: int
    jahr: int
    slot_bezeichnung: str
    artikel_id: int
    model_config = {"from_attributes": True}


class WochenQuelleCreate(BaseModel):
    slot_bezeichnung: str
    artikel_id: int


# ============================================================
# GENERATOR
# ============================================================

class GeneratorRequest(BaseModel):
    typ: str                    # z.B. "OG12"
    groesse: str = "S"          # S, M, L
    kw: int                     # Kalenderwoche
    jahr: int                   # Jahr


class KistenPosition(BaseModel):
    slot: str
    artikel_id: int
    name: str
    sid: str
    menge: float
    einheit: str
    preis_einheit: float
    preis_position: float
    min_menge: float
    max_menge: float


class GeneratorResponse(BaseModel):
    status: str
    kiste_id: Optional[int] = None
    sortiment_typ: Optional[str] = None
    groesse: Optional[str] = None
    kw: Optional[int] = None
    jahr: Optional[int] = None
    inhalt: Optional[list[KistenPosition]] = None
    gesamtpreis: Optional[float] = None
    zielpreis_min: Optional[float] = None
    zielpreis_max: Optional[float] = None
    match_score: Optional[float] = None
    match_quelle: Optional[str] = None
    methode: Optional[str] = None
    uebereinstimmungen: Optional[int] = None
    ersetzungen: Optional[int] = None
    slot_count: Optional[int] = None
    optimierung_versuche: Optional[int] = None
    match_nr: Optional[int] = None
    grund: Optional[str] = None
    matches_versucht: Optional[int] = None


# ============================================================
# HISTORIE
# ============================================================

class HistorieOut(BaseModel):
    id: int
    masterplan_id: int
    kalenderwoche: int
    jahr: int
    artikel_zuweisungen: list
    mengen_zuweisungen: list
    gesamtpreis: float
    model_config = {"from_attributes": True}


# ============================================================
# GENERIERTE KISTEN
# ============================================================

class GenerierteKisteOut(BaseModel):
    id: int
    masterplan_id: int
    kalenderwoche: int
    jahr: int
    inhalt: list
    gesamtpreis: float
    optimierung_versuche: int
    match_score: float
    match_quelle: Optional[str] = None
    methode: Optional[str] = None
    status: str
    model_config = {"from_attributes": True}


class KisteUpdate(BaseModel):
    """Schema zum manuellen Bearbeiten einer generierten Kiste."""
    inhalt: list  # Aktualisierte Positionen
    gesamtpreis: float  # Neu berechneter Gesamtpreis
