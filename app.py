"""
Paradieschen Kistengenerator fuer Snowflake Streamlit - VERSION V1.3
Mit ALLE 85+ ORIGINALEN KISTENTYPEN von shop.paradieschen.de
NEU: Upload-Funktion fuer Excel/CSV fuer ALLE Kistentypen
NEU: Auto-Fill Prioritaet: JSON Pool → Vorlage → Historie → Kategorie
ENTFERNT: Alte UI-Elemente, Standard-Autofill
"""

import streamlit as st
import pandas as pd
import json
import random
import uuid
import re
import hashlib
from datetime import datetime
from collections import Counter, defaultdict
import io

# =============================================================================
# EINDEUTIGE SESSION-ID
# =============================================================================
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# =============================================================================
# BACKUP-SYSTEM INITIALISIERUNG
# =============================================================================
def init_backup_system():
    backup_defaults = {
        'code_backups': [],
        'auto_backup_enabled': True,
        'last_backup_time': None,
        'current_code_hash': None,
        'backup_count': 0
    }
    
    for key, value in backup_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_backup_system()

# =============================================================================
# NEUE SESSION STATE INITIALISIERUNG - KISTEN-HISTORIE & VORLAGEN & POOLS
# =============================================================================
def init_template_system():
    """Initialisiert Kisten-Historie, Vorlagen-System und JSON Pools"""
    template_defaults = {
        'kisten_historie': {},
        'box_templates': {},
        'template_stats': {},
        'json_pools': {}  # NEU: Pool-Speicher fuer ALLE Kistentypen
    }
    
    for key, value in template_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_template_system()

# =============================================================================
# KATEGORY-ARTIKEL-ZUORDNUNG (Fuer Fallback)
# =============================================================================
CATEGORY_ARTICLE_MAP = {
    "Familienkisten": ["SID001", "SID002", "SID003", "SID007", "SID008", "SID025", "SID027", "SID041", "SID042", "SID043", "SID052", "SID053", "SID055", "SID057", "SID059", "SID060", "SID061", "SID079", "SID080", "SID081"],
    "Mutter und Kind": ["SID001", "SID002", "SID003", "SID007", "SID010", "SID011", "SID012", "SID025", "SID027", "SID041", "SID052", "SID053", "SID055", "SID079", "SID080"],
    "Buerobst": ["SID001", "SID002", "SID003", "SID004", "SID005", "SID007", "SID008", "SID025", "SID038", "SID039", "SID040"],
    "Gemuesekiste": ["SID041", "SID042", "SID043", "SID045", "SID047", "SID049", "SID051", "SID052", "SID053", "SID055", "SID056", "SID057", "SID059", "SID060", "SID061", "SID062", "SID063", "SID064", "SID065"],
    "Kunterbunte Kiste": ["SID001", "SID002", "SID003", "SID007", "SID041", "SID052", "SID053", "SID055", "SID057", "SID067", "SID068", "SID069", "SID071", "SID079", "SID080", "SID081", "SID082"],
    "Deutsche Ernte": ["SID001", "SID007", "SID036", "SID041", "SID042", "SID043", "SID047", "SID049", "SID060", "SID061", "SID062", "SID063", "SID064", "SID065"],
    "Rohkostkisten": ["SID041", "SID043", "SID049", "SID050", "SID051", "SID052", "SID055", "SID057", "SID059", "SID067", "SID068", "SID069", "SID070", "SID071"],
    "Schnupper-Kisten": ["SID001", "SID002", "SID003", "SID041", "SID052", "SID053", "SID079", "SID080"],
    "Knabberbox": ["SID001", "SID002", "SID008", "SID011", "SID012", "SID025", "SID041", "SID051", "SID052"],
    "Ferienkiste": ["SID001", "SID002", "SID003", "SID007", "SID022", "SID023", "SID025", "SID026", "SID027", "SID041", "SID052", "SID053"],
    "Deutsche Ernte Gemuese": ["SID041", "SID042", "SID043", "SID045", "SID047", "SID049", "SID060", "SID061", "SID062", "SID063", "SID064", "SID065"],
    "Tutti-Frutti": ["SID001", "SID002", "SID003", "SID004", "SID007", "SID008", "SID016", "SID017", "SID018", "SID025", "SID026", "SID027"],
    "Saisonkisten": ["SID001", "SID007", "SID036", "SID041", "SID042", "SID060", "SID061", "SID062", "SID063"],
    "Spezialkisten": ["SID001", "SID007", "SID010", "SID011", "SID012", "SID041", "SID052", "SID067", "SID068", "SID069", "SID071", "SID079", "SID080"],
    "Tueten": ["SID001", "SID007"],
    "Obstkisten": ["SID001", "SID003", "SID007"],
}

# =============================================================================
# BACKUP-FUNKTIONEN
# =============================================================================
def create_backup(code_content, backup_type="manual", description=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    backup_id = f"BK_{st.session_state.backup_count:04d}_{datetime.now().strftime('%H%M%S')}"
    code_hash = hashlib.md5(code_content.encode()).hexdigest()[:8]
    
    backup = {
        'id': backup_id,
        'timestamp': timestamp,
        'type': backup_type,
        'description': description or f"Backup vom {timestamp}",
        'code': code_content,
        'hash': code_hash,
        'size': len(code_content)
    }
    
    st.session_state.code_backups.insert(0, backup)
    st.session_state.backup_count += 1
    st.session_state.last_backup_time = timestamp
    st.session_state.current_code_hash = code_hash
    
    if len(st.session_state.code_backups) > 50:
        st.session_state.code_backups = st.session_state.code_backups[:50]
    
    return backup_id

def restore_backup(backup_id):
    for backup in st.session_state.code_backups:
        if backup['id'] == backup_id:
            st.session_state.kimi_code_buffer = backup['code']
            return True
    return False

def export_all_backups():
    return json.dumps(st.session_state.code_backups, indent=2, ensure_ascii=False)

# =============================================================================
# CSS STYLING
# =============================================================================
css_code = """
<style>
    :root {
        --paradieschen-green: #4CAF50;
        --paradieschen-orange: #FF7043;
        --backup-blue: #2196F3;
        --template-purple: #9C27B0;
        --pool-gold: #FFD700;
    }
    
    .main-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .template-header {
        background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .history-header {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .pool-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 2px solid #2E7D32;
    }
    
    .backup-panel {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .backup-card {
        background: white;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .template-card {
        background: white;
        border-left: 4px solid #9C27B0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .pool-card {
        background: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .history-card {
        background: white;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .box-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .kiste-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #FF7043;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .price-tag {
        background: #FF7043;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    .article-item {
        background: #F5F5F5;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .pool-item {
        background: #E8F5E9;
        border: 1px solid #4CAF50;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .template-item {
        background: #F3E5F5;
        border: 1px solid #9C27B0;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .history-item {
        background: #FFF3E0;
        border: 1px solid #FF9800;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
    }
    
    .add-box-btn {
        background: linear-gradient(135deg, #FF7043, #E64A19) !important;
    }
    
    .pool-btn {
        background: linear-gradient(135deg, #4CAF50, #2E7D32) !important;
        color: white !important;
    }
    
    .upload-btn {
        background: linear-gradient(135deg, #2196F3, #1976D2) !important;
        color: white !important;
    }
    
    .code-box {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
        border-left: 4px solid #4CAF50;
    }
    
    .error-box {
        background: #fee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #efe;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .upload-area {
        border: 2px dashed #2196F3;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    
    .upload-area:hover {
        background: #e3f2fd;
        border-color: #1976D2;
    }
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALISIERUNG
# =============================================================================
def init_session_state():
    defaults = {
        'articles': [],
        'custom_boxes': {},
        'import_history': [],
        'debug_logs': [],
        'llm_config': {'api_key': '', 'model': 'gpt-4', 'temperature': 0.7},
        'selected_category': 'Alle',
        'cart': [],
        'master_data': {},
        'kimi_code_buffer': '',
        'kimi_last_analysis': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# ALLE 85+ ORIGINAL PARADIESCHEN KISTENTYPEN
# =============================================================================
PARADIESCHEN_KISTENTYPEN = {
    "Familienkisten": [
        {"name": "Singlekiste XS", "size": "XS", "articles": 6, "base_price": 18.90, "category": "Familienkisten"},
        {"name": "Familie Klein S", "size": "S", "articles": 8, "base_price": 22.90, "category": "Familienkisten"},
        {"name": "Familie Mittel M", "size": "M", "articles": 10, "base_price": 27.90, "category": "Familienkisten"},
        {"name": "Familie Gross L", "size": "L", "articles": 12, "base_price": 32.90, "category": "Familienkisten"},
        {"name": "Familienkiste XS", "size": "XS", "articles": 8, "base_price": 22.90, "category": "Familienkisten"},
        {"name": "Familienkiste S", "size": "S", "articles": 10, "base_price": 27.90, "category": "Familienkisten"},
        {"name": "Familienkiste M", "size": "M", "articles": 12, "base_price": 32.90, "category": "Familienkisten"},
        {"name": "Familienkiste L", "size": "L", "articles": 15, "base_price": 39.90, "category": "Familienkisten"},
        {"name": "Familienkiste XL", "size": "XL", "articles": 18, "base_price": 46.90, "category": "Familienkisten"},
        {"name": "Familienkiste XXL", "size": "XXL", "articles": 22, "base_price": 55.90, "category": "Familienkisten"},
    ],
    "Mutter und Kind": [
        {"name": "Mutter und Kind XS", "size": "XS", "articles": 6, "base_price": 20.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind S", "size": "S", "articles": 8, "base_price": 24.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind M", "size": "M", "articles": 10, "base_price": 29.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind L", "size": "L", "articles": 12, "base_price": 34.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind Kiste S", "size": "S", "articles": 8, "base_price": 24.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind Kiste M", "size": "M", "articles": 10, "base_price": 29.90, "category": "Mutter und Kind"},
        {"name": "Mutter und Kind Kiste L", "size": "L", "articles": 12, "base_price": 34.90, "category": "Mutter und Kind"},
    ],
    "Buerobst": [
        {"name": "Buerobst fuer 15 Personen", "size": "15P", "articles": 15, "base_price": 45.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 20 Personen", "size": "20P", "articles": 20, "base_price": 58.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 25 Personen", "size": "25P", "articles": 25, "base_price": 71.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 30 Personen", "size": "30P", "articles": 30, "base_price": 84.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 35 Personen", "size": "35P", "articles": 35, "base_price": 97.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 40 Personen", "size": "40P", "articles": 40, "base_price": 110.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 45 Personen", "size": "45P", "articles": 45, "base_price": 123.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 75 Personen", "size": "75P", "articles": 75, "base_price": 199.90, "category": "Buerobst"},
        {"name": "Buerobst fuer 150 Personen", "size": "150P", "articles": 150, "base_price": 389.90, "category": "Buerobst"},
        {"name": "Buerobst Kiste XS", "size": "XS", "articles": 6, "base_price": 18.90, "category": "Buerobst"},
        {"name": "Buerobst Kiste S", "size": "S", "articles": 8, "base_price": 23.90, "category": "Buerobst"},
        {"name": "Buerobst Kiste M", "size": "M", "articles": 10, "base_price": 28.90, "category": "Buerobst"},
        {"name": "Buerobst Kiste L", "size": "L", "articles": 12, "base_price": 33.90, "category": "Buerobst"},
    ],
    "Gemuesekiste": [
        {"name": "Gemuesekiste XS-1", "size": "XS-1", "articles": 6, "base_price": 17.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste S-1", "size": "S-1", "articles": 8, "base_price": 22.90, "category": "Gemuesekiste"},
        {"name": "Zwei Gemuesekisten", "size": "2x", "articles": 18, "base_price": 49.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste GS25", "size": "GS25", "articles": 25, "base_price": 69.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste XS", "size": "XS", "articles": 7, "base_price": 19.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste S", "size": "S", "articles": 9, "base_price": 24.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste M", "size": "M", "articles": 11, "base_price": 29.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste L", "size": "L", "articles": 14, "base_price": 36.90, "category": "Gemuesekiste"},
        {"name": "Gemuesekiste XL", "size": "XL", "articles": 17, "base_price": 43.90, "category": "Gemuesekiste"},
    ],
    "Kunterbunte Kiste": [
        {"name": "Kunterbunte Kiste Kraeuter", "size": "KRAEUTER", "articles": 10, "base_price": 24.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste Salat", "size": "SALAT", "articles": 10, "base_price": 26.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste fuer 30", "size": "30P", "articles": 30, "base_price": 79.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste XS", "size": "XS", "articles": 8, "base_price": 21.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste S", "size": "S", "articles": 10, "base_price": 26.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste M", "size": "M", "articles": 12, "base_price": 31.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste L", "size": "L", "articles": 15, "base_price": 38.90, "category": "Kunterbunte Kiste"},
        {"name": "Kunterbunte Kiste XL", "size": "XL", "articles": 18, "base_price": 45.90, "category": "Kunterbunte Kiste"},
    ],
    "Deutsche Ernte": [
        {"name": "Deutsche Ernte Obst Saison XS", "size": "XS-OBST", "articles": 7, "base_price": 19.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte Obst Saison S", "size": "S-OBST", "articles": 9, "base_price": 24.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte Obst Saison M", "size": "M-OBST", "articles": 11, "base_price": 29.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte Obst Saison L", "size": "L-OBST", "articles": 14, "base_price": 36.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte XS", "size": "XS", "articles": 7, "base_price": 20.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte S", "size": "S", "articles": 9, "base_price": 25.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte M", "size": "M", "articles": 11, "base_price": 30.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte L", "size": "L", "articles": 14, "base_price": 37.90, "category": "Deutsche Ernte"},
        {"name": "Deutsche Ernte XL", "size": "XL", "articles": 17, "base_price": 44.90, "category": "Deutsche Ernte"},
    ],
    "Rohkostkisten": [
        {"name": "Rohkostkiste Gemuese XS", "size": "XS-GEM", "articles": 7, "base_price": 21.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste Gemuese S", "size": "S-GEM", "articles": 9, "base_price": 26.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste Gemuese M", "size": "M-GEM", "articles": 11, "base_price": 31.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste Gemuese L", "size": "L-GEM", "articles": 14, "base_price": 38.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste fuer 10 ohne Obst", "size": "10P-OHNE-OBST", "articles": 10, "base_price": 34.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste XS", "size": "XS", "articles": 8, "base_price": 23.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste S", "size": "S", "articles": 10, "base_price": 28.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste M", "size": "M", "articles": 12, "base_price": 33.90, "category": "Rohkostkisten"},
        {"name": "Rohkostkiste L", "size": "L", "articles": 15, "base_price": 40.90, "category": "Rohkostkisten"},
    ],
    "Schnupper-Kisten": [
        {"name": "Schnupper-Kiste S25", "size": "S25", "articles": 8, "base_price": 25.00, "category": "Schnupper-Kisten"},
        {"name": "Schnupper-Kiste SEN15", "size": "SEN15", "articles": 6, "base_price": 15.00, "category": "Schnupper-Kisten"},
        {"name": "Schnupper-Kiste S21", "size": "S21", "articles": 8, "base_price": 21.00, "category": "Schnupper-Kisten"},
        {"name": "Schnupperkiste Obst", "size": "M", "articles": 8, "base_price": 19.90, "category": "Schnupper-Kisten"},
        {"name": "Schnupperkiste Gemuese", "size": "M", "articles": 8, "base_price": 19.90, "category": "Schnupper-Kisten"},
        {"name": "Schnupperkiste Mix", "size": "M", "articles": 8, "base_price": 19.90, "category": "Schnupper-Kisten"},
    ],
    "Knabberbox": [
        {"name": "Knabberbox Gemischt", "size": "GEMISCHT", "articles": 8, "base_price": 22.90, "category": "Knabberbox"},
        {"name": "Knabberbox Obst", "size": "OBST", "articles": 8, "base_price": 24.90, "category": "Knabberbox"},
        {"name": "Knabberbox Rohkost", "size": "ROHKOST", "articles": 8, "base_price": 21.90, "category": "Knabberbox"},
        {"name": "Knabberbox S", "size": "S", "articles": 6, "base_price": 16.90, "category": "Knabberbox"},
        {"name": "Knabberbox M", "size": "M", "articles": 8, "base_price": 21.90, "category": "Knabberbox"},
        {"name": "Knabberbox L", "size": "L", "articles": 10, "base_price": 26.90, "category": "Knabberbox"},
    ],
    "Ferienkiste": [
        {"name": "Ferienkiste XS", "size": "XS", "articles": 8, "base_price": 26.90, "category": "Ferienkiste"},
        {"name": "Ferienkiste S", "size": "S", "articles": 10, "base_price": 29.90, "category": "Ferienkiste"},
        {"name": "Ferienkiste M", "size": "M", "articles": 12, "base_price": 34.90, "category": "Ferienkiste"},
        {"name": "Ferienkiste L", "size": "L", "articles": 15, "base_price": 41.90, "category": "Ferienkiste"},
    ],
    "Deutsche Ernte Gemuese": [
        {"name": "Deutsche Ernte Gemuese XS", "size": "XS", "articles": 7, "base_price": 19.90, "category": "Deutsche Ernte Gemuese"},
        {"name": "Deutsche Ernte Gemuese S", "size": "S", "articles": 9, "base_price": 24.90, "category": "Deutsche Ernte Gemuese"},
        {"name": "Deutsche Ernte Gemuese M", "size": "M", "articles": 11, "base_price": 29.90, "category": "Deutsche Ernte Gemuese"},
        {"name": "Deutsche Ernte Gemuese L", "size": "L", "articles": 14, "base_price": 36.90, "category": "Deutsche Ernte Gemuese"},
    ],
    "Tutti-Frutti": [
        {"name": "Tutti-Frutti XS", "size": "XS", "articles": 8, "base_price": 22.90, "category": "Tutti-Frutti"},
        {"name": "Tutti-Frutti S", "size": "S", "articles": 10, "base_price": 27.90, "category": "Tutti-Frutti"},
        {"name": "Tutti-Frutti M", "size": "M", "articles": 12, "base_price": 32.90, "category": "Tutti-Frutti"},
        {"name": "Tutti-Frutti L", "size": "L", "articles": 15, "base_price": 39.90, "category": "Tutti-Frutti"},
        {"name": "Tutti-Frutti XL", "size": "XL", "articles": 18, "base_price": 46.90, "category": "Tutti-Frutti"},
    ],
    "Saisonkisten": [
        {"name": "Fruehlingskiste", "size": "M", "articles": 12, "base_price": 31.90, "category": "Saisonkisten"},
        {"name": "Sommerkiste", "size": "M", "articles": 12, "base_price": 31.90, "category": "Saisonkisten"},
        {"name": "Herbstkiste", "size": "M", "articles": 12, "base_price": 31.90, "category": "Saisonkisten"},
        {"name": "Winterkiste", "size": "M", "articles": 12, "base_price": 31.90, "category": "Saisonkisten"},
    ],
    "Spezialkisten": [
        {"name": "Buerokaffee Ganze Bohne S", "size": "S-KAFFEE-GB", "articles": 1, "base_price": 12.90, "category": "Spezialkisten"},
        {"name": "Buerokaffee Ganze Bohne M", "size": "M-KAFFEE-GB", "articles": 1, "base_price": 19.90, "category": "Spezialkisten"},
        {"name": "Buerokaffee Ganze Bohne L", "size": "L-KAFFEE-GB", "articles": 1, "base_price": 26.90, "category": "Spezialkisten"},
        {"name": "Buerokaffee Gemahlen S", "size": "S-KAFFEE-GM", "articles": 1, "base_price": 12.90, "category": "Spezialkisten"},
        {"name": "Buerokaffee Gemahlen M", "size": "M-KAFFEE-GM", "articles": 1, "base_price": 19.90, "category": "Spezialkisten"},
        {"name": "Buerokaffee Gemahlen L", "size": "L-KAFFEE-GM", "articles": 1, "base_price": 26.90, "category": "Spezialkisten"},
        {"name": "Buero-Snacks", "size": "SNACKS", "articles": 10, "base_price": 24.90, "category": "Spezialkisten"},
        {"name": "Metzger-Spezial", "size": "METZGER", "articles": 8, "base_price": 34.90, "category": "Spezialkisten"},
        {"name": "Wurstpaket", "size": "WURST", "articles": 6, "base_price": 29.90, "category": "Spezialkisten"},
        {"name": "Kaese-Paket S", "size": "S-KAESE", "articles": 5, "base_price": 24.90, "category": "Spezialkisten"},
        {"name": "Kaese-Paket M", "size": "M-KAESE", "articles": 7, "base_price": 34.90, "category": "Spezialkisten"},
        {"name": "Kaese-Paket L", "size": "L-KAESE", "articles": 10, "base_price": 49.90, "category": "Spezialkisten"},
        {"name": "Smoothie-Kiste", "size": "M", "articles": 10, "base_price": 29.90, "category": "Spezialkisten"},
        {"name": "Salatkiste", "size": "M", "articles": 10, "base_price": 27.90, "category": "Spezialkisten"},
        {"name": "Suppengemuese-Kiste", "size": "M", "articles": 10, "base_price": 26.90, "category": "Spezialkisten"},
        {"name": "Backobst-Kiste", "size": "M", "articles": 10, "base_price": 28.90, "category": "Spezialkisten"},
    ],
    "Tueten": [
        {"name": "Tuete Aepfel Jonagored 2,5 kg", "size": "2,5kg", "articles": 1, "base_price": 7.90, "category": "Tueten"},
        {"name": "Tuete Aepfel Jonagored 1,5 kg", "size": "1,5kg", "articles": 1, "base_price": 5.50, "category": "Tueten"},
        {"name": "Tuete Apfel Ingol 2,5 kg", "size": "2,5kg", "articles": 1, "base_price": 7.90, "category": "Tueten"},
        {"name": "Tuete Apfel Natyra 2,5 kg", "size": "2,5kg", "articles": 1, "base_price": 7.90, "category": "Tueten"},
    ],
    "Obstkisten": [
        {"name": "Kiste Aepfel Ingol 5 kg", "size": "5kg", "articles": 1, "base_price": 14.90, "category": "Obstkisten"},
        {"name": "Kiste Aepfel Ingol 9 kg", "size": "9kg", "articles": 1, "base_price": 24.90, "category": "Obstkisten"},
        {"name": "Kiste Aepfel Topaz 5 kg", "size": "5kg", "articles": 1, "base_price": 14.90, "category": "Obstkisten"},
        {"name": "Kiste Aepfel Topaz 9 kg", "size": "9kg", "articles": 1, "base_price": 24.90, "category": "Obstkisten"},
        {"name": "Kiste Orangen 10 kg", "size": "10kg", "articles": 1, "base_price": 19.90, "category": "Obstkisten"},
        {"name": "Kiste Saftorangen 5 kg", "size": "5kg", "articles": 1, "base_price": 12.90, "category": "Obstkisten"},
    ]
}

# =============================================================================
# ARTIKELSTAMM (92 ARTIKEL)
# =============================================================================
def get_default_articles():
    return [
        {"sid": "SID001", "ean13": "400000000001", "art_nr": "OB001", "bezeichnung": "Aepfel", "einheit": "kg"},
        {"sid": "SID002", "ean13": "400000000002", "art_nr": "OB002", "bezeichnung": "Bananen", "einheit": "kg"},
        {"sid": "SID003", "ean13": "400000000003", "art_nr": "OB003", "bezeichnung": "Orangen", "einheit": "kg"},
        {"sid": "SID004", "ean13": "400000000004", "art_nr": "OB004", "bezeichnung": "Mandarinen", "einheit": "kg"},
        {"sid": "SID005", "ean13": "400000000005", "art_nr": "OB005", "bezeichnung": "Zitronen", "einheit": "kg"},
        {"sid": "SID006", "ean13": "400000000006", "art_nr": "OB006", "bezeichnung": "Grapefruit", "einheit": "Stueck"},
        {"sid": "SID007", "ean13": "400000000007", "art_nr": "OB007", "bezeichnung": "Birnen", "einheit": "kg"},
        {"sid": "SID008", "ean13": "400000000008", "art_nr": "OB008", "bezeichnung": "Trauben", "einheit": "kg"},
        {"sid": "SID009", "ean13": "400000000009", "art_nr": "OB009", "bezeichnung": "Kirschen", "einheit": "kg"},
        {"sid": "SID010", "ean13": "400000000010", "art_nr": "OB010", "bezeichnung": "Erdbeeren", "einheit": "500g"},
        {"sid": "SID011", "ean13": "400000000011", "art_nr": "OB011", "bezeichnung": "Himbeeren", "einheit": "125g"},
        {"sid": "SID012", "ean13": "400000000012", "art_nr": "OB012", "bezeichnung": "Blaubeeren", "einheit": "125g"},
        {"sid": "SID013", "ean13": "400000000013", "art_nr": "OB013", "bezeichnung": "Brombeeren", "einheit": "125g"},
        {"sid": "SID014", "ean13": "400000000014", "art_nr": "OB014", "bezeichnung": "Johannisbeeren", "einheit": "125g"},
        {"sid": "SID015", "ean13": "400000000015", "art_nr": "OB015", "bezeichnung": "Stachelbeeren", "einheit": "125g"},
        {"sid": "SID016", "ean13": "400000000016", "art_nr": "OB016", "bezeichnung": "Pfirsiche", "einheit": "kg"},
        {"sid": "SID017", "ean13": "400000000017", "art_nr": "OB017", "bezeichnung": "Nektarinen", "einheit": "kg"},
        {"sid": "SID018", "ean13": "400000000018", "art_nr": "OB018", "bezeichnung": "Aprikosen", "einheit": "kg"},
        {"sid": "SID019", "ean13": "400000000019", "art_nr": "OB019", "bezeichnung": "Pflaumen", "einheit": "kg"},
        {"sid": "SID020", "ean13": "400000000020", "art_nr": "OB020", "bezeichnung": "Mirabellen", "einheit": "kg"},
        {"sid": "SID021", "ean13": "400000000021", "art_nr": "OB021", "bezeichnung": "Zwetschgen", "einheit": "kg"},
        {"sid": "SID022", "ean13": "400000000022", "art_nr": "OB022", "bezeichnung": "Melone", "einheit": "Stueck"},
        {"sid": "SID023", "ean13": "400000000023", "art_nr": "OB023", "bezeichnung": "Wassermelone", "einheit": "Stueck"},
        {"sid": "SID024", "ean13": "400000000024", "art_nr": "OB024", "bezeichnung": "Honigmelone", "einheit": "Stueck"},
        {"sid": "SID025", "ean13": "400000000025", "art_nr": "OB025", "bezeichnung": "Kiwi", "einheit": "Stueck"},
        {"sid": "SID026", "ean13": "400000000026", "art_nr": "OB026", "bezeichnung": "Ananas", "einheit": "Stueck"},
        {"sid": "SID027", "ean13": "400000000027", "art_nr": "OB027", "bezeichnung": "Mango", "einheit": "Stueck"},
        {"sid": "SID028", "ean13": "400000000028", "art_nr": "OB028", "bezeichnung": "Papaya", "einheit": "Stueck"},
        {"sid": "SID029", "ean13": "400000000029", "art_nr": "OB029", "bezeichnung": "Kokosnuss", "einheit": "Stueck"},
        {"sid": "SID030", "ean13": "400000000030", "art_nr": "OB030", "bezeichnung": "Granatapfel", "einheit": "Stueck"},
        {"sid": "SID031", "ean13": "400000000031", "art_nr": "OB031", "bezeichnung": "Feigen", "einheit": "250g"},
        {"sid": "SID032", "ean13": "400000000032", "art_nr": "OB032", "bezeichnung": "Datteln", "einheit": "250g"},
        {"sid": "SID033", "ean13": "400000000033", "art_nr": "OB033", "bezeichnung": "Avocado", "einheit": "Stueck"},
        {"sid": "SID034", "ean13": "400000000034", "art_nr": "OB034", "bezeichnung": "Litschi", "einheit": "250g"},
        {"sid": "SID035", "ean13": "400000000035", "art_nr": "OB035", "bezeichnung": "Kaki", "einheit": "Stueck"},
        {"sid": "SID036", "ean13": "400000000036", "art_nr": "OB036", "bezeichnung": "Quitte", "einheit": "kg"},
        {"sid": "SID037", "ean13": "400000000037", "art_nr": "OB037", "bezeichnung": "Rhabarber", "einheit": "500g"},
        {"sid": "SID038", "ean13": "400000000038", "art_nr": "OB038", "bezeichnung": "Clementinen", "einheit": "kg"},
        {"sid": "SID039", "ean13": "400000000039", "art_nr": "OB039", "bezeichnung": "Limette", "einheit": "Stueck"},
        {"sid": "SID040", "ean13": "400000000040", "art_nr": "OB040", "bezeichnung": "Pomelo", "einheit": "Stueck"},
        {"sid": "SID041", "ean13": "400000000041", "art_nr": "GE001", "bezeichnung": "Karotten", "einheit": "kg"},
        {"sid": "SID042", "ean13": "400000000042", "art_nr": "GE002", "bezeichnung": "Kartoffeln", "einheit": "kg"},
        {"sid": "SID043", "ean13": "400000000043", "art_nr": "GE003", "bezeichnung": "Zwiebeln", "einheit": "kg"},
        {"sid": "SID044", "ean13": "400000000044", "art_nr": "GE004", "bezeichnung": "Knoblauch", "einheit": "Stueck"},
        {"sid": "SID045", "ean13": "400000000045", "art_nr": "GE005", "bezeichnung": "Lauch", "einheit": "Stueck"},
        {"sid": "SID046", "ean13": "400000000046", "art_nr": "GE006", "bezeichnung": "Porree", "einheit": "Stueck"},
        {"sid": "SID047", "ean13": "400000000047", "art_nr": "GE007", "bezeichnung": "Sellerie", "einheit": "Stueck"},
        {"sid": "SID048", "ean13": "400000000048", "art_nr": "GE008", "bezeichnung": "Pastinaken", "einheit": "kg"},
        {"sid": "SID049", "ean13": "400000000049", "art_nr": "GE009", "bezeichnung": "Rote Beete", "einheit": "kg"},
        {"sid": "SID050", "ean13": "400000000050", "art_nr": "GE010", "bezeichnung": "Rettich", "einheit": "Stueck"},
        {"sid": "SID051", "ean13": "400000000051", "art_nr": "GE011", "bezeichnung": "Radieschen", "einheit": "Bund"},
        {"sid": "SID052", "ean13": "400000000052", "art_nr": "GE012", "bezeichnung": "Gurke", "einheit": "Stueck"},
        {"sid": "SID053", "ean13": "400000000053", "art_nr": "GE013", "bezeichnung": "Tomaten", "einheit": "kg"},
        {"sid": "SID054", "ean13": "400000000054", "art_nr": "GE014", "bezeichnung": "Cherrytomaten", "einheit": "250g"},
        {"sid": "SID055", "ean13": "400000000055", "art_nr": "GE015", "bezeichnung": "Paprika", "einheit": "Stueck"},
        {"sid": "SID056", "ean13": "400000000056", "art_nr": "GE016", "bezeichnung": "Champignons", "einheit": "250g"},
        {"sid": "SID057", "ean13": "400000000057", "art_nr": "GE017", "bezeichnung": "Zucchini", "einheit": "Stueck"},
        {"sid": "SID058", "ean13": "400000000058", "art_nr": "GE018", "bezeichnung": "Aubergine", "einheit": "Stueck"},
        {"sid": "SID059", "ean13": "400000000059", "art_nr": "GE019", "bezeichnung": "Kohlrabi", "einheit": "Stueck"},
        {"sid": "SID060", "ean13": "400000000060", "art_nr": "GE020", "bezeichnung": "Blumenkohl", "einheit": "Stueck"},
        {"sid": "SID061", "ean13": "400000000061", "art_nr": "GE021", "bezeichnung": "Brokkoli", "einheit": "Stueck"},
        {"sid": "SID062", "ean13": "400000000062", "art_nr": "GE022", "bezeichnung": "Rosenkohl", "einheit": "kg"},
        {"sid": "SID063", "ean13": "400000000063", "art_nr": "GE023", "bezeichnung": "Rotkohl", "einheit": "Stueck"},
        {"sid": "SID064", "ean13": "400000000064", "art_nr": "GE024", "bezeichnung": "Weisskohl", "einheit": "Stueck"},
        {"sid": "SID065", "ean13": "400000000065", "art_nr": "GE025", "bezeichnung": "Wirsing", "einheit": "Stueck"},
        {"sid": "SID066", "ean13": "400000000066", "art_nr": "GE026", "bezeichnung": "Chinakohl", "einheit": "Stueck"},
        {"sid": "SID067", "ean13": "400000000067", "art_nr": "GE027", "bezeichnung": "Eisbergsalat", "einheit": "Stueck"},
        {"sid": "SID068", "ean13": "400000000068", "art_nr": "GE028", "bezeichnung": "Eichblattsalat", "einheit": "Stueck"},
        {"sid": "SID069", "ean13": "400000000069", "art_nr": "GE029", "bezeichnung": "Rucola", "einheit": "125g"},
        {"sid": "SID070", "ean13": "400000000070", "art_nr": "GE030", "bezeichnung": "Feldsalat", "einheit": "100g"},
        {"sid": "SID071", "ean13": "400000000071", "art_nr": "SA001", "bezeichnung": "Kopfsalat", "einheit": "Stueck"},
        {"sid": "SID072", "ean13": "400000000072", "art_nr": "SA002", "bezeichnung": "Romana Salat", "einheit": "Stueck"},
        {"sid": "SID073", "ean13": "400000000073", "art_nr": "SA003", "bezeichnung": "Lollo Rosso", "einheit": "Stueck"},
        {"sid": "SID074", "ean13": "400000000074", "art_nr": "SA004", "bezeichnung": "Lollo Bionda", "einheit": "Stueck"},
        {"sid": "SID075", "ean13": "400000000075", "art_nr": "SA005", "bezeichnung": "Radicchio", "einheit": "Stueck"},
        {"sid": "SID076", "ean13": "400000000076", "art_nr": "SA006", "bezeichnung": "Endiviensalat", "einheit": "Stueck"},
        {"sid": "SID077", "ean13": "400000000077", "art_nr": "SA007", "bezeichnung": "Maissalat", "einheit": "125g"},
        {"sid": "SID078", "ean13": "400000000078", "art_nr": "SA008", "bezeichnung": "Radieschensprossen", "einheit": "100g"},
        {"sid": "SID079", "ean13": "400000000079", "art_nr": "KR001", "bezeichnung": "Basilikum", "einheit": "Topf"},
        {"sid": "SID080", "ean13": "400000000080", "art_nr": "KR002", "bezeichnung": "Petersilie", "einheit": "Bund"},
        {"sid": "SID081", "ean13": "400000000081", "art_nr": "KR003", "bezeichnung": "Schnittlauch", "einheit": "Bund"},
        {"sid": "SID082", "ean13": "400000000082", "art_nr": "KR004", "bezeichnung": "Dill", "einheit": "Bund"},
        {"sid": "SID083", "ean13": "400000000083", "art_nr": "KR005", "bezeichnung": "Koriander", "einheit": "Bund"},
        {"sid": "SID084", "ean13": "400000000084", "art_nr": "KR006", "bezeichnung": "Minze", "einheit": "Bund"},
        {"sid": "SID085", "ean13": "400000000085", "art_nr": "KR007", "bezeichnung": "Rosmarin", "einheit": "Bund"},
        {"sid": "SID086", "ean13": "400000000086", "art_nr": "KR008", "bezeichnung": "Thymian", "einheit": "Bund"},
        {"sid": "SID087", "ean13": "400000000087", "art_nr": "TO001", "bezeichnung": "Rosinen", "einheit": "250g"},
        {"sid": "SID088", "ean13": "400000000088", "art_nr": "TO002", "bezeichnung": "Aprikosen getrocknet", "einheit": "250g"},
        {"sid": "SID089", "ean13": "400000000089", "art_nr": "TO003", "bezeichnung": "Feigen getrocknet", "einheit": "250g"},
        {"sid": "SID090", "ean13": "400000000090", "art_nr": "TO004", "bezeichnung": "Pflaumen getrocknet", "einheit": "250g"},
        {"sid": "SID091", "ean13": "400000000091", "art_nr": "TO005", "bezeichnung": "Datteln ohne Stein", "einheit": "250g"},
        {"sid": "SID092", "ean13": "400000000092", "art_nr": "TO006", "bezeichnung": "Cranberries getrocknet", "einheit": "250g"},
    ]

if not st.session_state.articles:
    st.session_state.articles = get_default_articles()

# =============================================================================
# NEUE FUNKTIONEN - JSON POOL GENERATOR FUER ALLE KISTENTYPEN
# =============================================================================
def generate_from_pool(pool_data, anzahl_artikel=10, saison_filter=True, diversitaet=0.8):
    """
    Generiert eine Kiste aus dem Pool mit Haeufigkeitsgewichtung
    
    Parameters:
    - pool_data: Dict mit 'artikel_pool' Liste
    - anzahl_artikel: Wie viele Artikel sollen ausgewaehlt werden
    - saison_filter: True = saisonale Artikel (SAISONENDE) ausschliessen
    - diversitaet: 0.0-1.0 = Wahrscheinlichkeit, weniger haeufige Artikel zu mischen
    
    Returns: Liste ausgewaehlter Artikel
    """
    if not pool_data or 'artikel_pool' not in pool_data:
        return []
    
    artikel_pool = pool_data['artikel_pool']
    
    # Saisonale Artikel filtern wenn gewuenscht
    if saison_filter:
        verfuegbare_artikel = [a for a in artikel_pool if not a.get('saisonal', False)]
    else:
        verfuegbare_artikel = artikel_pool
    
    if not verfuegbare_artikel:
        return []
    
    # Nach Haeufigkeit sortieren fuer Gewichtung
    verfuegbare_artikel.sort(key=lambda x: x.get('haeufigkeit', 1), reverse=True)
    
    ausgewaehlt = []
    verfuegbare_kopie = verfuegbare_artikel.copy()
    
    for i in range(min(anzahl_artikel, len(verfuegbare_artikel))):
        if not verfuegbare_kopie:
            break
        
        # Diversitaet: Manchmal weniger haeufige Artikel waehlen
        if random.random() > diversitaet and len(verfuegbare_kopie) > 5:
            # Waehle aus den weniger haeufigen (unteren 50%)
            start_idx = len(verfuegbare_kopie) // 2
            artikel = random.choice(verfuegbare_kopie[start_idx:])
        else:
            # Gewichtete Auswahl nach Haeufigkeit
            gewichte = [a.get('haeufigkeit', 1) for a in verfuegbare_kopie]
            artikel = random.choices(verfuegbare_kopie, weights=gewichte, k=1)[0]
        
        ausgewaehlt.append(artikel)
        verfuegbare_kopie.remove(artikel)
    
    return ausgewaehlt

def load_json_pool(uploaded_file):
    """Laedt und validiert eine JSON Pool-Datei"""
    try:
        content = uploaded_file.read().decode('utf-8')
        pool_data = json.loads(content)
        
        # Validierung
        required_fields = ['kistentyp', 'artikel_pool']
        for field in required_fields:
            if field not in pool_data:
                return None, f"Fehlendes Feld: {field}"
        
        if not isinstance(pool_data['artikel_pool'], list):
            return None, "artikel_pool muss eine Liste sein"
        
        return pool_data, None
        
    except json.JSONDecodeError as e:
        return None, f"Ungueltiges JSON: {str(e)}"
    except Exception as e:
        return None, f"Fehler: {str(e)}"

# =============================================================================
# NEU: UPLOAD-FUNKTION FUER ALLE KISTENTYPEN (EXCEL/CSV/TEXT)
# =============================================================================
def parse_uploaded_data(uploaded_file, text_input=None):
    """
    Parst hochgeladene Daten (Excel, CSV oder Text) und gibt DataFrame zurueck
    
    Returns: (DataFrame, error_message)
    """
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
                return df, None
            elif uploaded_file.name.endswith('.csv'):
                # Versuche verschiedene Trennzeichen
                try:
                    df = pd.read_csv(uploaded_file, sep=';')
                except:
                    try:
                        df = pd.read_csv(uploaded_file, sep=',')
                    except:
                        df = pd.read_csv(uploaded_file)
                return df, None
            else:
                return None, "Nicht unterstuetztes Dateiformat. Bitte .xlsx oder .csv verwenden."
        
        elif text_input:
            # Text-Eingabe parsen (CSV-Format erwartet)
            from io import StringIO
            try:
                df = pd.read_csv(StringIO(text_input), sep=';')
            except:
                try:
                    df = pd.read_csv(StringIO(text_input), sep=',')
                except:
                    df = pd.read_csv(StringIO(text_input))
            return df, None
        
        else:
            return None, "Keine Daten bereitgestellt"
            
    except Exception as e:
        return None, f"Fehler beim Parsen: {str(e)}"

def process_upload_for_kistentyp(kistentyp_key, df, box_template):
    """
    Verarbeitet hochgeladene Daten fuer einen Kistentyp
    
    Erwartete Spalten: Artikel, Menge (optional), Einheit (optional)
    """
    if df is None or df.empty:
        return None, "Keine Daten im Upload"
    
    # Spalten normalisieren (case-insensitive)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Artikel-Spalte finden
    artikel_col = None
    for col in df.columns:
        if 'artikel' in col or 'bezeichnung' in col or 'name' in col:
            artikel_col = col
            break
    
    if not artikel_col:
        return None, "Spalte 'Artikel' nicht gefunden. Erwartet: Artikel, Menge, Einheit"
    
    # Menge und Einheit (optional)
    menge_col = next((col for col in df.columns if 'menge' in col or 'anzahl' in col or 'count' in col), None)
    einheit_col = next((col for col in df.columns if 'einheit' in col or 'unit' in col), None)
    
    # Neue Kiste erstellen
    new_box = {
        "id": str(uuid.uuid4())[:8],
        "template": box_template,
        "name": f"{box_template['name']} #{len(st.session_state.custom_boxes.get(kistentyp_key, [])) + 1}",
        "articles": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Aus Upload",
        "fill_source": "Upload"
    }
    
    added_count = 0
    
    for _, row in df.iterrows():
        artikel_name = str(row[artikel_col]).strip()
        if not artikel_name or artikel_name.lower() == 'nan':
            continue
        
        # Suche Artikel im Stamm
        found_article = None
        for article in st.session_state.articles:
            if article['bezeichnung'].lower() == artikel_name.lower():
                found_article = article.copy()
                break
        
        # Wenn nicht gefunden, erstelle neuen Eintrag
        if found_article:
            article_entry = found_article
        else:
            # Neuer Artikel aus Upload
            article_entry = {
                'sid': f"UPLOAD_{added_count:03d}",
                'bezeichnung': artikel_name,
                'art_nr': 'UPLOAD',
                'einheit': str(row[einheit_col]) if einheit_col and pd.notna(row[einheit_col]) else 'Stueck',
                'ean13': ''
            }
        
        # Menge hinzufuegen wenn vorhanden
        if menge_col and pd.notna(row[menge_col]):
            try:
                menge = int(float(row[menge_col]))
                article_entry['upload_menge'] = menge
            except:
                article_entry['upload_menge'] = 1
        else:
            article_entry['upload_menge'] = 1
        
        new_box['articles'].append(article_entry)
        added_count += 1
    
    if added_count == 0:
        return None, "Keine gueltigen Artikel im Upload gefunden"
    
    # Kiste speichern
    if kistentyp_key not in st.session_state.custom_boxes:
        st.session_state.custom_boxes[kistentyp_key] = []
    st.session_state.custom_boxes[kistentyp_key].append(new_box)
    
    return new_box, None

# =============================================================================
# HILFSFUNKTIONEN - ARTIKEL-SUCHE
# =============================================================================
def get_article_by_sid(sid):
    for article in st.session_state.articles:
        if article['sid'] == sid:
            return article.copy()
    return None

def get_articles_by_category(category):
    sids = CATEGORY_ARTICLE_MAP.get(category, [])
    return [get_article_by_sid(sid) for sid in sids if get_article_by_sid(sid)]

# =============================================================================
# NEUE FUNKTIONEN - KISTEN-HISTORIE & VORLAGEN
# =============================================================================
def learn_from_history(kistentyp_key):
    if kistentyp_key not in st.session_state.kisten_historie:
        return []
    
    historie = st.session_state.kisten_historie[kistentyp_key]
    article_counter = Counter()
    for eintrag in historie:
        article_counter[eintrag['sid']] += eintrag.get('menge', 1)
    
    most_common = [sid for sid, count in article_counter.most_common()]
    log_debug(f"Historie fuer {kistentyp_key}: {len(most_common)} Artikel gefunden")
    return most_common

def fill_box_from_history(box, kistentyp_key, target_count=None):
    if target_count is None:
        target_count = box['template'].get('articles', 10)
    
    existing_sids = {a['sid'] for a in box['articles']}
    
    template_sids = []
    if kistentyp_key in st.session_state.box_templates:
        template_sids = st.session_state.box_templates[kistentyp_key].get('artikel', [])
        log_debug(f"Vorlage fuer {kistentyp_key}: {len(template_sids)} Artikel")
    
    history_sids = learn_from_history(kistentyp_key)
    category = box['template'].get('category', 'Familienkisten')
    fallback_sids = CATEGORY_ARTICLE_MAP.get(category, [])
    
    all_sids = []
    seen = set()
    
    for sid in template_sids + history_sids + fallback_sids:
        if sid not in seen and sid not in existing_sids:
            all_sids.append(sid)
            seen.add(sid)
    
    added_count = 0
    for sid in all_sids:
        if len(box['articles']) >= target_count:
            break
        
        article = get_article_by_sid(sid)
        if article:
            box['articles'].append(article)
            added_count += 1
    
    if added_count > 0:
        box['status'] = 'Befuellt'
    
    log_debug(f"Kiste {box['name']}: {added_count} Artikel hinzugefuegt (Ziel: {target_count})")
    return added_count

# =============================================================================
# NEUE AUTO-FILL FUNKTION MIT PRIORITAET
# =============================================================================
def auto_fill_with_priority(kistentyp_key, box_template):
    """
    Auto-Fill mit Prioritaet:
    1. JSON Pool (wenn vorhanden)
    2. Benutzerdefinierte Vorlage
    3. Kisten-Historie
    4. Kategorie-Standard
    """
    if kistentyp_key not in st.session_state.custom_boxes:
        st.session_state.custom_boxes[kistentyp_key] = []
    
    new_box = {
        "id": str(uuid.uuid4())[:8],
        "template": box_template,
        "name": f"{box_template['name']} #{len(st.session_state.custom_boxes[kistentyp_key]) + 1}",
        "articles": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Neu",
        "fill_source": "Automatisch"
    }
    
    target_count = box_template.get('articles', 10)
    filled = False
    
    # Prioritaet 1: JSON Pool (wenn vorhanden fuer diesen Kistentyp)
    if kistentyp_key in st.session_state.json_pools:
        pool_data = st.session_state.json_pools[kistentyp_key]
        pool_artikel = generate_from_pool(pool_data, anzahl_artikel=target_count)
        
        if pool_artikel:
            for art in pool_artikel:
                new_box['articles'].append({
                    'sid': art.get('name', 'UNKNOWN')[:20],
                    'bezeichnung': art.get('name', 'Unbekannt'),
                    'art_nr': 'POOL',
                    'einheit': art.get('kategorie', 'Stueck'),
                    'herkunft': art.get('herkunft', ''),
                    'haeufigkeit': art.get('haeufigkeit', 0)
                })
            new_box['fill_source'] = "JSON Pool"
            new_box['status'] = "Aus Pool"
            filled = True
            log_debug(f"Auto-Fill aus JSON Pool: {len(pool_artikel)} Artikel")
    
    # Prioritaet 2: Benutzerdefinierte Vorlage
    if not filled and kistentyp_key in st.session_state.box_templates:
        template_sids = st.session_state.box_templates[kistentyp_key].get('artikel', [])
        for sid in template_sids[:target_count]:
            article = get_article_by_sid(sid)
            if article:
                new_box['articles'].append(article)
        
        if new_box['articles']:
            new_box['fill_source'] = "Vorlage"
            new_box['status'] = "Aus Vorlage"
            filled = True
            log_debug(f"Auto-Fill aus Vorlage: {len(new_box['articles'])} Artikel")
    
    # Prioritaet 3: Kisten-Historie
    if not filled and kistentyp_key in st.session_state.kisten_historie:
        history_sids = learn_from_history(kistentyp_key)
        for sid in history_sids[:target_count]:
            article = get_article_by_sid(sid)
            if article:
                new_box['articles'].append(article)
        
        if new_box['articles']:
            new_box['fill_source'] = "Historie"
            new_box['status'] = "Aus Historie"
            filled = True
            log_debug(f"Auto-Fill aus Historie: {len(new_box['articles'])} Artikel")
    
    # Prioritaet 4: Kategorie-Standard
    if not filled:
        category = box_template.get('category', 'Familienkisten')
        fallback_sids = CATEGORY_ARTICLE_MAP.get(category, [])
        for sid in fallback_sids[:target_count]:
            article = get_article_by_sid(sid)
            if article:
                new_box['articles'].append(article)
        
        if new_box['articles']:
            new_box['fill_source'] = "Kategorie-Standard"
            new_box['status'] = "Standard"
            log_debug(f"Auto-Fill aus Kategorie: {len(new_box['articles'])} Artikel")
    
    st.session_state.custom_boxes[kistentyp_key].append(new_box)
    save_box_to_history(kistentyp_key, new_box)
    
    return new_box

def save_box_to_history(kistentyp_key, box):
    if kistentyp_key not in st.session_state.kisten_historie:
        st.session_state.kisten_historie[kistentyp_key] = []
    
    for article in box['articles']:
        historie_eintrag = {
            'sid': article['sid'],
            'bezeichnung': article['bezeichnung'],
            'menge': 1,
            'datum': datetime.now().strftime("%Y-%m-%d"),
            'kistentyp': box['template']['name']
        }
        st.session_state.kisten_historie[kistentyp_key].append(historie_eintrag)
    
    log_debug(f"Historie aktualisiert: {kistentyp_key} (+{len(box['articles'])} Eintraege)")

def import_history_from_dataframe(df):
    required_cols = ['Kistentyp', 'Artikel', 'Menge', 'Datum']
    
    df_cols_lower = [c.lower() for c in df.columns]
    for req in required_cols:
        if req.lower() not in df_cols_lower:
            return False, f"Fehlende Spalte: {req}"
    
    col_mapping = {}
    for req in required_cols:
        for col in df.columns:
            if col.lower() == req.lower():
                col_mapping[req] = col
                break
    
    imported_count = 0
    
    for _, row in df.iterrows():
        kistentyp = str(row[col_mapping['Kistentyp']])
        artikel_bez = str(row[col_mapping['Artikel']])
        menge = int(row[col_mapping['Menge']]) if pd.notna(row[col_mapping['Menge']]) else 1
        datum = str(row[col_mapping['Datum']])
        
        sid = None
        for article in st.session_state.articles:
            if article['bezeichnung'].lower() == artikel_bez.lower():
                sid = article['sid']
                break
        
        if sid:
            if kistentyp not in st.session_state.kisten_historie:
                st.session_state.kisten_historie[kistentyp] = []
            
            st.session_state.kisten_historie[kistentyp].append({
                'sid': sid,
                'bezeichnung': artikel_bez,
                'menge': menge,
                'datum': datum,
                'kistentyp': kistentyp
            })
            imported_count += 1
    
    log_debug(f"Historie importiert: {imported_count} Eintraege")
    return True, f"{imported_count} Historie-Eintraege importiert"

def create_template_from_history(kistentyp_key, top_n=10):
    history_sids = learn_from_history(kistentyp_key)
    
    if not history_sids:
        return None
    
    template = {
        'artikel': history_sids[:top_n],
        'letzte_aenderung': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'quelle': 'Historie',
        'anzahl_artikel': len(history_sids[:top_n])
    }
    
    return template

def export_templates():
    return json.dumps(st.session_state.box_templates, indent=2, ensure_ascii=False)

def import_templates(json_data):
    try:
        templates = json.loads(json_data)
        st.session_state.box_templates.update(templates)
        return True, f"{len(templates)} Vorlagen importiert"
    except Exception as e:
        return False, str(e)

# =============================================================================
# NEUE FUNKTION: ARTIKELSTAMM IMPORT (Excel + CSV)
# =============================================================================
def import_articles_from_dataframe(df, skip_duplicates=True):
    """
    Importiert Artikel aus einem DataFrame (Excel oder CSV) und erweitert den Artikelstamm.
    """
    required_cols = ['sid', 'ean13', 'art_nr', 'bezeichnung', 'einheit']
    
    df_cols_lower = [c.lower() for c in df.columns]
    missing_cols = []
    for req in required_cols:
        if req.lower() not in df_cols_lower:
            missing_cols.append(req)
    
    if missing_cols:
        return False, f"Fehlende Spalten: {', '.join(missing_cols)}", 0
    
    col_mapping = {}
    for req in required_cols:
        for col in df.columns:
            if col.lower() == req.lower():
                col_mapping[req] = col
                break
    
    existing_sids = {a['sid'] for a in st.session_state.articles}
    
    imported_count = 0
    skipped_count = 0
    
    for _, row in df.iterrows():
        sid = str(row[col_mapping['sid']]).strip()
        
        if sid in existing_sids:
            if skip_duplicates:
                skipped_count += 1
                continue
        
        new_article = {
            'sid': sid,
            'ean13': str(row[col_mapping['ean13']]).strip(),
            'art_nr': str(row[col_mapping['art_nr']]).strip(),
            'bezeichnung': str(row[col_mapping['bezeichnung']]).strip(),
            'einheit': str(row[col_mapping['einheit']]).strip()
        }
        
        st.session_state.articles.append(new_article)
        imported_count += 1
        existing_sids.add(sid)
    
    log_debug(f"Artikelstamm-Import: {imported_count} importiert, {skipped_count} uebersprungen")
    
    if skipped_count > 0:
        return True, f"{imported_count} Artikel importiert, {skipped_count} Duplikate uebersprungen", imported_count
    else:
        return True, f"{imported_count} Artikel erfolgreich importiert", imported_count

def get_csv_template():
    """Erstellt eine CSV-Vorlage fuer den Artikelstamm-Import."""
    template_csv = "sid;ean13;art_nr;bezeichnung;einheit\n"
    template_csv += "SID093;400000000093;OB041;Beispiel Artikel;kg\n"
    template_csv += "SID094;400000000094;OB042;Weiterer Artikel;Stueck\n"
    return template_csv.encode('utf-8')

def read_uploaded_file(uploaded_file):
    """
    Liest eine hochgeladene Datei (Excel oder CSV) und gibt ein DataFrame zurueck.
    Gibt None zurueck, wenn ein Fehler auftritt.
    """
    try:
        if uploaded_file.name.endswith('.xlsx'):
            try:
                import openpyxl
                df = pd.read_excel(uploaded_file)
                return df, None
            except ImportError:
                return None, "openpyxl nicht verfuegbar. Bitte verwenden Sie CSV-Dateien."
            except Exception as e:
                return None, f"Fehler beim Lesen der Excel-Datei: {str(e)}"
        elif uploaded_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, sep=';')
                return df, None
            except Exception as e:
                return None, f"Fehler beim Lesen der CSV-Datei: {str(e)}"
        else:
            return None, "Nicht unterstuetztes Dateiformat. Bitte verwenden Sie .xlsx oder .csv"
    except Exception as e:
        return None, f"Unerwarteter Fehler: {str(e)}"

# =============================================================================
# BESTEHENDE HILFSFUNKTIONEN
# =============================================================================
def log_debug(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.debug_logs.append({"timestamp": timestamp, "level": level, "message": message})
    if len(st.session_state.debug_logs) > 100:
        st.session_state.debug_logs = st.session_state.debug_logs[-100:]

def add_new_box(kistentyp_key, box_template):
    if kistentyp_key not in st.session_state.custom_boxes:
        st.session_state.custom_boxes[kistentyp_key] = []
    
    new_box = {
        "id": str(uuid.uuid4())[:8],
        "template": box_template,
        "name": f"{box_template['name']} #{len(st.session_state.custom_boxes[kistentyp_key]) + 1}",
        "articles": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Neu"
    }
    st.session_state.custom_boxes[kistentyp_key].append(new_box)
    log_debug(f"Neue Kiste erstellt: {new_box['name']}")
    return new_box

def delete_box(kistentyp_key, box_id):
    if kistentyp_key in st.session_state.custom_boxes:
        st.session_state.custom_boxes[kistentyp_key] = [
            b for b in st.session_state.custom_boxes[kistentyp_key] if b['id'] != box_id
        ]
        log_debug(f"Kiste geloescht: {box_id}")

def update_box_name(kistentyp_key, box_id, new_name):
    if kistentyp_key in st.session_state.custom_boxes:
        for box in st.session_state.custom_boxes[kistentyp_key]:
            if box['id'] == box_id:
                box['name'] = new_name
                break

def add_article_to_box(kistentyp_key, box_id, article):
    if kistentyp_key in st.session_state.custom_boxes:
        for box in st.session_state.custom_boxes[kistentyp_key]:
            if box['id'] == box_id:
                box['articles'].append(article)
                break

def remove_article_from_box(kistentyp_key, box_id, article_sid):
    if kistentyp_key in st.session_state.custom_boxes:
        for box in st.session_state.custom_boxes[kistentyp_key]:
            if box['id'] == box_id:
                box['articles'] = [a for a in box['articles'] if a['sid'] != article_sid]
                break

# =============================================================================
# KIMI CODE ASSISTANT FUNKTIONEN
# =============================================================================
def analyze_code(code):
    issues = []
    warnings = []
    suggestions = []
    
    if not code.strip():
        return {'issues': ['Kein Code eingegeben'], 'warnings': [], 'suggestions': [], 'score': 0}
    
    lines = code.split('\n')
    
    import_lines = [i for i, line in enumerate(lines) if line.strip().startswith('import ') or line.strip().startswith('from ')]
    if import_lines and import_lines[0] > 0:
        issues.append("Imports stehen nicht am Anfang")
        suggestions.append("Verschiebe alle Imports nach ganz oben")
    
    widget_patterns = [
        (r'st\.slider\([^)]*\)(?!.*key=)', "Slider ohne key"),
        (r'st\.button\([^)]*\)(?!.*key=)', "Button ohne key"),
        (r'st\.selectbox\([^)]*\)(?!.*key=)', "Selectbox ohne key"),
    ]
    
    for pattern, desc in widget_patterns:
        matches = re.findall(pattern, code)
        if matches:
            issues.append(f"{desc} ({len(matches)}x)")
            suggestions.append(f"Fuege key=f'unique_{{st.session_state.session_id}}' hinzu")
    
    umlauts = re.findall(r'[äöüÄÖÜß]', code)
    if umlauts:
        warnings.append(f"Umlaute: {set(umlauts)}")
        suggestions.append("Ersetze ae, oe, ue, ss")
    
    if 'EUR' in code:
        warnings.append("EUR statt Euro-Zeichen")
    
    if 'session_id' not in code and 'key=' in code:
        warnings.append("Keys ohne session_id")
        suggestions.append("Fuege session_id Initialisierung hinzu")
    
    score = max(0, 10 - len(issues)*2 - len(warnings))
    
    return {'issues': issues, 'warnings': warnings, 'suggestions': suggestions, 'score': score}

def generate_quick_fix(code):
    fixed = code
    
    if 'session_id' not in fixed:
        fixed = "import uuid\n\nif 'session_id' not in st.session_state:\n    st.session_state.session_id = str(uuid.uuid4())[:8]\n\n" + fixed
    
    umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ß': 'ss'}
    for old, new in umlaut_map.items():
        fixed = fixed.replace(old, new)
    
    return fixed

# =============================================================================
# NAVIGATION
# =============================================================================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Navigation",
    ["Startseite", "Kistengenerator", "Kisten-Vorlagen", "Artikelstamm", "Import/Export", "Kimi Assistant", "Backup & Versionen", "Einstellungen"],
    key=f"nav_radio_{st.session_state.session_id}"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Kategorie Filter")
all_categories = ["Alle"] + list(PARADIESCHEN_KISTENTYPEN.keys())
st.session_state.selected_category = st.sidebar.selectbox(
    "Kategorie",
    all_categories,
    key=f"cat_select_{st.session_state.session_id}"
)

# Backup-Status in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Status")
total_custom_boxes = sum(len(boxes) for boxes in st.session_state.custom_boxes.values())
st.sidebar.write(f"📦 Erstellte Kisten: **{total_custom_boxes}**")
st.sidebar.write(f"📋 Vorlagen: **{len(st.session_state.box_templates)}**")
st.sidebar.write(f"📜 Historie: **{sum(len(h) for h in st.session_state.kisten_historie.values())}**")

# Pool-Status anzeigen
pool_count = len(st.session_state.json_pools)
if pool_count > 0:
    st.sidebar.success(f"📜 JSON Pools: {pool_count}")
else:
    st.sidebar.info("📜 JSON Pools: 0")

if st.session_state.last_backup_time:
    st.sidebar.success(f"💾 Backup: {st.session_state.last_backup_time}")
else:
    st.sidebar.warning("💾 Noch kein Backup")

# =============================================================================
# STARTSEITE
# =============================================================================
if page == "Startseite":
    st.markdown("""
    <div class='main-header'>
        <h1>Paradieschen Kistengenerator</h1>
        <p>Alle 85+ originalen Kistentypen mit Upload-Funktion fuer alle Kistentypen</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_custom_boxes = sum(len(boxes) for boxes in st.session_state.custom_boxes.values())
    total_historie = sum(len(h) for h in st.session_state.kisten_historie.values())
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_kisten = sum(len(v) for v in PARADIESCHEN_KISTENTYPEN.values())
        st.metric("Kistentypen", total_kisten)
    with col2:
        st.metric("Artikel im Stamm", len(st.session_state.articles))
    with col3:
        st.metric("Erstellte Kisten", total_custom_boxes)
    with col4:
        st.metric("Historie-Eintraege", total_historie)
    with col5:
        st.metric("JSON Pools", len(st.session_state.json_pools))
    
    st.markdown("---")
    
    # Schnellstart: Pool Upload
    if len(st.session_state.json_pools) == 0:
        st.markdown("""
        <div class='pool-header'>
            <h3>🚀 Schnellstart: JSON Pool hochladen</h3>
            <p>Lade eine JSON Pool-Datei hoch, um mit dem Pool-Generator zu starten!</p>
        </div>
        """, unsafe_allow_html=True)
        
        quick_pool = st.file_uploader("JSON Pool hier ablegen", type=["json"], key=f"quick_pool_{st.session_state.session_id}")
        if quick_pool:
            pool_data, error = load_json_pool(quick_pool)
            if error:
                st.error(error)
            else:
                kistentyp = pool_data.get('kistentyp', 'Unbekannt')
                st.session_state.json_pools[kistentyp] = pool_data
                st.success(f"✅ Pool geladen: {kistentyp} mit {pool_data.get('gesamt_artikel', 0)} Artikeln!")
                st.rerun()
    
    st.subheader("Verfuegbare Kistentypen")
    
    for category, boxes in PARADIESCHEN_KISTENTYPEN.items():
        if st.session_state.selected_category == "Alle" or st.session_state.selected_category == category:
            with st.expander(f"📦 {category} ({len(boxes)} Varianten)"):
                for box in boxes:
                    kistentyp_key = f"{category}_{box['name']}".replace(" ", "_").replace(".", "")
                    has_template = "✅" if kistentyp_key in st.session_state.box_templates else "❌"
                    has_history = "📜" if kistentyp_key in st.session_state.kisten_historie else ""
                    has_pool = "📜" if kistentyp_key in st.session_state.json_pools else ""
                    
                    st.markdown(f"""
                    <div class='box-card'>
                        <strong>{box['name']}</strong> {has_template} {has_history} {has_pool}<br>
                        <small>Groesse: {box['size']} | Artikel: {box['articles']} | 
                        <span class='price-tag'>{box['base_price']:.2f} EUR</span></small>
                    </div>
                    """, unsafe_allow_html=True)

# =============================================================================
# KISTENGENERATOR - NEU MIT UPLOAD FUER ALLE KISTENTYPEN
# =============================================================================
elif page == "Kistengenerator":
    st.markdown("""
    <div class='main-header'>
        <h1>Kistengenerator</h1>
        <p>Erstelle Kisten mit Upload-Funktion fuer alle Kistentypen</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info zur neuen Prioritaet (ohne alte UI-Elemente)
    st.markdown("""
    <div class='info-box'>
        <strong>🔄 Auto-Fill Prioritaet:</strong> JSON Pool → Benutzerdefinierte Vorlage → Kisten-Historie → Kategorie-Standard
    </div>
    """, unsafe_allow_html=True)
    
    filtered_categories = {}
    for category, boxes in PARADIESCHEN_KISTENTYPEN.items():
        if st.session_state.selected_category == "Alle" or st.session_state.selected_category == category:
            filtered_categories[category] = boxes
    
    for category, boxes in filtered_categories.items():
        with st.expander(f"📦 {category}", expanded=True):
            for box_template in boxes:
                kistentyp_key = f"{category}_{box_template['name']}".replace(" ", "_").replace(".", "")
                
                has_template = kistentyp_key in st.session_state.box_templates
                has_history = kistentyp_key in st.session_state.kisten_historie
                has_pool = kistentyp_key in st.session_state.json_pools
                
                status_icons = ""
                if has_pool:
                    status_icons += "📜 "
                if has_template:
                    status_icons += "📋 "
                if has_history:
                    status_icons += "📜 "
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class='box-card' style='margin: 0.5rem 0;'>
                        <strong>{status_icons}{box_template['name']}</strong><br>
                        <small>Groesse: {box_template['size']} | Artikel: {box_template['articles']} | Basispreis: {box_template['base_price']:.2f} EUR</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # NEU: Upload-Button fuer alle Kistentypen
                    if st.button("📤 Upload", key=f"upload_btn_{kistentyp_key}_{st.session_state.session_id}", use_container_width=True):
                        st.session_state[f"show_upload_{kistentyp_key}"] = True
                
                with col3:
                    # Auto-Fill Button mit neuer Prioritaet
                    fill_source = "Pool" if has_pool else "Vorlage" if has_template else "Historie" if has_history else "Standard"
                    if st.button(f"✨ Auto-Fill", key=f"add_auto_{kistentyp_key}_{st.session_state.session_id}", use_container_width=True):
                        new_box = auto_fill_with_priority(kistentyp_key, box_template)
                        st.success(f"{box_template['name']} mit {len(new_box['articles'])} Artikeln ({new_box['fill_source']}) erstellt!")
                        st.rerun()
                
                with col4:
                    count = len(st.session_state.custom_boxes.get(kistentyp_key, []))
                    st.metric("Kisten", count, label_visibility="collapsed")
                
                # NEU: Upload-Bereich fuer diesen Kistentyp
                if st.session_state.get(f"show_upload_{kistentyp_key}", False):
                    with st.container():
                        st.markdown("---")
                        st.markdown(f"**📤 Daten fuer {box_template['name']} hochladen**")
                        
                        upload_col1, upload_col2 = st.columns(2)
                        
                        with upload_col1:
                            # Datei-Upload
                            uploaded_file = st.file_uploader(
                                "Excel oder CSV",
                                type=["xlsx", "csv"],
                                key=f"file_{kistentyp_key}_{st.session_state.session_id}"
                            )
                        
                        with upload_col2:
                            # Text-Eingabe (Paste)
                            text_input = st.text_area(
                                "Oder Text einfuegen (CSV-Format)",
                                placeholder="Artikel;Menge;Einheit\nAepfel;2;kg\nBananen;1;kg",
                                height=100,
                                key=f"text_{kistentyp_key}_{st.session_state.session_id}"
                            )
                        
                        # Drag & Drop Hinweis
                        st.markdown("""
                        <div class='upload-area'>
                            <p>📁 Drag & Drop unterstuetzt</p>
                            <p><small>Erwartetes Format: Artikel | Menge | Einheit</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_process, col_cancel = st.columns(2)
                        
                        with col_process:
                            if st.button("✅ Verarbeiten", key=f"process_{kistentyp_key}_{st.session_state.session_id}", use_container_width=True):
                                df, error = parse_uploaded_data(uploaded_file, text_input if text_input.strip() else None)
                                
                                if error:
                                    st.error(error)
                                else:
                                    new_box, error = process_upload_for_kistentyp(kistentyp_key, df, box_template)
                                    if error:
                                        st.error(error)
                                    else:
                                        st.success(f"✅ {len(new_box['articles'])} Artikel aus Upload hinzugefuegt!")
                                        st.session_state[f"show_upload_{kistentyp_key}"] = False
                                        st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ Abbrechen", key=f"cancel_{kistentyp_key}_{st.session_state.session_id}", use_container_width=True):
                                st.session_state[f"show_upload_{kistentyp_key}"] = False
                                st.rerun()
                        
                        st.markdown("---")
                
                # Bestehende Kisten anzeigen (nur wenn vorhanden)
                if kistentyp_key in st.session_state.custom_boxes and st.session_state.custom_boxes[kistentyp_key]:
                    st.markdown("---")
                    st.markdown("**Erstellte Kisten:**")
                    
                    for i, box in enumerate(st.session_state.custom_boxes[kistentyp_key]):
                        with st.container():
                            col_info, col_actions = st.columns([4, 1])
                            
                            with col_info:
                                new_name = st.text_input(
                                    "Kistenname",
                                    value=box['name'],
                                    key=f"name_{box['id']}_{st.session_state.session_id}",
                                    label_visibility="collapsed"
                                )
                                if new_name != box['name']:
                                    update_box_name(kistentyp_key, box['id'], new_name)
                                
                                fill_info = box.get('fill_source', 'Manuell')
                                st.markdown(f"<small>Erstellt: {box['created_at']} | Status: {box['status']} | Quelle: {fill_info}</small>", unsafe_allow_html=True)
                                
                                if box['articles']:
                                    st.markdown(f"**Artikel ({len(box['articles'])}):**")
                                    for article in box['articles']:
                                        herkunft = article.get('herkunft', '')
                                        herkunft_str = f" ({herkunft})" if herkunft else ""
                                        haeufigkeit = article.get('haeufigkeit', 0)
                                        haeufigkeit_str = f" [{haeufigkeit}x]" if haeufigkeit > 0 else ""
                                        menge = article.get('upload_menge', 1)
                                        menge_str = f" x{menge}" if menge > 1 else ""
                                        
                                        # Unterschiedliche Styles je nach Quelle
                                        if article.get('art_nr') == 'POOL':
                                            css_class = 'pool-item'
                                        elif article.get('art_nr') == 'UPLOAD':
                                            css_class = 'history-item'
                                        else:
                                            css_class = 'article-item'
                                        
                                        st.markdown(f"<span class='{css_class}'>{article['bezeichnung']}{menge_str}{herkunft_str}{haeufigkeit_str}</span>", unsafe_allow_html=True)
                                else:
                                    st.info("Noch keine Artikel hinzugefuegt")
                            
                            with col_actions:
                                if st.button("➕ Artikel", key=f"add_art_{box['id']}_{st.session_state.session_id}"):
                                    st.session_state[f"show_add_article_{box['id']}"] = True
                                
                                if st.button("🗑️", key=f"del_{box['id']}_{st.session_state.session_id}"):
                                    delete_box(kistentyp_key, box['id'])
                                    st.rerun()
                                
                                if st.button("📜 +Hist", key=f"add_hist_{box['id']}_{st.session_state.session_id}"):
                                    save_box_to_history(kistentyp_key, box)
                                    st.success("Zur Historie hinzugefuegt!")
                                    st.rerun()
                            
                            # Artikel hinzufuegen Dialog
                            if st.session_state.get(f"show_add_article_{box['id']}", False):
                                with st.container():
                                    st.markdown("**Artikel zur Kiste hinzufuegen:**")
                                    
                                    article_options = {f"{a['bezeichnung']} ({a['art_nr']})": a for a in st.session_state.articles}
                                    selected_article_label = st.selectbox(
                                        "Artikel waehlen",
                                        options=list(article_options.keys()),
                                        key=f"select_art_{box['id']}_{st.session_state.session_id}"
                                    )
                                    
                                    col_add, col_cancel = st.columns(2)
                                    with col_add:
                                        if st.button("Hinzufuegen", key=f"confirm_add_{box['id']}_{st.session_state.session_id}"):
                                            add_article_to_box(kistentyp_key, box['id'], article_options[selected_article_label])
                                            st.session_state[f"show_add_article_{box['id']}"] = False
                                            st.rerun()
                                    
                                    with col_cancel:
                                        if st.button("Abbrechen", key=f"cancel_add_{box['id']}_{st.session_state.session_id}"):
                                            st.session_state[f"show_add_article_{box['id']}"] = False
                                            st.rerun()
                            
                            # Artikel entfernen
                            if box['articles']:
                                st.markdown("**Artikel entfernen:**")
                                cols = st.columns(min(len(box['articles']), 4))
                                for idx, article in enumerate(box['articles']):
                                    with cols[idx % 4]:
                                        if st.button(f"❌ {article['bezeichnung'][:15]}", key=f"rem_{box['id']}_{article['sid']}_{st.session_state.session_id}"):
                                            remove_article_from_box(kistentyp_key, box['id'], article['sid'])
                                            st.rerun()
                    
                    st.markdown("---")

# =============================================================================
# KISTEN-VORLAGEN
# =============================================================================
elif page == "Kisten-Vorlagen":
    st.markdown("""
    <div class='template-header'>
        <h1>Kisten-Vorlagen</h1>
        <p>Definiere feste Artikel-Zusammensetzungen fuer jeden Kistentyp</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Vorlagen verwalten", "Historie importieren", "Vorlage bearbeiten", "Export/Import"])
    
    with tab1:
        st.subheader("Vorlagen-Uebersicht")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vorlagen gesamt", len(st.session_state.box_templates))
        with col2:
            vorlagen_mit_historie = sum(1 for k, v in st.session_state.box_templates.items() if v.get('quelle') == 'Historie')
            st.metric("Aus Historie", vorlagen_mit_historie)
        with col3:
            vorlagen_manuell = sum(1 for k, v in st.session_state.box_templates.items() if v.get('quelle') != 'Historie')
            st.metric("Manuell erstellt", vorlagen_manuell)
        
        st.markdown("---")
        
        if st.session_state.box_templates:
            for kistentyp_key, template in st.session_state.box_templates.items():
                with st.expander(f"📋 {kistentyp_key}"):
                    st.write(f"**Quelle:** {template.get('quelle', 'Unbekannt')}")
                    st.write(f"**Letzte Aenderung:** {template.get('letzte_aenderung', 'Unbekannt')}")
                    st.write(f"**Artikel-Anzahl:** {template.get('anzahl_artikel', len(template.get('artikel', [])))}")
                    
                    st.markdown("**Artikel in der Vorlage:**")
                    for sid in template.get('artikel', []):
                        article = get_article_by_sid(sid)
                        if article:
                            st.markdown(f"<span class='template-item'>{article['bezeichnung']} ({article['art_nr']})</span>", unsafe_allow_html=True)
                    
                    if st.button("Vorlage loeschen", key=f"del_tpl_{kistentyp_key}_{st.session_state.session_id}"):
                        del st.session_state.box_templates[kistentyp_key]
                        st.success("Vorlage geloescht!")
                        st.rerun()
        else:
            st.info("Noch keine Vorlagen vorhanden.")
    
    with tab2:
        st.subheader("Kisten-Historie als Vorlage importieren")
        
        st.markdown("""
        <div class='info-box'>
            <strong>Erwartetes Format:</strong><br>
            Excel oder CSV mit Spalten: <code>Kistentyp | Artikel | Menge | Datum</code>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Historie-Datei hochladen", type=["xlsx", "csv"], key=f"hist_upload_{st.session_state.session_id}")
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                
                st.write("**Vorschau der Datei:**")
                st.dataframe(df.head(10), use_container_width=True)
                st.write(f"**Gesamtzeilen:** {len(df)}")
                
                if st.button("Historie importieren", key=f"import_hist_btn_{st.session_state.session_id}"):
                    success, message = import_history_from_dataframe(df)
                    if success:
                        st.success(message)
                        
                        if st.checkbox("Automatisch Vorlagen aus Historie erstellen", value=True, key=f"auto_tpl_{st.session_state.session_id}"):
                            created = 0
                            for kistentyp_key in st.session_state.kisten_historie.keys():
                                template = create_template_from_history(kistentyp_key, top_n=10)
                                if template:
                                    st.session_state.box_templates[kistentyp_key] = template
                                    created += 1
                            st.success(f"{created} Vorlagen automatisch erstellt!")
                        
                        st.rerun()
                    else:
                        st.error(f"Fehler: {message}")
                
            except Exception as e:
                st.error(f"Fehler beim Lesen der Datei: {str(e)}")
        
        st.markdown("---")
        st.subheader("Oder: Historie manuell eingeben")
        
        col1, col2 = st.columns(2)
        with col1:
            hist_kistentyp = st.selectbox(
                "Kistentyp",
                [f"{cat}_{box['name']}".replace(" ", "_").replace(".", "") 
                 for cat, boxes in PARADIESCHEN_KISTENTYPEN.items() for box in boxes],
                key=f"hist_ktype_{st.session_state.session_id}"
            )
        with col2:
            hist_artikel = st.selectbox(
                "Artikel",
                [f"{a['bezeichnung']} ({a['sid']})" for a in st.session_state.articles],
                key=f"hist_art_{st.session_state.session_id}"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            hist_menge = st.number_input("Menge", min_value=1, value=1, key=f"hist_menge_{st.session_state.session_id}")
        with col4:
            hist_datum = st.date_input("Datum", datetime.now(), key=f"hist_datum_{st.session_state.session_id}")
        
        if st.button("Zur Historie hinzufuegen", key=f"add_hist_manual_{st.session_state.session_id}"):
            if hist_kistentyp not in st.session_state.kisten_historie:
                st.session_state.kisten_historie[hist_kistentyp] = []
            
            selected_sid = hist_artikel.split("(")[1].replace(")", "")
            selected_bez = hist_artikel.split(" (")[0]
            
            st.session_state.kisten_historie[hist_kistentyp].append({
                'sid': selected_sid,
                'bezeichnung': selected_bez,
                'menge': hist_menge,
                'datum': hist_datum.strftime("%Y-%m-%d"),
                'kistentyp': hist_kistentyp
            })
            
            st.success("Zur Historie hinzugefuegt!")
            st.rerun()
    
    with tab3:
        st.subheader("Vorlage manuell erstellen/bearbeiten")
        
        alle_kistentypen = []
        for cat, boxes in PARADIESCHEN_KISTENTYPEN.items():
            for box in boxes:
                kistentyp_key = f"{cat}_{box['name']}".replace(" ", "_").replace(".", "")
                alle_kistentypen.append((kistentyp_key, f"{cat} - {box['name']}"))
        
        selected_tpl = st.selectbox(
            "Kistentyp waehlen",
            options=[k for k, _ in alle_kistentypen],
            format_func=lambda x: next((label for k, label in alle_kistentypen if k == x), x),
            key=f"edit_tpl_select_{st.session_state.session_id}"
        )
        
        existing_artikel = []
        if selected_tpl in st.session_state.box_templates:
            existing_artikel = st.session_state.box_templates[selected_tpl].get('artikel', [])
            st.info(f"Bestehende Vorlage mit {len(existing_artikel)} Artikeln geladen")
        
        verfuegbare_artikel = {a['sid']: f"{a['bezeichnung']} ({a['art_nr']})" for a in st.session_state.articles}
        
        selected_artikel = st.multiselect(
            "Artikel fuer die Vorlage",
            options=list(verfuegbare_artikel.keys()),
            default=existing_artikel,
            format_func=lambda x: verfuegbare_artikel.get(x, x),
            key=f"edit_tpl_art_{st.session_state.session_id}"
        )
        
        if st.button("Vorlage speichern", key=f"save_tpl_{st.session_state.session_id}"):
            st.session_state.box_templates[selected_tpl] = {
                'artikel': selected_artikel,
                'letzte_aenderung': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'quelle': 'Manuell',
                'anzahl_artikel': len(selected_artikel)
            }
            st.success(f"Vorlage fuer {selected_tpl} gespeichert!")
            st.rerun()
    
    with tab4:
        st.subheader("Vorlagen Export & Import")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export**")
            if st.button("Vorlagen als JSON exportieren", key=f"export_tpl_{st.session_state.session_id}"):
                json_data = export_templates()
                st.download_button(
                    "JSON herunterladen",
                    json_data,
                    file_name=f"kisten_vorlagen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"dl_tpl_{st.session_state.session_id}"
                )
        
        with col2:
            st.markdown("**Import**")
            tpl_upload = st.file_uploader("Vorlagen-JSON hochladen", type=["json"], key=f"tpl_upload_{st.session_state.session_id}")
            if tpl_upload:
                json_content = tpl_upload.read().decode('utf-8')
                if st.button("Vorlagen importieren", key=f"import_tpl_btn_{st.session_state.session_id}"):
                    success, message = import_templates(json_content)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

# =============================================================================
# ARTIKELSTAMM - ERWEITERT MIT EXCEL/CSV IMPORT
# =============================================================================
elif page == "Artikelstamm":
    st.markdown("""
    <div class='main-header'>
        <h1>Artikelstamm</h1>
        <p>Verwaltung aller verfuegbaren Artikel</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Artikeluebersicht", "Neuer Artikel", "Stammartikel importieren"])
    
    with tab1:
        df = pd.DataFrame(st.session_state.articles)
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        col1.metric("Gesamtartikel", len(df))
        col2.metric("Kategorien", len(df['art_nr'].str[:2].unique()))
    
    with tab2:
        st.subheader("Neuen Artikel anlegen")
        col1, col2 = st.columns(2)
        with col1:
            new_sid = st.text_input("SID", value=f"SID{len(st.session_state.articles)+1:03d}", key=f"new_sid_{st.session_state.session_id}")
            new_ean13 = st.text_input("EAN13", value=f"400000000{len(st.session_state.articles)+1:03d}", key=f"new_ean_{st.session_state.session_id}")
            new_art_nr = st.text_input("Art.Nr.", value=f"ART{len(st.session_state.articles)+1:03d}", key=f"new_artnr_{st.session_state.session_id}")
        with col2:
            new_bezeichnung = st.text_input("Bezeichnung", key=f"new_bez_{st.session_state.session_id}")
            new_einheit = st.selectbox("Einheit", ["kg", "g", "Stueck", "Bund", "Topf", "500g", "250g", "125g", "100g"], key=f"new_unit_{st.session_state.session_id}")
        
        if st.button("Artikel speichern", key=f"save_btn_{st.session_state.session_id}"):
            new_article = {
                "sid": new_sid,
                "ean13": new_ean13,
                "art_nr": new_art_nr,
                "bezeichnung": new_bezeichnung,
                "einheit": new_einheit
            }
            st.session_state.articles.append(new_article)
            log_debug(f"Neuer Artikel angelegt: {new_bezeichnung}")
            st.success(f"Artikel '{new_bezeichnung}' wurde gespeichert!")
    
    with tab3:
        st.subheader("Stammartikel importieren")
        
        st.markdown("""
        <div class='info-box'>
            <strong>Erwartetes Format:</strong><br>
            Excel (.xlsx) oder CSV-Datei mit folgenden Spalten:<br>
            <code>sid | ean13 | art_nr | bezeichnung | einheit</code><br>
            <em>CSV-Dateien muessen mit Semikolon (;) getrennt sein.</em>
        </div>
        """, unsafe_allow_html=True)
        
        # Download-Button fuer CSV-Vorlage
        st.markdown("**Vorlage herunterladen:**")
        template_bytes = get_csv_template()
        st.download_button(
            "📥 CSV-Vorlage herunterladen",
            template_bytes,
            file_name="artikelstamm_vorlage.csv",
            mime="text/csv",
            key=f"dl_template_{st.session_state.session_id}"
        )
        
        st.markdown("---")
        
        # Datei-Upload (Excel + CSV)
        st.markdown("**Datei hochladen:**")
        uploaded_file = st.file_uploader(
            "Excel- oder CSV-Datei mit Artikeln hochladen",
            type=["xlsx", "csv"],
            key=f"article_import_{st.session_state.session_id}"
        )
        
        if uploaded_file:
            # Datei lesen mit der neuen Funktion
            df, error = read_uploaded_file(uploaded_file)
            
            if error:
                st.error(error)
                st.info("💡 Tipp: Verwenden Sie die CSV-Vorlage, wenn Excel nicht funktioniert.")
            elif df is not None:
                st.write("**Vorschau der hochgeladenen Datei:**")
                st.dataframe(df.head(10), use_container_width=True)
                st.write(f"**Gesamtzeilen:** {len(df)}")
                
                # Optionen fuer Import
                skip_duplicates = st.checkbox(
                    "Duplikate (gleiche SID) ueberspringen",
                    value=True,
                    key=f"skip_dup_{st.session_state.session_id}"
                )
                
                if st.button("Artikel importieren", key=f"import_articles_btn_{st.session_state.session_id}"):
                    success, message, count = import_articles_from_dataframe(df, skip_duplicates)
                    
                    if success:
                        st.success(message)
                        
                        # Speichere Import im Verlauf
                        st.session_state.import_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'filename': uploaded_file.name,
                            'count': count,
                            'type': 'Artikelstamm'
                        })
                        
                        st.rerun()
                    else:
                        st.error(message)

# =============================================================================
# IMPORT/EXPORT
# =============================================================================
elif page == "Import/Export":
    st.markdown("""
    <div class='main-header'>
        <h1>Import / Export</h1>
        <p>Excel/CSV Import und Export fuer Artikel</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Artikel importieren", "Export", "Import-Verlauf"])
    
    with tab1:
        st.subheader("Artikel aus Excel/CSV importieren")
        uploaded_file = st.file_uploader("Datei hochladen", type=["xlsx", "csv"], key=f"file_up_{st.session_state.session_id}")
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                st.write("**Vorschau:**")
                st.dataframe(df.head())
                
                st.subheader("Spaltenzuordnung")
                col_mapping = {
                    'sid': st.selectbox("SID-Spalte", df.columns, key=f"map_sid_{st.session_state.session_id}"),
                    'ean13': st.selectbox("EAN13-Spalte", df.columns, key=f"map_ean_{st.session_state.session_id}"),
                    'art_nr': st.selectbox("Art.Nr.-Spalte", df.columns, key=f"map_artnr_{st.session_state.session_id}"),
                    'bezeichnung': st.selectbox("Bezeichnung-Spalte", df.columns, key=f"map_bez_{st.session_state.session_id}"),
                    'einheit': st.selectbox("Einheit-Spalte", df.columns, key=f"map_unit_{st.session_state.session_id}"),
                }
                
                if st.button("Importieren", key=f"imp_btn_{st.session_state.session_id}"):
                    imported_count = 0
                    for _, row in df.iterrows():
                        new_article = {
                            'sid': str(row[col_mapping['sid']]),
                            'ean13': str(row[col_mapping['ean13']]),
                            'art_nr': str(row[col_mapping['art_nr']]),
                            'bezeichnung': str(row[col_mapping['bezeichnung']]),
                            'einheit': str(row[col_mapping['einheit']])
                        }
                        st.session_state.articles.append(new_article)
                        imported_count += 1
                    
                    st.session_state.import_history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'filename': uploaded_file.name,
                        'count': imported_count
                    })
                    log_debug(f"Import: {imported_count} Artikel aus {uploaded_file.name}")
                    st.success(f"{imported_count} Artikel erfolgreich importiert!")
                    
            except Exception as e:
                st.error(f"Fehler beim Import: {str(e)}")
                log_debug(f"Import-Fehler: {str(e)}", "ERROR")
    
    with tab2:
        st.subheader("Export")
        export_format = st.radio("Format", ["Excel", "CSV", "JSON"], key=f"exp_format_{st.session_state.session_id}")
        
        if st.button("Exportieren", key=f"exp_btn_{st.session_state.session_id}"):
            df = pd.DataFrame(st.session_state.articles)
            if export_format == "Excel":
                output = df.to_excel(index=False)
                st.download_button("Excel herunterladen", output, file_name="artikel_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_xlsx_{st.session_state.session_id}")
            elif export_format == "CSV":
                output = df.to_csv(index=False)
                st.download_button("CSV herunterladen", output, file_name="artikel_export.csv", mime="text/csv", key=f"dl_csv_{st.session_state.session_id}")
            else:
                output = json.dumps(st.session_state.articles, indent=2)
                st.download_button("JSON herunterladen", output, file_name="artikel_export.json", mime="application/json", key=f"dl_json_{st.session_state.session_id}")
    
    with tab3:
        st.subheader("Import-Verlauf")
        if st.session_state.import_history:
            history_df = pd.DataFrame(st.session_state.import_history)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("Noch keine Importe durchgefuehrt.")

# =============================================================================
# KIMI ASSISTANT
# =============================================================================
elif page == "Kimi Assistant":
    st.markdown("""
    <div class='main-header'>
        <h1>Kimi Code Assistant</h1>
        <p>Live Code-Analyse mit automatischem Backup</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_code = st.session_state.get('kimi_code_buffer', '')
    if current_code and st.session_state.auto_backup_enabled:
        current_hash = hashlib.md5(current_code.encode()).hexdigest()[:8]
        if current_hash != st.session_state.current_code_hash:
            create_backup(current_code, "auto", "Automatisches Backup vor Bearbeitung")
            st.toast("Auto-Backup erstellt!", icon="✅")
    
    tab1, tab2 = st.tabs(["Code Analyse", "Quick Fix"])
    
    with tab1:
        st.subheader("Code analysieren")
        code_input = st.text_area(
            "Dein Code:",
            value=current_code,
            height=300,
            key=f"code_editor_{st.session_state.session_id}"
        )
        st.session_state.kimi_code_buffer = code_input
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Analysieren", key=f"btn_analyze_{st.session_state.session_id}", use_container_width=True):
                if code_input.strip():
                    if st.session_state.auto_backup_enabled:
                        bid = create_backup(code_input, "pre_change", "Vor Code-Analyse")
                        st.info(f"Backup erstellt: {bid}")
                    
                    result = analyze_code(code_input)
                    st.metric("Code-Qualitaet", f"{result['score']}/10")
                    
                    if result['issues']:
                        st.markdown("### Fehler")
                        for issue in result['issues']:
                            st.markdown(f"<div class='error-box'>{issue}</div>", unsafe_allow_html=True)
                    
                    if result['warnings']:
                        st.markdown("### Warnungen")
                        for warning in result['warnings']:
                            st.markdown(f"<div class='warning-box'>{warning}</div>", unsafe_allow_html=True)
        
        with col2:
            if st.button("Auto-Fix", key=f"btn_fix_{st.session_state.session_id}", use_container_width=True):
                if code_input.strip():
                    create_backup(code_input, "pre_change", "Vor Auto-Fix")
                    fixed = generate_quick_fix(code_input)
                    st.session_state.kimi_code_buffer = fixed
                    st.success("Code bereinigt! (Backup erstellt)")
                    st.rerun()
        
        with col3:
            if st.button("Backup erstellen", key=f"btn_backup_{st.session_state.session_id}", use_container_width=True):
                if code_input.strip():
                    bid = create_backup(code_input, "manual", "Manuelles Backup")
                    st.success(f"Backup erstellt: {bid}")

# =============================================================================
# BACKUP & VERSIONEN
# =============================================================================
elif page == "Backup & Versionen":
    st.markdown("""
    <div class='backup-panel'>
        <h1>Backup & Versionskontrolle</h1>
        <p>Verwalte alle Code-Versionen und stelle sie wieder her</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gesamt Backups", len(st.session_state.code_backups))
    with col2:
        manual_count = len([b for b in st.session_state.code_backups if b['type'] == 'manual'])
        st.metric("Manuelle", manual_count)
    with col3:
        auto_count = len([b for b in st.session_state.code_backups if b['type'] == 'auto'])
        st.metric("Automatische", auto_count)
    with col4:
        st.metric("Letztes", st.session_state.last_backup_time or "Nie")
    
    st.subheader("Verfuegbare Backups")
    
    if not st.session_state.code_backups:
        st.info("Noch keine Backups vorhanden.")
    else:
        for i, backup in enumerate(st.session_state.code_backups[:10]):
            with st.container():
                col_info, col_actions = st.columns([3, 2])
                
                with col_info:
                    type_icon = "🤖" if backup['type'] == 'auto' else "👤" if backup['type'] == 'manual' else "⚠️"
                    st.markdown(f"""
                    <div class='backup-card {backup['type']}'>
                        <strong>{type_icon} {backup['id']}</strong><br>
                        <small>🕐 {backup['timestamp']} | 📏 {backup['size']} Zeichen | #{backup['hash']}</small><br>
                        <em>{backup['description']}</em>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_actions:
                    if st.button("Anzeigen", key=f"view_{backup['id']}_{st.session_state.session_id}"):
                        st.code(backup['code'], language='python')
                    
                    if st.button("Wiederherstellen", key=f"restore_{backup['id']}_{st.session_state.session_id}"):
                        if restore_backup(backup['id']):
                            st.success(f"Backup {backup['id']} wiederhergestellt!")
                        else:
                            st.error("Fehler beim Wiederherstellen")
    
    st.markdown("---")
    st.subheader("Export & Import")
    
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        if st.button("Alle Backups exportieren", key=f"export_btn_{st.session_state.session_id}"):
            json_data = export_all_backups()
            st.download_button(
                "JSON Speichern",
                json_data,
                file_name=f"kistengenerator_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"dl_backup_{st.session_state.session_id}"
            )

# =============================================================================
# EINSTELLUNGEN
# =============================================================================
elif page == "Einstellungen":
    st.markdown("<div class='main-header'><h1>Einstellungen</h1></div>", unsafe_allow_html=True)
    
    st.subheader("Backup-Einstellungen")
    auto_backup = st.toggle(
        "Automatisches Backup aktivieren",
        value=st.session_state.auto_backup_enabled,
        key=f"toggle_backup_{st.session_state.session_id}"
    )
    st.session_state.auto_backup_enabled = auto_backup
    
    if auto_backup:
        st.success("Automatisches Backup ist aktiv")
    else:
        st.warning("Automatisches Backup ist deaktiviert")
    
    st.markdown("---")
    st.subheader("Kisten verwalten")
    total_boxes = sum(len(boxes) for boxes in st.session_state.custom_boxes.values())
    st.write(f"Aktuell erstellte Kisten: **{total_boxes}**")
    
    if st.button("Alle Kisten loeschen", key=f"reset_boxes_{st.session_state.session_id}"):
        st.session_state.custom_boxes = {}
        st.success("Alle Kisten wurden geloescht!")
        st.rerun()
    
    st.markdown("---")
    st.subheader("Vorlagen verwalten")
    total_templates = len(st.session_state.box_templates)
    st.write(f"Aktuelle Vorlagen: **{total_templates}**")
    
    if st.button("Alle Vorlagen loeschen", key=f"reset_tpl_{st.session_state.session_id}"):
        st.session_state.box_templates = {}
        st.success("Alle Vorlagen wurden geloescht!")
        st.rerun()
    
    st.markdown("---")
    st.subheader("Historie verwalten")
    total_history = sum(len(h) for h in st.session_state.kisten_historie.values())
    st.write(f"Aktuelle Historie-Eintraege: **{total_history}**")
    
    if st.button("Gesamte Historie loeschen", key=f"reset_hist_{st.session_state.session_id}"):
        st.session_state.kisten_historie = {}
        st.success("Gesamte Historie wurde geloescht!")
        st.rerun()
    
    st.markdown("---")
    st.subheader("JSON Pools verwalten")
    pool_count = len(st.session_state.json_pools)
    st.write(f"Geladene Pools: **{pool_count}**")
    
    if st.session_state.json_pools:
        for pool_key in list(st.session_state.json_pools.keys()):
            col_pool, col_del = st.columns([3, 1])
            with col_pool:
                pool_data = st.session_state.json_pools[pool_key]
                st.write(f"📜 {pool_key}: {pool_data.get('gesamt_artikel', 0)} Artikel")
            with col_del:
                if st.button(f"🗑️", key=f"del_pool_{pool_key}_{st.session_state.session_id}"):
                    del st.session_state.json_pools[pool_key]
                    st.success(f"Pool {pool_key} entfernt!")
                    st.rerun()
    
    if st.button("Alle Pools loeschen", key=f"reset_pools_{st.session_state.session_id}"):
        st.session_state.json_pools = {}
        st.success("Alle Pools wurden geloescht!")
        st.rerun()

# Footer
st.markdown("---")
total_custom_boxes = sum(len(boxes) for boxes in st.session_state.custom_boxes.values())
total_templates = len(st.session_state.box_templates)
total_history = sum(len(h) for h in st.session_state.kisten_historie.values())
pool_count = len(st.session_state.json_pools)
st.markdown(f"""
<div style='text-align: center;'>
    <p>Paradieschen Kistengenerator V1.3 | Session: {st.session_state.session_id} | 
    Kisten: {total_custom_boxes} | Vorlagen: {total_templates} | Historie: {total_history} | Pools: {pool_count} | Backups: {len(st.session_state.code_backups)}</p>
</div>
""", unsafe_allow_html=True)
