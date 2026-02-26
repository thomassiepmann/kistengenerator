import { useState, useEffect } from 'react';
import { Upload, Download, Layers } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { getMasterplaene, importMasterplan, downloadVorlage } from '../services/api';
import './Masterplaene.css';

const Masterplaene = () => {
  const [masterplaene, setMasterplaene] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    loadMasterplaene();
  }, []);

  const loadMasterplaene = async () => {
    try {
      const data = await getMasterplaene();
      setMasterplaene(data);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
      alert('Fehler beim Laden der Masterplaene');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await importMasterplan(file);
      await loadMasterplaene();
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

  if (loading) {
    return (
      <Layout title="Masterplaene">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Masterplaene">
      <div className="masterplaene">
        {/* Toolbar */}
        <div className="masterplaene-toolbar">
          <div className="toolbar-left">
            <p className="text-muted">{masterplaene.length} Masterplaene</p>
          </div>
          <div className="toolbar-right">
            <button className="btn btn-secondary" onClick={() => downloadVorlage('masterplan')}>
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

        {/* Masterplaene Grid */}
        <div className="masterplaene-grid">
          {masterplaene.map(mp => (
            <div 
              key={mp.id} 
              className={`masterplan-card ${selectedPlan?.id === mp.id ? 'selected' : ''}`}
              onClick={() => setSelectedPlan(mp)}
            >
              <div className="masterplan-header">
                <h3>{mp.name}</h3>
                <span className={`badge ${mp.ist_aktiv ? 'badge-success' : 'badge-error'}`}>
                  {mp.ist_aktiv ? 'Aktiv' : 'Inaktiv'}
                </span>
              </div>
              <p className="masterplan-description">{mp.beschreibung}</p>
              <div className="masterplan-details">
                <div className="detail-item">
                  <span className="detail-label">Größe:</span>
                  <span className="detail-value">{mp.groesse}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Slots:</span>
                  <span className="detail-value">{mp.slots?.length || 0}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Zielpreis:</span>
                  <span className="detail-value">
                    {formatPrice(mp.zielpreis_min)} - {formatPrice(mp.zielpreis_max)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Detail-Ansicht */}
        {selectedPlan && (
          <div className="masterplan-detail card">
            <h2>Slot-Details: {selectedPlan.name}</h2>
            <div className="slots-table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Kategorie</th>
                    <th>Pflicht</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedPlan.slots?.sort((a, b) => a.slot_nummer - b.slot_nummer).map(slot => (
                    <tr key={slot.id}>
                      <td><strong>#{slot.slot_nummer}</strong></td>
                      <td>
                        <span className={`badge badge-${slot.kategorie.toLowerCase()}`}>
                          {slot.kategorie}
                        </span>
                      </td>
                      <td>
                        {slot.ist_pflicht ? (
                          <span className="badge badge-error">Pflicht</span>
                        ) : (
                          <span className="badge badge-success">Optional</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty State */}
        {masterplaene.length === 0 && (
          <div className="empty-state">
            <Layers size={64} />
            <h3>Keine Masterplaene vorhanden</h3>
            <p>Importieren Sie Masterplaene über die Excel-Vorlage</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Masterplaene;
