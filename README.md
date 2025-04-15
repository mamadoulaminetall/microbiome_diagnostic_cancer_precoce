

# 🧬 microbiome_diagnostic_cancer_precoce

## 🎯 Objectif
Créer une application de **diagnostic précoce du cancer** à partir des **données de séquençage du microbiome** (procaryotes & eucaryotes), en utilisant des **modèles de machine learning**, intégrée dans une application Streamlit dockerisée.

---

## 🧱 Architecture du Projet

microbiome_diagnostic_cancer_precoce/ ├── app/ │ └── app.py # Interface Streamlit ├── data/ # Données d'exemple (si autorisé) ├── models/ # Modèles ML sauvegardés (.joblib) ├── notebooks/ # Analyses exploratoires (optionnel) ├── scripts/ │ └── evaluate_models.py # Script d'entraînement et évaluation ML ├── Dockerfile # Conteneurisation ├── requirements.txt # Dépendances Python ├── README.md # Documentation


---

## 🧠 Modèles de Machine Learning utilisés
- Random Forest ✅
- XGBoost ✅
- SVM ✅
- Logistic Regression ✅
- LightGBM (à venir)
- SHAP pour l’interprétation des modèles ✅

---

## 🖥️ Stack Technologique

| Catégorie            | Outils utilisés                        |
|----------------------|----------------------------------------|
| Bioinformatique      | QIIME 2, Kraken2, MetaPhlAn            |
| Machine Learning     | scikit-learn, XGBoost, LightGBM        |
| Visualisation        | Streamlit, SHAP, Matplotlib            |
| Conteneurisation     | Docker                                 |
| Déploiement à venir  | GitHub, DockerHub, ou cloud            |

---

## 🚀 Lancement de l'application

### En local (Streamlit uniquement)

```bash
cd app/
streamlit run app.py

Via Docker

docker build -t microbiome_diagnostic .
docker run -p 8501:8501 microbiome_diagnostic

Puis accéder à : http://localhost:8501
📥 Upload de vos données

    .csv contenant les features microbiennes (1 ligne = 1 échantillon).

    Optionnel : format .fastq (traitement en cours de développement via QIIME 2).

✅ Statut actuel

Modèle ML Random Forest validé (précision 100% sur dataset test)

Interface Streamlit fonctionnelle

SHAP intégré pour interprétation

Dockerfile opérationnel

Intégration de QIIME 2 pour le FASTQ

    Déploiement cloud (à venir)

👨‍💻 Auteur

Mamadou Lamine TALL
📧 Contact : mamadoulaminetallgithub@gmail.com
🔗 GitHub: @mamadoulaminetall
📄 Licence

Ce projet est open-source sous licence MIT.


---
