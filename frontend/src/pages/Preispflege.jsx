import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Upload, Download, Save, X } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { 
  getPreise, getArtikel, createPreis, updatePreis, deletePreis, importPreise, downloadVorlage,
  getKistenpreise, getMasterplaene, createKistenpreis, updateKistenpreis, deleteKistenpreis
} from '../services/api';
import './Preispflege.css';

const Preispflege = () => {
  const [activeTab, setActiveTab] = useState('artikel');

  return (
    <Layout title="Preispflege">
      <div className="preispflege">
        {/* Tab-Navigation */}
        <div className="tabs">
          <button 
            className={activeTab === 'artikel' ? 'active' : ''}
            onClick={() => setActiveTab('artikel')}
          >
            Artikel-Preise
          </button>
          <button 
            className={activeTab === 'kisten' ? 'active' : ''}
            onClick={() => setActiveTab('kisten')}
          >
            Kisten-Preise
          </button>
        </div>

        {/* Tab-Inhalt */}
        {activeTab === 'artikel' && <ArtikelPreiseTab />}
        {activeTab === 'kisten' && <KistenPreiseTab />}
      </div>
    </Layout>
  );
};

// ==================== ARTIKEL-PREISE TAB ====================

const ArtikelPreiseTab = () => {
  const [preise, setPreise] = useState([]);
  const [artikel, setArtikel] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    artikel_id: '',
    preis_pro_einheit: '',
    gueltig_ab: new Date().toISOString().split('T')[0],
    gueltig_bis: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [preiseData, artikelData] = await Promise.all([getPreise(), getArtikel()]);
      setPreise(preiseData);
      setArtikel(artikelData);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
      alert('Fehler beim Laden der Daten');
    } finally {
      setLoading(false);
    }
  };

  const getArtikelName = (artikelId) => {
    const a = artikel.find(art => art.id === artikelId);
    return a ? `${a.name} (${a.sid})` : 'Unbekannt';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createPreis(formData);
      await loadData();
      closeModal();
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert(error.response?.data?.detail || 'Fehler beim Speichern');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Preis wirklich löschen?')) return;
    try {
      await deletePreis(id);
      await loadData();
    } catch (error) {
      console.error('Fehler beim Löschen:', error);
      alert('Fehler beim Löschen');
    }
  };

  const startEdit = (preis) => {
    setEditingId(preis.id);
    setEditData({
      preis_pro_einheit: preis.preis_pro_einheit,
      gueltig_bis: preis.gueltig_bis || ''
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditData({});
  };

  const saveEdit = async (id) => {
    try {
      await updatePreis(id, editData);
      await loadData();
      setEditingId(null);
      setEditData({});
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert('Fehler beim Speichern');
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setFormData({
      artikel_id: '',
      preis_pro_einheit: '',
      gueltig_ab: new Date().toISOString().split('T')[0],
      gueltig_bis: ''
    });
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await importPreise(file);
      await loadData();
      alert('Import erfolgreich!');
    } catch (error) {
      console.error('Import-Fehler:', error);
      alert('Fehler beim Import');
    }
    e.target.value = '';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('de-DE');
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="artikel-preise-tab">
      {/* Toolbar */}
      <div className="preise-toolbar">
        <div className="toolbar-left">
          <p className="text-muted">{preise.length} Preise • Inline-Editing aktiviert</p>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-secondary" onClick={() => downloadVorlage('preise')}>
            <Download size={18} />
            Vorlage
          </button>
          <label className="btn btn-secondary">
            <Upload size={18} />
            Import
            <input type="file" accept=".xlsx,.xls" onChange={handleImport} style={{ display: 'none' }} />
          </label>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={18} />
            Neuer Preis
          </button>
        </div>
      </div>

      {/* Tabelle */}
      <div className="preise-table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Artikel</th>
              <th>Preis/Einheit</th>
              <th>Gültig ab</th>
              <th>Gültig bis</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {preise.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center text-muted">Keine Preise vorhanden</td>
              </tr>
            ) : (
              preise.map(p => (
                <tr key={p.id}>
                  <td><strong>{getArtikelName(p.artikel_id)}</strong></td>
                  <td>
                    {editingId === p.id ? (
                      <input
                        type="number"
                        step="0.01"
                        className="form-input inline-edit"
                        value={editData.preis_pro_einheit}
                        onChange={(e) => setEditData({...editData, preis_pro_einheit: parseFloat(e.target.value)})}
                      />
                    ) : (
                      <span className="price-value">{formatPrice(p.preis_pro_einheit)}</span>
                    )}
                  </td>
                  <td>{formatDate(p.gueltig_ab)}</td>
                  <td>
                    {editingId === p.id ? (
                      <input
                        type="date"
                        className="form-input inline-edit"
                        value={editData.gueltig_bis}
                        onChange={(e) => setEditData({...editData, gueltig_bis: e.target.value})}
                      />
                    ) : (
                      formatDate(p.gueltig_bis)
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      {editingId === p.id ? (
                        <>
                          <button className="btn-icon btn-icon-success" onClick={() => saveEdit(p.id)} title="Speichern">
                            <Save size={16} />
                          </button>
                          <button className="btn-icon btn-icon-secondary" onClick={cancelEdit} title="Abbrechen">
                            <X size={16} />
                          </button>
                        </>
                      ) : (
                        <>
                          <button className="btn-icon btn-icon-primary" onClick={() => startEdit(p)} title="Bearbeiten">
                            <Edit2 size={16} />
                          </button>
                          <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(p.id)} title="Löschen">
                            <Trash2 size={16} />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Neuer Preis</h2>
              <button className="modal-close" onClick={closeModal}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Artikel *</label>
                  <select
                    className="form-select"
                    value={formData.artikel_id}
                    onChange={(e) => setFormData({...formData, artikel_id: parseInt(e.target.value)})}
                    required
                  >
                    <option value="">Bitte wählen...</option>
                    {artikel.map(a => (
                      <option key={a.id} value={a.id}>{a.name} ({a.sid})</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Preis pro Einheit (€) *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    value={formData.preis_pro_einheit}
                    onChange={(e) => setFormData({...formData, preis_pro_einheit: e.target.value})}
                    required
                    placeholder="z.B. 2.50"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Gültig ab *</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.gueltig_ab}
                    onChange={(e) => setFormData({...formData, gueltig_ab: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Gültig bis (optional)</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.gueltig_bis}
                    onChange={(e) => setFormData({...formData, gueltig_bis: e.target.value})}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Abbrechen</button>
                <button type="submit" className="btn btn-primary">Erstellen</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// ==================== KISTEN-PREISE TAB ====================

const KistenPreiseTab = () => {
  const [kistenpreise, setKistenpreise] = useState([]);
  const [masterplaene, setMasterplaene] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    masterplan_id: '',
    groesse: 'S',
    festpreis: '',
    gueltig_ab: new Date().toISOString().split('T')[0],
    gueltig_bis: '',
    ist_aktiv: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [preise, plaene] = await Promise.all([getKistenpreise(), getMasterplaene()]);
      setKistenpreise(preise);
      setMasterplaene(plaene);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
      alert('Fehler beim Laden der Daten');
    } finally {
      setLoading(false);
    }
  };

  const getMasterplanName = (id) => {
    const mp = masterplaene.find(m => m.id === id);
    return mp ? mp.name : 'Unbekannt';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateKistenpreis(editingId, formData);
      } else {
        await createKistenpreis(formData);
      }
      await loadData();
      closeModal();
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert(error.response?.data?.detail || 'Fehler beim Speichern');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Kistenpreis wirklich löschen?')) return;
    try {
      await deleteKistenpreis(id);
      await loadData();
    } catch (error) {
      console.error('Fehler beim Löschen:', error);
      alert('Fehler beim Löschen');
    }
  };

  const startEdit = (preis) => {
    setEditingId(preis.id);
    setFormData({
      masterplan_id: preis.masterplan_id,
      groesse: preis.groesse,
      festpreis: preis.festpreis,
      gueltig_ab: preis.gueltig_ab,
      gueltig_bis: preis.gueltig_bis || '',
      ist_aktiv: preis.ist_aktiv
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({
      masterplan_id: '',
      groesse: 'S',
      festpreis: '',
      gueltig_ab: new Date().toISOString().split('T')[0],
      gueltig_bis: '',
      ist_aktiv: true
    });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('de-DE');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="kisten-preise-tab">
      {/* Toolbar */}
      <div className="preise-toolbar">
        <div className="toolbar-left">
          <p className="text-muted">{kistenpreise.length} Kistenpreise • Festpreise für ganze Kisten</p>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={18} />
            Neuer Kistenpreis
          </button>
        </div>
      </div>

      {/* Tabelle */}
      <div className="preise-table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Masterplan</th>
              <th>Größe</th>
              <th>Festpreis</th>
              <th>Gültig ab</th>
              <th>Gültig bis</th>
              <th>Status</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {kistenpreise.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center text-muted">Keine Kistenpreise vorhanden</td>
              </tr>
            ) : (
              kistenpreise.map(p => (
                <tr key={p.id}>
                  <td><strong>{getMasterplanName(p.masterplan_id)}</strong></td>
                  <td><span className="badge">{p.groesse}</span></td>
                  <td><span className="price-value">{p.festpreis.toFixed(2)} €</span></td>
                  <td>{formatDate(p.gueltig_ab)}</td>
                  <td>{formatDate(p.gueltig_bis)}</td>
                  <td>
                    <span className={`badge ${p.ist_aktiv ? 'badge-success' : 'badge-secondary'}`}>
                      {p.ist_aktiv ? 'Aktiv' : 'Inaktiv'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-icon btn-icon-primary" onClick={() => startEdit(p)} title="Bearbeiten">
                        <Edit2 size={16} />
                      </button>
                      <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(p.id)} title="Löschen">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingId ? 'Kistenpreis bearbeiten' : 'Neuer Kistenpreis'}</h2>
              <button className="modal-close" onClick={closeModal}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Masterplan *</label>
                  <select
                    className="form-select"
                    value={formData.masterplan_id}
                    onChange={(e) => setFormData({...formData, masterplan_id: parseInt(e.target.value)})}
                    required
                  >
                    <option value="">Bitte wählen...</option>
                    {masterplaene.map(m => (
                      <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Größe *</label>
                  <select
                    className="form-select"
                    value={formData.groesse}
                    onChange={(e) => setFormData({...formData, groesse: e.target.value})}
                    required
                  >
                    <option value="S">S</option>
                    <option value="M">M</option>
                    <option value="L">L</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Festpreis (€) *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    value={formData.festpreis}
                    onChange={(e) => setFormData({...formData, festpreis: e.target.value})}
                    required
                    placeholder="z.B. 14.50"
                  />
                  <small className="text-muted">Generator wird Kiste für genau diesen Preis erstellen</small>
                </div>
                <div className="form-group">
                  <label className="form-label">Gültig ab *</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.gueltig_ab}
                    onChange={(e) => setFormData({...formData, gueltig_ab: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Gültig bis (optional)</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.gueltig_bis}
                    onChange={(e) => setFormData({...formData, gueltig_bis: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData.ist_aktiv}
                      onChange={(e) => setFormData({...formData, ist_aktiv: e.target.checked})}
                    />
                    Aktiv
                  </label>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Abbrechen</button>
                <button type="submit" className="btn btn-primary">
                  {editingId ? 'Speichern' : 'Erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Preispflege;
