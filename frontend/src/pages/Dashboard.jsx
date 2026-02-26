import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, ShoppingCart, Layers, TrendingUp, RefreshCw, Link } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { getStatus } from '../services/api';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [integrationStatus, setIntegrationStatus] = useState(null);

  useEffect(() => {
    loadStats();
    loadIntegrationStatus();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStatus();
      setStats(data);
    } catch (error) {
      console.error('Fehler beim Laden der Statistiken:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadIntegrationStatus = async () => {
    try {
      const response = await api.get('/api/integration/status');
      setIntegrationStatus(response.data);
    } catch (error) {
      console.error('Fehler beim Laden des Integrationsstatus:', error);
    }
  };

  const syncArtikel = async () => {
    try {
      const response = await api.post('/api/integration/sync-artikel');
      alert(`Artikel synchronisiert: ${response.data.neu} neu, ${response.data.aktualisiert} aktualisiert`);
      loadStats();
    } catch (error) {
      alert('Fehler beim Synchronisieren der Artikel');
    }
  };

  const syncPreise = async () => {
    try {
      const response = await api.post('/api/integration/sync-preise');
      alert(`Preise synchronisiert: ${response.data.neu} neu`);
    } catch (error) {
      alert('Fehler beim Synchronisieren der Preise');
    }
  };

  if (loading) {
    return (
      <Layout title="Dashboard">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard">
      <div className="dashboard">
        {/* Willkommens-Bereich */}
        <div className="dashboard-welcome">
          <h1>Willkommen beim Paradieschen Kistengenerator</h1>
          <p className="text-muted">
            Verwalten Sie Ihre Artikel, Preise und generieren Sie automatisch optimierte Kisten-Sortimente.
          </p>
        </div>

        {/* Statistik-Karten */}
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'var(--cat-gemuese-light)', color: 'var(--cat-gemuese)' }}>
              <ShoppingCart size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Artikel</p>
              <p className="stat-value">{stats?.artikel || 0}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'var(--cat-obst-light)', color: 'var(--cat-obst)' }}>
              <Layers size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Masterplaene</p>
              <p className="stat-value">{stats?.masterplaene || 0}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'var(--info-light)', color: 'var(--info)' }}>
              <Package size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Generierte Kisten</p>
              <p className="stat-value">{stats?.generierte_kisten || 0}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'var(--success-light)', color: 'var(--success)' }}>
              <TrendingUp size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">Historische Kisten</p>
              <p className="stat-value">{stats?.historische_kisten || 0}</p>
            </div>
          </div>
        </div>

        {/* Schnell-Aktionen */}
        <div className="dashboard-actions">
          <h2>Schnell-Aktionen</h2>
          <div className="action-grid">
            <button 
              className="action-card"
              onClick={() => navigate('/generator')}
            >
              <Package size={32} className="action-icon" />
              <h3>Neue Kiste generieren</h3>
              <p>Erstellen Sie eine optimierte Kiste basierend auf Verfügbarkeit und Historie</p>
            </button>

            <button 
              className="action-card"
              onClick={() => navigate('/artikel')}
            >
              <ShoppingCart size={32} className="action-icon" />
              <h3>Artikel verwalten</h3>
              <p>Artikel anlegen, bearbeiten oder löschen</p>
            </button>

            <button 
              className="action-card"
              onClick={() => navigate('/preise')}
            >
              <TrendingUp size={32} className="action-icon" />
              <h3>Preise pflegen</h3>
              <p>Aktuelle Preise für alle Artikel verwalten</p>
            </button>

            <button 
              className="action-card"
              onClick={() => navigate('/wochenquelle')}
            >
              <Layers size={32} className="action-icon" />
              <h3>Wochenplanung</h3>
              <p>Verfügbare Artikel für die aktuelle Woche festlegen</p>
            </button>
          </div>
        </div>

        {/* PC-Gärtner Integration */}
        {integrationStatus && (
          <div className="dashboard-integration">
            <h2>
              <Link size={20} style={{ marginRight: '8px' }} />
              PC-Gärtner Integration
            </h2>
            <div className="integration-card">
              <div className="integration-status">
                <div className="status-indicator">
                  <span className={`status-dot ${integrationStatus.konfiguriert ? 'status-success' : 'status-warning'}`}></span>
                  <span className="status-text">
                    {integrationStatus.konfiguriert ? 'Konfiguriert' : 'Nicht konfiguriert'}
                  </span>
                </div>
                {integrationStatus.letzte_sync && (
                  <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '4px' }}>
                    Letzte Synchronisation: {new Date(integrationStatus.letzte_sync).toLocaleString('de-DE')}
                  </p>
                )}
                {integrationStatus.hinweis && (
                  <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '4px' }}>
                    {integrationStatus.hinweis}
                  </p>
                )}
              </div>
              
              <div className="integration-actions">
                <button 
                  className="btn btn-primary"
                  onClick={syncArtikel}
                  disabled={!integrationStatus.konfiguriert}
                >
                  <RefreshCw size={16} />
                  Artikel synchronisieren
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={syncPreise}
                  disabled={!integrationStatus.konfiguriert}
                >
                  <RefreshCw size={16} />
                  Preise synchronisieren
                </button>
              </div>

              {!integrationStatus.konfiguriert && (
                <div className="alert alert-warning" style={{ marginTop: '1rem' }}>
                  <strong>Hinweis:</strong> Die PC-Gärtner Integration ist nicht konfiguriert. 
                  Nutzen Sie alternativ den CSV-Import unter "Artikel verwalten" und "Preise pflegen".
                </div>
              )}
            </div>
          </div>
        )}

        {/* Info-Box */}
        <div className="dashboard-info">
          <div className="alert alert-info">
            <strong>Tipp:</strong> Beginnen Sie mit der Wochenplanung, um die verfügbaren Artikel festzulegen. 
            Anschließend können Sie automatisch optimierte Kisten generieren lassen.
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
