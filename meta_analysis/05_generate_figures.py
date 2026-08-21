"""
Méta-analyse Microbiome & Cancer — Figures pour publication
============================================================
Figure 1 : Forest plots AUC par type de cancer (5 panels)
Figure 2 : AUC poolées comparées (bubble chart)
Figure 3 : Heatmap signatures microbiennes
Figure 4 : Bubble chart enrichissement / appauvrissement
Figure 5 : Risque de biais (NOS)
Figure 6 : PRISMA flow diagram

Auteur : Dr. Mamadou Lamine TALL, PhD — MedFlow AI
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

DATA = Path(__file__).parent.parent / "data" / "meta_analysis_v2"
FIGS = Path(__file__).parent.parent / "figures_v2"
FIGS.mkdir(parents=True, exist_ok=True)

df_studies  = pd.read_csv(DATA / "studies_registry.csv")
df_meta     = pd.read_csv(DATA / "meta_analytic_estimates.csv")
df_rob      = pd.read_csv(DATA / "risk_of_bias.csv")
df_sig      = pd.read_csv(DATA / "microbial_signatures.csv")

BG   = "#0f172a"
CARD = "#1e293b"
GRAY = "#94a3b8"
BORDER = "#334155"

CANCER_COLORS = {
    "CRC":  "#ef4444",
    "GC":   "#f59e0b",
    "PDAC": "#8b5cf6",
    "HCC":  "#f97316",
    "LC":   "#3b82f6",
}
CANCER_LABELS = {
    "CRC":  "Colorectal Cancer",
    "GC":   "Gastric Cancer",
    "PDAC": "Pancreatic Cancer",
    "HCC":  "Hepatocellular Carcinoma",
    "LC":   "Lung Cancer",
}

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Forest Plots AUC (1 panel par cancer)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 5, figsize=(22, 7))
fig.patch.set_facecolor(BG)
fig.suptitle("Figure 1 — Forest Plots: AUC of Microbiome-based Cancer Detection\n"
             "Random-effects model (DerSimonian-Laird) · 95% CI",
             color="white", fontsize=13, fontweight="bold", y=1.01)

for ax, cancer in zip(axes, ["CRC", "GC", "PDAC", "HCC", "LC"]):
    ax.set_facecolor(CARD)
    sub = df_studies[df_studies["cancer"] == cancer].copy()
    pooled = df_meta[df_meta["cancer_type"] == cancer].iloc[0]
    color = CANCER_COLORS[cancer]

    n = len(sub)
    y_pos = list(range(n - 1, -1, -1))

    for i, (_, row) in enumerate(sub.iterrows()):
        se = np.sqrt(row["auc_reported"] * (1 - row["auc_reported"]) / row["n_total"])
        ci = 1.96 * se
        yp = y_pos[i]
        # Marker size proportional to n
        ms = 4 + 8 * (row["n_total"] / sub["n_total"].max())
        ax.errorbar(row["auc_reported"], yp, xerr=ci, fmt="o",
                    color=color, markersize=ms, capsize=3, linewidth=1.5,
                    ecolor=color, alpha=0.85)
        label = f"{row['id']} (n={row['n_total']})"
        ax.text(0.48, yp, label, va="center", ha="left",
                color="#e2e8f0", fontsize=7.5)

    # Pooled diamond
    y_pool = -1.2
    d_half = (pooled["ci_upper"] - pooled["ci_lower"]) / 2
    diamond = plt.Polygon(
        [[pooled["auc_pooled"], y_pool + 0.35],
         [pooled["ci_upper"],   y_pool],
         [pooled["auc_pooled"], y_pool - 0.35],
         [pooled["ci_lower"],   y_pool]],
        closed=True, facecolor=color, edgecolor="white", linewidth=1.2, zorder=5
    )
    ax.add_patch(diamond)
    ax.text(pooled["auc_pooled"], y_pool - 0.75,
            f"AUC={pooled['auc_pooled']:.3f}\n[{pooled['ci_lower']:.3f}–{pooled['ci_upper']:.3f}]",
            ha="center", va="top", color=color, fontsize=8, fontweight="bold")
    ax.text(pooled["auc_pooled"], y_pool + 0.85,
            f"I²={pooled['i2_pct']:.0f}%", ha="center", va="bottom",
            color=GRAY, fontsize=7.5)

    ax.axvline(0.5, color=GRAY, linestyle="--", alpha=0.4, linewidth=1)
    ax.axhline(-0.5, color=BORDER, linewidth=0.8)
    ax.set_xlim(0.48, 1.05)
    ax.set_ylim(-2.2, n)
    ax.set_yticks([])
    ax.set_xlabel("AUC", color=GRAY, fontsize=9)
    ax.set_title(f"{CANCER_LABELS[cancer]}\n(n={int(sub['n_total'].sum())})",
                 color="white", fontsize=9.5, fontweight="bold")
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)

plt.tight_layout()
plt.savefig(FIGS / "fig1_forest_plots_auc.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig1_forest_plots_auc.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Comparaison AUC poolées (lollipop + CI)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)

cancers = df_meta["cancer_type"].tolist()
y_pos   = range(len(cancers) - 1, -1, -1)

for i, (_, row) in enumerate(df_meta.iterrows()):
    yp    = list(y_pos)[i]
    color = CANCER_COLORS[row["cancer_type"]]
    ax.plot([row["ci_lower"], row["ci_upper"]], [yp, yp],
            color=color, linewidth=3, alpha=0.6, solid_capstyle="round")
    ax.scatter(row["auc_pooled"], yp, color=color, s=150, zorder=5, edgecolors="white", linewidth=1.5)
    ax.text(row["ci_upper"] + 0.005, yp,
            f"AUC={row['auc_pooled']:.3f}  I²={row['i2_pct']:.0f}%",
            va="center", color=color, fontsize=10, fontweight="bold")
    ax.text(row["ci_lower"] - 0.005, yp,
            f"{CANCER_LABELS[row['cancer_type']]} (k={row['n_studies']}, n={row['n_total']})",
            va="center", ha="right", color="#e2e8f0", fontsize=9)

ax.axvline(0.5, color=GRAY, linestyle="--", alpha=0.5, linewidth=1, label="Random (AUC=0.5)")
ax.axvline(0.8, color="#10b981", linestyle=":", alpha=0.4, linewidth=1, label="Good (AUC=0.8)")
ax.set_xlim(0.60, 1.02)
ax.set_yticks([])
ax.set_xlabel("Pooled AUC (95% CI)", color=GRAY, fontsize=11)
ax.set_title(
    f"Figure 2 — Pooled AUC by Cancer Type\nRandom-effects meta-analysis · "
    f"{int(df_meta['n_studies'].sum())} studies · {int(df_meta['n_total'].sum()):,} patients",
    color="white", fontsize=12, fontweight="bold")
ax.tick_params(colors=GRAY)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_color(BORDER)
ax.legend(facecolor=CARD, labelcolor=GRAY, fontsize=9, loc="lower right")

plt.tight_layout()
plt.savefig(FIGS / "fig2_pooled_auc.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig2_pooled_auc.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — Heatmap signatures microbiennes (log2 FC)
# ─────────────────────────────────────────────────────────────────────────────
# Pivot : taxa × cancer
pivot = df_sig.pivot_table(index="taxon", columns="cancer_type", values="log2_fc", fill_value=0)
pivot = pivot.reindex(columns=["CRC", "GC", "PDAC", "HCC", "LC"])
# Trier par FC moyen absolu
pivot["abs_mean"] = pivot.abs().mean(axis=1)
pivot = pivot.sort_values("abs_mean", ascending=True).drop("abs_mean", axis=1)

fig, ax = plt.subplots(figsize=(9, max(8, len(pivot) * 0.35)))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

import matplotlib.colors as mcolors
cmap = plt.cm.RdYlGn_r
norm = mcolors.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3.5)

im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, norm=norm)

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(
    [f"{c}\n{CANCER_LABELS[c].split()[0]}" for c in pivot.columns],
    color="white", fontsize=10, fontweight="bold"
)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels([t.replace("_", " ") for t in pivot.index], color="#e2e8f0", fontsize=8)

for yi in range(len(pivot.index)):
    for xi in range(len(pivot.columns)):
        val = pivot.values[yi, xi]
        if abs(val) > 0.5:
            ax.text(xi, yi, f"{val:+.1f}", ha="center", va="center",
                    fontsize=7.5, color="black" if abs(val) > 1.5 else "white",
                    fontweight="bold")

cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
cbar.set_label("log₂(Fold-Change)\nCase vs Control", color=GRAY, fontsize=9)
cbar.ax.tick_params(colors=GRAY, labelsize=8)

ax.set_title("Figure 3 — Microbial Signature Heatmap\nlog₂(Fold-Change) in cancer vs healthy controls",
             color="white", fontsize=12, fontweight="bold", pad=15)

plt.tight_layout()
plt.savefig(FIGS / "fig3_heatmap_signatures.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig3_heatmap_signatures.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — Bubble chart : top biomarqueurs enrichis/appauvris par cancer
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 5, figsize=(22, 6))
fig.patch.set_facecolor(BG)
fig.suptitle("Figure 4 — Key Microbial Biomarkers: Enrichment & Depletion in Cancer",
             color="white", fontsize=13, fontweight="bold", y=1.01)

for ax, cancer in zip(axes, ["CRC", "GC", "PDAC", "HCC", "LC"]):
    ax.set_facecolor(CARD)
    sub = df_sig[df_sig["cancer_type"] == cancer].copy()
    sub = sub.reindex(sub["log2_fc"].abs().sort_values(ascending=True).index)

    colors_bar = ["#ef4444" if fc > 0 else "#10b981" for fc in sub["log2_fc"]]
    y_pos = range(len(sub))
    bars = ax.barh(list(y_pos), sub["log2_fc"], color=colors_bar, alpha=0.85, height=0.7)

    ax.axvline(0, color=GRAY, linewidth=0.8)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(
        [t.replace("_", " ").replace(" sp", ".") for t in sub["taxon"]],
        fontsize=6.5, color="#e2e8f0"
    )
    ax.set_xlabel("log₂(FC)", color=GRAY, fontsize=8)
    ax.set_title(f"{cancer}\n{CANCER_LABELS[cancer].split()[0]}", color="white",
                 fontsize=9.5, fontweight="bold")
    ax.tick_params(colors=GRAY, labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color(BORDER)

# Legend
from matplotlib.patches import Patch
legend_el = [Patch(facecolor="#ef4444", label="Enriched in cancer"),
             Patch(facecolor="#10b981", label="Depleted in cancer")]
fig.legend(handles=legend_el, loc="lower center", ncol=2,
           facecolor=CARD, labelcolor="white", fontsize=10,
           bbox_to_anchor=(0.5, -0.04))
plt.tight_layout()
plt.savefig(FIGS / "fig4_biomarkers_enrichment.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig4_biomarkers_enrichment.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — Risque de biais (NOS scores)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)

quality_colors = {"High": "#10b981", "Moderate": "#f59e0b", "Low": "#ef4444"}
y_labels = df_rob["study"].tolist()
y_pos    = range(len(y_labels))
bar_colors = [quality_colors[q] for q in df_rob["quality"]]

ax.barh(list(y_pos), df_rob["total_nos"], color=bar_colors, alpha=0.85, height=0.65)
ax.axvline(7, color="#f59e0b", linestyle="--", alpha=0.5, linewidth=1)
ax.axvline(8, color="#10b981", linestyle="--", alpha=0.5, linewidth=1)

for yp, (_, row) in zip(y_pos, df_rob.iterrows()):
    ax.text(row["total_nos"] + 0.05, yp,
            f"{row['total_nos']}/9  ({row['quality']})",
            va="center", color="#e2e8f0", fontsize=8)

y_labels_combined = [f"{s} [{c}]" for s, c in zip(df_rob["study"], df_rob["cancer_type"])]
ax.set_yticks(list(y_pos))
ax.set_yticklabels(y_labels_combined, color="#e2e8f0", fontsize=8)
ax.set_xlim(0, 10.5)
ax.set_xlabel("Newcastle-Ottawa Scale Score (/9)", color=GRAY, fontsize=10)
ax.set_title(f"Figure 5 — Risk of Bias Assessment (Newcastle-Ottawa Scale)\n"
             f"{len(df_rob)} included studies",
             color="white", fontsize=12, fontweight="bold")
ax.tick_params(colors=GRAY)
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["bottom", "left"]].set_color(BORDER)

legend_el = [Patch(facecolor=v, label=k) for k, v in quality_colors.items()]
ax.legend(handles=legend_el, facecolor=CARD, labelcolor="white", fontsize=9, loc="lower right")

plt.tight_layout()
plt.savefig(FIGS / "fig5_risk_of_bias.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig5_risk_of_bias.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 — PRISMA Flow Diagram
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 11))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)

def prisma_box(ax, x, y, w, h, text, color="#1e293b", border="#3b82f6", fontsize=9):
    rect = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1", facecolor=color, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", color="white",
            fontsize=fontsize, multialignment="center",
            wrap=True)

def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.5))

# Identification
prisma_box(ax, 5, 11.2, 5.5, 0.8,
           "Records identified through database searching\nPubMed (n=284) · Embase (n=211) · WoS (n=167)\nTotal: n=662",
           border="#3b82f6", fontsize=9)
arrow(ax, 5, 10.8, 5, 10.2)

prisma_box(ax, 5, 9.8, 5.5, 0.8,
           "Records after duplicates removed\nn=498", border="#3b82f6")
arrow(ax, 5, 9.4, 5, 8.8)

prisma_box(ax, 5, 8.4, 5.5, 0.8,
           "Records screened (title/abstract)\nn=498", border="#f59e0b")
arrow(ax, 5, 8.0, 5, 7.4)
# Excluded box
prisma_box(ax, 8.2, 7.7, 2.8, 0.8,
           "Excluded\nn=391\n(not microbiome/cancer)", color="#1e293b", border="#ef4444", fontsize=8)
ax.annotate("", xy=(6.8, 7.7), xytext=(5.3, 7.8),
            arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2))

prisma_box(ax, 5, 7.0, 5.5, 0.8,
           "Full-text articles assessed for eligibility\nn=107", border="#f59e0b")
arrow(ax, 5, 6.6, 5, 6.0)
# Excluded full-text
prisma_box(ax, 8.2, 6.3, 2.8, 1.0,
           "Excluded (n=89)\n• No AUC reported (n=32)\n• <20 cases (n=24)\n• Review/editorial (n=18)\n• Duplicate cohort (n=15)",
           color="#1e293b", border="#ef4444", fontsize=7.5)
ax.annotate("", xy=(6.8, 6.3), xytext=(5.3, 6.3),
            arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2))

prisma_box(ax, 5, 5.5, 5.5, 0.8,
           "Studies included in meta-analysis\nn=14", border="#10b981")
arrow(ax, 5, 5.1, 5, 4.5)

prisma_box(ax, 5, 4.1, 5.5, 1.2,
           "Studies included in quantitative synthesis\n"
           "CRC: 5 studies (n=824)\nGC: 2 studies (n=306)\n"
           "PDAC: 3 studies (n=277)\nHCC: 2 studies (n=422)\nLC: 2 studies (n=277)\n"
           "Total: 14 studies · 2,106 patients",
           color="#0f3460", border="#10b981", fontsize=8.5)

ax.set_title("Figure 6 — PRISMA 2020 Flow Diagram",
             color="white", fontsize=13, fontweight="bold", pad=15)

plt.tight_layout()
plt.savefig(FIGS / "fig6_prisma_flow.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅ fig6_prisma_flow.png")

print(f"\n✅ Toutes les figures sauvegardées dans figures_v2/")
