import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

from preprocessing import load_and_clean_data, get_cv_splitter, get_preprocessors

warnings.filterwarnings('ignore')


print("Ładowanie i czyszczenie danych...")
X, y = load_and_clean_data('data/cirrhosis.csv')


models = {
    'NaiveBayes': GaussianNB(),
    'DecisionTree': DecisionTreeClassifier(random_state=42)
}

# warianty przetwqrzania i kfold
preprocessors = get_preprocessors()
skf = get_cv_splitter(n_splits=5)

results_list = []

print("\nRozpoczynam eksperymenty (porównywanie wariantów przetwarzania)...")


for model_name, model in models.items():
    for prep_name, prep_steps in preprocessors.items():
        
        # pipeline
        steps = []
        if prep_steps is not None:
            if isinstance(prep_steps, list):
                for i, step in enumerate(prep_steps):
                    steps.append((f'prep_{i}', step))
            else:
                steps.append(('prep', prep_steps))
        
        steps.append(('classifier', model))
        clf = Pipeline(steps)
        
        # listy do zierania wynikow z 5 foldow
        acc_scores, prec_scores, rec_scores, f1_scores = [], [], [], []
        
        # walidacja krzyzowa 5x
        for train_index, test_index in skf.split(X, y):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            clf.fit(X_train, y_train)
            
            y_pred = clf.predict(X_test)
            
            # ewaliuacja
            acc_scores.append(accuracy_score(y_test, y_pred))
            prec_scores.append(precision_score(y_test, y_pred, average='macro', zero_division=0))
            rec_scores.append(recall_score(y_test, y_pred, average='macro', zero_division=0))
            f1_scores.append(f1_score(y_test, y_pred, average='macro', zero_division=0))
            
        # wyniki srednia z 5 foldow
        results_list.append({
            'Model': model_name,
            'Przetwarzanie': prep_name,
            'Accuracy': np.mean(acc_scores),
            'Precision (Macro)': np.mean(prec_scores),
            'Recall (Macro)': np.mean(rec_scores),
            'F1-Score (Macro)': np.mean(f1_scores)
        })

results_df = pd.DataFrame(results_list).round(4)

print("\n--- WYNIKI EKSPERYMENTÓW ---")
print(results_df.to_string(index=False))

results_df.to_csv('wyniki_porownanie_metod.csv', index=False)
print("\nWyniki zostały zapisane do pliku 'wyniki_porownanie_metod.csv'.")