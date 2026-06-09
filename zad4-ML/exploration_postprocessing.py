import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

from preprocessing import load_and_clean_data

warnings.filterwarnings('ignore')
os.makedirs('charts', exist_ok=True)
sns.set_theme(style="whitegrid")

file_path = 'data/cirrhosis.csv'
try:
    df_before = pd.read_csv(file_path)
    if 'ID' in df_before.columns:
        df_before = df_before.drop(columns=['ID'])
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku {file_path}. ")
    exit()


print("load_and_clean_data z preprocessing.py\n")
X_after, y_after = load_and_clean_data(file_path)

# X i y w jedna tab
df_after = pd.concat([X_after, y_after], axis=1)


print("\n" + "="*50)
print("--- PORÓWNANIE ZBIORÓW: PRZED VS PO PREPROCESSINGU ---")
print("="*50)

print(f"Liczba wierszy (pacjentów): Przed = {len(df_before)}  |  Po = {len(df_after)}")
print(f"Liczba kolumn (cechy+cel):  Przed = {df_before.shape[1]}   |  Po = {df_after.shape[1]} (wzrost przez One-Hot Encoding)")
print(f"Łączna liczba pustych komórek przed: {df_before.isnull().sum().sum()}")
print(f"Łączna liczba pustych komórek po:    {df_after.isnull().sum().sum()}")



missing_comparison = pd.DataFrame({
    'Przed preprocessingiem': df_before.isnull().sum(),
    # Po preprocessingu wiemy, że nie ma już żadnych braków
    'Po preprocessingu': pd.Series(0, index=df_before.columns) 
})

missing_melted = missing_comparison.reset_index().melt(
    id_vars='index', var_name='Stan', value_name='Liczba braków'
)
missing_melted.rename(columns={'index': 'Atrybut'}, inplace=True)

plt.figure(figsize=(12, 10))
ax = sns.barplot(
    data=missing_melted, 
    x='Liczba braków', 
    y='Atrybut', 
    hue='Stan', 
    palette=['salmon', 'mediumseagreen']
)
plt.title('Porównanie braków danych u pacjentów (Przed vs Po)', fontsize=16)
plt.xlabel('Liczba brakujących wartości', fontsize=12)
plt.ylabel('Atrybut', fontsize=12)


plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.savefig('charts/07_braki_danych_przed_vs_po.png', dpi=300, bbox_inches='tight')
plt.close()


continuous_cols = ['Bilirubin', 'Cholesterol', 'Albumin', 'Copper', 'Alk_Phos', 'SGOT', 'Tryglicerides', 'Platelets', 'Prothrombin']

cols_with_na = [col for col in continuous_cols if df_before[col].isnull().sum() > 0]

if cols_with_na:
    fig, axes = plt.subplots(nrows=len(cols_with_na), ncols=2, figsize=(15, 4 * len(cols_with_na)))
    fig.suptitle('Wpływ imputacji medianą na rozkłady (Lewa: Przed NA, Prawa: Po imputacji)', fontsize=16)

    for i, col in enumerate(cols_with_na):
        sns.histplot(df_before[col].dropna(), kde=True, ax=axes[i, 0], color='lightcoral', bins=30)
        axes[i, 0].set_title(f'{col} (PRZED - ignorowanie braków)')
        axes[i, 0].set_ylabel('Częstość')
        
        sns.histplot(df_after[col], kde=True, ax=axes[i, 1], color='teal', bins=30)
        axes[i, 1].set_title(f'{col} (PO - z imputacją)')
        axes[i, 1].set_ylabel('Częstość')

    plt.tight_layout(rect=[0, 0.01, 1, 0.98])
    plt.savefig('charts/08_rozkłady_imputacja_porownanie.png', dpi=300, bbox_inches='tight')
plt.close()


plt.figure(figsize=(20, 16))
corr_matrix_after = df_after.select_dtypes(include=['float64', 'int64', 'uint8', 'bool']).corr()


sns.heatmap(
    corr_matrix_after, 
    cmap='coolwarm', 
    vmin=-1, 
    vmax=1, 
    fmt=".2f", 
    annot=True, 
    annot_kws={"size": 9}
)
plt.title('Macierz korelacji PO preprocessingu', fontsize=18)
plt.savefig('charts/09_macierz_korelacji_po_prep.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nZaktualizowano wykresy. Gotowe do sprawdzenia w folderze 'charts/'.")