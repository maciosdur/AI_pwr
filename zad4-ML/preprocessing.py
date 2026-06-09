import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold

def load_and_clean_data(filepath='data/cirrhosis.csv'):

    df = pd.read_csv(filepath)
    
    # usuniecie id
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])
        
    
    # Usuwamy pacjentów którzy mają >= 9 brakujących cech
    df = df[df.isnull().sum(axis=1) <= 8].copy()
    print(f"Rozmiar zbioru po usunięciu najbardziej 'dziurawych' wierszy: {df.shape}")

    # rozdzielenie X i y
    X = df.drop(columns=['Status'])
    y = df['Status']

    # klumny numeryczne i kategoryczne
    num_cols = X.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = X.select_dtypes(include=['object']).columns

    # imputacja mediana
    num_imputer = SimpleImputer(strategy='median')
    X[num_cols] = num_imputer.fit_transform(X[num_cols])

    # imputacaja moda
    cat_imputer = SimpleImputer(strategy='most_frequent')
    X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

    # one hot encoding
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
    
    return X, y

def get_cv_splitter(n_splits=5):
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

def get_preprocessors():

    return {
        'Wariant_Bazowy': None,  
        
        'Wariant_1_Standaryzacja': StandardScaler(),
        

        'Wariant_2_Standaryzacja_PCA': [StandardScaler(), PCA(n_components=0.95)],
        
        'Wariant_3_Stand_Selekcja': [StandardScaler(), SelectKBest(score_func=f_classif, k=10)]
    
    }

if __name__ == "__main__":
    X, y = load_and_clean_data()
    print("\nKształt cech po czyszczeniu i kodowaniu:", X.shape)
    print("\nPierwsze 3 wiersze przetworzonych cech:")
    print(X.head(3))