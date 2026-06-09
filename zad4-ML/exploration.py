import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


os.makedirs('charts', exist_ok=True)


sns.set_theme(style="whitegrid")


file_path = 'data/cirrhosis.csv'
try:
    df = pd.read_csv(file_path)
    print(f"Pomyślnie wczytano dane. Kształt zbioru: {df.shape}\n")
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku {file_path}.")
    exit()

# statystyki w konsoli
print("--- PODSTAWOWE INFORMACJE O ZBIORZE ---")
df.info()
print("\n--- BRAKUJĄCE WARTOŚCI ---")
missing_values = df.isnull().sum()
print(missing_values[missing_values > 0].sort_values(ascending=False))

print("\n--- STATYSTYKI OPISOWE (ZMIENNE LICZBOWE) ---")
print(df.describe().round(2))

print("\n--- STATYSTYKI OPISOWE (ZMIENNE KATEGORYCZNE) ---")
print(df.describe(include=['object', 'category']).T)

print("\n--- ANALIZA BRAKÓW DANYCH NA POZIOMIE WIERSZY ---")
missing_per_row = df.isnull().sum(axis=1)

missing_distribution = missing_per_row.value_counts().sort_index()

print("Liczba braków w wierszu | Liczba takich pacjentów (wierszy)")
print("-" * 60)
for missing_count, num_rows in missing_distribution.items():
    print(f"       {missing_count:2d}               |           {num_rows}")


plt.figure(figsize=(10, 6))
ax = sns.barplot(x=missing_distribution.index, y=missing_distribution.values, color='coral')
plt.title('Rozkład liczby brakujących wartości na pacjenta')
plt.xlabel('Liczba brakujących cech (NA) u jednego pacjenta')
plt.ylabel('Liczba pacjentów')


for p in ax.patches:
    ax.annotate(format(p.get_height(), '.0f'), 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', 
                xytext = (0, 9), 
                textcoords = 'offset points')

plt.savefig('charts/06_braki_wierszami.png', dpi=300, bbox_inches='tight')
plt.close()



# Rozkład zmiennej docelowej status
plt.figure(figsize=(8, 6))
sns.countplot(data=df, x='Status', hue='Status', palette='Set2', legend=False)
plt.title('Rozkład klas zmiennej docelowej (Status)')
plt.xlabel('Status (C - ocenzurowana, CL - przeszczep, D - śmierć)')
plt.ylabel('Liczba pacjentów')
plt.savefig('charts/01_rozkład_zmiennej_docelowej.png', dpi=300, bbox_inches='tight')
plt.close()

# rozkład zmiennych kategorycznych
categorical_cols = ['Drug', 'Sex', 'Ascites', 'Hepatomegaly', 'Spiders', 'Edema', 'Stage']
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
fig.suptitle('Rozkład zmiennych kategorycznych', fontsize=16)

axes = axes.flatten()
for i, col in enumerate(categorical_cols):
    if col in df.columns:
        sns.countplot(data=df, x=col, hue=col, ax=axes[i], palette='muted', legend=False)
        axes[i].set_title(col)
        axes[i].set_ylabel('')

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('charts/02_rozkład_zmiennych_kategorycznych.png', dpi=300, bbox_inches='tight')
plt.close()

# histogramy
continuous_cols = ['N_Days', 'Age', 'Bilirubin', 'Cholesterol', 'Albumin', 'Copper', 
                   'Alk_Phos', 'SGOT', 'Tryglicerides', 'Platelets', 'Prothrombin']

fig, axes = plt.subplots(nrows=6, ncols=2, figsize=(15, 24))
fig.suptitle('Rozkład zmiennych ciągłych', fontsize=16)

axes = axes.flatten()
for i, col in enumerate(continuous_cols):
    if col in df.columns:
        sns.histplot(df[col], kde=True, ax=axes[i], color='teal', bins=30)
        axes[i].set_title(col)
        axes[i].set_ylabel('Częstość')
        
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('charts/03_rozkład_zmiennych_ciaglych.png', dpi=300, bbox_inches='tight')
plt.close()

# boxploty
fig, axes = plt.subplots(nrows=6, ncols=2, figsize=(15, 24))
fig.suptitle('Zmienne ciągłe w podziale na Status', fontsize=16)

axes = axes.flatten()
for i, col in enumerate(continuous_cols):
    if col in df.columns:
        sns.boxplot(data=df, x='Status', y=col, hue='Status', ax=axes[i], palette='Set2', legend=False)
        axes[i].set_title(f'{col} vs Status')
        
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('charts/04_zmienne_ciagle_vs_status.png', dpi=300, bbox_inches='tight')
plt.close()

# macierz korelacji
plt.figure(figsize=(12, 10))

numeric_df = df.select_dtypes(include=['float64', 'int64'])

if not numeric_df.empty:
    corr_matrix = numeric_df.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
    plt.title('Macierz korelacji cech numerycznych', fontsize=16)
    plt.savefig('charts/05_macierz_korelacji.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nEksploracja zakończona. Wykresy zostały zapisane w folderze 'charts/'.")