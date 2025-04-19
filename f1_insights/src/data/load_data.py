import pandas as pd
import os


def preprocess_f1_results():
    # Chemin racine du projet
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "f1_insights"))

    # Chemins vers les données
    input_path = os.path.join(project_root, "data", "processed", "f1_full_results_2024_2025.csv")
    output_path = os.path.join(project_root, "data", "processed", "f1_driver_race_results.csv")

    # Chargement du CSV brut
    df = pd.read_csv(input_path)

    # Standardisation du nom de colonne pilote
    possible_driver_columns = ["Driver", "Full Name", "Driver.1", "Name"]
    df["Driver"] = df[[col for col in df.columns if col in possible_driver_columns]].bfill(axis=1).iloc[:, 0]
    df["Driver"] = df["Driver"].str.strip()

    # Séparation par type de tableau
    key = ["year", "race_id", "race_name", "Driver"]
    race = df[df["result_type"] == "race-result"]
    quali = df[df["result_type"] == "qualifying"]
    grid = df[df["result_type"] == "starting-grid"]
    fastest = df[df["result_type"] == "fastest-laps"]
    pitstops = df[df["result_type"] == "pit-stop-summary"]

    # Ajout essais libres
    practice_times = {}
    for session in ["practice/1", "practice/2", "practice/3"]:
        practice_df = df[df["result_type"] == session]
        if not practice_df.empty:
            session_clean = practice_df[key + ["Time"]].rename(columns={"Time": f"Practice{session[-1]}Time"})
            practice_times[session] = session_clean

    # Nettoyage & sélection des colonnes importantes
    race_clean = race[key + ["Pos", "Car", "Laps", "Time/retired", "Pts"]].rename(columns={
        "Pos": "FinalPosition", "Car": "Team", "Laps": "LapsCompleted", "Time/retired": "Status", "Pts": "Points"
    })

    quali_clean = quali[key + ["Pos", "Q1", "Q2", "Q3"]].rename(columns={"Pos": "QualiPosition"})
    grid_clean = grid[key + ["Pos"]].rename(columns={"Pos": "GridPosition"})
    fastest_clean = fastest[key + ["Time", "Avg speed"]].rename(columns={
        "Time": "FastestLapTime", "Avg speed": "FastestLapSpeed"
    })

    # Pour pit-stop, on garde uniquement le nombre total de stops
    pitstops_clean = (
        pitstops.groupby(key).size().reset_index(name="PitStopCount")
    )

    # Fusion progressive
    merged = race_clean \
        .merge(quali_clean, on=key, how="left") \
        .merge(grid_clean, on=key, how="left") \
        .merge(fastest_clean, on=key, how="left") \
        .merge(pitstops_clean, on=key, how="left")

    # Ajout des séances d’essais
    for session_key, df_practice in practice_times.items():
        merged = merged.merge(df_practice, on=key, how="left")

    # Nettoyage final
    merged["FinalPosition"] = pd.to_numeric(merged["FinalPosition"], errors="coerce")
    merged["QualiPosition"] = pd.to_numeric(merged["QualiPosition"], errors="coerce")
    merged["GridPosition"] = pd.to_numeric(merged["GridPosition"], errors="coerce")
    merged["Points"] = pd.to_numeric(merged["Points"], errors="coerce")
    merged["PitStopCount"] = merged["PitStopCount"].fillna(0).astype(int)

    # Sauvegarde
    merged.to_csv(output_path, index=False)
    print(f"✅ Dataset pilote/course sauvegardé dans : {output_path}")

    return merged
