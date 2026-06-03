import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold

def load_and_clean_data(filepath='data/cirrhosis.csv'):
    """
    Wczytuje dane, stosuje hybrydowe podejście do braków danych 
    i koduje zmienne kategoryczne.
    """
    # 1. Wczytanie danych
    df = pd.read_csv(filepath)
    
    # Usunięcie kolumny ID (nie niesie wartości analitycznej)
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])
        
    # 2. POSTĘPOWANIE Z BRAKUJĄCYMI WARTOŚCIAMI (Podejście Hybrydowe)
    # Usuwamy wiersze (pacjentów), którzy mają >= 9 brakujących cech
    df = df[df.isnull().sum(axis=1) <= 8].copy()
    print(f"Rozmiar zbioru po usunięciu najbardziej 'dziurawych' wierszy: {df.shape}")

    # Rozdzielenie cech (X) i etykiety (y)
    X = df.drop(columns=['Status'])
    y = df['Status']

    # Identyfikacja kolumn numerycznych i kategorycznych
    num_cols = X.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = X.select_dtypes(include=['object']).columns

    # Imputacja pojedynczych braków dla zmiennych numerycznych (Mediana)
    num_imputer = SimpleImputer(strategy='median')
    X[num_cols] = num_imputer.fit_transform(X[num_cols])

    # Imputacja pojedynczych braków dla zmiennych kategorycznych (Moda / najczęstsza)
    cat_imputer = SimpleImputer(strategy='most_frequent')
    X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

    # 3. KODOWANIE ZMIENNYCH KATEGORYCZNYCH (One-Hot Encoding)
    # Zamienia kategorie (np. płeć F/M) na kolumny numeryczne (0 lub 1)
    # drop_first=True zapobiega współliniowości (np. tworzy tylko kolumnę Sex_M, gdzie 0 to F)
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
    
    return X, y

def get_cv_splitter(n_splits=5):
    """
    Zwraca obiekt do 5-krotnej walidacji krzyżowej z zachowaniem proporcji klas (Stratified).
    """
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

def get_preprocessors():
    """
    Zwraca słownik z metodami przetwarzania do nałożenia wewnątrz pętli walidacji krzyżowej.
    """
    return {
        'Wariant_Bazowy': None,  # Brak dodatkowego przetwarzania
        
        'Wariant_1_Standaryzacja': StandardScaler(),
        
        # Używamy PCA z parametrem 0.95, co oznacza "zostaw tyle głównych składowych, 
        # aby zachować 95% wariancji (informacji) z oryginalnych danych"
        'Wariant_2_Standaryzacja_PCA': [StandardScaler(), PCA(n_components=0.95)],
        
        # Standaryzacja + Wybór 10 najlepszych oryginalnych cech
        'Wariant_3_Stand_Selekcja': [StandardScaler(), SelectKBest(score_func=f_classif, k=10)]
    
    }

if __name__ == "__main__":
    # Szybki test działania skryptu
    X, y = load_and_clean_data()
    print("\nKształt cech po czyszczeniu i kodowaniu:", X.shape)
    print("\nPierwsze 3 wiersze przetworzonych cech:")
    print(X.head(3))