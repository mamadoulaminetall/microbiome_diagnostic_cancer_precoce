from pathlib import Path
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("❌ Usage : python preprocess_otu.py <chemin_fichier_csv>")
    sys.exit(1)

input_path = Path(sys.argv[1])
output_path = Path("data") / "otu_preprocessed.csv"

try:
    # Gérer l'en-tête spécial (il commence par "#OTU ID")
    df = pd.read_csv(input_path, comment='#')  # Ignore la ligne de commentaire
    df.columns = pd.read_csv(input_path, skiprows=0, nrows=0).columns  # Corrige les noms des colonnes

    # Vérifie les colonnes essentielles
    if "taxonomy" in df.columns:
        df = df.drop(columns=["taxonomy"])  # Supprime la colonne non utilisée ici

    # Vérifie si l’index est dans la première colonne
    if df.columns[0].lower() in ['#otu id', 'otu id']:
        df = df.rename(columns={df.columns[0]: "OTU_ID"})
        df.set_index("OTU_ID", inplace=True)

    # Remplace les valeurs NaN éventuelles par 0
    df.fillna(0, inplace=True)

    # Conversion explicite en float si besoin
    df = df.astype(float)

    df.to_csv(output_path)
    print("✅ Prétraitement terminé et fichier sauvegardé.")
except Exception as e:
    print(f"❌ Erreur lors du prétraitement : {e}")
    sys.exit(1)
