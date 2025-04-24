import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import urllib3
from datetime import date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
today = date.today()

races_2025_schedule = [
    ('australia', date(2025, 3, 15)),
    ('china', date(2025, 3, 22)),
    ('japan', date(2025, 3, 29)),
    ('bahrain', date(2025, 4, 5)),
    ('saudi-arabia', date(2025, 4, 20)),
    ('miami', date(2025, 5, 4)),
    ('emilia-romagna', date(2025, 5, 18)),
    ('monaco', date(2025, 5, 25)),
    ('canada', date(2025, 6, 8)),
    ('spain', date(2025, 6, 22)),
    ('austria', date(2025, 6, 29)),
    ('great-britain', date(2025, 7, 6)),
    ('hungary', date(2025, 7, 20)),
    ('belgium', date(2025, 7, 27)),
    ('netherlands', date(2025, 8, 31)),
    ('italy', date(2025, 9, 7)),
    ('azerbaijan', date(2025, 9, 21)),
    ('singapore', date(2025, 10, 5)),
    ('united-states', date(2025, 10, 19)),
    ('mexico', date(2025, 10, 26)),
    ('brazil', date(2025, 11, 9)),
    ('las-vegas', date(2025, 11, 22)),
    ('qatar', date(2025, 11, 30)),
    ('abu-dhabi', date(2025, 12, 5)),
]

races_2025 = [(i + 1254, name) for i, (name, d) in enumerate(races_2025_schedule) if d <= today]

SESSIONS_CONFIG = {
    'practice/1': {'columns': ['Pos', 'Driver', 'Car', 'Time'], 'rename': {'Time': 'Practice1Time', 'Pos': 'Practice1_Position'}},
    'practice/2': {'columns': ['Pos', 'Driver', 'Car', 'Time'], 'rename': {'Time': 'Practice2Time', 'Pos': 'Practice2_Position'}},
    'practice/3': {'columns': ['Pos', 'Driver', 'Car', 'Time'], 'rename': {'Time': 'Practice3Time', 'Pos': 'Practice3_Position'}},
    'qualifying': {'columns': ['Pos', 'Driver', 'Car', 'Q1', 'Q2', 'Q3'], 'rename': {'Pos': 'Quali_Position'}},
    'race-result': {'columns': ['Pos', 'Driver', 'Car', 'Laps', 'Pts'], 'rename': {'Pos': 'Race_Position'}},
    'pit-stop-summary': {'columns': ['Driver', 'Stops'], 'rename': {'Stops': 'PitStopCount'}},
    'fastest-laps': {'columns': ['Pos', 'Driver', 'Car', 'Time', 'Avg speed'], 'rename': {'Pos': 'FastestLap_Position', 'Time': 'FastestLap_Time'}}
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_driver_race_results.csv")

COLUMN_ORDER = [
    "year", "race_id", "race_name", "Driver", "Car",
    "Practice1_Position", "Practice1Time",
    "Practice2_Position", "Practice2Time",
    "Practice3_Position", "Practice3Time",
    "Quali_Position", "Q1", "Q2", "Q3",
    "Race_Position", "Laps", "Pts", "Avg speed",
    "PitStopCount", "FastestLap_Position", "FastestLap_Time"
]


def scrape_table(url):
    try:
        r = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find("table")
        if table:
            df = pd.read_html(StringIO(str(table)))[0]
            return df
    except Exception as e:
        print(f"❌ Erreur scraping {url} : {e}")
    return None


def update_results():
    if os.path.exists(DATA_PATH):
        full_df = pd.read_csv(DATA_PATH)
    else:
        full_df = pd.DataFrame(columns=COLUMN_ORDER)

    new_data = []

    for race_id, race_name in races_2025:
        race_dfs = []

        for session, info in SESSIONS_CONFIG.items():
            url = f"https://www.formula1.com/en/results/2025/races/{race_id}/{race_name}/{session}"
            print(f"🔎 Scraping {url}")
            df = scrape_table(url)

            if df is None or "Driver" not in df.columns:
                print("  ➤ Aucune donnée.")
                continue

            df = df[[col for col in info['columns'] if col in df.columns]]
            df = df.rename(columns=info['rename'])
            df["race_id"] = race_id
            df["race_name"] = race_name
            df["year"] = 2025

            if 'Car' in df.columns and any('Car' in d.columns for d in race_dfs):
                df = df.drop(columns=['Car'])

            race_dfs.append(df)

        if race_dfs:
            merged = race_dfs[0]
            for other in race_dfs[1:]:
                merged = pd.merge(merged, other, on=["Driver", "race_id", "race_name", "year"], how="outer")
            new_data.append(merged)

    if new_data:
        update_df = pd.concat(new_data, ignore_index=True)
        combined_df = pd.concat([full_df, update_df], ignore_index=True)
        combined_df.drop_duplicates(subset=["Driver", "race_id", "race_name", "year"], keep="last", inplace=True)

        combined_df = combined_df[[col for col in COLUMN_ORDER if col in combined_df.columns]]
        combined_df.to_csv(DATA_PATH, index=False)
        print(f"\n✅ Données mises à jour dans {DATA_PATH}")
    else:
        print("\n❌ Aucune nouvelle donnée récupérée.")


if __name__ == "__main__":
    update_results()
