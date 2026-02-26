# 🎯 KISTENPREISE-FUNKTION - Vollständige Implementation

## ✅ BEREITS ERLEDIGT:

- [x] Datenbank-Modell `KistenFestpreis` erstellt
- [x] Pydantic Schemas erstellt

---

## 📋 NOCH ZU TUN:

### 1. BACKEND API-ENDPOINTS (main.py)

Fügen Sie folgende Endpoints hinzu:

```python
# ============================================================
# KISTENPREISE ENDPOINTS
# ============================================================

@app.get("/api/kistenpreise", response_model=list[schemas.KistenFestpreisOut])
def get_kistenpreise(db: Session = Depends(get_db)):
    """Alle Kistenpreise abrufen."""
    return db.query(models.KistenFestpreis).all()


@app.post("/api/kistenpreise", response_model=schemas.KistenFestpreisOut)
def create_kistenpreis(
    preis: schemas.KistenFestpreisCreate,
    db: Session = Depends(get_db)
):
    """Neuen Kistenpreis erstellen."""
    db_preis = models.KistenFestpreis(**preis.dict())
    db.add(db_preis)
    db.commit()
    db.refresh(db_preis)
    return db_preis


@app.put("/api/kistenpreise/{preis_id}", response_model=schemas.KistenFestpreisOut)
def update_kistenpreis(
    preis_id: int,
    preis: schemas.KistenFestpreisUpdate,
    db: Session = Depends(get_db)
):
    """Kistenpreis aktualisieren."""
    db_preis = db.query(models.KistenFestpreis).filter(
        models.KistenFestpreis.id == preis_id
    ).first()
    
    if not db_preis:
        raise HTTPException(status_code=404, detail="Kistenpreis nicht gefunden")
    
    for key, value in preis.dict(exclude_unset=True).items():
        setattr(db_preis, key, value)
    
    db.commit()
    db.refresh(db_preis)
    return db_preis


@app.delete("/api/kistenpreise/{preis_id}")
def delete_kistenpreis(preis_id: int, db: Session = Depends(get_db)):
    """Kistenpreis löschen."""
    db_preis = db.query(models.KistenFestpreis).filter(
        models.KistenFestpreis.id == preis_id
    ).first()
    
    if not db_preis:
        raise HTTPException(status_code=404, detail="Kistenpreis nicht gefunden")
    
    db.delete(db_preis)
    db.commit()
    return {"status": "deleted"}


@app.get("/api/kistenpreise/masterplan/{masterplan_id}/{groesse}")
def get_aktiver_kistenpreis(
    masterplan_id: int,
    groesse: str,
    db: Session = Depends(get_db)
):
    """Aktuell gültigen Festpreis für Masterplan + Größe abrufen."""
    from datetime import date
    heute = date.today().isoformat()
    
    preis = db.query(models.KistenFestpreis).filter(
        models.KistenFestpreis.masterplan_id == masterplan_id,
        models.KistenFestpreis.groesse == groesse,
        models.KistenFestpreis.ist_aktiv == True,
        models.KistenFestpreis.gueltig_ab <= heute,
        (models.KistenFestpreis.gueltig_bis == None) | 
        (models.KistenFestpreis.gueltig_bis >= heute)
    ).first()
    
    if preis:
        return {"festpreis": preis.festpreis, "id": preis.id}
    return {"festpreis": None}
```

---

### 2. FRONTEND API-SERVICE (services/api.js)

Fügen Sie hinzu:

```javascript
// Kistenpreise
export const getKistenpreise = () => api.get('/kistenpreise');
export const createKistenpreis = (data) => api.post('/kistenpreise', data);
export const updateKistenpreis = (id, data) => api.put(`/kistenpreise/${id}`, data);
export const deleteKistenpreis = (id) => api.delete(`/kistenpreise/${id}`);
export const getAktiverKistenpreis = (masterplanId, groesse) => 
  api.get(`/kistenpreise/masterplan/${masterplanId}/${groesse}`);
```

---

### 3. FRONTEND PREISPFLEGE MIT TABS

Ersetzen Sie `frontend/src/pages/Preispflege.jsx` mit Tab-System:

**Struktur:**
```jsx
const [activeTab, setActiveTab] = useState('artikel'); // 'artikel' oder 'kisten'

return (
  <Layout title="Preispflege">
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
  </Layout>
);
```

---

### 4. KISTEN-PREISE TAB KOMPONENTE

```jsx
const KistenPreiseTab = () => {
  const [kistenpreise, setKistenpreise] = useState([]);
  const [masterplaene, setMasterplaene] = useState([]);
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
    const [preise, plaene] = await Promise.all([
      getKistenpreise(),
      getMasterplaene()
    ]);
    setKistenpreise(preise);
    setMasterplaene(plaene);
  };

  const getMasterplanName = (id) => {
    const mp = masterplaene.find(m => m.id === id);
    return mp ? mp.name : 'Unbekannt';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editingId) {
      await updateKistenpreis(editingId, formData);
    } else {
      await createKistenpreis(formData);
    }
    await loadData();
    closeModal();
  };

  const handleDelete = async (id) => {
    if (!confirm('Kistenpreis wirklich löschen?')) return;
    await deleteKistenpreis(id);
    await loadData();
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

  return (
    <div className="kisten-preise-tab">
      {/* Toolbar */}
      <div className="toolbar">
        <p className="text-muted">
          {kistenpreise.length} Kistenpreise • Festpreise für ganze Kisten
        </p>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={18} />
          Neuer Kistenpreis
        </button>
      </div>

      {/* Tabelle */}
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
          {kistenpreise.map(p => (
            <tr key={p.id}>
              <td><strong>{getMasterplanName(p.masterplan_id)}</strong></td>
              <td><span className="badge">{p.groesse}</span></td>
              <td><span className="price-value">{p.festpreis.toFixed(2)} €</span></td>
              <td>{new Date(p.gueltig_ab).toLocaleDateString('de-DE')}</td>
              <td>{p.gueltig_bis ? new Date(p.gueltig_bis).toLocaleDateString('de-DE') : '-'}</td>
              <td>
                <span className={`badge ${p.ist_aktiv ? 'badge-success' : 'badge-secondary'}`}>
                  {p.ist_aktiv ? 'Aktiv' : 'Inaktiv'}
                </span>
              </td>
              <td>
                <button className="btn-icon btn-icon-primary" onClick={() => startEdit(p)}>
                  <Edit2 size={16} />
                </button>
                <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(p.id)}>
                  <Trash2 size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

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
                  <label>Masterplan *</label>
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
                  <label>Größe *</label>
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
                  <label>Festpreis (€) *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    value={formData.festpreis}
                    onChange={(e) => setFormData({...formData, festpreis: e.target.value})}
                    required
                    placeholder="z.B. 14.50"
                  />
                  <small className="text-muted">
                    Generator wird Kiste für genau diesen Preis erstellen
                  </small>
                </div>
                <div className="form-group">
                  <label>Gültig ab *</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.gueltig_ab}
                    onChange={(e) => setFormData({...formData, gueltig_ab: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Gültig bis (optional)</label>
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
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Abbrechen
                </button>
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
```

---

### 5. CSS FÜR TABS

Fügen Sie zu `Preispflege.css` hinzu:

```css
.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border-color);
}

.tabs button {
  padding: 1rem 2rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-muted);
  transition: all 0.2s;
}

.tabs button:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tabs button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.price-value {
  font-weight: 600;
  color: var(--success-color);
  font-size: 1.1rem;
}
```

---

### 6. GENERATOR-LOGIK ANPASSEN

In `backend/generator.py`, fügen Sie Festpreis-Check hinzu:

```python
def get_zielpreis(db: Session, masterplan_id: int, groesse: str, kw: int, jahr: int):
    """Zielpreis ermitteln: Festpreis oder Masterplan-Range."""
    from datetime import date
    heute = date.today().isoformat()
    
    # Prüfe ob Festpreis existiert
    festpreis = db.query(models.KistenFestpreis).filter(
        models.KistenFestpreis.masterplan_id == masterplan_id,
        models.KistenFestpreis.groesse == groesse,
        models.KistenFestpreis.ist_aktiv == True,
        models.KistenFestpreis.gueltig_ab <= heute,
        (models.KistenFestpreis.gueltig_bis == None) | 
        (models.KistenFestpreis.gueltig_bis >= heute)
    ).first()
    
    if festpreis:
        # Festpreis gefunden → Nutze diesen
        return {
            'typ': 'festpreis',
            'min': festpreis.festpreis,
            'max': festpreis.festpreis,
            'ziel': festpreis.festpreis
        }
    else:
        # Kein Festpreis → Nutze Masterplan-Range
        masterplan = db.query(models.Masterplan).filter(
            models.Masterplan.id == masterplan_id
        ).first()
        return {
            'typ': 'range',
            'min': masterplan.zielpreis_min,
            'max': masterplan.zielpreis_max,
            'ziel': (masterplan.zielpreis_min + masterplan.zielpreis_max) / 2
        }
```

Dann in der Generierungs-Funktion:

```python
# Zielpreis ermitteln
zielpreis_info = get_zielpreis(db, masterplan.id, groesse, kw, jahr)

if zielpreis_info['typ'] == 'festpreis':
    # Optimiere für EXAKTEN Preis
    toleranz = 0.05  # ±5 Cent
    ziel = zielpreis_info['ziel']
else:
    # Optimiere innerhalb Range
    toleranz = (zielpreis_info['max'] - zielpreis_info['min']) / 2
    ziel = zielpreis_info['ziel']
```

---

### 7. DATENBANK MIGRATION

Erstellen Sie die neue Tabelle:

```bash
ssh root@89.167.83.224
cd /var/www/kistengenerator/backend
source venv/bin/activate
python

>>> from database import engine, Base
>>> from models import KistenFestpreis
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

---

### 8. TESTING

Testen Sie die Funktion:

1. Backend neu starten
2. Frontend neu bauen
3. In Preispflege → Tab "Kisten-Preise"
4. Neuen Festpreis erstellen (z.B. OG12 S = 14.50€)
5. Kiste generieren
6. Prüfen ob Preis exakt 14.50€ ist

---

## ✅ CHECKLISTE

- [ ] Backend API-Endpoints hinzugefügt
- [ ] Frontend API-Service erweitert
- [ ] Preispflege mit Tabs umgebaut
- [ ] Kisten-Preise Tab implementiert
- [ ] CSS für Tabs hinzugefügt
- [ ] Generator-Logik angepasst
- [ ] Datenbank-Tabelle erstellt
- [ ] Backend neu gestartet
- [ ] Frontend neu gebaut
- [ ] Getestet

---

**Diese Dokumentation enthält alle notwendigen Code-Änderungen!** 🚀
