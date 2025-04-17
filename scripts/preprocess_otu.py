import pandas as pd

def preprocess_otu():
    # Charger le fichier OTU brut
    input_path = 'data/otu_test.csv'  # Tu as dit que c'est le fichier brut
    otu_df = pd.read_csv(input_path)

    # Transformation des données : création de la colonne 'label'
    # Exemple : Supposons que nous ajoutons un label basé sur les groupes Control et Model
    otu_df['label'] = otu_df[['Controlgroup1', 'Modelgroup1']].apply(
        lambda x: 0 if x['Controlgroup1'] > 0 else 1, axis=1)  # Condition à adapter selon ton besoin

    # Sauvegarder le fichier prétraité avec la nouvelle colonne 'label'
    output_path = 'data/otu_preprocessed.csv'
    otu_df.to_csv(output_path, index=False)
    print("Prétraitement terminé et fichier sauvegardé.")

if __name__ == "__main__":
    preprocess_otu()
