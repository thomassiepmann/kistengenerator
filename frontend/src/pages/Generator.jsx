import { useState, useEffect } from 'react';
import { Play, Save, Download, RefreshCw, Edit3, CheckCircle } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { getMasterplaene, getWochenquelle } from '../services/api';
import api from '../services/api';
import './Generator.css';

export default function Generator() {
  const [masterplaene, setMasterplaene] = useState([]);
  const [selectedMasterplan, setSelectedMasterplan] = useState('');
  const [kw, setKw] = useState(26);
  const [jahr, setJahr] = useState(2025);
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [ergebnis, setErgebnis] = useState(null);
  const [batchErgebnisse, setBatchErgebnisse] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedInhalt, setEditedInhalt] = useState([]);

  useEffect(() => {
    loadMasterplaene();
  }, []);

  const loadMasterplaene = async () => {
    try {
      const data = await getMasterplaene();
      setMasterplaene(data);
      if (data.length > 0) {
        setSelectedMasterplan(data[0].name);
      }
    } catch (error) {
      console.error('Fehler beim Laden der Masterplaene:', error);
    }
  };

  const generiereEinzelkiste = async () => {
    if (!selectedMasterplan) {
      alert('Bitte Masterplan auswählen');
      return;
    }

    setLoading(true);
    setBatchErgebnisse(null);
    
    try {
      const mp = masterplaene.find(m => m.name === selectedMasterplan);
      const response = await api.post('/api/kiste/generieren', {
        typ: selectedMasterplan,
        groesse: mp.groesse,
        kw: kw,
        jahr: jahr
      });
      
      setErgebnis(response.data);
      setEditedInhalt(response.data.inhalt || []);
      setEditMode(false);
    } catch (error) {
      console.error('Fehler beim Generieren:', error);
      alert('Fehler beim Generieren der Kiste');
    } finally {
      setLoading(false);
    }
  };

  const generiereAlleSortimente = async () => {
    setBatchLoading(true);
    setErgebnis(null);
    
    try {
      const response = await api.post(`/api/kiste/generieren-alle?kw=${kw}&jahr=${jahr}`);
      setBatchErgebnisse(response.data);
    } catch (error) {
      console.error('Fehler beim Batch-Generieren:', error);
      alert('Fehler beim Generieren aller Sortimente');
    } finally {
      setBatchLoading(false);
    }
  };

  const exportCSV = async (kisteId) => {
    try {
      const baseURL = api.defaults.baseURL || '';
      window.open(`${baseURL}/api/kiste/${kisteId}/export/csv`, '_blank');
    } catch (error) {
      console.error('Fehler beim CSV-Export:', error);
    }
  };

  const speichereBearbeitung = async () => {
    if (!ergebnis || !ergebnis.kiste_id) return;

    try {
      const gesamtpreis = editedInhalt.reduce((sum, pos) => sum + pos.preis_position, 0);
      
      await api.put(`/api/kiste/${ergebnis.kiste_id}`, {
        inhalt: editedInhalt,
        gesamtpreis: gesamtpreis
      });
      
      alert('Änderungen gespeichert!');
      setEditMode(false);
      // Ergebnis aktualisieren
      setErgebnis({
        ...ergebnis,
        inhalt: editedInhalt,
        gesamtpreis: gesamtpreis
      });
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert('Fehler beim Speichern');
    }
  };

  const updateMenge = (index, neueMenge) => {
    const updated = [...editedInhalt];
    updated[index].menge = parseFloat(neueMenge);
    updated[index].preis_position = updated[index].menge * updated[index].preis_einheit;
    setEditedInhalt(updated);
  };

  const getMatchingScorePercent = (score) => {
    return Math.round(score * 100);
  };

  const getStatusColor = (status) => {
    if (status === 'erfolg') return '#2d8a4e';
    if (status === 'preis_nicht_erreichbar') return '#d97706';
    return '#dc2626';
  };

  return (
    <Layout>
      <div className="generator-container">
        <div className="generator-header">
          <h1>🎯 Sortiment-Generator</h1>
          <p>Automatische Kistengenerierung mit historischem Matching</p>
        </div>

        {/* Steuerung */}
        <div className="generator-controls">
          <div className="control-group">
            <label>Masterplan</label>
            <select 
              value={selectedMasterplan} 
              onChange={(e) => setSelectedMasterplan(e.target.value)}
              disabled={loading || batchLoading}
            >
              {masterplaene.map(mp => (
                <option key={mp.id} value={mp.name}>
                  {mp.name} - {mp.beschreibung} ({mp.groesse})
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Kalenderwoche</label>
            <input 
              type="number" 
              value={kw} 
              onChange={(e) => setKw(parseInt(e.target.value))}
              min="1" 
              max="53"
              disabled={loading || batchLoading}
            />
          </div>

          <div className="control-group">
            <label>Jahr</label>
            <input 
              type="number" 
              value={jahr} 
              onChange={(e) => setJahr(parseInt(e.target.value))}
              min="2020" 
              max="2030"
              disabled={loading || batchLoading}
            />
          </div>

          <button 
            className="btn-primary" 
            onClick={generiereEinzelkiste}
            disabled={loading || batchLoading}
          >
            <Play size={18} />
            {loading ? 'Generiere...' : 'Sortiment generieren'}
          </button>

          <button 
            className="btn-batch" 
            onClick={generiereAlleSortimente}
            disabled={loading || batchLoading}
          >
            <RefreshCw size={18} />
            {batchLoading ? 'Generiere alle...' : 'ALLE Sortimente generieren'}
          </button>
        </div>

        {/* Einzelergebnis */}
        {ergebnis && ergebnis.status === 'erfolg' && (
          <div className="ergebnis-container">
            <div className="ergebnis-header">
              <h2>✅ {ergebnis.sortiment_typ} - KW{ergebnis.kw}/{ergebnis.jahr}</h2>
              <div className="ergebnis-actions">
                {!editMode && (
                  <>
                    <button className="btn-secondary" onClick={() => setEditMode(true)}>
                      <Edit3 size={16} />
                      Mengen anpassen
                    </button>
                    <button className="btn-secondary" onClick={() => exportCSV(ergebnis.kiste_id)}>
                      <Download size={16} />
                      Als CSV exportieren
                    </button>
                  </>
                )}
                {editMode && (
                  <>
                    <button className="btn-primary" onClick={speichereBearbeitung}>
                      <Save size={16} />
                      Speichern
                    </button>
                    <button className="btn-secondary" onClick={() => {
                      setEditMode(false);
                      setEditedInhalt(ergebnis.inhalt);
                    }}>
                      Abbrechen
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Matching-Info */}
            <div className="matching-info">
              <div className="matching-score">
                <span className="score-label">Matching-Score:</span>
                <span className="score-value">{getMatchingScorePercent(ergebnis.match_score)}%</span>
                <span className="score-source">({ergebnis.match_quelle})</span>
              </div>
              <div className="matching-details">
                <span>✓ {ergebnis.uebereinstimmungen} Übereinstimmungen</span>
                <span>↔ {ergebnis.ersetzungen} Ersetzungen</span>
                <span>🔧 {ergebnis.optimierung_versuche} Optimierungsschritte</span>
              </div>
            </div>

            {/* Sortiment-Tabelle */}
            <div className="sortiment-table-container">
              <table className="sortiment-table">
                <thead>
                  <tr>
                    <th>Slot</th>
                    <th>Artikel</th>
                    <th>SID</th>
                    <th>Menge</th>
                    <th>Einheit</th>
                    <th>Einzelpreis</th>
                    <th>Positionspreis</th>
                  </tr>
                </thead>
                <tbody>
                  {(editMode ? editedInhalt : ergebnis.inhalt).map((pos, idx) => (
                    <tr key={idx}>
                      <td>{pos.slot}</td>
                      <td><strong>{pos.name}</strong></td>
                      <td className="sid">{pos.sid}</td>
                      <td>
                        {editMode ? (
                          <input 
                            type="number" 
                            value={pos.menge}
                            onChange={(e) => updateMenge(idx, e.target.value)}
                            step="0.05"
                            min={pos.min_menge}
                            max={pos.max_menge}
                            className="menge-input"
                          />
                        ) : (
                          pos.menge
                        )}
                      </td>
                      <td>{pos.einheit}</td>
                      <td>{pos.preis_einheit.toFixed(2)} €</td>
                      <td className="preis-position">{pos.preis_position.toFixed(2)} €</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="gesamt-row">
                    <td colSpan="6"><strong>GESAMTPREIS</strong></td>
                    <td className="gesamt-preis">
                      <strong>
                        {editMode 
                          ? editedInhalt.reduce((sum, p) => sum + p.preis_position, 0).toFixed(2)
                          : ergebnis.gesamtpreis.toFixed(2)
                        } €
                      </strong>
                    </td>
                  </tr>
                  <tr className="zielpreis-row">
                    <td colSpan="6">Zielpreis-Rahmen</td>
                    <td className="zielpreis">
                      {ergebnis.zielpreis_min.toFixed(2)} € - {ergebnis.zielpreis_max.toFixed(2)} €
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Methode */}
            <div className="methode-info">
              <strong>Methode:</strong> {ergebnis.methode}
            </div>
          </div>
        )}

        {/* Batch-Ergebnisse */}
        {batchErgebnisse && (
          <div className="batch-ergebnisse">
            <h2>📦 Alle Sortimente für KW{batchErgebnisse.kw}/{batchErgebnisse.jahr}</h2>
            <div className="batch-summary">
              <span className="success">✅ {batchErgebnisse.generiert} erfolgreich</span>
              {batchErgebnisse.fehler > 0 && (
                <span className="error">❌ {batchErgebnisse.fehler} Fehler</span>
              )}
            </div>

            <div className="batch-grid">
              {batchErgebnisse.ergebnisse.map((erg, idx) => (
                <div key={idx} className="batch-card">
                  <div className="batch-card-header">
                    <h3>{erg.masterplan}</h3>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(erg.status) }}
                    >
                      {erg.status}
                    </span>
                  </div>
                  <div className="batch-card-body">
                    <div className="batch-info-row">
                      <span>Gesamtpreis:</span>
                      <strong>{erg.gesamtpreis?.toFixed(2)} €</strong>
                    </div>
                    <div className="batch-info-row">
                      <span>Matching:</span>
                      <strong>{getMatchingScorePercent(erg.match_score)}%</strong>
                    </div>
                    <div className="batch-methode">
                      {erg.methode}
                    </div>
                  </div>
                  {erg.kiste_id && (
                    <button 
                      className="btn-export-small"
                      onClick={() => exportCSV(erg.kiste_id)}
                    >
                      <Download size={14} />
                      CSV
                    </button>
                  )}
                </div>
              ))}
            </div>

            {batchErgebnisse.fehler_details && batchErgebnisse.fehler_details.length > 0 && (
              <div className="fehler-liste">
                <h3>⚠️ Fehler</h3>
                {batchErgebnisse.fehler_details.map((f, idx) => (
                  <div key={idx} className="fehler-item">
                    <strong>{f.masterplan}:</strong> {f.fehler}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Fehler-Anzeige */}
        {ergebnis && ergebnis.status !== 'erfolg' && (
          <div className="error-container">
            <h3>⚠️ Generierung nicht erfolgreich</h3>
            <p><strong>Status:</strong> {ergebnis.status}</p>
            <p><strong>Grund:</strong> {ergebnis.grund}</p>
            {ergebnis.matches_versucht && (
              <p>Es wurden {ergebnis.matches_versucht} historische Matches versucht.</p>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
