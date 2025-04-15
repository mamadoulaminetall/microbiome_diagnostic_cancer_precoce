import streamlit as st
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt

# Configuration de la page Streamlit
st.set_page_config(page_title="Détection précoce du cancer via le microbiome", layout="wide")

# Titre et description de l'application
st.title("🧬 Détection Précoce du Cancer via le Microbiome")
st.markdown("Chargez vos données de séquençage brut (FASTQ ou CSV) pour commencer l'analyse.")

# Téléchargement du fichier CSV ou FASTQ
uploaded_file = st.file_uploader("📁 Upload des données de séquençage", type=["csv", "fastq", "fq"])

@st.cache_resource
def load_model():
    try:
        # Charger le modèle RandomForest (à remplacer par ton modèle choisi)
        return joblib.load("models/RandomForest_model.joblib")  # Assure-toi que le bon modèle est sélectionné
    except FileNotFoundError:
        st.error("❌ Le modèle 'RandomForest_model.joblib' n'a pas été trouvé dans le dossier 'models'.")
        return None

# Charger le modèle
model = load_model()

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        try:
            # Lire le fichier CSV
            df = pd.read_csv(uploaded_file)

            # Afficher un aperçu des données
            st.subheader("📊 Aperçu des données chargées")
            st.dataframe(df.head())

            # Retirer la colonne 'label' si elle est présente
            if 'label' in df.columns:
                df_features = df.drop(columns=['label'])
            else:
                df_features = df

            # Bouton pour lancer la prédiction
            if st.button("🔍 Lancer la prédiction"):
                if model:
                    try:
                        # Prédiction avec le modèle
                        preds = model.predict(df_features)
                        st.subheader("🔬 Résultats de la prédiction")
                        st.write(preds)

                        # Explication du modèle avec SHAP
                        try:
                            explainer = shap.Explainer(model)
                            shap_values = explainer(df_features)

                            st.subheader("🧠 Interprétation du modèle (SHAP)")
                            plt.figure()
                            shap.summary_plot(shap_values, df_features, show=False)
                            st.pyplot(plt)
                        except Exception as e:
                            st.warning(f"SHAP n'a pas pu s'exécuter : {e}")

                    except Exception as e:
                        st.error(f"Erreur lors de la prédiction : {e}")
                else:
                    st.error("❌ Le modèle n'a pas pu être chargé. Veuillez vérifier les fichiers du modèle.")

        except pd.errors.EmptyDataError:
            st.error("❌ Le fichier est vide ou mal formaté. Veuillez vérifier le CSV.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    else:
        st.success(f"Fichier {uploaded_file.name} chargé. Prêt pour le prétraitement FASTQ.")
        st.markdown("➡️ Traitement FASTQ à implémenter...")
