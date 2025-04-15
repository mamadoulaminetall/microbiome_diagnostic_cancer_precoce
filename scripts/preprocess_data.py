import pandas as pd
import numpy as np

# Chemin d'entrée pour les données brutes
raw_file = "data/sample_data.csv"  # Modification du chemin vers le fichier correct

# Chargement des données brutes
try:
    df = pd.read_csv(raw_file)
    print(f"✅ Fichier {raw_file} chargé avec succès.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du fichier {raw_file}: {e}")
    exit(1)

# Vérification de l'aperçu des données
print("Aperçu des données chargées :")
print(df.head())

# Exemple de nettoyage des données
# Supprimer les lignes avec des valeurs manquantes
df_cleaned = df.dropna()

# Enregistrement du fichier nettoyé
output_file = "data/processed/clean_data.csv"  # Modification du chemin de sortie
try:
    df_cleaned.to_csv(output_file, index=False)
    print(f"✅ Données nettoyées sauvegardées sous {output_file}.")
except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde du fichier nettoyé : {e}")
    exit(1)
