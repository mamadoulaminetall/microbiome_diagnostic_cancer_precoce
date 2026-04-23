"""
MedFlow AI — Microbiome Cancer Diagnostic Platform
Home page
"""
import streamlit as st
import pandas as pd
from utils.scoring import (
    load_estimates, load_studies, CANCER_LABELS, CANCER_COLORS
)

st.set_page_config(
    page_title="MedFlow AI — Microbiome Diagnostic",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
[data-testid="stSidebarNav"]       { padding-top: 1rem; }

.hero {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
    border-radius: 16px; padding: 40px 48px; margin-bottom: 28px;
    border: 1px solid #1e3a5f;
}
.hero-title  { font-size: 2rem; font-weight: 700; color: #f1f5f9; margin: 0 0 8px 0; }
.hero-sub    { font-size: 1.1rem; color: #94a3b8; margin: 0 0 20px 0; }
.hero-badges span {
    display: inline-block; margin: 0 6px 0 0; padding: 4px 12px;
    border-radius: 20px; font-size: 0.8rem; font-weight: 600;
}
.badge-green  { background: #064e3b; color: #6ee7b7; }
.badge-blue   { background: #1e3a5f; color: #93c5fd; }
.badge-purple { background: #3b0764; color: #c4b5fd; }

.stat-card {
    background: #1e293b; border-radius: 12px; padding: 24px 20px;
    border: 1px solid #334155; text-align: center;
}
.stat-value { font-size: 2.2rem; font-weight: 700; color: #10b981; }
.stat-label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

.nav-card {
    background: #1e293b; border-radius: 14px; padding: 24px;
    border: 1px solid #334155; height: 100%;
    transition: border-color 0.2s;
}
.nav-card:hover { border-color: #10b981; }
.nav-card-icon  { font-size: 2rem; margin-bottom: 10px; }
.nav-card-title { font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 6px; }
.nav-card-desc  { font-size: 0.88rem; color: #94a3b8; line-height: 1.5; }

.cancer-pill {
    display: inline-block; padding: 6px 14px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600; margin: 4px;
}
.footer { margin-top: 48px; padding-top: 20px; border-top: 1px solid #334155;
          color: #475569; font-size: 0.8rem; text-align: center; }
.biorxiv-badge {
    background: #7c2d12; color: #fed7aa; padding: 4px 12px;
    border-radius: 6px; font-size: 0.8rem; font-weight: 600;
    display: inline-block; margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 MedFlow AI")
    st.markdown("**Microbiome Cancer Diagnostic**")
    st.markdown("---")
    st.markdown("""
    **Navigation**
    - 🏠 Accueil *(cette page)*
    - 🔬 Analyse OTU
    - 📊 Méta-Analyse
    - 🧫 Signatures
    - 📄 Rapport PDF
    """)
    st.markdown("---")
    st.markdown("""
    **Publication**
    BIORXIV/2026/719461
    *TALL ML, MedFlow AI, 2026*
    """)
    st.caption("v2.0 · Avril 2026")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🧬 MedFlow AI — Diagnostic Microbiome</div>
  <div class="hero-sub">
    Détection précoce du cancer par analyse des signatures microbiennes intestinales<br>
    Méta-analyse validée · 18 études · 2 587 patients · 5 types de cancer
  </div>
  <div class="hero-badges">
    <span class="badge-green">✓ 74 signatures validées</span>
    <span class="badge-blue">AUC 0.780–0.853</span>
    <span class="badge-purple">bioRxiv 2026</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────────
est = load_estimates()
studies = load_studies()

c1, c2, c3, c4, c5 = st.columns(5)
stats = [
    ("18", "Études incluses"),
    ("2 587", "Patients"),
    ("5", "Types de cancer"),
    ("74", "Signatures validées"),
    ("0.853", "AUC max (PDAC)"),
]
for col, (val, lab) in zip([c1, c2, c3, c4, c5], stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{val}</div>
          <div class="stat-label">{lab}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── AUC by cancer ──────────────────────────────────────────────────────────────
st.markdown("### Performances diagnostiques par type de cancer")
cols = st.columns(5)
cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]
for col, ct in zip(cols, cancer_order):
    row = est[est["cancer_type"] == ct].iloc[0]
    with col:
        pct = int(row["auc_pooled"] * 100)
        color = CANCER_COLORS[ct]
        st.markdown(f"""
        <div class="stat-card" style="border-left: 4px solid {color};">
          <div style="font-size:0.8rem;color:{color};font-weight:600;margin-bottom:6px;">{CANCER_LABELS[ct]}</div>
          <div class="stat-value" style="color:{color};">{row['auc_pooled']:.3f}</div>
          <div class="stat-label">AUC · I²={row['i2_pct']:.0f}% · n={row['n_total']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation cards ───────────────────────────────────────────────────────────
st.markdown("### Modules disponibles")
nc1, nc2, nc3, nc4 = st.columns(4)

with nc1:
    st.markdown("""
    <div class="nav-card">
      <div class="nav-card-icon">🔬</div>
      <div class="nav-card-title">Analyse OTU</div>
      <div class="nav-card-desc">
        Importez votre fichier OTU/16S, obtenez un score de risque par cancer,
        un indice de dysbiose et les signatures concordantes.
      </div>
    </div>
    """, unsafe_allow_html=True)

with nc2:
    st.markdown("""
    <div class="nav-card">
      <div class="nav-card-icon">📊</div>
      <div class="nav-card-title">Méta-Analyse</div>
      <div class="nav-card-desc">
        Visualisez les résultats de la méta-analyse : forest plots, AUC poolées,
        hétérogénéité, biais de publication.
      </div>
    </div>
    """, unsafe_allow_html=True)

with nc3:
    st.markdown("""
    <div class="nav-card">
      <div class="nav-card-icon">🧫</div>
      <div class="nav-card-title">Signatures Microbiennes</div>
      <div class="nav-card-desc">
        Explorez les 74 signatures microbiennes validées par cancer :
        log₂FC, prévalence, direction, concordance inter-études.
      </div>
    </div>
    """, unsafe_allow_html=True)

with nc4:
    st.markdown("""
    <div class="nav-card">
      <div class="nav-card-icon">📄</div>
      <div class="nav-card-title">Rapport Clinique PDF</div>
      <div class="nav-card-desc">
        Générez un rapport PDF structuré pour le clinicien : scores,
        signatures détectées, indice de dysbiose, avertissements.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Biomarkers cross-cancer ────────────────────────────────────────────────────
st.markdown("### Biomarqueurs cross-cancer identifiés")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.markdown("""
    **Déplétés dans les 5 cancers**
    - *Faecalibacterium prausnitzii* ↓
    - *Akkermansia muciniphila* ↓
    """)
with col_b2:
    st.markdown("""
    **Enrichis CRC / GC / PDAC**
    - *Fusobacterium nucleatum* ↑
    - *Peptostreptococcus stomatis* ↑
    """)
with col_b3:
    st.markdown("""
    **Spécifiques par cancer**
    - HCC : *Bacteroides fragilis* ↑
    - LC : *Veillonella parvula* ↑
    """)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  MedFlow AI © 2026 · Dr. Mamadou Lamine TALL, PhD · Bioinformatique & IA médicale<br>
  <span class="biorxiv-badge">bioRxiv BIORXIV/2026/719461</span><br><br>
  ⚠️ Usage exploratoire uniquement — non destiné au diagnostic clinique direct.
</div>
""", unsafe_allow_html=True)
