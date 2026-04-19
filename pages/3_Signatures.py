"""
Page 3 — Microbial Signatures Explorer
Browse and filter 74 validated signatures from the meta-analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import matplotlib.colors as mcolors

from utils.scoring import load_signatures, CANCER_LABELS, CANCER_COLORS

st.set_page_config(page_title="Signatures · MedFlow AI", page_icon="🧫", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

sigs = load_signatures()

st.markdown("## 🧫 Signatures Microbiennes Validées")
st.markdown(f"**{len(sigs)} signatures** issues de 18 études publiées · méta-analyse DerSimonian-Laird")

# ── Filters ────────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    sel_cancers = st.multiselect(
        "Type de cancer",
        options=list(CANCER_LABELS.keys()),
        default=list(CANCER_LABELS.keys()),
        format_func=lambda k: CANCER_LABELS[k],
    )
with col_f2:
    direction = st.selectbox("Direction", ["Toutes", "enriched", "depleted"])
with col_f3:
    min_lfc = st.slider("log₂FC minimum (|valeur|)", 0.0, 5.0, 0.0, 0.1)

filtered = sigs[sigs["cancer_type"].isin(sel_cancers)].copy()
if direction != "Toutes":
    filtered = filtered[filtered["direction"] == direction]
filtered = filtered[filtered["log2_fc"].abs() >= min_lfc]

st.caption(f"{len(filtered)} signatures affichées")

# ── Stats row ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total affiché", len(filtered))
with c2:
    st.metric("Enrichis (cancer)", int((filtered["direction"] == "enriched").sum()))
with c3:
    st.metric("Déplétés (cancer)", int((filtered["direction"] == "depleted").sum()))
with c4:
    st.metric("log₂FC moyen", f"{filtered['log2_fc'].mean():+.2f}")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Tableau complet", "Heatmap log₂FC", "Top biomarqueurs"])

with tab1:
    disp = filtered.copy()
    disp["Cancer"] = disp["cancer_type"].map(CANCER_LABELS)
    disp["Taxon"] = disp["taxon"].str.replace("_", " ")
    disp = disp[["Cancer", "Taxon", "log2_fc", "prevalence_case", "prevalence_ctrl", "direction"]]
    disp.columns = ["Cancer", "Taxon", "log₂FC", "Prévalence cas", "Prévalence ctrl", "Direction"]
    disp = disp.sort_values(["Cancer", "log₂FC"], ascending=[True, False])

    def color_direction(val):
        if val == "enriched":
            return "color: #ef4444"
        return "color: #10b981"

    def color_lfc(val):
        if val > 0:
            return f"color: #ef4444"
        return f"color: #10b981"

    styled = disp.style.applymap(color_direction, subset=["Direction"]) \
                       .applymap(color_lfc, subset=["log₂FC"]) \
                       .format({"log₂FC": "{:+.2f}", "Prévalence cas": "{:.2f}", "Prévalence ctrl": "{:.2f}"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Télécharger signatures (CSV)",
        data=filtered.to_csv(index=False).encode(),
        file_name="microbial_signatures_filtered.csv",
        mime="text/csv",
    )

with tab2:
    st.markdown("### Heatmap log₂FC — tous cancers")

    pivot = sigs.pivot_table(index="taxon", columns="cancer_type", values="log2_fc", aggfunc="mean")
    pivot = pivot.sort_values("CRC", ascending=False)
    pivot.index = [i.replace("_", " ") for i in pivot.index]

    fig, ax = plt.subplots(figsize=(10, max(6, len(pivot) * 0.35)), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")

    max_val = pivot.abs().max().max()
    norm = TwoSlopeNorm(vmin=-max_val, vcenter=0, vmax=max_val)
    im = ax.imshow(pivot.values, cmap="RdYlGn_r", norm=norm, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([CANCER_LABELS.get(c, c) for c in pivot.columns],
                       color="#f1f5f9", fontsize=8, rotation=20, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, color="#94a3b8", fontsize=7, style="italic")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:+.1f}", ha="center", va="center",
                        color="white" if abs(val) > max_val * 0.5 else "#1f2937",
                        fontsize=6)

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("log₂FC", color="#94a3b8")
    cbar.ax.yaxis.set_tick_params(color="#94a3b8")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#94a3b8")

    ax.set_title("log₂FC cancer vs contrôle (rouge=enrichi, vert=déplété)", color="#f1f5f9", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with tab3:
    st.markdown("### Top biomarqueurs par cancer")

    n_top = st.slider("Nombre de taxons à afficher", 5, 20, 10)

    fig2, axes = plt.subplots(1, 5, figsize=(18, 5), facecolor="#0f172a")
    cancer_order = ["CRC", "GC", "PDAC", "HCC", "LC"]

    for ax, ct in zip(axes, cancer_order):
        ct_sigs = sigs[sigs["cancer_type"] == ct].copy()
        ct_sigs = ct_sigs.reindex(ct_sigs["log2_fc"].abs().sort_values(ascending=False).index)
        ct_top = ct_sigs.head(n_top)
        ax.set_facecolor("#1e293b")

        colors_bar = ["#ef4444" if d == "enriched" else "#10b981"
                      for d in ct_top["direction"]]
        taxa_names = [t.replace("_", " ")[:22] for t in ct_top["taxon"]]

        ax.barh(taxa_names, ct_top["log2_fc"], color=colors_bar, height=0.6, edgecolor="#334155")
        ax.axvline(0, color="#94a3b8", lw=0.8)
        ax.set_title(ct, color=CANCER_COLORS[ct], fontsize=9, fontweight="bold")
        ax.set_xlabel("log₂FC", color="#94a3b8", fontsize=7)
        ax.tick_params(colors="#94a3b8", labelsize=6)
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")

    enriched_patch = mcolors.Patch(color="#ef4444", label="Enrichi (cancer)")
    depleted_patch = mcolors.Patch(color="#10b981", label="Déplété (cancer)")
    fig2.legend(handles=[enriched_patch, depleted_patch], loc="lower center",
                facecolor="#1e293b", labelcolor="#f1f5f9", ncol=2, fontsize=9,
                bbox_to_anchor=(0.5, -0.05))
    plt.suptitle("Top biomarqueurs microbiens par cancer (log₂FC)", color="#f1f5f9", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Cross-cancer biomarkers
    st.markdown("### Biomarqueurs communs à plusieurs cancers")
    taxon_counts = sigs.groupby("taxon").agg(
        n_cancers=("cancer_type", "nunique"),
        mean_log2fc=("log2_fc", "mean"),
        direction=("direction", lambda x: x.mode()[0]),
    ).reset_index().sort_values("n_cancers", ascending=False)

    multi = taxon_counts[taxon_counts["n_cancers"] >= 2].copy()
    multi["taxon"] = multi["taxon"].str.replace("_", " ")
    multi.columns = ["Taxon", "N cancers", "log₂FC moyen", "Direction"]
    st.dataframe(multi, use_container_width=True, hide_index=True)
