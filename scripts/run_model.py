import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns

def run_models(data):
    # Vérifier si la colonne 'label' existe
    if 'label' not in data.columns:
        print("Erreur : La colonne 'label' est manquante dans les données.")
        return
    
    # Séparer les features (X) et la cible (y)
    X = data.drop(['label', 'taxonomy'], axis=1)  # On supprime la colonne 'taxonomy' aussi
    y = data['label']

    # Séparation des données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialisation et entraînement du modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Prédictions sur les données de test
    y_pred = model.predict(X_test)

    # Évaluation du modèle
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Précision du modèle sur les données de test : {accuracy * 100:.2f}%")

    # Calcul de la courbe ROC
    fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:, 1])
    roc_auc = auc(fpr, tpr)

    # Affichage des résultats
    print(f"Courbe ROC - AUC : {roc_auc:.2f}")

    # Importance des features
    print("Importance des features :")
    feature_importance = model.feature_importances_
    for feature, importance in zip(X.columns, feature_importance):
        print(f"{feature}: {importance:.4f}")

    # Sauvegarde des graphiques
    # Importance des features
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(X.columns), y=feature_importance)
    plt.title("Importance des Features - Modèle Random Forest")
    plt.xticks(rotation=90)
    plt.xlabel("Features")
    plt.ylabel("Importance")
    plt.tight_layout()
    plt.savefig('outputs/feat_imp_RandomForest.png')  # Sauvegarde du graphique
    plt.close()

    # Courbe ROC
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'Courbe ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de faux positifs (FPR)')
    plt.ylabel('Taux de vrais positifs (TPR)')
    plt.title('Courbe ROC - Modèle Random Forest')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig('outputs/roc_curve_RandomForest.png')  # Sauvegarde du graphique
    plt.close()

    # Sauvegarde du modèle
    joblib.dump(model, 'models/random_forest_model.joblib')
    print("Modèle entraîné et sauvegardé avec succès")

    # Sauvegarder les résultats dans un fichier JSON
    results = {
        'accuracy': accuracy,
        'roc_auc': roc_auc,
    }
    with open('data/results.json', 'w') as results_file:
        json.dump(results, results_file)
    print("Résultats sauvegardés dans results.json")

    return "Modèle entraîné avec succès"

if __name__ == "__main__":
    try:
        # Charger les données prétraitées
        df = pd.read_csv('data/otu_preprocessed.csv')

        # Exécuter la fonction de modélisation
        run_models(df)
    except Exception as e:
        print(f"Erreur lors de l'exécution du modèle : {e}")
