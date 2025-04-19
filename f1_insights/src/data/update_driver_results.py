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

SESSIONS = ['practice/1', 'practice/2', 'practice/3', 'qualifying', 'race-result', 'pit-stop-summary', 'fastest-laps']

# === DÉFINITION DES CHEMINS ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "f1_driver_race_results.csv")


def get_current_gp():
    today = datetime.today().date()
    calendar = {
        'saudi-arabia': datetime(2025, 4, 19).date(),
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
    return df


def update_driver_results():
    current_gp = get_current_gp()
    if current_gp is None:
        print("Aucune course à venir trouvée.")
        return

    race_id = GP_ID_MAP[current_gp]
    print(f"🟢 Course en cours : {current_gp} (ID {race_id})")

    session_data = {
        "practice/1": ("Practice1Time", "Time"),
        "practice/2": ("Practice2Time", "Time"),
        "practice/3": ("Practice3Time", "Time"),
        "qualifying": ("QualiPosition", "Pos"),
        "race-result": ("FinalPosition", "Pos"),
        "fastest-laps": ("FastestLapTime", "Time"),
        "pit-stop-summary": ("PitStopCount", "Stops")
    }

    # Charger les données existantes
    if os.path.exists(PROCESSED_PATH):
        df_base = pd.read_csv(PROCESSED_PATH)
    else:
        df_base = pd.DataFrame()

    for session, (target_col, source_col) in session_data.items():
        url = f"https://www.formula1.com/en/results/{CURRENT_YEAR}/races/{race_id}/{current_gp}/{session}"
        print(f"Scraping {session} → {url}")
        df = scrape_table(url)

        if df is None or "Driver" not in df.columns or source_col not in df.columns:
            print(f"Aucune donnée trouvée pour {session}.")
            continue

        df = df[["Driver", source_col]].copy()
        df.columns = ["Driver", target_col]
        df["race_id"] = race_id
        df["race_name"] = current_gp
        df["year"] = CURRENT_YEAR

        for _, row in df.iterrows():
            mask = (
                (df_base["Driver"] == row["Driver"]) &
                (df_base["race_id"] == race_id) &
                (df_base["race_name"] == current_gp) &
                (df_base["year"] == CURRENT_YEAR)
            )

            if mask.any():
                df_base.loc[mask, target_col] = row[target_col]
            else:
                new_row = {
                    "Driver": row["Driver"],
                    "race_id": race_id,
                    "race_name": current_gp,
                    "year": CURRENT_YEAR,
                    target_col: row[target_col]
                }
                df_base = pd.concat([df_base, pd.DataFrame([new_row])], ignore_index=True)

    print("Aperçu des données mises à jour :")
    print(df_base[df_base["race_id"] == race_id].tail())

    df_base.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Données mises à jour dans {PROCESSED_PATH}")


if __name__ == "__main__":
    update_driver_results()
