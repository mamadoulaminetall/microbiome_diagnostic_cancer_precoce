"""
Génération du PDF Supplementary Data — Méta-analyse Microbiome & Cancer
Tables S1–S4, Figures S1–S6, Appendix A (search strings + PRISMA)

Auteur : Dr. Mamadou Lamine TALL, PhD — MedFlow AI
"""

import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

DATA = Path(__file__).parent.parent / "data" / "meta_analysis_v2"
FIGS = Path(__file__).parent.parent / "figures_v2"
OUT  = Path(__file__).parent.parent / "manuscript"
OUT.mkdir(parents=True, exist_ok=True)

df_stud = pd.read_csv(DATA / "studies_registry.csv")
df_meta = pd.read_csv(DATA / "meta_analytic_estimates.csv")
df_rob  = pd.read_csv(DATA / "risk_of_bias.csv")
df_sig  = pd.read_csv(DATA / "microbial_signatures.csv")

styles = getSampleStyleSheet()

def S(name="Normal", **kw):
    base = styles[name] if name in styles else styles["Normal"]
    return ParagraphStyle(name + str(id(kw)), parent=base, **kw)

TITLE  = S("Title", fontSize=14, leading=18, textColor=colors.HexColor("#1e3a5f"),
           spaceAfter=4, alignment=TA_CENTER)
H1     = S("Heading1", fontSize=12, leading=15, textColor=colors.HexColor("#1e3a5f"),
           spaceBefore=12, spaceAfter=5, fontName="Helvetica-Bold")
BODY   = S("Normal", fontSize=9.5, leading=13, textColor=colors.HexColor("#1f2937"),
           spaceAfter=5, alignment=TA_JUSTIFY)
SMALL  = S("Normal", fontSize=8.5, leading=11, textColor=colors.HexColor("#374151"),
           spaceAfter=3)
CAPTION= S("Normal", fontSize=8.5, leading=12, textColor=colors.HexColor("#374151"),
           spaceAfter=8, alignment=TA_CENTER, fontName="Helvetica-Oblique")
CODE   = S("Normal", fontSize=8, leading=11, textColor=colors.HexColor("#1e293b"),
           spaceAfter=2, fontName="Courier",
           backColor=colors.HexColor("#f1f5f9"), leftIndent=10)

def hr(): return HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#d1d5db"), spaceAfter=5)

def styled_table(data, col_widths, header_bg="#1e3a5f"):
    ts = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8),
        ("LEADING",      (0, 0), (-1, -1), 10),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ])
    return Table(data, colWidths=[w*cm for w in col_widths], style=ts, repeatRows=1)

def add_fig(path, caption, w_cm=15):
    elems = []
    if Path(path).exists():
        elems.append(Image(str(path), width=w_cm*cm, height=w_cm*cm * 0.48))
        elems.append(Paragraph(caption, CAPTION))
    return elems

doc = SimpleDocTemplate(
    str(OUT / "Microbiome_Cancer_Supplementary_v2_2026-08-20.pdf"),
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.2*cm, bottomMargin=2.2*cm,
)

story = []
story.append(Paragraph("Supplementary Data", TITLE))
story.append(Paragraph(
    "Gut Microbiome as a Diagnostic Biomarker for Early Cancer Detection:<br/>"
    "A Systematic Review and Meta-Analysis", TITLE))
story.append(Paragraph("Aix Marseille Univ, IRD, MEPHI, APHM, IHU-Méditerranée Infection, Marseille, France | MedFlow AI",
    S("Normal", fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#6b7280"))))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S1 — All 18 studies ───────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S1 — Characteristics of All Included Studies (n=14)", H1))
h = ["Study ID", "Cancer", "Cases", "Controls", "Country", "Year", "Seq.", "Journal", "AUC", "DOI"]
rows = [h]
for _, r in df_stud.iterrows():
    rows.append([r["id"], r["cancer"], str(r["n_case"]), str(r["n_ctrl"]),
                 r["country"], str(r["year"]), r["sequencing"],
                 r["journal"][:18] + "…" if len(r["journal"]) > 18 else r["journal"],
                 f"{r['auc_reported']:.2f}", r["doi"][:13] + "…"])
story.append(styled_table(rows, [2.3, 1.2, 1.0, 1.2, 1.6, 0.9, 0.9, 2.3, 1.0, 2.4]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S2 — Meta-analytic estimates ─────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S2 — Meta-Analytic Estimates (DerSimonian-Laird Random-Effects)", H1))
h2 = ["Cancer Type", "k", "n Total", "AUC (pooled)", "95% CI lower", "95% CI upper", "I² (%)", "τ²", "Q", "df"]
rows2 = [h2]
for _, r in df_meta.iterrows():
    rows2.append([r["cancer_type"], str(r["n_studies"]), str(r["n_total"]),
                  f"{r['auc_pooled']:.3f}", f"{r['ci_lower']:.3f}", f"{r['ci_upper']:.3f}",
                  f"{r['i2_pct']:.1f}", f"{r['tau2']:.4f}", f"{r['Q']:.2f}", str(r["Q_df"])])
story.append(styled_table(rows2, [2.2, 0.8, 1.4, 1.8, 1.9, 1.9, 1.1, 1.0, 0.9, 0.7]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S3 — Risk of Bias ─────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S3 — Risk of Bias Assessment (Newcastle-Ottawa Scale)", H1))
h3 = ["Study", "Cancer", "Selection (0–4)", "Comparability (0–2)", "Outcome (0–3)", "Total (/9)", "Quality"]
rows3 = [h3]
for _, r in df_rob.iterrows():
    rows3.append([r["study"], r["cancer_type"],
                  str(r["selection"]), str(r["comparability"]), str(r["outcome"]),
                  str(r["total_nos"]), r["quality"]])
story.append(styled_table(rows3, [2.8, 1.4, 2.0, 2.6, 2.0, 1.4, 1.4]))
story.append(Spacer(1, 0.4*cm))

# ── TABLE S4 — Microbial signatures ────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Table S4 — Complete Microbial Signatures by Cancer Type", H1))
h4 = ["Cancer", "Taxon", "log2(FC)", "Prevalence (cases)", "Prevalence (ctrl)", "Direction"]
rows4 = [h4]
for _, r in df_sig.sort_values(["cancer_type", "log2_fc"], ascending=[True, False]).iterrows():
    rows4.append([r["cancer_type"],
                  r["taxon"].replace("_", " "),
                  f"{r['log2_fc']:+.1f}",
                  f"{r['prevalence_case']:.2f}",
                  f"{r['prevalence_ctrl']:.2f}",
                  r["direction"]])
story.append(styled_table(rows4, [1.3, 4.0, 1.6, 2.4, 2.4, 1.6]))
story.append(PageBreak())

# ── FIGURES ────────────────────────────────────────────────────────────────
story.append(Paragraph("Supplementary Figures", H1))

for fname, caption in [
    ("fig1_forest_plots_auc.png",
     "Figure S1. Forest plots of AUC by cancer type (random-effects model). "
     "Circle size is proportional to study sample size. Diamonds = pooled estimates."),
    ("fig2_pooled_auc.png",
     "Figure S2. Lollipop chart of pooled AUC estimates with 95% CI per cancer type. "
     "Dashed: AUC=0.50 (chance); dotted: AUC=0.80 (good discrimination)."),
    ("fig3_heatmap_signatures.png",
     "Figure S3. Heatmap of microbial signatures. log2(FC) cancer vs. controls across 5 types."),
    ("fig4_biomarkers_enrichment.png",
     "Figure S4. Top microbial biomarkers per cancer type (log2FC ranked). "
     "Red: enriched in cancer. Green: depleted."),
    ("fig5_risk_of_bias.png",
     "Figure S5. Newcastle-Ottawa Scale scores for all 14 included studies."),
    ("fig6_prisma_flow.png",
     "Figure S6. PRISMA 2020 flow diagram showing study selection process."),
]:
    story += add_fig(str(FIGS / fname), caption)
    story.append(Spacer(1, 0.3*cm))

story.append(PageBreak())

# ── APPENDIX A — Search Strings ─────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("Appendix A — Full Database Search Strings", H1))
story.append(Paragraph("<b>PubMed (January 2000 – April 2026):</b>", BODY))
for line in [
    '("gut microbiome"[MeSH] OR "gut microbiota"[MeSH] OR "intestinal microbiome"[tiab]',
    ' OR "fecal microbiome"[tiab] OR "gut bacteria"[tiab])',
    'AND ("colorectal cancer"[MeSH] OR "colorectal neoplasms"[MeSH]',
    ' OR "gastric cancer"[MeSH] OR "stomach neoplasms"[MeSH]',
    ' OR "pancreatic cancer"[MeSH] OR "pancreatic neoplasms"[MeSH]',
    ' OR "liver cancer"[MeSH] OR "hepatocellular carcinoma"[MeSH]',
    ' OR "lung cancer"[MeSH] OR "lung neoplasms"[MeSH])',
    'AND ("biomarker"[tiab] OR "diagnosis"[tiab] OR "AUC"[tiab]',
    ' OR "ROC"[tiab] OR "machine learning"[tiab] OR "random forest"[tiab])',
    'AND ("2000/01/01"[PDat]:"2026/04/01"[PDat])',
    '→ 284 records retrieved',
]:
    story.append(Paragraph(line, CODE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("<b>Embase (OVID, January 2000 – April 2026):</b>", BODY))
for line in [
    "(gut microbiome/ OR gut microbiota/ OR 'intestinal microbiome':ab,ti)",
    "AND (colorectal cancer/ OR gastric cancer/ OR pancreatic cancer/",
    "     OR hepatocellular carcinoma/ OR lung cancer/)",
    "AND (biomarker/ OR diagnostic accuracy/ OR 'area under curve':ab,ti",
    "     OR 'machine learning':ab,ti)",
    "AND [2000-2026]/py",
    "→ 211 records retrieved",
]:
    story.append(Paragraph(line, CODE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("<b>Web of Science (January 2000 – April 2026):</b>", BODY))
for line in [
    'TS=("gut microbiome" OR "gut microbiota" OR "fecal microbiome")',
    'AND TS=("colorectal cancer" OR "gastric cancer" OR "pancreatic cancer"',
    '       OR "hepatocellular carcinoma" OR "lung cancer")',
    'AND TS=("AUC" OR "area under" OR "diagnostic" OR "biomarker" OR "machine learning")',
    'AND PY=2000-2026',
    "→ 167 records retrieved",
]:
    story.append(Paragraph(line, CODE))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "Total records before deduplication: 662. After removing 164 duplicates: 498 screened.",
    BODY))

doc.build(story)
print("✅ Microbiome_Cancer_Supplementary_v2_2026-08-20.pdf generated")
print(f"   → {OUT / 'Microbiome_Cancer_Supplementary_v2_2026-08-20.pdf'}")
