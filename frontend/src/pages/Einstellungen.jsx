import { useState, useEffect } from 'react';
import { Download, Database, FileText, Settings as SettingsIcon } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { getStatus, downloadVorlage } from '../services/api';
import './Einstellungen.css';

const Einstellungen = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await getStatus();
      setStatus(data);
    } catch (error) {
      console.error('Fehler beim Laden:', error);
    } finally {
      setLoading(false);
    }
  };

  const vorlagen = [
    { typ: 'artikel', name: 'Artikel', icon: FileText, beschreibung: '1. Vorlage herunterladen → 2. Ausfüllen → 3. In "Artikel verwalten" importieren' },
    { typ: 'preise', name: 'Preise', icon: FileText, beschreibung: '1. Vorlage herunterladen → 2. Ausfüllen → 3. In "Preise pflegen" importieren' },
    { typ: 'wochenquelle', name: 'Wochenquelle', icon: FileText, beschreibung: '1. Vorlage herunterladen → 2. Ausfüllen → 3. In "Wochenplanung" importieren' },
    { typ: 'masterplan', name: 'Masterplan', icon: FileText, beschreibung: '1. Vorlage herunterladen → 2. Ausfüllen → 3. In "Masterplaene" importieren' },
    { typ: 'historie', name: 'Historie', icon: FileText, beschreibung: '1. Vorlage herunterladen → 2. Ausfüllen → 3. In "Historie" importieren' },
  ];

  if (loading) {
    return (
      <Layout title="Einstellungen">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Einstellungen">
      <div className="einstellungen">
        {/* System-Status */}
        <div className="settings-section card">
          <div className="section-header">
            <Database size={24} />
            <h2>System-Status</h2>
          </div>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">API-Status:</span>
              <span className="badge badge-success">{status?.status || 'Online'}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Artikel:</span>
              <span className="status-value">{status?.artikel || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Masterplaene:</span>
              <span className="status-value">{status?.masterplaene || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Preise:</span>
              <span className="status-value">{status?.preise || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Generierte Kisten:</span>
              <span className="status-value">{status?.generierte_kisten || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Historische Kisten:</span>
              <span className="status-value">{status?.historische_kisten || 0}</span>
            </div>
          </div>
        </div>

        {/* Excel-Vorlagen */}
        <div className="settings-section card">
          <div className="section-header">
            <FileText size={24} />
            <h2>Excel-Vorlagen</h2>
          </div>
          <p className="text-muted">
            <strong>Schritt 1:</strong> Vorlage herunterladen → <strong>Schritt 2:</strong> In Excel ausfüllen → <strong>Schritt 3:</strong> In der jeweiligen Seite importieren (Upload)
          </p>
          <div className="vorlagen-grid">
            {vorlagen.map(vorlage => {
              const Icon = vorlage.icon;
              return (
                <div key={vorlage.typ} className="vorlage-card">
                  <div className="vorlage-icon">
                    <Icon size={32} />
                  </div>
                  <div className="vorlage-info">
                    <h3>{vorlage.name}</h3>
                    <p>{vorlage.beschreibung}</p>
                  </div>
                  <button 
                    className="btn btn-secondary btn-sm"
                    onClick={() => downloadVorlage(vorlage.typ)}
                    title="Schritt 1: Leere Vorlage herunterladen"
                  >
                    <Download size={16} />
                    Vorlage herunterladen
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Über die App */}
        <div className="settings-section card">
          <div className="section-header">
            <SettingsIcon size={24} />
            <h2>Über die App</h2>
          </div>
          <div className="about-content">
            <h3>Elementarwesens Sortimentsgenerator</h3>
            <p className="version">Version 1.0</p>
            <p className="description">
              Automatisierte Sortimentsgenerierung für Bio-Obst & Gemüse-Kisten.
              Optimiert Kisten basierend auf Verfügbarkeit, Preisen und historischen Daten.
            </p>
            <div className="features">
              <h4>Features:</h4>
              <ul>
                <li>✓ Automatische Kistengenerierung mit KI-gestützter Optimierung</li>
                <li>✓ Wochenplanung mit Slot-basiertem System</li>
                <li>✓ Preis-Optimierung innerhalb definierter Zielbereiche</li>
                <li>✓ Historisches Lernen aus vergangenen Sortimenten</li>
                <li>✓ Excel-Import/Export für alle Datenbereiche</li>
                <li>✓ Editierbare Slots für manuelle Anpassungen</li>
              </ul>
            </div>
            <div className="tech-stack">
              <h4>Technologie:</h4>
              <p>
                <strong>Backend:</strong> Python, FastAPI, SQLAlchemy, SQLite<br />
                <strong>Frontend:</strong> React, Vite, Lucide Icons<br />
                <strong>Design:</strong> Paradieschen Corporate Design
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Einstellungen;
