#!/usr/bin/env python3
"""
Script zum Importieren der Masterplan-Daten aus Excel
"""
import sys
from pathlib import Path

# Backend-Pfad zum Python-Path hinzufügen
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from database import SessionLocal
from import_handler import import_masterplan_from_excel

def main():
    """Importiert Masterplan-Daten aus Excel-Datei."""
    
    excel_file = backend_path / "masterplan_import.xlsx"
    
    if not excel_file.exists():
        print(f"❌ Fehler: Datei nicht gefunden: {excel_file}")
        return 1
    
    print(f"📂 Lese Excel-Datei: {excel_file}")
    
    # Datei einlesen
    with open(excel_file, 'rb') as f:
        file_content = f.read()
    
    # Datenbank-Session erstellen
    db = SessionLocal()
    
    try:
        print("🔄 Importiere Masterplan-Daten...")
        result = import_masterplan_from_excel(db, file_content)
        
        print("\n" + "="*60)
        print("📊 IMPORT-ERGEBNIS")
        print("="*60)
        
        if result["status"] == "erfolg":
            print(f"✅ Status: ERFOLGREICH")
            print(f"📦 Neu erstellt: {result['neu_erstellt']} Masterplaene")
            print(f"🔄 Aktualisiert: {result['aktualisiert']} Masterplaene")
            print(f"🎯 Slots gesamt: {result['slots_gesamt']}")
            
            if result['fehler']:
                print(f"\n⚠️  Warnungen ({len(result['fehler'])}):")
                for fehler in result['fehler']:
                    print(f"   - {fehler}")
            else:
                print("\n✨ Keine Fehler!")
                
        else:
            print(f"❌ Status: FEHLER")
            print(f"💥 Grund: {result.get('grund', 'Unbekannter Fehler')}")
            
            if result.get('fehler'):
                print(f"\nDetails:")
                for fehler in result['fehler']:
                    print(f"   - {fehler}")
        
        print("="*60)
        
        return 0 if result["status"] == "erfolg" else 1
        
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
