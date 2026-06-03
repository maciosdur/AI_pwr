import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

# Importujemy funkcje z Twojego pliku preprocessing.py
from preprocessing import load_and_clean_data, get_cv_splitter, get_preprocessors

# Ignorowanie mało istotnych ostrzeżeń (np. o dzieleniu przez zero w metrykach)
warnings.filterwarnings('ignore')

# 1. Załadowanie przygotowanych danych
print("Ładowanie i czyszczenie danych...")
# Zakładamy, że plik 'cirrhosis.csv' znajduje się w folderze 'data/'
X, y = load_and_clean_data('data/cirrhosis.csv')

# 2. Definicja modeli do przetestowania (Krok 3 zadania)
models = {
    'NaiveBayes': GaussianNB(),
    'DecisionTree': DecisionTreeClassifier(random_state=42)
}

# 3. Pobranie wariantów przetwarzania i obiektu walidacji krzyżowej
preprocessors = get_preprocessors()
skf = get_cv_splitter(n_splits=5)

results_list = []

print("\nRozpoczynam eksperymenty (porównywanie wariantów przetwarzania)...")

# 4. Główna pętla eksperymentu
for model_name, model in models.items():
    for prep_name, prep_steps in preprocessors.items():
        
        # Budowanie odpowiednich kroków do rurociągu (Pipeline)
        steps = []
        if prep_steps is not None:
            if isinstance(prep_steps, list):
                # Jeśli to lista (np. Standaryzacja + PCA z pliku preprocessing.py)
                for i, step in enumerate(prep_steps):
                    steps.append((f'prep_{i}', step))
            else:
                # Jeśli to pojedynczy krok (np. sama Standaryzacja)
                steps.append(('prep', prep_steps))
        
        # Dodanie klasyfikatora na sam koniec rurociągu
        steps.append(('classifier', model))
        clf = Pipeline(steps)
        
        # Listy na wyniki z 5 foldów walidacji krzyżowej
        acc_scores, prec_scores, rec_scores, f1_scores = [], [], [], []
        
        # Pętla walidacji krzyżowej (5 iteracji)
        for train_index, test_index in skf.split(X, y):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            # Trening (Pipeline dba o to, żeby preprocesory uczyły się TYLKO na X_train)
            clf.fit(X_train, y_train)
            
            # Predykcja (Pipeline automatycznie transformuje X_test przed predykcją)
            y_pred = clf.predict(X_test)
            
            # Ewaluacja (z parametrem macro dla niezbalansowanych klas C, CL, D)
            acc_scores.append(accuracy_score(y_test, y_pred))
            prec_scores.append(precision_score(y_test, y_pred, average='macro', zero_division=0))
            rec_scores.append(recall_score(y_test, y_pred, average='macro', zero_division=0))
            f1_scores.append(f1_score(y_test, y_pred, average='macro', zero_division=0))
            
        # Agregacja wyników (średnia z 5 foldów) dla danej kombinacji model + przetwarzanie
        results_list.append({
            'Model': model_name,
            'Przetwarzanie': prep_name,
            'Accuracy': np.mean(acc_scores),
            'Precision (Macro)': np.mean(prec_scores),
            'Recall (Macro)': np.mean(rec_scores),
            'F1-Score (Macro)': np.mean(f1_scores)
        })

# 5. Zapis i wyświetlenie podsumowania
results_df = pd.DataFrame(results_list).round(4)

print("\n--- WYNIKI EKSPERYMENTÓW ---")
print(results_df.to_string(index=False))

results_df.to_csv('wyniki_porownanie_metod.csv', index=False)
print("\nWyniki zostały zapisane do pliku 'wyniki_porownanie_metod.csv'.")