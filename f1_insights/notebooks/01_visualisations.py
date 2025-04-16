from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Base directory: le dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Chemins vers les fichiers
data_2024_path = BASE_DIR / "data" / "raw" / "pilot_f1_ranking_2024_cleaned.xlsx"
data_2025_path = BASE_DIR / "data" / "raw" / "pilot_f1_ranking_2025_cleaned.xlsx"

# Chargement des données
df_2024 = pd.read_excel(data_2024_path)
df_2025 = pd.read_excel(data_2025_path)

# Colonnes à remplir avec 0
cols_with_points = ['Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China', 'United States',
                    'Italy', 'Monaco', 'Canada', 'Spain', 'Austria', 'United Kingdom', 'Hungary',
                    'Belgium', 'Netherlands', 'Italy_2', 'Azerbaijan', 'Singapore', 'United States_2',
                    'Mexico', 'Brazil', 'United States_3', 'Qatar', 'United Arab Emirates']
df_2024[cols_with_points] = df_2024[cols_with_points].fillna(0)
df_2025[cols_with_points] = df_2025[cols_with_points].fillna(0)

# Ajouter une colonne "Année" pour chaque dataset
df_2024["Année"] = 2024
df_2025["Année"] = 2025

# Ajouter l’année en préfixe aux colonnes de GP
df_2024 = df_2024.rename(columns=lambda col: col if col in ["Pilote", "Équipe", "Country", "Année"] else f"2024_{col}")
df_2025 = df_2025.rename(columns=lambda col: col if col in ["Pilote", "Équipe", "Country", "Année"] else f"2025_{col}")

# Fusion verticale
df_all = pd.concat([df_2024, df_2025], ignore_index=True)

# Colonnes de GP
course_columns = [col for col in df_all.columns if col.startswith(('2024_', '2025_'))]

# Restructuration en long format
df_long = df_all.melt(id_vars=["Pilote", "Équipe", "Country", "Année"], value_vars=course_columns,
                      var_name="Grand Prix", value_name="Points")

# Récupérer le vrai nom du Grand Prix et l’année
df_long["GP"] = df_long["Grand Prix"].str.replace(r"2024_|2025_", "", regex=True)
df_long["Annee_GP"] = df_long["Grand Prix"].str.extract(r"(2024|2025)").astype(int)
associations_valides = df_long[["Pilote", "Équipe"]].drop_duplicates()
print(associations_valides.loc[associations_valides['Pilote'] == "L. Hamilton"])

# Ajout explicite de l'année de chaque Grand Prix déjà extraite précédemment
df_long["Year"] = df_long["Annee_GP"]

# Étape 1 : Ajouter l’année à associations_valides pour créer des associations valides uniques
associations_valides["key"] = associations_valides["Pilote"] + "_" + associations_valides["Équipe"]
print(associations_valides['key'])

df_long["key"] = df_long["Pilote"] + "_" + df_long["Équipe"]
print(df_long['key'])
# Étape 2 : Filtrer uniquement les lignes où l'association Pilote–Équipe existe vraiment
df_filtered = df_long[df_long["key"].isin(associations_valides["key"])].copy()

# Étape 3 : Filtrer les 7 pilotes d'intérêt
pilotes_cibles = ['L. Hamilton']
df_filtered = df_filtered[df_filtered["Pilote"].isin(pilotes_cibles)]
print(df_filtered)
# Étape 4 : Créer un label unique 'Pilote (Équipe - Année)'
df_filtered["Pilote_Equipe_Annee"] = df_filtered["Pilote"] + " (" + df_filtered["Équipe"] + " - " + df_filtered["Year"].astype(str) + ")"
print(df_filtered)
# Étape 5 : Ordre chronologique des Grand Prix
gp_2024_valides = [f"2024_{gp}" for gp in [
    'Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China', 'United States', 'Italy', 'Monaco',
    'Canada', 'Spain', 'Austria', 'United Kingdom', 'Hungary', 'Belgium', 'Netherlands',
    'Italy_2', 'Azerbaijan', 'Singapore', 'United States_2', 'Mexico', 'Brazil', 'United States_3',
    'Qatar', 'United Arab Emirates'
]]
gp_2025_valides = [f"2025_{gp}" for gp in ['Australia', 'Japan', 'China', 'Bahrain']]
gp_order = list(dict.fromkeys(gp_2024_valides + gp_2025_valides))

# Étape 6 : Appliquer l'ordre des GP
df_filtered = df_filtered[df_filtered["Grand Prix"].isin(gp_order)]
df_filtered["Grand Prix"] = pd.Categorical(df_filtered["Grand Prix"], categories=gp_order, ordered=True)

# Étape 7 : Visualisation avec matplotlib
import matplotlib.pyplot as plt

plt.figure(figsize=(18, 9))
plt.style.use('bmh')

for name, group in df_filtered.groupby("Pilote_Equipe_Annee"):
    plt.plot(group["Grand Prix"], group["Points"], marker='o', linewidth=2, label=name)

plt.title("Points marqués par Grand Prix (2024–2025)", fontsize=18)
plt.xlabel("Grand Prix", fontsize=14)
plt.ylabel("Points marqués", fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend(title="Pilote (Équipe - Année)", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(True)
plt.show()

