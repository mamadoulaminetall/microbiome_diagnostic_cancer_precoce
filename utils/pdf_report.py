"""
Clinical PDF report generator — ReportLab
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

DARK_BLUE   = colors.HexColor("#1e3a5f")
MID_BLUE    = colors.HexColor("#2563eb")
LIGHT_GRAY  = colors.HexColor("#f8fafc")
DARK_TEXT   = colors.HexColor("#1f2937")
GRAY_TEXT   = colors.HexColor("#6b7280")
GREEN       = colors.HexColor("#059669")
AMBER       = colors.HexColor("#d97706")
ORANGE      = colors.HexColor("#ea580c")
RED         = colors.HexColor("#dc2626")
BORDER      = colors.HexColor("#e2e8f0")

RISK_COLORS = {
    "Faible":     GREEN,
    "Modéré":     AMBER,
    "Élevé":      ORANGE,
    "Très élevé": RED,
}


def _styles():
    base = getSampleStyleSheet()
    def S(name="Normal", **kw):
        return ParagraphStyle(name + str(id(kw)), parent=base.get(name, base["Normal"]), **kw)
    return dict(
        title  = S("Title", fontSize=16, leading=20, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=4),
        sub    = S("Normal", fontSize=10, leading=14, textColor=GRAY_TEXT, alignment=TA_CENTER, spaceAfter=2),
        h1     = S("Heading1", fontSize=12, leading=15, textColor=DARK_BLUE, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
        body   = S("Normal", fontSize=9.5, leading=13, textColor=DARK_TEXT, spaceAfter=5, alignment=TA_JUSTIFY),
        small  = S("Normal", fontSize=8.5, leading=11, textColor=GRAY_TEXT, spaceAfter=3),
        bold   = S("Normal", fontSize=9.5, leading=13, textColor=DARK_TEXT, fontName="Helvetica-Bold"),
        warn   = S("Normal", fontSize=8.5, leading=12, textColor=AMBER, spaceAfter=4, fontName="Helvetica-Oblique"),
        center = S("Normal", fontSize=9.5, leading=13, textColor=DARK_TEXT, alignment=TA_CENTER),
    )


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6)


def _risk_table(scores: dict, st: dict) -> Table:
    rows = [["Type de cancer", "Score (0–1)", "AUC méta", "Niveau de risque"]]
    for cancer, info in scores.items():
        risk_color = RISK_COLORS.get(info["risk"], DARK_TEXT)
        rows.append([
            Paragraph(info["label"], st["body"]),
            Paragraph(f"{info['score']:.3f}", st["center"]),
            Paragraph(f"{info['auc_meta']:.3f}", st["center"]),
            Paragraph(f"<font color='#{risk_color.hexval()[2:]}''><b>{info['risk']}</b></font>", st["center"]),
        ])
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])
    return Table(rows, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3.5*cm], style=ts, repeatRows=1)


def _sig_table(matched: list, st: dict) -> Table:
    rows = [["Taxon", "Direction attendue", "log₂FC", "Observé", "Référence", "Concordant"]]
    for s in matched[:20]:
        conc_text = "Oui" if s["concordant"] else "Non"
        conc_color = "#059669" if s["concordant"] else "#dc2626"
        rows.append([
            Paragraph(f"<i>{s['taxon']}</i>", st["small"]),
            Paragraph(s["direction_expected"], st["small"]),
            Paragraph(f"{s['log2_fc']:+.1f}", st["small"]),
            Paragraph(f"{s['observed']:.3f}", st["small"]),
            Paragraph(f"{s['reference']:.3f}", st["small"]),
            Paragraph(f"<font color='{conc_color}'><b>{conc_text}</b></font>", st["small"]),
        ])
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
    ])
    return Table(rows, colWidths=[5.0*cm, 2.8*cm, 1.5*cm, 1.8*cm, 1.8*cm, 1.6*cm], style=ts, repeatRows=1)


def generate_pdf(
    scores: dict,
    dysbiosis: float,
    patient_id: str,
    sample_id: str,
    n_taxa: int,
    n_matched: int,
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )
    st = _styles()
    story = []

    # Header
    story.append(Paragraph("MedFlow AI — Rapport Clinique", st["title"]))
    story.append(Paragraph("Diagnostic Prédictif par Analyse du Microbiome Intestinal", st["sub"]))
    story.append(Paragraph(
        f"Patient : <b>{patient_id}</b> &nbsp;|&nbsp; Échantillon : <b>{sample_id}</b> &nbsp;|&nbsp; "
        f"Date : <b>{datetime.today().strftime('%d/%m/%Y')}</b>",
        st["sub"],
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(_hr())

    # Dysbiosis banner
    di_pct = round(dysbiosis * 100, 1)
    di_color = "#059669" if dysbiosis < 0.25 else "#d97706" if dysbiosis < 0.5 else "#dc2626"
    story.append(KeepTogether([
        Paragraph("Indice de Dysbiose Global", st["h1"]),
        Paragraph(
            f"<font color='{di_color}' size=22><b>{di_pct}%</b></font> &nbsp; "
            f"(score normalisé 0–100 % · basé sur {n_matched}/{n_taxa} taxons détectés)",
            st["body"],
        ),
        Spacer(1, 0.2*cm),
    ]))

    # Risk scores
    story.append(Paragraph("Scores de Risque par Type de Cancer", st["h1"]))
    story.append(Paragraph(
        f"Scores calculés par concordance avec {n_matched} signatures microbiennes validées "
        "(méta-analyse · 18 études · 2 587 patients), calibrés par l'AUC poolée.",
        st["body"],
    ))
    story.append(_risk_table(scores, st))
    story.append(Spacer(1, 0.4*cm))

    # Per-cancer signature details
    for cancer, info in scores.items():
        if not info["matched_signatures"]:
            continue
        n_conc = sum(1 for s in info["matched_signatures"] if s["concordant"])
        story.append(KeepTogether([
            _hr(),
            Paragraph(f"Signatures détectées — {info['label']}", st["h1"]),
            Paragraph(
                f"Taxons concordants : {n_conc}/{info['n_matched']} · "
                f"Score brut : {info['raw_score']:.3f} · Score calibré : {info['score']:.3f} · "
                f"Risque : <b>{info['risk']}</b>",
                st["body"],
            ),
            _sig_table(info["matched_signatures"], st),
            Spacer(1, 0.3*cm),
        ]))

    story.append(PageBreak())

    # Scientific basis
    story.append(Paragraph("Base Scientifique", st["h1"]))
    story.append(Paragraph(
        "Ce rapport est généré à partir des données de référence issues de la méta-analyse "
        "\"Gut Microbiome as a Diagnostic Biomarker for Early Cancer Detection\" "
        "(TALL ML, MedFlow AI, bioRxiv BIORXIV/2026/719461, avril 2026).",
        st["body"],
    ))
    story.append(Paragraph(
        "La méta-analyse a inclus 18 études publiées (2 587 patients, 5 types de cancer) et "
        "identifié 74 signatures microbiennes validées avec des AUC poolées de 0.780–0.853.",
        st["body"],
    ))

    # Disclaimer
    story.append(Spacer(1, 0.4*cm))
    story.append(_hr())
    story.append(Paragraph(
        "⚠️ AVERTISSEMENT : Cet outil est à usage exploratoire et de recherche uniquement. "
        "Les résultats ne constituent pas un diagnostic médical et doivent être interprétés "
        "par un professionnel de santé qualifié dans le contexte clinique du patient.",
        st["warn"],
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "MedFlow AI © 2026 · Dr. Mamadou Lamine TALL, PhD · Bioinformatique & IA médicale · "
        "mamadoulaminetallgithub@gmail.com",
        st["small"],
    ))

    doc.build(story)
    return buf.getvalue()
