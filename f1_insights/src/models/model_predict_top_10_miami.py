import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report

# === CONFIGURATION ===
CURRENT_YEAR = 2025
CURRENT_RACE_ID = 1259  # Miami
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_driver_race_results.csv")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_csv(DATA_PATH)

# === NETTOYAGE DES LIGNES NON UTILISABLES (notes, pénalités, etc.) ===
df = df[~df.apply(lambda row: row.astype(str).str.contains("Note - ").any(), axis=1)]

# === GARDER LES LIGNES AVEC QUALIFICATION ===
df = df[df["Q1"].notna()]

# === CONVERSION TEMPS EN SECONDES ===
time_cols = ["Practice1Time", "Practice2Time", "Practice3Time", "FastestLap_Time", "Q1", "Q2", "Q3"]
for col in time_cols:
    df[col] = pd.to_timedelta(df[col], errors='coerce').dt.total_seconds()

# === CONVERSION DES COLONNES NUMÉRIQUES ===
num_cols = ["Quali_Position", "PitStopCount", "Race_Position", "Avg speed"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# === ENCODAGE DES ÉCURIES ===
le_car = LabelEncoder()
df["Car_encoded"] = le_car.fit_transform(df["Car"].fillna("Unknown"))

# === LABEL À PRÉDIRE : TOP 10 ===
df["top10"] = df["Race_Position"].apply(lambda x: 1 if not pd.isna(x) and x <= 10 else 0)

# === SÉPARATION TRAIN / PREDICTION ===
df_train = df[df["race_id"] < CURRENT_RACE_ID].copy()

features = [
    "Practice1_Position", "Practice2_Position", "Practice3_Position",
    "Practice1Time", "Practice2Time", "Practice3Time",
    "Quali_Position", "Q1", "Q2", "Q3", "Race_Position",
    "Car_encoded", "FastestLap_Time", "Avg speed", "PitStopCount"
]

X_train = df_train[features].fillna(-1)
y_train = df_train["top10"]

# === GÉNÉRATION DES DONNÉES POUR MIAMI SI ABSENTES ===
if df[df["race_id"] == CURRENT_RACE_ID].empty:
    print("📊 Aucun résultat pour Miami – génération de lignes fictives basées sur l'historique.")

    last_race_df = df[df["race_id"] < CURRENT_RACE_ID]
    last_race_df = last_race_df.sort_values(by=["Driver", "race_id"])

    recent_form = (
        last_race_df.groupby("Driver").tail(5)
        .groupby("Driver").agg({
            "Practice1Time": "mean",
            "Practice1_Position": "mean",
            "Practice2Time": "mean",
            "Practice2_Position": "mean",
            "Practice3Time": "mean",
            "Practice3_Position": "mean",
            "Quali_Position": "mean",
            "Q1": "mean",
            "Q2": "mean",
            "Q3": "mean",
            "FastestLap_Time": "mean",
            "Avg speed": "mean",
            "PitStopCount": "mean",
            "Car_encoded": "first",
            "Race_Position": "mean"
        }).reset_index()
    )
    recent_form["race_id"] = CURRENT_RACE_ID
    recent_form["recent_avg_position"] = recent_form["Race_Position"]

    drivers_latest_info = last_race_df.sort_values("race_id").groupby("Driver").tail(1)[["Driver", "Car"]]
    df_pred = recent_form.merge(drivers_latest_info, on="Driver", how="left")

else:
    df_pred = df[df["race_id"] == CURRENT_RACE_ID].copy()
    df_pred["recent_avg_position"] = (
        df[df["race_id"] < CURRENT_RACE_ID]
        .groupby("Driver")["Race_Position"].apply(lambda x: x.tail(4).mean())
        .reindex(df_pred["Driver"])
        .values
    )

X_pred = df_pred[features].fillna(-1)

# === ENTRAÎNEMENT ===
base_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=5,
    min_samples_leaf=10,
    random_state=42,
    class_weight="balanced"
)
model = CalibratedClassifierCV(base_model, cv=5)
model.fit(X_train, y_train)

# === PRÉDICTION ===
df_pred["top10_pred"] = model.predict(X_pred)
df_pred["top10_proba"] = model.predict_proba(X_pred)[:, 1]
df_pred = df_pred.sort_values(by="top10_proba", ascending=False)

top10_prediction = df_pred[["Driver", "Car", "Quali_Position", "recent_avg_position", "top10_proba"]].head(10)

print("\n🏁 Prédiction Top 10 pour Miami 2025 :")
print(top10_prediction.to_string(index=False))
