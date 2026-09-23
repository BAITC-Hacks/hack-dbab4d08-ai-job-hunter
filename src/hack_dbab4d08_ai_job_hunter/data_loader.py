from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "hackathon-dataset-anonymized.csv"


def load_contractors() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    df["categories"] = df["categories"].str.split("|")
    df["event_formats"] = df["event_formats"].str.split("|")
    df["languages"] = df["languages"].str.split("|")

    df["busy_dates"] = df["busy_dates"].apply(
        lambda value: set(value.split("|")) if pd.notna(value) else set()
    )

    return df