import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import warnings

from preprocessing import load_and_clean_data

warnings.filterwarnings('ignore')

print("Ładowanie danych...")
X, y = load_and_clean_data('data/cirrhosis.csv')

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# --- KONFIGURACJA GRID SEARCH DLA RANDOM FOREST ---
rf_pipeline = Pipeline([
    ('classifier', RandomForestClassifier(random_state=42))
])

rf_param_grid = {
    'classifier__n_estimators': [50, 100, 200],
    'classifier__max_depth': [3, 5, None],
    # 'class_weight': ['balanced'] # Opcjonalnie, gdy klasy są bardzo nierówne
}

print("\n--- Rozpoczynam GridSearch dla Random Forest ---")
rf_grid = GridSearchCV(rf_pipeline, rf_param_grid, cv=skf, scoring='f1_macro', n_jobs=-1)
rf_grid.fit(X, y)

print(f"Najlepsze parametry Random Forest: {rf_grid.best_params_}")
print(f"Najlepszy F1-Score (Macro): {rf_grid.best_score_:.4f}")


# --- KONFIGURACJA GRID SEARCH DLA SVM ---
svm_pipeline = Pipeline([
    ('scaler', StandardScaler()), # SVM wymusza skalowanie!
    ('classifier', SVC(random_state=42))
])

svm_param_grid = {
    'classifier__kernel': ['rbf', 'linear'],
    'classifier__C': [0.1, 1.0, 10.0]
}

print("\n--- Rozpoczynam GridSearch dla SVM ---")
svm_grid = GridSearchCV(svm_pipeline, svm_param_grid, cv=skf, scoring='f1_macro', n_jobs=-1)
svm_grid.fit(X, y)

print(f"Najlepsze parametry SVM: {svm_grid.best_params_}")
print(f"Najlepszy F1-Score (Macro): {svm_grid.best_score_:.4f}")
