import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, confusion_matrix
import warnings

from preprocessing import load_and_clean_data

warnings.filterwarnings('ignore')

os.makedirs('charts', exist_ok=True)

print("Ładowanie danych...")
X, y = load_and_clean_data('data/cirrhosis.csv')

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

experiments = {
    'NB_Wygładzanie_Domyślne': (GaussianNB(var_smoothing=1e-9), [StandardScaler(), PCA(n_components=0.95)]),
    'NB_Wygładzanie_Średnie': (GaussianNB(var_smoothing=1e-3), [StandardScaler(), PCA(n_components=0.95)]),
    'NB_Wygładzanie_Silne': (GaussianNB(var_smoothing=1e-1), [StandardScaler(), PCA(n_components=0.95)]),

    'DT_Gini_BezLimitow': (DecisionTreeClassifier(criterion='gini', max_depth=None, random_state=42), []),
    'DT_Entropia_BezLimitow': (DecisionTreeClassifier(criterion='entropy', max_depth=None, random_state=42), []),
    'DT_Gini_Przyciete_Glebokosc3': (DecisionTreeClassifier(criterion='gini', max_depth=3, random_state=42), []),

    'Bonus_RandomForest_Opt': (RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42), []),
    'Bonus_SVM_Linear_Opt': (SVC(kernel='linear', C=1.0, random_state=42), [StandardScaler()])
}

results = []
confusion_matrices = {} # Słownik do przechowywania macierzy

print("\nRozpoczynam strojenie hiperparametrów, badanie przeuczenia i generowanie macierzy...\n")

for name, (model, prep_steps) in experiments.items():
    steps = [(f'prep_{i}', step) for i, step in enumerate(prep_steps)]
    steps.append(('classifier', model))
    clf = Pipeline(steps)
    
    train_f1_scores, test_f1_scores, test_acc_scores = [], [], []
    test_prec_scores, test_rec_scores = [], []
    
    all_y_test = []
    all_y_pred = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        clf.fit(X_train, y_train)
        
        y_train_pred = clf.predict(X_train)
        train_f1_scores.append(f1_score(y_train, y_train_pred, average='macro', zero_division=0))
        
        y_test_pred = clf.predict(X_test)
        
        test_acc_scores.append(accuracy_score(y_test, y_test_pred))
        test_prec_scores.append(precision_score(y_test, y_test_pred, average='macro', zero_division=0))
        test_rec_scores.append(recall_score(y_test, y_test_pred, average='macro', zero_division=0))
        test_f1_scores.append(f1_score(y_test, y_test_pred, average='macro', zero_division=0))
        
        all_y_test.extend(y_test)
        all_y_pred.extend(y_test_pred)
        
    # Zapis macierzy do słownika zamiast od razu rysować
    confusion_matrices[name] = confusion_matrix(all_y_test, all_y_pred, labels=['C', 'CL', 'D'])
        
    results.append({
        'Eksperyment': name,
        'Train F1': np.mean(train_f1_scores),
        'Test F1': np.mean(test_f1_scores),
        'Test Acc': np.mean(test_acc_scores),
        'Test Precision': np.mean(test_prec_scores),
        'Test Recall': np.mean(test_rec_scores),
        'Różnica (Train-Test F1)': np.mean(train_f1_scores) - np.mean(test_f1_scores)
    })

# --- RYSOWANIE ZBIORCZEGO WYKRESU MACIERZY POMYŁEK ---
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(20, 10))
fig.suptitle('Zbiorcze Zestawienie Macierzy Pomyłek dla Wszystkich Modeli', fontsize=20, y=1.05)
axes = axes.flatten()

for i, (name, cm) in enumerate(confusion_matrices.items()):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['C', 'CL', 'D'], yticklabels=['C', 'CL', 'D'], ax=axes[i])
    axes[i].set_title(name, fontsize=12, pad=10)
    axes[i].set_ylabel('Rzeczywista klasa')
    axes[i].set_xlabel('Przewidziana klasa')

plt.tight_layout()
plt.savefig('charts/10_Zbiorcza_Macierz_Pomylek.png', dpi=300, bbox_inches='tight')
plt.close()

# Zapis wyników do tabeli
results_df = pd.DataFrame(results).round(4)
print(results_df.to_string(index=False))

results_df.to_csv('wyniki_pelna_ewaluacja_hiperparametry.csv', index=False)
print("\nWygenerowano 1 zbiorczy wykres macierzy pomyłek w folderze 'charts/'.")