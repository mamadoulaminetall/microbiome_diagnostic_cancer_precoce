from sklearn.model_selection import LeaveOneOut
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Exemple de données (remplace avec tes données réelles)
# X_train, y_train = load_data()  # Charge tes données ici
# Pour un exemple, utilisons un jeu de données intégré comme iris
data = load_iris()
X_train = data.data
y_train = data.target

# Initialiser Leave-One-Out (LOO)
cv = LeaveOneOut()

# Initialiser le modèle RandomForest
rf = RandomForestClassifier()

# Définir les paramètres pour GridSearch
param_grid = {
    'n_estimators': [100, 200], 
    'max_depth': [5, 10]
}

# GridSearch avec validation Leave-One-Out
grid_rf = GridSearchCV(estimator=rf, param_grid=param_grid, cv=cv)
grid_rf.fit(X_train, y_train)

# Afficher les meilleurs paramètres
print("Meilleurs paramètres : ", grid_rf.best_params_)

# Évaluer les résultats
y_pred = grid_rf.predict(X_train)
print("Classification Report:\n", classification_report(y_train, y_pred))

# Afficher les résultats de la recherche
print("Résultats de la validation croisée:")
print("Meilleur score: ", grid_rf.best_score_)
print("Meilleurs paramètres: ", grid_rf.best_params_)
