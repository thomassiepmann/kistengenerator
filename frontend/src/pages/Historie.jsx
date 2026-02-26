import { useState, useEffect } from 'react';
import { Upload, Download, History, Eye } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { getHistorie, importHistorie, downloadVorlage } from '../services/api';
import './Historie.css';

const Historie = () => {
  const [historie, setHistorie] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterMasterplan, setFilterMasterplan] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    loadHistorie();
  }, []);

  const loadHistorie = async () => {
    try {
      const data = await getHistorie();
      setHistorie(data);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
      alert('Fehler beim Laden der Historie');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await importHistorie(file);
      await loadHistorie();
      alert('Import erfolgreich!');
    } catch (error) {
      console.error('Import-Fehler:', error);
      alert('Fehler beim Import');
    }
    e.target.value = '';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const getMasterplanNames = () => {
    const names = new Set(historie.map(h => `Masterplan ${h.masterplan_id}`));
    return Array.from(names);
  };

  const filteredHistorie = filterMasterplan
    ? historie.filter(h => `Masterplan ${h.masterplan_id}` === filterMasterplan)
    : historie;

  if (loading) {
    return (
      <Layout title="Historie">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Historie">
      <div className="historie">
        {/* Toolbar */}
        <div className="historie-toolbar">
          <div className="toolbar-left">
            <select
              className="form-select"
              value={filterMasterplan}
              onChange={(e) => setFilterMasterplan(e.target.value)}
            >
              <option value="">Alle Masterplaene</option>
              {getMasterplanNames().map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
            <p className="text-muted">
              {filteredHistorie.length} Einträge
            </p>
          </div>
          <div className="toolbar-right">
            <button className="btn btn-secondary" onClick={() => downloadVorlage('historie')}>
              <Download size={18} />
              Vorlage
            </button>
            <label className="btn btn-secondary">
              <Upload size={18} />
              Import
              <input type="file" accept=".xlsx,.xls" onChange={handleImport} style={{ display: 'none' }} />
            </label>
          </div>
        </div>

        {/* Tabelle */}
        <div className="historie-table-container">
          <table className="table">
            <thead>
              <tr>
                <th>KW/Jahr</th>
                <th>Masterplan</th>
                <th>Positionen</th>
                <th>Gesamtpreis</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistorie.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center text-muted">
                    Keine historischen Sortimente vorhanden
                  </td>
                </tr>
              ) : (
                filteredHistorie.map(h => (
                  <tr key={h.id}>
                    <td>
                      <strong>KW {h.kalenderwoche}/{h.jahr}</strong>
                    </td>
                    <td>Masterplan {h.masterplan_id}</td>
                    <td>{h.artikel_zuweisungen?.length || 0} Artikel</td>
                    <td>
                      <strong className="price-value">{formatPrice(h.gesamtpreis)}</strong>
                    </td>
                    <td>
                      <button 
                        className="btn-icon btn-icon-primary"
                        onClick={() => setSelectedEntry(h)}
                        title="Details anzeigen"
                      >
                        <Eye size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Detail Modal */}
        {selectedEntry && (
          <div className="modal-overlay" onClick={() => setSelectedEntry(null)}>
            <div className="modal modal-large" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>
                  Sortiment KW {selectedEntry.kalenderwoche}/{selectedEntry.jahr}
                </h2>
                <button className="modal-close" onClick={() => setSelectedEntry(null)}>&times;</button>
              </div>
              <div className="modal-body">
                <div className="detail-info">
                  <div className="info-item">
                    <span className="info-label">Masterplan:</span>
                    <span className="info-value">Masterplan {selectedEntry.masterplan_id}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Gesamtpreis:</span>
                    <span className="info-value price-value">
                      {formatPrice(selectedEntry.gesamtpreis)}
                    </span>
                  </div>
                </div>

                <h3>Artikel-Zuweisungen</h3>
                <div className="artikel-list">
                  {selectedEntry.artikel_zuweisungen?.map((artikel, index) => (
                    <div key={index} className="artikel-item">
                      <span className="artikel-slot">Slot {index + 1}</span>
                      <span className="artikel-name">{artikel}</span>
                    </div>
                  ))}
                </div>

                {selectedEntry.mengen_zuweisungen && selectedEntry.mengen_zuweisungen.length > 0 && (
                  <>
                    <h3>Mengen</h3>
                    <div className="mengen-list">
                      {selectedEntry.mengen_zuweisungen.map((menge, index) => (
                        <div key={index} className="menge-item">
                          <span className="menge-slot">Slot {index + 1}</span>
                          <span className="menge-value">{menge}</span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setSelectedEntry(null)}>
                  Schließen
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {historie.length === 0 && (
          <div className="empty-state">
            <History size={64} />
            <h3>Keine Historie vorhanden</h3>
            <p>Historische Sortimente werden automatisch beim Freigeben von Kisten erstellt</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Historie;
