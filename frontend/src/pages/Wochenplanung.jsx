import { useState, useEffect } from 'react';
import { Copy, Save, Upload, Download, Calendar } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { 
  getWochenquelle,
  setWochenquelle,
  kopiereWochenquelle,
  getArtikel,
  getMasterplaene,
  importWochenquelle,
  downloadVorlage
} from '../services/api';
import './Wochenplanung.css';

const Wochenplanung = () => {
  const [artikel, setArtikel] = useState([]);
  const [masterplaene, setMasterplaene] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Aktuelle Woche
  const getCurrentWeek = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const diff = now - start;
    const oneWeek = 1000 * 60 * 60 * 24 * 7;
    return Math.ceil(diff / oneWeek);
  };

  const [kw, setKw] = useState(getCurrentWeek());
  const [jahr, setJahr] = useState(new Date().getFullYear());
  const [slots, setSlots] = useState({});
  const [selectedMasterplan, setSelectedMasterplan] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (kw && jahr) {
      loadWochenquelle();
    }
  }, [kw, jahr]);

  const loadData = async () => {
    try {
      const [artikelData, masterplaeneData] = await Promise.all([
        getArtikel(),
        getMasterplaene()
      ]);
      setArtikel(artikelData.filter(a => a.status === 'aktiv'));
      setMasterplaene(masterplaeneData);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
      alert('Fehler beim Laden der Daten');
    } finally {
      setLoading(false);
    }
  };

  const loadWochenquelle = async () => {
    try {
      const data = await getWochenquelle(kw, jahr);
      const slotsObj = {};
      data.forEach(item => {
        slotsObj[item.slot_bezeichnung] = item.artikel_id;
      });
      setSlots(slotsObj);
    } catch (error) {
      console.error('Fehler beim Laden der Wochenquelle:', error);
      setSlots({});
    }
  };

  const getSlotDefinitions = () => {
    if (!selectedMasterplan) return [];
    const mp = masterplaene.find(m => m.id === parseInt(selectedMasterplan));
    if (!mp || !mp.slots) return [];
    return mp.slots.sort((a, b) => a.slot_nummer - b.slot_nummer);
  };

  const handleSlotChange = (slotBezeichnung, artikelId) => {
    setSlots({
      ...slots,
      [slotBezeichnung]: artikelId ? parseInt(artikelId) : null
    });
  };

  const handleSave = async () => {
    if (!selectedMasterplan) {
      alert('Bitte wählen Sie einen Masterplan aus');
      return;
    }

    setSaving(true);
    try {
      const eintraege = Object.entries(slots)
        .filter(([_, artikelId]) => artikelId)
        .map(([slot_bezeichnung, artikel_id]) => ({
          slot_bezeichnung,
          artikel_id
        }));

      await setWochenquelle(kw, jahr, eintraege);
      alert('Wochenplanung gespeichert!');
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleKopieren = async () => {
    const quellKw = prompt('Von welcher KW kopieren?', kw - 1);
    const quellJahr = prompt('Aus welchem Jahr?', jahr);
    
    if (!quellKw || !quellJahr) return;

    try {
      await kopiereWochenquelle(kw, jahr, parseInt(quellKw), parseInt(quellJahr));
      await loadWochenquelle();
      alert(`Erfolgreich von KW${quellKw}/${quellJahr} kopiert!`);
    } catch (error) {
      console.error('Fehler beim Kopieren:', error);
      alert(error.response?.data?.detail || 'Fehler beim Kopieren');
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await importWochenquelle(file);
      await loadWochenquelle();
      alert('Import erfolgreich!');
    } catch (error) {
      console.error('Import-Fehler:', error);
      alert('Fehler beim Import');
    }
    e.target.value = '';
  };

  const getArtikelByKategorie = (kategorie) => {
    return artikel.filter(a => a.kategorie === kategorie);
  };

  const getArtikelName = (artikelId) => {
    const a = artikel.find(art => art.id === artikelId);
    return a ? a.name : '';
  };

  const slotDefinitions = getSlotDefinitions();
  const filledSlots = Object.values(slots).filter(v => v).length;
  const totalSlots = slotDefinitions.length;

  if (loading) {
    return (
      <Layout title="Wochenplanung">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Wochenplanung">
      <div className="wochenplanung">
        {/* Header */}
        <div className="wochen-header">
          <div className="wochen-selector">
            <Calendar size={20} />
            <input
              type="number"
              min="1"
              max="53"
              value={kw}
              onChange={(e) => setKw(parseInt(e.target.value))}
              className="form-input week-input"
            />
            <span>/</span>
            <input
              type="number"
              min="2020"
              max="2030"
              value={jahr}
              onChange={(e) => setJahr(parseInt(e.target.value))}
              className="form-input year-input"
            />
          </div>

          <div className="wochen-actions">
            <button className="btn btn-secondary" onClick={handleKopieren}>
              <Copy size={18} />
              Von anderer Woche kopieren
            </button>
            <button className="btn btn-secondary" onClick={() => downloadVorlage('wochenquelle')}>
              <Download size={18} />
              Vorlage
            </button>
            <label className="btn btn-secondary">
              <Upload size={18} />
              Import
              <input type="file" accept=".xlsx,.xls" onChange={handleImport} style={{ display: 'none' }} />
            </label>
            <button 
              className="btn btn-primary" 
              onClick={handleSave}
              disabled={saving || !selectedMasterplan}
            >
              <Save size={18} />
              {saving ? 'Speichert...' : 'Speichern'}
            </button>
          </div>
        </div>

        {/* Masterplan Auswahl */}
        <div className="masterplan-selector card">
          <h3>Masterplan auswählen</h3>
          <select
            className="form-select"
            value={selectedMasterplan}
            onChange={(e) => setSelectedMasterplan(e.target.value)}
          >
            <option value="">Bitte Masterplan wählen...</option>
            {masterplaene.map(mp => (
              <option key={mp.id} value={mp.id}>
                {mp.name} ({mp.groesse}) - {mp.slots?.length || 0} Slots
              </option>
            ))}
          </select>
          {selectedMasterplan && (
            <p className="text-muted mt-sm">
              {filledSlots} von {totalSlots} Slots befüllt
            </p>
          )}
        </div>

        {/* Slot Grid */}
        {selectedMasterplan ? (
          <div className="slots-grid">
            {slotDefinitions.map(slot => {
              const artikelListe = getArtikelByKategorie(slot.kategorie);
              const selectedArtikel = slots[`Slot${slot.slot_nummer}`];
              
              return (
                <div key={slot.id} className="slot-card">
                  <div className="slot-header">
                    <span className="slot-nummer">#{slot.slot_nummer}</span>
                    <span className={`badge badge-${slot.kategorie.toLowerCase()}`}>
                      {slot.kategorie}
                    </span>
                    {slot.ist_pflicht && (
                      <span className="badge badge-error">Pflicht</span>
                    )}
                  </div>
                  <div className="slot-body">
                    <select
                      className="form-select"
                      value={selectedArtikel || ''}
                      onChange={(e) => handleSlotChange(`Slot${slot.slot_nummer}`, e.target.value)}
                    >
                      <option value="">-- Artikel wählen --</option>
                      {artikelListe.map(a => (
                        <option key={a.id} value={a.id}>
                          {a.name} ({a.einheit})
                        </option>
                      ))}
                    </select>
                    {selectedArtikel && (
                      <p className="selected-artikel">
                        ✓ {getArtikelName(selectedArtikel)}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-state">
            <Calendar size={64} />
            <h3>Kein Masterplan ausgewählt</h3>
            <p>Bitte wählen Sie oben einen Masterplan aus, um die Wochenplanung zu starten.</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Wochenplanung;
