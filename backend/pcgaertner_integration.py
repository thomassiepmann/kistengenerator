"""
PC-Gärtner Integration
Synchronisiert Daten zwischen PC-Gärtner Software und Kistengenerator

Module:
- Artikelmanager: https://pcgaertner.de/pc-gaertner-module/artikelmanager/
- Kundenstamm: https://pcgaertner.de/pc-gaertner-module/kundenstamm/
"""
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models import ArtikelStamm, PreisPflege
from typing import Optional, Dict, List


class PCGaertnerAPI:
    """
    Schnittstelle zur PC-Gärtner Software.
    
    Unterstützt verschiedene Integrationsmethoden:
    - REST API (wenn verfügbar)
    - CSV Import/Export
    - Datenbank-Direktzugriff
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, db_connection: str = None):
        """
        Initialisiert die PC-Gärtner Integration.
        
        Args:
            base_url: URL der PC-Gärtner API (falls vorhanden)
            api_key: API-Schlüssel für Authentifizierung
            db_connection: Datenbank-Connection-String (Alternative)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.db_connection = db_connection
        self.last_sync = None
        self.sync_log = []
    
    # ============================================================
    # ARTIKEL-SYNCHRONISATION
    # ============================================================
    
    def sync_artikel_from_pcgaertner(self, db: Session) -> Dict:
        """
        Synchronisiert Artikel aus PC-Gärtner Artikelmanager.
        
        Importiert:
        - Artikel-SID
        - Artikel-Name
        - Kategorie
        - Einheit (kg/Stück)
        
        Returns:
            Dict mit Sync-Status und Statistiken
        """
        try:
            # TODO: Implementierung abhängig von verfügbarer Schnittstelle
            # Beispiel für REST API:
            if self.base_url:
                return self._sync_artikel_via_api(db)
            # Beispiel für CSV:
            else:
                return self._sync_artikel_via_csv(db)
        except Exception as e:
            return {
                "status": "fehler",
                "fehler": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _sync_artikel_via_api(self, db: Session) -> Dict:
        """Synchronisiert Artikel über REST API."""
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        
        try:
            # Beispiel-Request (muss an echte API angepasst werden)
            response = requests.get(
                f"{self.base_url}/api/artikel",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            artikel_data = response.json()
            return self._import_artikel_data(db, artikel_data)
            
        except requests.RequestException as e:
            return {
                "status": "fehler",
                "fehler": f"API-Fehler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _sync_artikel_via_csv(self, db: Session, csv_path: str = None) -> Dict:
        """
        Synchronisiert Artikel über CSV-Import.
        
        CSV-Format (Beispiel):
        SID;Name;Kategorie;Einheit
        13;Zucchini;Gemuese;Kilogramm
        241;Paprika gelb;Gemuese;Kilogramm
        """
        # Placeholder für CSV-Import
        return {
            "status": "info",
            "nachricht": "CSV-Import muss manuell über /api/import/artikel erfolgen",
            "timestamp": datetime.now().isoformat()
        }
    
    def _import_artikel_data(self, db: Session, artikel_data: List[Dict]) -> Dict:
        """Importiert Artikel-Daten in die Datenbank."""
        neu = 0
        aktualisiert = 0
        fehler = []
        
        for artikel_info in artikel_data:
            try:
                sid = artikel_info.get("sid") or artikel_info.get("SID")
                name = artikel_info.get("name") or artikel_info.get("Name")
                kategorie = artikel_info.get("kategorie") or artikel_info.get("Kategorie", "Gemuese")
                einheit = artikel_info.get("einheit") or artikel_info.get("Einheit", "Kilogramm")
                
                if not sid or not name:
                    fehler.append(f"Fehlende Daten: {artikel_info}")
                    continue
                
                # Prüfen ob Artikel existiert
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                
                if artikel:
                    # Aktualisieren
                    artikel.name = name
                    artikel.kategorie = kategorie
                    artikel.einheit = einheit
                    aktualisiert += 1
                else:
                    # Neu anlegen
                    artikel = ArtikelStamm(
                        sid=sid,
                        name=name,
                        kategorie=kategorie,
                        einheit=einheit,
                        status="aktiv"
                    )
                    db.add(artikel)
                    neu += 1
                    
            except Exception as e:
                fehler.append(f"Fehler bei {artikel_info}: {str(e)}")
        
        db.commit()
        self.last_sync = datetime.now()
        
        return {
            "status": "erfolg",
            "neu": neu,
            "aktualisiert": aktualisiert,
            "fehler": len(fehler),
            "fehler_details": fehler[:10],  # Nur erste 10 Fehler
            "timestamp": self.last_sync.isoformat()
        }
    
    # ============================================================
    # PREIS-SYNCHRONISATION
    # ============================================================
    
    def sync_preise_from_pcgaertner(self, db: Session) -> Dict:
        """
        Synchronisiert aktuelle Preise aus PC-Gärtner.
        
        Importiert:
        - Artikel-SID
        - Preis pro Einheit
        - Gültigkeitsdatum
        
        Returns:
            Dict mit Sync-Status
        """
        try:
            if self.base_url:
                return self._sync_preise_via_api(db)
            else:
                return self._sync_preise_via_csv(db)
        except Exception as e:
            return {
                "status": "fehler",
                "fehler": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _sync_preise_via_api(self, db: Session) -> Dict:
        """Synchronisiert Preise über REST API."""
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/preise",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            preise_data = response.json()
            return self._import_preise_data(db, preise_data)
            
        except requests.RequestException as e:
            return {
                "status": "fehler",
                "fehler": f"API-Fehler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _sync_preise_via_csv(self, db: Session) -> Dict:
        """Placeholder für CSV-Preis-Import."""
        return {
            "status": "info",
            "nachricht": "CSV-Import muss manuell über /api/import/preise erfolgen",
            "timestamp": datetime.now().isoformat()
        }
    
    def _import_preise_data(self, db: Session, preise_data: List[Dict]) -> Dict:
        """Importiert Preis-Daten in die Datenbank."""
        neu = 0
        aktualisiert = 0
        fehler = []
        
        for preis_info in preise_data:
            try:
                sid = preis_info.get("sid") or preis_info.get("SID")
                preis = preis_info.get("preis") or preis_info.get("Preis")
                gueltig_ab = preis_info.get("gueltig_ab", datetime.now().strftime("%Y-%m-%d"))
                
                if not sid or preis is None:
                    fehler.append(f"Fehlende Daten: {preis_info}")
                    continue
                
                # Artikel finden
                artikel = db.query(ArtikelStamm).filter(ArtikelStamm.sid == sid).first()
                if not artikel:
                    fehler.append(f"Artikel {sid} nicht gefunden")
                    continue
                
                # Neuen Preis anlegen
                neuer_preis = PreisPflege(
                    artikel_id=artikel.id,
                    preis_pro_einheit=float(preis),
                    gueltig_ab=gueltig_ab,
                    gueltig_bis=None
                )
                db.add(neuer_preis)
                neu += 1
                
            except Exception as e:
                fehler.append(f"Fehler bei {preis_info}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "erfolg",
            "neu": neu,
            "aktualisiert": aktualisiert,
            "fehler": len(fehler),
            "fehler_details": fehler[:10],
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================================
    # SORTIMENT-EXPORT
    # ============================================================
    
    def export_sortiment_to_pcgaertner(self, db: Session, kiste_id: int) -> Dict:
        """
        Exportiert ein generiertes Sortiment an PC-Gärtner.
        
        Args:
            kiste_id: ID der generierten Kiste
            
        Returns:
            Dict mit Export-Status
        """
        from models import GenerierteKisten, Masterplan
        
        kiste = db.query(GenerierteKisten).filter(GenerierteKisten.id == kiste_id).first()
        if not kiste:
            return {
                "status": "fehler",
                "fehler": "Kiste nicht gefunden"
            }
        
        masterplan = db.query(Masterplan).filter(Masterplan.id == kiste.masterplan_id).first()
        
        # Sortiment-Daten formatieren
        sortiment_data = {
            "sortiment_typ": masterplan.name if masterplan else "Unbekannt",
            "kalenderwoche": kiste.kalenderwoche,
            "jahr": kiste.jahr,
            "gesamtpreis": kiste.gesamtpreis,
            "positionen": [
                {
                    "sid": pos.get("sid"),
                    "name": pos.get("name"),
                    "menge": pos.get("menge"),
                    "einheit": pos.get("einheit"),
                    "preis_einheit": pos.get("preis_einheit"),
                    "preis_position": pos.get("preis_position")
                }
                for pos in kiste.inhalt
            ]
        }
        
        try:
            if self.base_url:
                return self._export_sortiment_via_api(sortiment_data)
            else:
                return self._export_sortiment_via_csv(sortiment_data)
        except Exception as e:
            return {
                "status": "fehler",
                "fehler": str(e)
            }
    
    def _export_sortiment_via_api(self, sortiment_data: Dict) -> Dict:
        """Exportiert Sortiment über REST API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/sortimente",
                json=sortiment_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "status": "erfolg",
                "nachricht": "Sortiment erfolgreich exportiert",
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            return {
                "status": "fehler",
                "fehler": f"API-Fehler: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _export_sortiment_via_csv(self, sortiment_data: Dict) -> Dict:
        """Exportiert Sortiment als CSV (wird über /api/kiste/{id}/export/csv gemacht)."""
        return {
            "status": "info",
            "nachricht": "CSV-Export über /api/kiste/{id}/export/csv verfügbar",
            "sortiment_typ": sortiment_data.get("sortiment_typ"),
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================================
    # STATUS & KONFIGURATION
    # ============================================================
    
    def get_integration_status(self) -> Dict:
        """
        Gibt den aktuellen Status der Integration zurück.
        
        Returns:
            Dict mit Status-Informationen
        """
        return {
            "konfiguriert": bool(self.base_url or self.db_connection),
            "api_verfuegbar": bool(self.base_url),
            "db_verfuegbar": bool(self.db_connection),
            "letzte_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_methode": "API" if self.base_url else "CSV/Manuell",
            "timestamp": datetime.now().isoformat()
        }
    
    def test_connection(self) -> Dict:
        """
        Testet die Verbindung zu PC-Gärtner.
        
        Returns:
            Dict mit Test-Ergebnis
        """
        if self.base_url:
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                response = requests.get(
                    f"{self.base_url}/api/status",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                return {
                    "status": "erfolg",
                    "verbindung": "OK",
                    "nachricht": "Verbindung zu PC-Gärtner erfolgreich",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "status": "fehler",
                    "verbindung": "FEHLER",
                    "fehler": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "status": "info",
                "verbindung": "Nicht konfiguriert",
                "nachricht": "Keine API-URL konfiguriert. Nutzen Sie CSV-Import/Export.",
                "timestamp": datetime.now().isoformat()
            }


# ============================================================
# GLOBALE INSTANZ (wird in main.py initialisiert)
# ============================================================

# Wird beim Start der App initialisiert
pcgaertner_api: Optional[PCGaertnerAPI] = None


def init_pcgaertner_integration(base_url: str = None, api_key: str = None):
    """
    Initialisiert die PC-Gärtner Integration.
    
    Wird beim Start der App aufgerufen (in main.py).
    """
    global pcgaertner_api
    pcgaertner_api = PCGaertnerAPI(base_url=base_url, api_key=api_key)
    return pcgaertner_api
