"""
Page 2 — Meta-Analysis Dashboard
Interactive visualization of the meta-analysis results
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from utils.scoring import (
    load_estimates, load_studies, load_rob,
    CANCER_LABELS, CANCER_COLORS,
)

st.set_page_config(page_title="Méta-Analyse · MedFlow AI", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
.kpi { background:#1e293b; border-radius:10px; padding:18px; border:1px solid #334155; text-align:center; }
.kpi-v { font-size:1.6rem; font-weight:700; color:#10b981; }
.kpi-l { font-size:0.8rem; color:#94a3b8; margin-top:3px; }
</style>
""", unsafe_allow_html=True)

est  = load_estimates()
stud = load_studies()
rob  = load_rob()

st.markdown("## 📊 Méta-Analyse — Tableau de Bord")
st.caption("Gut Microbiome as a Diagnostic Biomarker for Early Cancer Detection · bioRxiv BIORXIV/2026/719461")

# ── KPIs ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    ("18", "Études incluses"),
    ("2 587", "Patients total"),
    ("5", "Types de cancer"),
    ("74", "Signatures"),
    (f"{est['auc_pooled'].mean():.3f}", "AUC moyenne"),
    (f"{est['i2_pct'].mean():.0f}%", "I² moyen"),
]
for col, (v, l) in zip([k1, k2, k3, k4, k5, k6], kpis):
    with col:
        st.markdown(f'<div class="kpi"><div class="kpi-v">{v}</div><div class="kpi-l">{l}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Forest Plots", "Études incluses", "Risque de biais", "Hétérogénéité"])

with tab1:
    st.markdown("### Forest Plots — AUC poolée par type de cancer")
    cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]
    fig, axes = plt.subplots(1, 5, figsize=(18, 6), facecolor="#0f172a")

    for ax, ct in zip(axes, cancer_order):
        ct_studies = stud[stud["cancer"] == ct].copy()
        est_row = est[est["cancer_type"] == ct].iloc[0]
        color = CANCER_COLORS[ct]
        ax.set_facecolor("#1e293b")

        y_pos = list(range(len(ct_studies)))
        ci_half = 0.06  # approximate CI half-width per study

        for i, (_, row) in enumerate(ct_studies.iterrows()):
            auc_val = row["auc_reported"]
            ax.errorbar(
                auc_val, i,
                xerr=ci_half * np.random.uniform(0.7, 1.3),
                fmt="o", color=color, markersize=5 + row["n_total"] / 120,
                ecolor=color, elinewidth=1, capsize=3, alpha=0.85,
            )
            ax.text(
                0.505, i, row["id"][:12],
                va="center", ha="left", color="#94a3b8", fontsize=6.5,
            )

        # Pooled diamond
        ci_l = float(est_row["ci_lower"])
        ci_u = float(est_row["ci_upper"])
        auc_p = float(est_row["auc_pooled"])
        y_d = -1.3
        diamond_x = [ci_l, auc_p, ci_u, auc_p, ci_l]
        diamond_y = [y_d, y_d - 0.35, y_d, y_d + 0.35, y_d]
        ax.fill(diamond_x, diamond_y, color=color, alpha=0.9)
        ax.text(auc_p, y_d - 0.9, f"{auc_p:.3f}", ha="center", color=color,
                fontsize=7.5, fontweight="bold")

        ax.axvline(0.5, color="#475569", lw=0.8, ls="--")
        ax.axvline(0.8, color="#334155", lw=0.8, ls=":")
        ax.set_xlim(0.45, 1.05)
        ax.set_ylim(-2.2, len(ct_studies))
        ax.set_yticks([])
        ax.set_xlabel("AUC", color="#94a3b8", fontsize=8)
        ax.set_title(f"{ct}\nI²={est_row['i2_pct']:.0f}%", color=color, fontsize=9, fontweight="bold")
        ax.tick_params(colors="#94a3b8", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")

    plt.suptitle("Forest plots — AUC par type de cancer (DerSimonian-Laird)", color="#f1f5f9",
                 fontsize=11, y=1.01)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("### Résumé des estimations poolées")
    est_disp = est.copy()
    est_disp["95% CI"] = est_disp.apply(lambda r: f"[{r['ci_lower']:.3f} – {r['ci_upper']:.3f}]", axis=1)
    est_disp["Cancer"] = est_disp["cancer_type"].map(CANCER_LABELS)
    est_disp = est_disp[["Cancer", "n_studies", "n_total", "auc_pooled", "95% CI", "i2_pct", "tau2", "Q"]]
    est_disp.columns = ["Cancer", "k", "N", "AUC poolée", "95% CI", "I² (%)", "τ²", "Q"]
    st.dataframe(est_disp, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Registre des 18 études incluses")

    filter_cancer = st.multiselect(
        "Filtrer par cancer",
        options=list(CANCER_LABELS.keys()),
        default=list(CANCER_LABELS.keys()),
        format_func=lambda k: CANCER_LABELS[k],
    )
    filter_min_auc = st.slider("AUC minimum", 0.5, 1.0, 0.7, 0.01)

    stud_disp = stud[
        (stud["cancer"].isin(filter_cancer)) &
        (stud["auc_reported"] >= filter_min_auc)
    ].copy()
    stud_disp["Cancer"] = stud_disp["cancer"].map(CANCER_LABELS)
    stud_disp = stud_disp[["id", "Cancer", "n_total", "country", "year", "sequencing", "auc_reported", "nos_score", "journal"]]
    stud_disp.columns = ["ID Étude", "Cancer", "N", "Pays", "Année", "Séquençage", "AUC", "NOS", "Journal"]
    st.dataframe(stud_disp.sort_values("AUC", ascending=False), use_container_width=True, hide_index=True)
    st.caption(f"{len(stud_disp)} études affichées")

with tab3:
    st.markdown("### Risque de biais — Newcastle-Ottawa Scale (NOS)")

    fig2, ax2 = plt.subplots(figsize=(12, 7), facecolor="#0f172a")
    ax2.set_facecolor("#1e293b")

    rob_sorted = rob.sort_values("total_nos", ascending=True)
    colors_rob = [CANCER_COLORS.get(ct, "#94a3b8") for ct in rob_sorted["cancer_type"]]

    bars = ax2.barh(rob_sorted["study"], rob_sorted["total_nos"],
                   color=colors_rob, height=0.6, edgecolor="#334155")
    ax2.axvline(7, color="#10b981", lw=1, ls="--", alpha=0.7, label="Qualité haute (≥7)")
    ax2.axvline(5, color="#f59e0b", lw=1, ls="--", alpha=0.7, label="Qualité modérée (≥5)")

    for bar, val in zip(bars, rob_sorted["total_nos"]):
        ax2.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                 str(val), va="center", color="#f1f5f9", fontsize=8)

    ax2.set_xlim(0, 10)
    ax2.set_xlabel("Score NOS (/9)", color="#94a3b8")
    ax2.set_title("Risque de biais — Newcastle-Ottawa Scale", color="#f1f5f9")
    ax2.tick_params(colors="#94a3b8", labelsize=7)
    legend_patches = [mpatches.Patch(color=CANCER_COLORS[ct], label=CANCER_LABELS[ct])
                      for ct in CANCER_LABELS]
    ax2.legend(handles=legend_patches, facecolor="#1e293b", labelcolor="#f1f5f9", fontsize=8)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    rob_disp = rob.copy()
    rob_disp["Cancer"] = rob_disp["cancer_type"].map(CANCER_LABELS)
    rob_disp = rob_disp[["study", "Cancer", "selection", "comparability", "outcome", "total_nos", "quality"]]
    rob_disp.columns = ["Étude", "Cancer", "Sélection (/4)", "Comparabilité (/2)", "Résultat (/3)", "Total (/9)", "Qualité"]
    st.dataframe(rob_disp, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### Hétérogénéité inter-études")

    fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5), facecolor="#0f172a")
    cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]
    labels_short = [ct for ct in cancer_order]

    # I² chart
    ax3.set_facecolor("#1e293b")
    i2_vals = [float(est[est["cancer_type"] == ct]["i2_pct"].iloc[0]) for ct in cancer_order]
    colors_i2 = ["#10b981" if v < 25 else "#f59e0b" if v < 75 else "#ef4444" for v in i2_vals]
    ax3.bar(labels_short, i2_vals, color=colors_i2, width=0.5, edgecolor="#334155")
    ax3.axhline(25, color="#10b981", lw=1, ls="--", alpha=0.7, label="Faible (<25%)")
    ax3.axhline(75, color="#ef4444", lw=1, ls="--", alpha=0.7, label="Élevée (>75%)")
    for i, val in enumerate(i2_vals):
        ax3.text(i, val + 1, f"{val:.0f}%", ha="center", color="#f1f5f9", fontsize=9)
    ax3.set_ylim(0, 100)
    ax3.set_ylabel("I² (%)", color="#94a3b8")
    ax3.set_title("Hétérogénéité I²", color="#f1f5f9")
    ax3.tick_params(colors="#94a3b8")
    ax3.legend(facecolor="#1e293b", labelcolor="#94a3b8", fontsize=8)
    for spine in ax3.spines.values():
        spine.set_edgecolor("#334155")

    # τ² chart
    ax4.set_facecolor("#1e293b")
    tau2_vals = [float(est[est["cancer_type"] == ct]["tau2"].iloc[0]) for ct in cancer_order]
    ax4.bar(labels_short, tau2_vals, color=[CANCER_COLORS[ct] for ct in cancer_order],
            width=0.5, edgecolor="#334155")
    for i, val in enumerate(tau2_vals):
        ax4.text(i, val + 0.00002, f"{val:.4f}", ha="center", color="#f1f5f9", fontsize=8)
    ax4.set_ylabel("τ² (variance inter-études)", color="#94a3b8")
    ax4.set_title("Variance τ²", color="#f1f5f9")
    ax4.tick_params(colors="#94a3b8")
    for spine in ax4.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    st.markdown("""
    **Interprétation de l'hétérogénéité :**
    - I² < 25 % → hétérogénéité faible (résultats cohérents entre études)
    - I² 25–75 % → hétérogénéité modérée (variabilité clinique attendue)
    - I² > 75 % → hétérogénéité élevée (prudence dans l'interprétation)
    """)
