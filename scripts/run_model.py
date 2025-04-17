import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, auc, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import json  # Importation du module json pour sauvegarder les résultats

def run_models(data):
    # Vérifier si la colonne 'label' existe
    if 'label' not in data.columns:
        print("Erreur : La colonne 'label' est manquante dans les données.")
        return
    
    # Séparer les features (X) et la cible (y)
    X = data.drop(['label', 'taxonomy'], axis=1)  # On supprime la colonne 'taxonomy' aussi
    y = data['label']

    # Vérifier et convertir les colonnes non numériques en numériques
    for column in X.columns:
        if X[column].dtype == 'object':  # Si la colonne contient des chaînes de caractères
            le = LabelEncoder()  # Utilisation du LabelEncoder pour transformer les chaînes en chiffres
            X[column] = le.fit_transform(X[column])
    
    # Séparation des données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialisation des modèles
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(random_state=42),
        'SVM': SVC(probability=True, random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42)
    }

    results = {}

    # Entraînement et évaluation des modèles
    for model_name, model in models.items():
        print(f"Entraînement du modèle {model_name}...")
        model.fit(X_train, y_train)

        # Prédictions sur les données de test
        y_pred = model.predict(X_test)

        # Calcul de la précision
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Précision du modèle {model_name} : {accuracy * 100:.2f}%")

        # Calcul de la courbe ROC
        fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:, 1])
        roc_auc = auc(fpr, tpr)
        print(f"Courbe ROC - AUC : {roc_auc:.2f}")

        # Matrice de confusion
        cm = confusion_matrix(y_test, y_pred)
        print(f"Matrice de confusion : \n{cm}")

        # Sauvegarde des résultats du modèle
        results[model_name] = {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'confusion_matrix': cm.tolist()  # Convertir la matrice de confusion en liste pour JSON
        }

        # Sauvegarde des graphiques
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', lw=2, label=f'Courbe ROC (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Taux de faux positifs (FPR)')
        plt.ylabel('Taux de vrais positifs (TPR)')
        plt.title(f'Courbe ROC - {model_name}')
        plt.legend(loc='lower right')
        plt.tight_layout()
        plt.savefig(f'outputs/roc_curve_{model_name}.png')
        plt.close()

        # Importance des features pour RandomForest et XGBoost
        if model_name in ['Random Forest', 'XGBoost']:
            feature_importance = model.feature_importances_
            plt.figure(figsize=(10, 6))
            sns.barplot(x=list(X.columns), y=feature_importance)
            plt.title(f"Importance des Features - {model_name}")
            plt.xticks(rotation=90)
            plt.xlabel("Features")
            plt.ylabel("Importance")
            plt.tight_layout()
            plt.savefig(f'outputs/feat_imp_{model_name}.png')
            plt.close()

    # Sauvegarde des résultats dans un fichier JSON
    with open('data/results.json', 'w') as results_file:
        json.dump(results, results_file, indent=4)

    print("Modèles entraînés et sauvegardés avec succès")

if __name__ == "__main__":
    try:
        # Charger les données prétraitées
        df = pd.read_csv('data/otu_preprocessed.csv')

        # Exécuter la fonction de modélisation
        run_models(df)
    except Exception as e:
        print(f"Erreur lors de l'exécution du modèle : {e}")
