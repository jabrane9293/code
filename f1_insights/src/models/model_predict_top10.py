import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# === CONFIGURATION ===
CURRENT_YEAR = 2025
CURRENT_RACE_ID = 1259  # Miami
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_driver_race_results.csv")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_csv(DATA_PATH)

# Supprimer toutes les lignes contenant "Note - " dans n'importe quelle cellule
mask_note = df.astype(str).apply(lambda row: row.str.contains("Note", na=False)).any(axis=1)
df = df[~mask_note]
print(f"✅ {mask_note.sum()} lignes contenant 'Note' supprimées du dataset.")


# === NETTOYAGE ===
df = df[df["Q1"].notna()]

# Nettoyer les colonnes de temps
time_cols = ["Practice1Time", "Practice2Time", "Practice3Time", "FastestLap_Time", "Q1", "Q2", "Q3"]
for col in time_cols:
    df[col] = pd.to_timedelta(df[col], errors='coerce').dt.total_seconds()

# Conversion de colonnes numériques
num_cols = ["Practice1_Position", "Practice2_Position", "Practice3_Position", "Quali_Position", "PitStopCount", "Race_Position", "Avg speed"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Encodage de l'écurie
le_car = LabelEncoder()
df["Car_encoded"] = le_car.fit_transform(df["Car"].fillna("Unknown"))

# === LABEL À PRÉDIRE ===
df["top10"] = df["Race_Position"].apply(lambda x: 1 if not pd.isna(x) and x <= 10 else 0)

# === ENTRAÎNEMENT ===
df_train = df[df["race_id"] < CURRENT_RACE_ID].copy()
print(df_train.shape)
features = [
    "Practice1_Position", "Practice2_Position", "Practice3_Position",
    "Practice1Time", "Practice2Time", "Practice3Time",
    "Quali_Position", "Q1", "Q2", "Q3", "Race_Position",
    "Car_encoded", "FastestLap_Time", "Avg speed", "PitStopCount"
]

X_train = df_train[features].fillna(-1)
y_train = df_train["top10"]

model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

# === GÉNÉRATION D’UNE ENTRÉE FAUSSE POUR CHAQUE PILOTE À PRÉDIRE ===
# Moyenne des dernières courses de chaque pilote
df_recent = df_train.sort_values("race_id", ascending=False).groupby("Driver").head(3)
df_pred = df_recent.groupby("Driver")[features].mean().reset_index()

# Car_encoded doit être recalculé
df_pred["Car_encoded"] = df_recent.groupby("Driver")["Car_encoded"].agg(lambda x: x.mode().iloc[0]).values

X_pred = df_pred[features].fillna(-1)
df_pred["top10_proba"] = model.predict_proba(X_pred)[:, 1]

# Trier par probabilité décroissante
df_pred = df_pred.sort_values(by="top10_proba", ascending=False)

# Affichage
print("🏁 Prédiction Top 10 pour Miami 2025 (basé sur historique uniquement) :")
print(df_pred[["Driver", "top10_proba"]].head(10).to_string(index=False))


