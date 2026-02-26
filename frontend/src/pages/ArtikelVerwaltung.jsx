import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Upload, Download, Search } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { 
  getArtikel, 
  createArtikel, 
  updateArtikel, 
  deleteArtikel,
  importArtikel,
  downloadVorlage 
} from '../services/api';
import './ArtikelVerwaltung.css';

const ArtikelVerwaltung = () => {
  const [artikel, setArtikel] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterKategorie, setFilterKategorie] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingArtikel, setEditingArtikel] = useState(null);
  const [formData, setFormData] = useState({
    sid: '',
    name: '',
    kategorie: '',
    einheit: '',
    status: 'aktiv'
  });

  const kategorien = ['Gemüse', 'Obst', 'Rohkost', 'Salat', 'Kräuter'];
  const einheiten = ['kg', 'Stück', 'Bund', 'Packung'];

  useEffect(() => {
    loadArtikel();
  }, []);

  const loadArtikel = async () => {
    try {
      const data = await getArtikel();
      setArtikel(data);
    } catch (error) {
      console.error('Fehler beim Laden der Artikel:', error);
      alert('Fehler beim Laden der Artikel');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingArtikel) {
        await updateArtikel(editingArtikel.id, formData);
      } else {
        await createArtikel(formData);
      }
      await loadArtikel();
      closeModal();
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert(error.response?.data?.detail || 'Fehler beim Speichern');
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Artikel "${name}" wirklich löschen?`)) return;
    try {
      await deleteArtikel(id);
      await loadArtikel();
    } catch (error) {
      console.error('Fehler beim Löschen:', error);
      alert('Fehler beim Löschen');
    }
  };

  const handleEdit = (artikel) => {
    setEditingArtikel(artikel);
    setFormData({
      sid: artikel.sid,
      name: artikel.name,
      kategorie: artikel.kategorie,
      einheit: artikel.einheit,
      status: artikel.status
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingArtikel(null);
    setFormData({
      sid: '',
      name: '',
      kategorie: '',
      einheit: '',
      status: 'aktiv'
    });
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await importArtikel(file);
      await loadArtikel();
      alert('Import erfolgreich!');
    } catch (error) {
      console.error('Import-Fehler:', error);
      alert('Fehler beim Import');
    }
    e.target.value = '';
  };

  const filteredArtikel = artikel.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         a.sid.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesKategorie = !filterKategorie || a.kategorie === filterKategorie;
    return matchesSearch && matchesKategorie;
  });

  const getCategoryBadgeClass = (kategorie) => {
    const map = {
      'Gemüse': 'badge-gemuese',
      'Obst': 'badge-obst',
      'Rohkost': 'badge-rohkost',
      'Salat': 'badge-salat',
      'Kräuter': 'badge-kraeuter'
    };
    return map[kategorie] || 'badge-gemuese';
  };

  if (loading) {
    return (
      <Layout title="Artikel-Verwaltung">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Artikel-Verwaltung">
      <div className="artikel-verwaltung">
        {/* Toolbar */}
        <div className="artikel-toolbar">
          <div className="toolbar-left">
            <div className="search-box">
              <Search size={20} />
              <input
                type="text"
                placeholder="Artikel suchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              className="form-select"
              value={filterKategorie}
              onChange={(e) => setFilterKategorie(e.target.value)}
            >
              <option value="">Alle Kategorien</option>
              {kategorien.map(k => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>
          <div className="toolbar-right">
            <button className="btn btn-secondary" onClick={() => downloadVorlage('artikel')}>
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
              Neuer Artikel
            </button>
          </div>
        </div>

        {/* Tabelle */}
        <div className="artikel-table-container">
          <table className="table">
            <thead>
              <tr>
                <th>SID</th>
                <th>Name</th>
                <th>Kategorie</th>
                <th>Einheit</th>
                <th>Status</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {filteredArtikel.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center text-muted">
                    Keine Artikel gefunden
                  </td>
                </tr>
              ) : (
                filteredArtikel.map(a => (
                  <tr key={a.id}>
                    <td><code>{a.sid}</code></td>
                    <td><strong>{a.name}</strong></td>
                    <td>
                      <span className={`badge ${getCategoryBadgeClass(a.kategorie)}`}>
                        {a.kategorie}
                      </span>
                    </td>
                    <td>{a.einheit}</td>
                    <td>
                      <span className={`badge ${a.status === 'aktiv' ? 'badge-success' : 'badge-error'}`}>
                        {a.status}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="btn-icon btn-icon-primary" 
                          onClick={() => handleEdit(a)}
                          title="Bearbeiten"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button 
                          className="btn-icon btn-icon-danger" 
                          onClick={() => handleDelete(a.id, a.name)}
                          title="Löschen"
                        >
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
                <h2>{editingArtikel ? 'Artikel bearbeiten' : 'Neuer Artikel'}</h2>
                <button className="modal-close" onClick={closeModal}>&times;</button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="form-group">
                    <label className="form-label">SID *</label>
                    <input
                      type="text"
                      className="form-input"
                      value={formData.sid}
                      onChange={(e) => setFormData({...formData, sid: e.target.value})}
                      required
                      placeholder="z.B. GEM001"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      placeholder="z.B. Karotten"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Kategorie *</label>
                    <select
                      className="form-select"
                      value={formData.kategorie}
                      onChange={(e) => setFormData({...formData, kategorie: e.target.value})}
                      required
                    >
                      <option value="">Bitte wählen...</option>
                      {kategorien.map(k => (
                        <option key={k} value={k}>{k}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Einheit *</label>
                    <select
                      className="form-select"
                      value={formData.einheit}
                      onChange={(e) => setFormData({...formData, einheit: e.target.value})}
                      required
                    >
                      <option value="">Bitte wählen...</option>
                      {einheiten.map(e => (
                        <option key={e} value={e}>{e}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Status</label>
                    <select
                      className="form-select"
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value})}
                    >
                      <option value="aktiv">Aktiv</option>
                      <option value="inaktiv">Inaktiv</option>
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeModal}>
                    Abbrechen
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingArtikel ? 'Speichern' : 'Erstellen'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ArtikelVerwaltung;
