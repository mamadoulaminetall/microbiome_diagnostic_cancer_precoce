import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Charger les données
df = pd.read_csv('data/sample_data.csv')
X = df.drop(columns=['label'])
y = df['label']

# Entraîner un modèle Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Sauvegarder le modèle
joblib.dump(clf, 'models/rf_model.joblib')
print("✅ Modèle entraîné et sauvegardé dans models/")
