"""
Page 1 — Analyse OTU
Upload microbiome data → signature scoring → dysbiosis index → results
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils.scoring import (
    load_signatures, load_estimates,
    match_taxa, score_sample, dysbiosis_index,
    generate_demo_sample, CANCER_LABELS, CANCER_COLORS,
)

st.set_page_config(page_title="Analyse OTU · MedFlow AI", page_icon="🔬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
.risk-badge {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-weight:700; font-size:0.95rem;
}
.score-card {
    background:#1e293b; border-radius:12px; padding:20px;
    border: 1px solid #334155; text-align:center;
}
.score-value { font-size:1.8rem; font-weight:700; }
.score-label { font-size:0.8rem; color:#94a3b8; margin-top:4px; }
.info-box {
    background:#0f2744; border-radius:8px; padding:16px;
    border-left:4px solid #3b82f6; color:#93c5fd; font-size:0.9rem;
}
.warn-box {
    background:#1c1007; border-radius:8px; padding:14px;
    border-left:4px solid #f59e0b; color:#fbbf24; font-size:0.85rem;
    margin-top:16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🔬 Analyse des Signatures Microbiennes")
st.markdown("Importez un fichier OTU/16S (CSV) avec une colonne par taxon, une ligne par échantillon.")

sigs = load_signatures()
ests = load_estimates()

# ── Sidebar options ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Options d'analyse")
    demo_cancer = st.selectbox(
        "Cancer dominant (démo)",
        options=list(CANCER_LABELS.keys()),
        format_func=lambda k: CANCER_LABELS[k],
    )
    st.markdown("---")
    st.markdown("**Format attendu**")
    st.caption("CSV · lignes = échantillons · colonnes = taxons · valeurs = abondances relatives [0–1]")
    st.code("Fusobacterium_nucleatum,Faecalibacterium_prausnitzii,...\n0.72,0.08,...", language="text")
    st.markdown("---")
    st.markdown("**Fichier de test**")
    try:
        with open("data/test_otu_patients.csv", "rb") as f:
            st.download_button(
                "📥 CSV test (6 patients)",
                data=f.read(),
                file_name="test_otu_patients.csv",
                mime="text/csv",
                use_container_width=True,
                help="2 CRC · 1 PDAC · 1 GC · 2 contrôles",
            )
    except FileNotFoundError:
        pass

# ── Upload / Demo ──────────────────────────────────────────────────────────────
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader("Fichier OTU (CSV)", type=["csv", "xlsx"])
with col_demo:
    st.markdown("<br>", unsafe_allow_html=True)
    use_demo = st.button("🧪 Données démo", use_container_width=True, type="secondary")

df = None
sample_id = "demo_patient_01"

if uploaded:
    ext = uploaded.name.split(".")[-1]
    df = pd.read_excel(uploaded) if ext == "xlsx" else pd.read_csv(uploaded)
    sample_id = uploaded.name.replace(".csv", "").replace(".xlsx", "")
    st.success(f"✅ {df.shape[0]} échantillon(s) · {df.shape[1]} colonnes chargées")
    st.dataframe(df.head(3), use_container_width=True)

elif use_demo:
    demo_series = generate_demo_sample(sigs, dominant_cancer=demo_cancer)
    df = demo_series.to_frame().T
    st.info(f"Données démo générées — profil dominant : **{CANCER_LABELS[demo_cancer]}**")
    st.dataframe(df.head(1), use_container_width=True)

# ── Analysis ───────────────────────────────────────────────────────────────────
if df is not None:
    drop_cols = [c for c in ["label", "sample_id", "patient_id", "#OTU ID"] if c in df.columns]
    df_otu = df.drop(columns=drop_cols).select_dtypes(include=[np.number])

    col_to_taxon = match_taxa(list(df_otu.columns), sigs)
    n_taxa   = len(df_otu.columns)
    n_matched = len(col_to_taxon)

    st.markdown("---")
    if n_matched == 0:
        st.warning("Aucun taxon reconnu dans les colonnes. Vérifiez les noms (ex: `Fusobacterium_nucleatum`).")
        st.stop()

    st.markdown(f"**{n_matched} taxons reconnus** sur {n_taxa} colonnes")

    # Analyse first sample
    sample = df_otu.iloc[0]
    scores = score_sample(sample, sigs, ests, col_to_taxon)
    di = dysbiosis_index(scores)

    # ── Dysbiosis index ────────────────────────────────────────────────────────
    di_pct = round(di * 100, 1)
    di_color = "#10b981" if di < 0.25 else "#f59e0b" if di < 0.50 else "#ef4444"
    st.markdown("### Indice de Dysbiose Global")
    c_di1, c_di2 = st.columns([1, 3])
    with c_di1:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-value" style="color:{di_color};">{di_pct}%</div>
          <div class="score-label">Dysbiose globale</div>
        </div>
        """, unsafe_allow_html=True)
    with c_di2:
        st.markdown(f"""
        <div class="info-box">
        L'indice de dysbiose est calculé comme le score maximal parmi les 5 types de cancer,
        calibré par l'AUC poolée de la méta-analyse.
        Il reflète l'ampleur des altérations microbiennes concordantes avec un profil cancéreux.
        <br><br>
        <b>{n_matched}</b> taxons détectés sur <b>{n_taxa}</b> colonnes importées.
        </div>
        """, unsafe_allow_html=True)

    # ── Risk scores per cancer ─────────────────────────────────────────────────
    st.markdown("### Scores de risque par type de cancer")
    cols = st.columns(5)
    cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]
    for col, ct in zip(cols, cancer_order):
        if ct not in scores:
            continue
        info = scores[ct]
        with col:
            st.markdown(f"""
            <div class="score-card" style="border-left:4px solid {info['color']};">
              <div style="font-size:0.75rem;color:{info['color']};font-weight:600;margin-bottom:6px;">
                {info['label']}
              </div>
              <div class="score-value" style="color:{info['color']};">{info['score']:.3f}</div>
              <div class="score-label">
                <span class="risk-badge" style="background:{info['risk_color']}22;color:{info['risk_color']};">
                  {info['risk']}
                </span>
              </div>
              <div class="score-label" style="margin-top:8px;">
                {info['n_matched']} signatures · AUC {info['auc_meta']:.3f}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Radar / Bar chart ──────────────────────────────────────────────────────
    st.markdown("### Profil de risque — comparaison inter-cancers")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0f172a")

    # Bar chart
    ax = axes[0]
    ax.set_facecolor("#1e293b")
    cts = [ct for ct in cancer_order if ct in scores]
    vals = [scores[ct]["score"] for ct in cts]
    colors_bar = [scores[ct]["color"] for ct in cts]
    labels = [CANCER_LABELS[ct].split(" ")[0] for ct in cts]
    bars = ax.barh(labels, vals, color=colors_bar, height=0.55, edgecolor="#334155")
    ax.axvline(0.25, color="#10b981", lw=1, ls="--", alpha=0.7, label="Seuil faible")
    ax.axvline(0.50, color="#f59e0b", lw=1, ls="--", alpha=0.7, label="Seuil modéré")
    ax.axvline(0.75, color="#ef4444", lw=1, ls="--", alpha=0.7, label="Seuil élevé")
    for bar, val in zip(bars, vals):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", color="#f1f5f9", fontsize=9)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Score calibré (0–1)", color="#94a3b8")
    ax.set_title("Scores de risque par cancer", color="#f1f5f9", fontsize=11)
    ax.tick_params(colors="#94a3b8")
    ax.legend(facecolor="#1e293b", labelcolor="#94a3b8", fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    # Matched signatures concordance
    ax2 = axes[1]
    ax2.set_facecolor("#1e293b")
    conc_rates = []
    for ct in cts:
        sigs_m = scores[ct]["matched_signatures"]
        if sigs_m:
            rate = sum(1 for s in sigs_m if s["concordant"]) / len(sigs_m)
        else:
            rate = 0.0
        conc_rates.append(rate * 100)
    bars2 = ax2.bar(labels, conc_rates, color=[scores[ct]["color"] for ct in cts],
                    width=0.5, edgecolor="#334155")
    for bar, val in zip(bars2, conc_rates):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 1,
                 f"{val:.0f}%", ha="center", color="#f1f5f9", fontsize=9)
    ax2.set_ylim(0, 110)
    ax2.set_ylabel("% signatures concordantes", color="#94a3b8")
    ax2.set_title("Concordance des signatures", color="#f1f5f9", fontsize=11)
    ax2.tick_params(colors="#94a3b8")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Matched signatures table ───────────────────────────────────────────────
    st.markdown("### Signatures détectées")
    tabs = st.tabs([CANCER_LABELS[ct] for ct in cancer_order if ct in scores])
    for tab, ct in zip(tabs, [c for c in cancer_order if c in scores]):
        with tab:
            info = scores[ct]
            if not info["matched_signatures"]:
                st.info("Aucune signature de ce type détectée dans le fichier.")
                continue
            sig_df = pd.DataFrame(info["matched_signatures"])
            sig_df["concordant"] = sig_df["concordant"].map({True: "✅", False: "❌"})
            sig_df.columns = ["Taxon", "Direction attendue", "log₂FC", "Observé", "Référence", "Concordant"]
            st.dataframe(sig_df, use_container_width=True, hide_index=True)

    # ── Clinical interpretation for the physician ──────────────────────────────
    st.markdown("---")
    st.markdown("### Interprétation clinique")

    CLINICAL_NOTES = {
        "CRC": {
            "enriched_key": ["Fusobacterium nucleatum", "Peptostreptococcus stomatis", "Parvimonas micra"],
            "depleted_key": ["Faecalibacterium prausnitzii", "Roseburia intestinalis"],
            "note": (
                "**Colorectal (CRC)** — *F. nucleatum* est le biomarqueur CRC le plus répliqué "
                "(>15 études, OR≈4). Sa présence élevée est associée à l'invasion de la muqueuse colique "
                "et à un phénotype moléculaire MSI-H. Un score CRC élevé justifie une coloscopie de contrôle "
                "et un dosage du calprotectine fécale."
            ),
        },
        "GC": {
            "enriched_key": ["Helicobacter pylori", "Fusobacterium nucleatum"],
            "depleted_key": ["Faecalibacterium prausnitzii", "Akkermansia muciniphila"],
            "note": (
                "**Gastrique (GC)** — *H. pylori* reste le principal facteur étiologique (classé IARC groupe 1). "
                "Une dysbiose gastrique combinée à *F. nucleatum* enrichi suggère une atrophie progressive. "
                "Recommander une gastroscopie avec biopsies selon les critères de Sydney et un test CLO."
            ),
        },
        "PDAC": {
            "enriched_key": ["Fusobacterium nucleatum", "Bacteroides fragilis"],
            "depleted_key": ["Faecalibacterium prausnitzii", "Bifidobacterium longum"],
            "note": (
                "**Pancréatique (PDAC)** — AUC méta la plus élevée (0.853). "
                "*F. nucleatum* et *B. fragilis* entérotoxinogène sont enrichis dès les stades I–II. "
                "En cas de score élevé avec antécédents familiaux ou syndrome BRCA2, orienter vers une "
                "IRM pancréatique et un dosage CA 19-9 / CEA."
            ),
        },
        "HCC": {
            "enriched_key": ["Bacteroides fragilis", "Clostridium hathewayi"],
            "depleted_key": ["Akkermansia muciniphila", "Faecalibacterium prausnitzii"],
            "note": (
                "**Hépatocarcinome (HCC)** — La déplétion d'*A. muciniphila* altère la barrière intestinale "
                "et favorise la translocation bactérienne vers le foie (axe intestin-foie). "
                "Un score HCC élevé chez un patient cirrhotique ou porteur VHB/VHC renforce l'indication "
                "d'une surveillance échographique et alpha-fœtoprotéine tous les 6 mois."
            ),
        },
        "LC": {
            "enriched_key": ["Veillonella parvula", "Streptococcus salivarius"],
            "depleted_key": ["Akkermansia muciniphila", "Faecalibacterium prausnitzii"],
            "note": (
                "**Pulmonaire (LC)** — L'axe microbiome intestin-poumon est médialisé par les acides gras "
                "à chaîne courte (AGCC). *V. parvula* produit du propionate favorisant l'inflammation "
                "pulmonaire chronique. Un score LC élevé chez un fumeur ou exposé à l'amiante justifie "
                "un scanner thoracique basse dose (dépistage NLST/NELSON)."
            ),
        },
    }

    cancer_order_disp = ["CRC", "GC", "PDAC", "HCC", "LC"]
    for ct in cancer_order_disp:
        if ct not in scores:
            continue
        info = scores[ct]
        note_data = CLINICAL_NOTES.get(ct, {})
        risk_color = info["risk_color"]
        with st.expander(f"{info['label']} — Risque **{info['risk']}** · Score {info['score']:.3f}", expanded=info["risk"] in ["Élevé", "Très élevé"]):
            st.markdown(f"""
            <div style="background:#0f172a;border-left:4px solid {info['color']};padding:14px 18px;border-radius:6px;margin-bottom:10px;">
            {note_data.get('note', '')}
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Biomarqueurs-clés enrichis (cancer) :**")
                for t in note_data.get("enriched_key", []):
                    st.markdown(f"- 🔴 *{t}*")
            with col_b:
                st.markdown("**Biomarqueurs-clés déplétés (cancer) :**")
                for t in note_data.get("depleted_key", []):
                    st.markdown(f"- 🟢 *{t}*")

            n_conc = sum(1 for s in info["matched_signatures"] if s["concordant"])
            st.caption(f"Signatures concordantes : {n_conc}/{info['n_matched']} · AUC méta-analyse : {info['auc_meta']:.3f}")

    # ── Export button ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Export des résultats")

    # Download test CSV
    with open("data/test_otu_patients.csv", "rb") as f:
        st.download_button(
            "📥 Télécharger un fichier test (6 patients)",
            data=f.read(),
            file_name="test_otu_patients.csv",
            mime="text/csv",
            help="CSV avec 2 patients CRC, 1 PDAC, 1 GC et 2 contrôles sains",
        )

    result_rows = []
    for ct, info in scores.items():
        result_rows.append({
            "Cancer": info["label"],
            "Score": info["score"],
            "Risque": info["risk"],
            "N_signatures": info["n_matched"],
            "AUC_meta": info["auc_meta"],
        })
    result_df = pd.DataFrame(result_rows)
    st.download_button(
        "⬇️ Télécharger résultats (CSV)",
        data=result_df.to_csv(index=False).encode(),
        file_name=f"microbiome_scores_{sample_id}.csv",
        mime="text/csv",
    )

    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>Usage exploratoire uniquement.</b> Ces scores ne constituent pas un diagnostic médical.
    Ils doivent être interprétés par un professionnel de santé dans le contexte clinique du patient.
    </div>
    """, unsafe_allow_html=True)
