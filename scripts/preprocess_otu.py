from pathlib import Path
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("❌ Usage : python preprocess_otu.py <chemin_fichier_csv>")
    sys.exit(1)

# CORRECTION ICI : transformer les chemins en objets Path
input_path = Path(sys.argv[1])
output_path = Path("data") / "otu_preprocessed.csv"

try:
    df = pd.read_csv(input_path)

    # … Ton prétraitement ici …

    df.to_csv(output_path, index=False)
    print("✅ Prétraitement terminé et fichier sauvegardé.")
except Exception as e:
    print(f"❌ Erreur lors du prétraitement : {e}")
    sys.exit(1)
