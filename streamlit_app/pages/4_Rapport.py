"""
Page 4 — Clinical PDF Report Generator
"""
import streamlit as st
import pandas as pd
import numpy as np

from utils.scoring import (
    load_signatures, load_estimates,
    match_taxa, score_sample, dysbiosis_index,
    generate_demo_sample, CANCER_LABELS,
)
from utils.pdf_report import generate_pdf

st.set_page_config(page_title="Rapport PDF · MedFlow AI", page_icon="📄", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
.report-preview {
    background: #1e293b; border-radius: 12px; padding: 28px;
    border: 1px solid #334155; margin-top: 16px;
}
.risk-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 📄 Rapport Clinique PDF")
st.markdown("Générez un rapport structuré pour le clinicien, incluant les scores de risque et les signatures détectées.")

sigs  = load_signatures()
ests  = load_estimates()

# ── Step 1 — Patient info ──────────────────────────────────────────────────────
st.markdown("### Étape 1 — Informations patient")
col1, col2, col3 = st.columns(3)
with col1:
    patient_id = st.text_input("ID Patient", value="PAT-2026-001")
with col2:
    sample_id = st.text_input("ID Échantillon", value="SAMP-16S-001")
with col3:
    clinician = st.text_input("Clinicien référent", value="Dr. —")

# ── Step 2 — OTU data ─────────────────────────────────────────────────────────
st.markdown("### Étape 2 — Données OTU")
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader("Fichier OTU (CSV)", type=["csv", "xlsx"], key="report_upload")
with col_demo:
    st.markdown("<br>", unsafe_allow_html=True)
    demo_cancer = st.selectbox("Cancer démo", list(CANCER_LABELS.keys()),
                               format_func=lambda k: CANCER_LABELS[k])
    use_demo = st.button("Données démo", use_container_width=True)

df = None
if uploaded:
    ext = uploaded.name.split(".")[-1]
    df = pd.read_excel(uploaded) if ext == "xlsx" else pd.read_csv(uploaded)
    st.success(f"✅ {df.shape[0]} échantillon(s) · {df.shape[1]} colonnes")
elif use_demo:
    demo_series = generate_demo_sample(sigs, dominant_cancer=demo_cancer)
    df = demo_series.to_frame().T
    st.info(f"Données démo — profil dominant : **{CANCER_LABELS[demo_cancer]}**")

# ── Step 3 — Generate ─────────────────────────────────────────────────────────
if df is not None:
    drop_cols = [c for c in ["label", "sample_id", "patient_id", "#OTU ID"] if c in df.columns]
    df_otu = df.drop(columns=drop_cols).select_dtypes(include=[np.number])
    col_to_taxon = match_taxa(list(df_otu.columns), sigs)

    if not col_to_taxon:
        st.warning("Aucun taxon reconnu. Vérifiez les noms de colonnes.")
        st.stop()

    sample = df_otu.iloc[0]
    scores = score_sample(sample, sigs, ests, col_to_taxon)
    di = dysbiosis_index(scores)

    st.markdown("### Aperçu du rapport")
    with st.container():
        st.markdown(f"""
        <div class="report-preview">
          <h4 style="color:#f1f5f9;margin-top:0;">Rapport — {patient_id} · {sample_id}</h4>
          <p style="color:#94a3b8;">Clinicien : {clinician}</p>
          <p style="color:#94a3b8;">
            Indice de dysbiose global : <b style="color:{'#10b981' if di < 0.25 else '#f59e0b' if di < 0.5 else '#ef4444'};">
            {di*100:.1f}%</b>
          </p>
        """, unsafe_allow_html=True)

        cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]
        for ct in cancer_order:
            if ct not in scores:
                continue
            info = scores[ct]
            color = info["risk_color"]
            st.markdown(f"""
            <div class="risk-row">
              <span style="color:#f1f5f9;">{info['label']}</span>
              <span style="color:#94a3b8;font-size:0.85rem;">Score : {info['score']:.3f}</span>
              <span style="background:{color}22;color:{color};padding:3px 12px;border-radius:12px;font-weight:700;font-size:0.85rem;">
                {info['risk']}
              </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Étape 3 — Télécharger le rapport")

    if st.button("📄 Générer le rapport PDF", type="primary", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            pdf_bytes = generate_pdf(
                scores=scores,
                dysbiosis=di,
                patient_id=patient_id,
                sample_id=sample_id,
                n_taxa=len(df_otu.columns),
                n_matched=len(col_to_taxon),
            )
        st.download_button(
            label="⬇️ Télécharger le rapport PDF",
            data=pdf_bytes,
            file_name=f"rapport_microbiome_{patient_id}_{sample_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.success("✅ Rapport PDF généré avec succès.")

    st.markdown("""
    > ⚠️ **Avertissement** : Ce rapport est à usage exploratoire et de recherche uniquement.
    > Il ne constitue pas un diagnostic médical et doit être interprété par un professionnel de santé.
    """)
