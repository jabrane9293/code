import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
from io import StringIO
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
CURRENT_YEAR = 2025
GP_LIST = [
    'australia', 'china', 'japan', 'bahrain', 'saudi-arabia', 'miami', 'emilia-romagna', 'monaco',
    'spain', 'canada', 'austria', 'great-britain', 'belgium', 'hungary', 'netherlands',
    'italy', 'azerbaijan', 'singapore', 'united-states', 'mexico', 'brazil', 'las-vegas',
    'qatar', 'abu-dhabi'
]

START_RACE_ID = 1254  # Australia 2025
GP_ID_MAP = {race: START_RACE_ID + i for i, race in enumerate(GP_LIST)}

SESSIONS = ['practice/1', 'practice/2', 'practice/3', 'qualifying', 'starting-grid',
            'pit-stop-summary', 'fastest-laps', 'race-result']

# === DÉFINITION DES CHEMINS ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_full_results_2024_2025.csv")


def get_current_gp():
    today = datetime.today().date()
    calendar = {
        'saudi-arabia': datetime(2025, 4, 18).date(),
    'miami': datetime(2025, 5, 2).date(),
    'emilia-romagna': datetime(2025, 5, 16).date(),
    'monaco': datetime(2025, 5, 25).date(),
    'spain': datetime(2025, 6, 8).date(),
    'canada': datetime(2025, 6, 15).date(),
    'austria': datetime(2025, 6, 29).date(),
    'great-britain': datetime(2025, 7, 6).date(),
    'hungary': datetime(2025, 7, 20).date(),
    'belgium': datetime(2025, 7, 27).date(),
    'netherlands': datetime(2025, 8, 31).date(),
    'italy': datetime(2025, 9, 7).date(),
    'azerbaijan': datetime(2025, 9, 21).date(),
    'singapore': datetime(2025, 10, 5).date(),
    'united-states': datetime(2025, 10, 19).date(),
    'mexico': datetime(2025, 10, 26).date(),
    'brazil': datetime(2025, 11, 9).date(),
    'las-vegas': datetime(2025, 11, 22).date(),
    'qatar': datetime(2025, 11, 30).date(),
    'abu-dhabi': datetime(2025, 12, 5).date(),
    }
    for gp, date in calendar.items():
        if today <= date:
            return gp
    return None


def scrape_table(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    if table is None:
        return None
    df = pd.read_html(StringIO(str(table)))[0]
    df.columns = [col.strip().capitalize().replace("Pts", "PTS")
                  .replace("Time/retired", "Time/Retired")
                  .replace("Avg speed (km/h)", "Avg speed") for col in df.columns]
    return df


def update_gp_data():
    current_gp = get_current_gp()
    if current_gp is None:
        print("Aucune course à venir trouvée.")
        return

    race_id = GP_ID_MAP[current_gp]
    print(f"Course en cours : {current_gp} (ID {race_id})")

    all_dfs = []
    os.makedirs(RAW_DIR, exist_ok=True)

    for session in SESSIONS:
        url = f"https://www.formula1.com/en/results/{CURRENT_YEAR}/races/{race_id}/{current_gp}/{session}"
        print(f"Scraping {session} → {url}")
        df = scrape_table(url)
        if df is not None:
            df['Session'] = session
            df['Grand_Prix'] = current_gp
            df['Year'] = CURRENT_YEAR
            df['Race_ID'] = race_id

            filename = f"{CURRENT_YEAR}_{race_id}_{current_gp}_{session.replace('/', '-')}.csv"
            df.to_csv(os.path.join(RAW_DIR, filename), index=False)
            all_dfs.append(df)
        else:
            print(f"Aucune table trouvée pour {session}.")

    if not all_dfs:
        print("⚠️ Aucune donnée collectée.")
        return

    new_data = pd.concat(all_dfs, ignore_index=True)

    # Harmonisation des colonnes
    new_data = new_data.rename(columns={
        'Session': 'result_type',
        'Grand_Prix': 'race_name',
        'Year': 'year',
        'Race_ID': 'race_id'
    })

    for col in ['table_index', 'Q1', 'Q2', 'Q3', 'Stops', 'Lap', 'Time of day', 'Total',
                'Avg speed', 'Time/retired', 'Pts']:
        if col not in new_data.columns:
            new_data[col] = None

    columns_order = [
        "Pos", "No", "Driver", "Car", "Time", "Gap", "Laps",
        "year", "race_id", "race_name", "result_type", "table_index",
        "Q1", "Q2", "Q3", "Stops", "Lap", "Time of day", "Total",
        "Avg speed", "Time/retired", "Pts"
    ]
    new_data = new_data[[col for col in columns_order if col in new_data.columns]]

    if os.path.exists(PROCESSED_PATH):
        existing_data = pd.read_csv(PROCESSED_PATH)

        # Supprimer de new_data les lignes déjà présentes dans existing_data
        merge_keys = ['race_id', 'result_type', 'Driver']
        merged = new_data.merge(existing_data[merge_keys], on=merge_keys, how='left', indicator=True)
        new_data = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])

        if new_data.empty:
            print("🟡 Aucune nouvelle donnée à ajouter (tout est déjà dans le dataset).")
            return

        full_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        full_data = new_data

    full_data.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Données mises à jour dans {PROCESSED_PATH}")


if __name__ == "__main__":
    update_gp_data()
