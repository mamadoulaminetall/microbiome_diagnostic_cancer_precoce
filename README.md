 🧬 Microbiome Diagnostic Cancer Précoce

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Enabled-brightgreen?logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/)
[![GitHub repo size](https://img.shields.io/github/repo-size/mamadoulaminetall/microbiome_diagnostic_cancer_precoce)](https://github.com/mamadoulaminetall/microbiome_diagnostic_cancer_precoce)

# 🧬 microbiome_diagnostic_cancer_precoce

## 🎯 Objectif
Créer une application de **diagnostic précoce du cancer** à partir des **données de séquençage du microbiome** (procaryotes & eucaryotes), en utilisant des **modèles de machine learning**, intégrée dans une application Streamlit dockerisée.

---

## 🧱 Architecture du Projet

```plaintext
microbiome_diagnostic_cancer_precoce/
├── app/                           # Interface Streamlit
│   └── app.py                     # Application principale
├── data/                          # Données d'exemple (si autorisé)
│   ├── otu_preprocessed.csv       # Fichier de données OTU prétraitées
│   ├── otu_test.csv               # Fichier de test OTU
│   ├── results.json               # Résultats de l'analyse
│   └── uploaded_otu.csv           # Fichier OTU téléchargé par l'utilisateur
├── Dockerfile                     # Conteneurisation
├── models/                        # Modèles ML sauvegardés (.joblib)
│   ├── feature_names.joblib       # Noms des features
│   ├── LogisticRegression_model.joblib
│   ├── random_forest_model.joblib
│   ├── RandomForest_model.joblib
│   ├── random_forest_model.pkl
│   ├── rf_model.joblib
│   ├── SVM_model.joblib
│   └── XGBoost_model.joblib
├── notebooks/                     # Analyses exploratoires (optionnel)
│   └── test_pipeline.ipynb        # Notebook d'exemple
├── scripts/                       
│   ├── preprocess_otu.py         # Script de prétraitement des données OTU
│   └── run_model.py              # Script pour exécuter le modèle ML
├── outputs/                       # Résultats visuels et modèles
│   ├── cm_LogisticRegression.png  # Matrice de confusion (Logistic Regression)
│   ├── cm_RandomForest.png       # Matrice de confusion (RandomForest)
│   ├── cm_SVM.png                # Matrice de confusion (SVM)
│   ├── cm_XGBoost.png            # Matrice de confusion (XGBoost)
│   ├── feat_imp_RandomForest.png # Importance des features (RandomForest)
│   ├── feat_imp_XGBoost.png      # Importance des features (XGBoost)
│   ├── model_comparison.csv      # Comparaison des modèles
│   ├── roc_curve_RandomForest.png# Courbe ROC (RandomForest)
│   └── roc_curves.png            # Courbes ROC combinées
├── README.md                     # Documentation
├── requirements.txt              # Dépendances Python
├── screenshot_app.png            # Capture d'écran de l'application
└── Dockerfile                    # Conteneurisation

🧠 Modèles de Machine Learning utilisés

    Random Forest ✅

    XGBoost ✅

    SVM ✅

    Logistic Regression ✅

    LightGBM (à venir)

    SHAP pour l’interprétation des modèles ✅

🖥️ Stack Technologique
Catégorie	Outils utilisés
Bioinformatique	QIIME 2, Kraken2, MetaPhlAn
Machine Learning	scikit-learn, XGBoost, LightGBM
Visualisation	Streamlit, SHAP, Matplotlib
Conteneurisation	Docker
Déploiement à venir	GitHub, DockerHub, ou cloud
🚀 Lancement de l'application
En local (Streamlit uniquement)

cd app/
streamlit run app.py

Via Docker

docker build -t microbiome_diagnostic .
docker run -p 8501:8501 microbiome_diagnostic

Ensuite, accédez à l'application via http://localhost:8501.
📥 Upload de vos données

Téléchargez un fichier .csv contenant les features microbiennes (une ligne = un échantillon).
Optionnel : format .fastq (en cours de développement avec QIIME 2).
✅ Statut actuel

    Modèle Random Forest validé (précision 100% sur dataset test)

    Interface Streamlit fonctionnelle

    SHAP intégré pour l'interprétation des modèles

    Dockerfile opérationnel

    Intégration de QIIME 2 pour le format FASTQ

    Déploiement cloud (à venir)

👨‍💻 Auteur

Mamadou Lamine TALL
📧 Contact : Email
🔗 GitHub : @mamadoulaminetall
📄 Licence

Ce projet est open-source sous licence MIT.
💡 Comment contribuer ?

    Forkez ce projet

    Créez votre branche de fonctionnalité (git checkout -b feature/feature-name)

    Committez vos modifications (git commit -m 'Ajout d'une nouvelle fonctionnalité')

    Poussez sur votre branche (git push origin feature/feature-name)

    Créez une pull request

🔧 Dépendances

Installez les dépendances Python en utilisant le fichier requirements.txt :

pip install -r requirements.txt
