from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# === Chargement des données ===
BASE_DIR = Path(__file__).resolve().parent.parent
data_2024_path = BASE_DIR / "data" / "raw" / "pilot_f1_ranking_2024_cleaned.xlsx"
data_2025_path = BASE_DIR / "data" / "raw" / "pilot_f1_ranking_2025_cleaned.xlsx"

df_2024 = pd.read_excel(data_2024_path)
df_2025 = pd.read_excel(data_2025_path)

# === Prétraitement ===
gp_2024 = ['Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China', 'United States',
           'Italy', 'Monaco', 'Canada', 'Spain', 'Austria', 'United Kingdom', 'Hungary',
           'Belgium', 'Netherlands', 'Italy_2', 'Azerbaijan', 'Singapore', 'United States_2',
           'Mexico', 'Brazil', 'United States_3', 'Qatar', 'United Arab Emirates']
gp_2025 = ['Australia', 'Japan', 'China', 'Bahrain']

# Remplir les NaN avec 0
df_2024[gp_2024] = df_2024[gp_2024].fillna(0)
df_2025[gp_2025] = df_2025[gp_2025].fillna(0)

# Ajouter colonne année
df_2024["Année"] = 2024
df_2025["Année"] = 2025

# Renommer les colonnes des GP avec préfixe d'année
df_2024 = df_2024.rename(columns={col: f"2024_{col}" if col in gp_2024 else col for col in df_2024.columns})
df_2025 = df_2025.rename(columns={col: f"2025_{col}" if col in gp_2025 else col for col in df_2025.columns})

# Fusion verticale
df_all = pd.concat([df_2024, df_2025], ignore_index=True)

# Colonnes des Grand Prix
gp_cols = [col for col in df_all.columns if col.startswith(('2024_', '2025_'))]

# Renommer la colonne "Points" existante si elle existe déjà (ex: points cumulés)
if "Points" in df_all.columns:
    df_all = df_all.rename(columns={"Points": "Points_total"})

# Passage en format long
df_long = df_all.melt(id_vars=["Pilote", "Équipe", "Country", "Année"],
                      value_vars=gp_cols,
                      var_name="Grand Prix", value_name="Points")

# Extraction de l'année et nom de GP
df_long["GP"] = df_long["Grand Prix"].str.replace(r"2024_|2025_", "", regex=True)
df_long["Annee_GP"] = df_long["Grand Prix"].str.extract(r"(2024|2025)").astype(int)

# Supprimer les combinaisons Pilote-Équipe-Année sans aucun point
points_par_combinaison = (
    df_long.groupby(["Pilote", "Équipe", "Année"])["Points"]
    .sum()
    .reset_index()
)
combinaisons_valides = points_par_combinaison[points_par_combinaison["Points"] > 0]
df_long = df_long.merge(combinaisons_valides[["Pilote", "Équipe", "Année"]],
                        on=["Pilote", "Équipe", "Année"], how="inner")

# Format : Pilote (Équipe - Année)
df_long["Pilote_Equipe_Annee"] = df_long.apply(
    lambda row: f"{row['Pilote']} ({row['Équipe']} - {row['Année']})", axis=1
)

# Filtrer les 7 pilotes d'intérêt
pilotes_cibles = ['L. Hamilton']
df_filtered = df_long[df_long["Pilote"].isin(pilotes_cibles)].copy()

# Ordonner les Grand Prix
gp_order = [f"2024_{gp}" for gp in gp_2024] + [f"2025_{gp}" for gp in gp_2025]
df_filtered = df_filtered[df_filtered["Grand Prix"].isin(gp_order)]
df_filtered["Grand Prix"] = pd.Categorical(df_filtered["Grand Prix"], categories=gp_order, ordered=True)

# === Visualisation avec Matplotlib ===
plt.figure(figsize=(16, 9))
pilotes_uniques = df_filtered["Pilote_Equipe_Annee"].unique()

for pilote in pilotes_uniques:
    data = df_filtered[df_filtered["Pilote_Equipe_Annee"] == pilote]
    plt.plot(data["Grand Prix"], data["Points"], label=pilote, marker='o', linewidth=2)

plt.title("Évolution des points par Grand Prix - 2024 à Bahrain 2025", fontsize=18)
plt.xlabel("Grand Prix", fontsize=14)
plt.ylabel("Points marqués", fontsize=14)
plt.xticks(rotation=45)
plt.legend(title="Pilote (Équipe - Année)", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
