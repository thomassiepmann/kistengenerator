/**
 * API Service für Paradieschen Kistengenerator
 * Alle Backend-Calls zentralisiert
 */
import axios from 'axios';

const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8001' 
  : 'http://89.167.83.224:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== STATUS ====================

export const getStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// ==================== ARTIKEL ====================

export const getArtikel = async (kategorie = null) => {
  const params = kategorie ? { kategorie } : {};
  const response = await api.get('/api/artikel', { params });
  return response.data;
};

export const getArtikelDetail = async (id) => {
  const response = await api.get(`/api/artikel/${id}`);
  return response.data;
};

export const createArtikel = async (data) => {
  const response = await api.post('/api/artikel', data);
  return response.data;
};

export const updateArtikel = async (id, data) => {
  const response = await api.put(`/api/artikel/${id}`, data);
  return response.data;
};

export const deleteArtikel = async (id) => {
  const response = await api.delete(`/api/artikel/${id}`);
  return response.data;
};

// ==================== MASTERPLAENE ====================

export const getMasterplaene = async () => {
  const response = await api.get('/api/masterplan');
  return response.data;
};

export const getMasterplanDetail = async (id) => {
  const response = await api.get(`/api/masterplan/${id}`);
  return response.data;
};

// ==================== PREISE ====================

export const getPreise = async () => {
  const response = await api.get('/api/preise');
  return response.data;
};

export const createPreis = async (data) => {
  const response = await api.post('/api/preise', data);
  return response.data;
};

export const updatePreis = async (id, data) => {
  const response = await api.put(`/api/preise/${id}`, data);
  return response.data;
};

export const deletePreis = async (id) => {
  const response = await api.delete(`/api/preise/${id}`);
  return response.data;
};

// ==================== KISTENPREISE ====================

export const getKistenpreise = async () => {
  const response = await api.get('/api/kistenpreise');
  return response.data;
};

export const createKistenpreis = async (data) => {
  const response = await api.post('/api/kistenpreise', data);
  return response.data;
};

export const updateKistenpreis = async (id, data) => {
  const response = await api.put(`/api/kistenpreise/${id}`, data);
  return response.data;
};

export const deleteKistenpreis = async (id) => {
  const response = await api.delete(`/api/kistenpreise/${id}`);
  return response.data;
};

export const getAktiverKistenpreis = async (masterplanId, groesse) => {
  const response = await api.get(`/api/kistenpreise/masterplan/${masterplanId}/${groesse}`);
  return response.data;
};

// ==================== WOCHENQUELLE ====================

export const getWochenquelle = async (kw, jahr) => {
  const response = await api.get(`/api/quelle/${kw}/${jahr}`);
  return response.data;
};

export const setWochenquelle = async (kw, jahr, eintraege) => {
  const response = await api.post(`/api/quelle/${kw}/${jahr}`, eintraege);
  return response.data;
};

export const kopiereWochenquelle = async (kw, jahr, quellKw, quellJahr) => {
  const response = await api.post(`/api/quelle/${kw}/${jahr}/kopieren-von/${quellKw}/${quellJahr}`);
  return response.data;
};

// ==================== GENERATOR ====================

export const generiereKiste = async (data) => {
  const response = await api.post('/api/kiste/generieren', data);
  return response.data;
};

export const getKiste = async (id) => {
  const response = await api.get(`/api/kiste/${id}`);
  return response.data;
};

export const updateKiste = async (id, data) => {
  const response = await api.put(`/api/kiste/${id}`, data);
  return response.data;
};

export const kisteFreigeben = async (id) => {
  const response = await api.put(`/api/kiste/${id}/freigeben`);
  return response.data;
};

export const getAlleKisten = async (status = null) => {
  const params = status ? { status } : {};
  const response = await api.get('/api/kisten', { params });
  return response.data;
};

// ==================== HISTORIE ====================

export const getHistorie = async (masterplanName = null) => {
  const params = masterplanName ? { masterplan_name: masterplanName } : {};
  const response = await api.get('/api/historie', { params });
  return response.data;
};

// ==================== MUSTER ====================

export const musterLernen = async () => {
  const response = await api.post('/api/muster/lernen');
  return response.data;
};

// ==================== IMPORT ====================

export const importArtikel = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/import/artikel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const importHistorie = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/import/historie', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const importPreise = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/import/preise', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const importWochenquelle = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/import/wochenquelle', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const importMasterplan = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/import/masterplan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const downloadVorlage = async (typ) => {
  const response = await api.get(`/api/import/vorlage/${typ}`, {
    responseType: 'blob',
  });
  
  // Download-Link erstellen
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `Vorlage_${typ}.xlsx`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export default api;
