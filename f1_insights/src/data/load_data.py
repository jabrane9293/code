import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import urllib3
from datetime import date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
today = date(2025, 4, 20)

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

races_config = {
    "2020": {
        "start_id": 1045,
        "races": [
            'austria', 'styria', 'hungary', 'great-britain', '70th-anniversary',
            'spain', 'belgium', 'italy', 'tuscany', 'russia', 'eifel', 'portugal',
            'emilia-romagna', 'turkey', 'bahrain', 'sakhir', 'abu-dhabi'
        ]
    },
    "2021": {
        "start_id": 1064,
        "races": [
            'bahrain', 'emilia-romagna', 'portugal', 'spain', 'monaco', 'azerbaijan',
            'france', 'styria', 'austria', 'great-britain', 'hungary', 'belgium',
            'netherlands', 'italy', 'russia', 'turkey', 'united-states', 'mexico',
            'brazil', 'qatar', 'saudi-arabia', 'abu-dhabi'
        ]
    },
    "2022": {
        "start_id": 1124,
        "races": [
            'bahrain', 'saudi-arabia', 'australia', 'emilia-romagna', 'miami', 'spain',
            'monaco', 'azerbaijan', 'canada', 'great-britain', 'austria', 'france',
            'hungary', 'belgium', 'netherlands', 'italy', 'singapore', 'japan',
            'united-states', 'mexico', 'brazil', 'abu-dhabi'
        ]
    },
    "2023": {
        "start_id": 1141,
        "races": [
            'bahrain', 'saudi-arabia', 'australia', 'azerbaijan', 'miami', 'monaco',
            'spain', 'canada', 'austria', 'great-britain', 'hungary', 'belgium',
            'netherlands', 'italy', 'singapore', 'japan', 'qatar', 'united-states',
            'mexico', 'brazil', 'las-vegas', 'abu-dhabi'
        ]
    },
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
        "races": [name for name, gp_date in races_2025_schedule if gp_date <= today]
    }
}

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
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_driver_race_results.csv")


def scrape_table(url):
    try:
        r = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find("table")
        if table:
            df = pd.read_html(StringIO(str(table)))[0]
            return df
    except Exception as e:
        print(f"❌ Erreur lors du scraping de {url} : {e}")
    return None


def main():
    all_race_driver_data = []

    for year, config in races_config.items():
        year = int(year)
        start_id = config["start_id"]
        races = config["races"]

        for i, race in enumerate(races):
            race_id = start_id + i
            race_dfs = []

            for session, info in SESSIONS_CONFIG.items():
                url = f"https://www.formula1.com/en/results/{year}/races/{race_id}/{race}/{session}"
                print(f"🔎 Scraping {year} - {race} ({session}) → {url}")
                df = scrape_table(url)

                if df is None or "Driver" not in df.columns:
                    print("  ➤ Aucune donnée.")
                    continue

                df = df[[col for col in info['columns'] if col in df.columns]]

                df = df.rename(columns=info.get('rename', {}))
                df["race_id"] = race_id
                df["race_name"] = race
                df["year"] = year

                # Supprimer 'Car' s’il a déjà été fusionné
                if 'Car' in df.columns and any('Car' in d.columns for d in race_dfs):
                    df = df.drop(columns=['Car'])

                race_dfs.append(df)

            if race_dfs:
                merged = race_dfs[0]
                for other in race_dfs[1:]:
                    merged = pd.merge(merged, other, on=["Driver", "race_id", "race_name", "year"], how="outer")
                all_race_driver_data.append(merged)

    if all_race_driver_data:
        full_df = pd.concat(all_race_driver_data, ignore_index=True)
        full_df.drop_duplicates(subset=["Driver", "race_id", "race_name", "year"], inplace=True)

        # Réordonner les colonnes
        column_order = [
            "year", "race_id", "race_name", "Driver", "Car",
            "Practice1_Position", "Practice1Time",
            "Practice2_Position", "Practice2Time",
            "Practice3_Position", "Practice3Time",
            "Quali_Position", "Q1", "Q2", "Q3",
            "Race_Position", "Laps", "Pts", "Avg speed",
            "PitStopCount", "FastestLap_Position", "FastestLap_Time"
        ]
        full_df = full_df[[col for col in column_order if col in full_df.columns]]

        full_df.to_csv(OUTPUT_PATH, index=False)
        print(f"\n✅ Données enregistrées dans {OUTPUT_PATH}")
    else:
        print("\n❌ Aucune donnée récupérée.")


if __name__ == "__main__":
    main()
