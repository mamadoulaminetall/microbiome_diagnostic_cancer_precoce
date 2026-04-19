"""
Signature-based dysbiosis scoring engine.
Matches OTU columns to validated meta-analysis signatures and computes
a concordance score per cancer type, calibrated with pooled AUC.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

CANCER_LABELS = {
    "CRC":  "Colorectal (CRC)",
    "GC":   "Gastrique (GC)",
    "PDAC": "Pancréatique (PDAC)",
    "HCC":  "Hépatocarcinome (HCC)",
    "LC":   "Pulmonaire (LC)",
}

CANCER_COLORS = {
    "CRC":  "#3b82f6",
    "GC":   "#f59e0b",
    "PDAC": "#8b5cf6",
    "HCC":  "#10b981",
    "LC":   "#ef4444",
}

RISK_THRESHOLDS = {
    "Faible":  0.25,
    "Modéré":  0.50,
    "Élevé":   0.75,
}


@pd.core.common.cache_readonly if hasattr(pd.core.common, "cache_readonly") else lambda f: f
def _noop(f): return f


def load_signatures() -> pd.DataFrame:
    return pd.read_csv(DATA / "microbial_signatures.csv")


def load_estimates() -> pd.DataFrame:
    return pd.read_csv(DATA / "meta_analytic_estimates.csv")


def load_studies() -> pd.DataFrame:
    return pd.read_csv(DATA / "studies_registry.csv")


def load_rob() -> pd.DataFrame:
    return pd.read_csv(DATA / "risk_of_bias.csv")


def _normalize_name(name: str) -> str:
    return name.lower().replace("_", " ").replace("-", " ").strip()


def match_taxa(otu_columns: list[str], signatures: pd.DataFrame) -> dict[str, str]:
    """Return {otu_col: taxon} mapping for matched signatures."""
    matches = {}
    sig_taxa = signatures["taxon"].unique()
    for col in otu_columns:
        col_norm = _normalize_name(col)
        for taxon in sig_taxa:
            taxon_norm = _normalize_name(taxon)
            if col_norm == taxon_norm or taxon_norm in col_norm or col_norm in taxon_norm:
                matches[col] = taxon
                break
    return matches


def score_sample(
    sample: pd.Series,
    signatures: pd.DataFrame,
    estimates: pd.DataFrame,
    col_to_taxon: dict[str, str],
) -> dict:
    """
    Compute concordance score per cancer type for a single OTU sample.
    Returns dict with score, risk_level, matched_signatures per cancer type.
    """
    results = {}
    for cancer_type in CANCER_LABELS:
        cancer_sigs = signatures[signatures["cancer_type"] == cancer_type]
        if cancer_sigs.empty:
            continue

        total_weight = 0.0
        concordant_weight = 0.0
        matched = []

        for col, taxon in col_to_taxon.items():
            sig_row = cancer_sigs[cancer_sigs["taxon"] == taxon]
            if sig_row.empty:
                continue
            sig = sig_row.iloc[0]
            w = abs(sig["log2_fc"])
            total_weight += w
            abundance = float(sample[col])
            ref = float(sig["prevalence_ctrl"])
            concordant = (
                (sig["direction"] == "enriched" and abundance > ref) or
                (sig["direction"] == "depleted" and abundance < ref)
            )
            if concordant:
                concordant_weight += w
            matched.append({
                "taxon": taxon.replace("_", " "),
                "direction_expected": sig["direction"],
                "log2_fc": sig["log2_fc"],
                "observed": round(abundance, 3),
                "reference": round(ref, 3),
                "concordant": concordant,
            })

        raw_score = concordant_weight / total_weight if total_weight > 0 else 0.0

        est_row = estimates[estimates["cancer_type"] == cancer_type]
        auc = float(est_row["auc_pooled"].iloc[0]) if not est_row.empty else 0.8
        calibrated = raw_score * auc

        if calibrated < RISK_THRESHOLDS["Faible"]:
            risk = "Faible"
            risk_color = "#10b981"
        elif calibrated < RISK_THRESHOLDS["Modéré"]:
            risk = "Modéré"
            risk_color = "#f59e0b"
        elif calibrated < RISK_THRESHOLDS["Élevé"]:
            risk = "Élevé"
            risk_color = "#f97316"
        else:
            risk = "Très élevé"
            risk_color = "#ef4444"

        results[cancer_type] = {
            "label": CANCER_LABELS[cancer_type],
            "score": round(calibrated, 3),
            "raw_score": round(raw_score, 3),
            "auc_meta": auc,
            "risk": risk,
            "risk_color": risk_color,
            "n_matched": len(matched),
            "n_total_sigs": len(cancer_sigs),
            "matched_signatures": matched,
            "color": CANCER_COLORS[cancer_type],
        }

    return results


def dysbiosis_index(scores: dict) -> float:
    """Global dysbiosis index = max calibrated score across all cancer types."""
    if not scores:
        return 0.0
    return max(v["score"] for v in scores.values())


def generate_demo_sample(signatures: pd.DataFrame, dominant_cancer: str = "CRC") -> pd.Series:
    """
    Generate a realistic demo OTU sample with elevated signatures for dominant_cancer.
    """
    np.random.seed(42)
    data = {}
    for _, row in signatures.iterrows():
        base = float(row["prevalence_ctrl"])
        if row["cancer_type"] == dominant_cancer:
            if row["direction"] == "enriched":
                val = base * np.random.uniform(2.5, 4.0)
            else:
                val = base * np.random.uniform(0.1, 0.4)
        else:
            val = base * np.random.uniform(0.7, 1.3)
        data[row["taxon"]] = round(min(max(val, 0.0), 1.0), 4)
    return pd.Series(data)
