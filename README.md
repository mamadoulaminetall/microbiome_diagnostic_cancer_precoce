# 🧬 Microbiome Cancer Diagnostic — MedFlow AI

> **Plateforme de détection précoce du cancer par analyse du microbiome intestinal**  
> Basée sur une méta-analyse validée · 18 études · 2 587 patients · 5 types de cancer

[![bioRxiv](https://img.shields.io/badge/bioRxiv-BIORXIV%2F2026%2F719461-b31b1b)](https://www.biorxiv.org)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Présentation

Cette plateforme Streamlit permet l'analyse de données de microbiome intestinal (OTU/16S) pour évaluer le risque de 5 types de cancer, en se basant sur **74 signatures microbiennes validées** issues d'une méta-analyse systématique publiée.

### Types de cancer couverts

| Code | Cancer | AUC poolée | I² | k études |
|------|--------|-----------|-----|---------|
| CRC  | Colorectal | **0.785** [0.750–0.819] | 30.6% | 5 |
| GC   | Gastrique | **0.834** [0.781–0.887] | 56.6% | 3 |
| PDAC | Pancréatique | **0.853** [0.812–0.894] | 18.4% | 4 |
| HCC  | Hépatocarcinome | **0.809** [0.762–0.856] | 42.1% | 3 |
| LC   | Pulmonaire | **0.780** [0.738–0.822] | 25.8% | 3 |

---

## Modules

### 🔬 Analyse OTU
- Import fichier CSV/XLSX (OTU table · abondances relatives)
- Correspondance automatique avec les 74 signatures validées
- Score de risque calibré par l'AUC poolée de la méta-analyse
- Indice de dysbiose global
- Tableaux de signatures concordantes par cancer

### 📊 Méta-Analyse
- Forest plots interactifs par type de cancer
- Tableau des 18 études (filtre par cancer, AUC, année)
- Évaluation du risque de biais (Newcastle-Ottawa Scale)
- Analyse de l'hétérogénéité I² et τ²

### 🧫 Signatures Microbiennes
- Exploration des 74 signatures avec filtres (cancer, direction, log₂FC)
- Heatmap log₂FC tous cancers
- Top biomarqueurs par cancer
- Biomarqueurs communs (cross-cancer)

### 📄 Rapport Clinique PDF
- Génération d'un rapport structuré pour le clinicien
- Indice de dysbiose, scores par cancer, signatures détectées
- Téléchargement PDF immédiat

---

## Installation

```bash
git clone https://github.com/mamadoulaminetall/microbiome_diagnostic_cancer_precoce.git
cd microbiome_diagnostic_cancer_precoce
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

---

## Format des données d'entrée

Le fichier OTU doit être un **CSV ou XLSX** avec :
- **Une ligne par échantillon**
- **Une colonne par taxon** (nommée avec le nom du micro-organisme)
- **Valeurs = abondances relatives** [0–1]

```csv
Fusobacterium_nucleatum,Faecalibacterium_prausnitzii,Akkermansia_muciniphila,...
0.72,0.08,0.03,...
```

Un bouton **"Données démo"** est disponible dans chaque module pour tester sans données réelles.

---

## Structure du projet

```
microbiome_diagnostic_cancer_precoce/
├── app.py                    # Page d'accueil
├── pages/
│   ├── 1_Analyse.py          # Analyse OTU → scores de risque
│   ├── 2_Meta_Analyse.py     # Dashboard méta-analyse
│   ├── 3_Signatures.py       # Explorateur de signatures
│   └── 4_Rapport.py          # Générateur de rapport PDF
├── utils/
│   ├── scoring.py            # Moteur de scoring par signature
│   └── pdf_report.py         # Génération PDF (ReportLab)
├── data/
│   ├── meta_analytic_estimates.csv   # AUC poolées, I², τ²
│   ├── microbial_signatures.csv      # 74 signatures validées
│   ├── studies_registry.csv          # 18 études incluses
│   └── risk_of_bias.csv              # Scores NOS
├── .streamlit/
│   └── config.toml           # Thème dark
└── requirements.txt
```

---

## Méthode scientifique

### Méta-analyse
- **Modèle** : DerSimonian-Laird (effets aléatoires)
- **Mesure** : AUC-ROC poolée (variance : formule Hanley-McNeil)
- **Hétérogénéité** : Cochran Q, I², τ²
- **Biais** : Newcastle-Ottawa Scale (NOS)

### Scoring de risque
1. Correspondance des colonnes OTU avec les taxons de référence (matching lexical)
2. Pour chaque signature : vérification de la concordance direction (enrichi/déplété)
3. Score brut = somme des poids log₂FC concordants / somme totale des poids
4. Score calibré = Score brut × AUC poolée (méta-analyse)
5. Seuils : Faible <25% · Modéré 25–50% · Élevé 50–75% · Très élevé >75%

---

## Publication de référence

> **TALL ML** (2026). Gut Microbiome as a Diagnostic Biomarker for Early Cancer Detection:  
> A Systematic Review and Meta-Analysis of 18 Studies across Five Cancer Types.  
> *bioRxiv* BIORXIV/2026/719461. MedFlow AI, Aix-Marseille Universite.

---

## Avertissement

> ⚠️ **Usage exploratoire et de recherche uniquement.**  
> Cet outil ne fournit pas de diagnostic médical. Les résultats doivent être interprétés  
> par un professionnel de santé qualifié dans le contexte clinique du patient.  
> Non validé pour un usage clinique direct.

---

## Auteur

**Dr. Mamadou Lamine TALL, PhD**  
Bioinformatique & Intelligence Artificielle médicale  
MedFlow AI · Aix-Marseille Universite  
📧 mamadoulaminetallgithub@gmail.com  
🐙 [github.com/mamadoulaminetall](https://github.com/mamadoulaminetall)

---

*MedFlow AI © 2026*
