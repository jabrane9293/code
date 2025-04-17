import pandas as pd
import os

# Détection du chemin racine du projet (en partant du dossier notebooks/)
NOTEBOOKS_DIR = os.path.dirname(os.path.abspath(__file__))  # chemin vers notebooks/
PROJECT_ROOT = os.path.abspath(os.path.join(NOTEBOOKS_DIR, ".."))  # <- f1_insights/

# Répertoires de destination
raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

# URL de base
base_url = "https://www.formula1.com/en/results/"

# Configuration des courses
races_config = {
    "2024": {
        "start_id": 1229,
        "races": [
            'bahrain', 'saudi-arabia', 'australia', 'japan', 'china', 'miami',
            'emilia-romagna', 'monaco', 'canada', 'spain', 'austria', 'great-britain',
            'hungary', 'belgium', 'netherlands', 'italy', 'azerbaijan', 'singapore',
            'united-states', 'mexico', 'brazil', 'las-vegas', 'qatar', 'abu-dhabi'
        ]
    },
    "2025": {
        "start_id": 1254,
        "races": [
            'australia', 'china', 'japan', 'bahrain'  # ✅ Ordre corrigé
        ]
    }
}

# Types de résultats disponibles
result_types = [
    'practice/1', 'practice/2', 'practice/3',
    'qualifying', 'starting-grid', 'pit-stop-summary',
    'fastest-laps', 'race-result'
]

# Liste pour concaténer toutes les données
all_dataframes = []

# Boucle principale
for year, config in races_config.items():
    race_id = config["start_id"]
    for race_name in config["races"]:
        for result_type in result_types:
            url = f"{base_url}{year}/races/{race_id}/{race_name}/{result_type}"
            try:
                tables = pd.read_html(url)
                for i, table in enumerate(tables):
                    # Sauvegarde brute
                    filename = f"{year}_{race_id}_{race_name}_{result_type.replace('/', '-')}_table{i+1}.csv"
                    filepath = os.path.join(raw_dir, filename)
                    table.to_csv(filepath, index=False)
                    print(f"✅ Sauvegardé : {filepath}")

                    # Ajout des colonnes contextuelles
                    table['year'] = year
                    table['race_id'] = race_id
                    table['race_name'] = race_name
                    table['result_type'] = result_type
                    table['table_index'] = i + 1  # au cas où plusieurs tableaux

                    all_dataframes.append(table)

            except Exception as e:
                print(f"❌ Échec pour : {url} ({e})")
        race_id += 1

# Concaténation globale
if all_dataframes:
    final_df = pd.concat(all_dataframes, ignore_index=True)
    final_path = os.path.join(processed_dir, "f1_full_results_2024_2025.csv")
    final_df.to_csv(final_path, index=False)
    print(f"\n✅ Tous les tableaux combinés dans : {final_path}")
else:
    print("\n⚠️ Aucun tableau n’a pu être récupéré.")
