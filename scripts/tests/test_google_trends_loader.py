import glob
import os

import pandas as pd

from loaders.google_trends import (
    save_processed_google_trends_all_csv,
    save_processed_google_trends_year_csv,
    save_raw_google_trends_batch_csv,
)


def test_save_raw_batch_creates_canonical_and_snapshot(tmp_path):
    output_dir = os.path.join(str(tmp_path), "dados-brutos")
    index = pd.to_datetime(["2022-03-13"])
    index.name = "date"
    raw_df = pd.DataFrame({"Lula": [80], "isPartial": [False]}, index=index)

    canonical_path = save_raw_google_trends_batch_csv(
        raw_df, output_dir, election_year="2022", batch_id="batch_01"
    )

    assert canonical_path == os.path.join(
        output_dir, "google_trends_2022_batch_01.csv"
    )
    assert os.path.exists(canonical_path)

    snapshots = glob.glob(
        os.path.join(output_dir, "google_trends_2022_batch_01_*.csv")
    )
    assert len(snapshots) == 1

    saved = pd.read_csv(canonical_path)
    assert list(saved.columns) == ["date", "Lula", "isPartial"]
    assert saved.iloc[0]["date"] == "2022-03-13"


def _processed_frame():
    return pd.DataFrame(
        {
            "date": ["2022-03-13"],
            "election_year": ["2022"],
            "term": ["Lula"],
            "interest_raw": [80],
            "interest_scaled": [80.0],
            "geo": ["BR"],
            "timeframe": ["2022-01-01 2022-12-31"],
            "source": ["google_trends"],
            "batch_id": ["batch_01"],
            "anchor_term": ["Lula"],
            "is_anchor": [True],
            "is_partial": [False],
            "collected_at": ["2026-06-18T20:00:00"],
        }
    )


def test_save_processed_year_creates_canonical_and_snapshot(tmp_path):
    output_dir = os.path.join(str(tmp_path), "dados-processados")

    canonical_path = save_processed_google_trends_year_csv(
        _processed_frame(), output_dir, election_year="2022"
    )

    assert canonical_path == os.path.join(
        output_dir, "google_trends_2022_interest_long.csv"
    )
    assert os.path.exists(canonical_path)
    snapshots = glob.glob(
        os.path.join(output_dir, "google_trends_2022_interest_long_*.csv")
    )
    assert len(snapshots) == 1

    saved = pd.read_csv(canonical_path)
    assert saved.iloc[0]["term"] == "Lula"
    assert saved.iloc[0]["interest_raw"] == 80


def test_save_processed_all_creates_consolidated_file(tmp_path):
    output_dir = os.path.join(str(tmp_path), "dados-processados")

    canonical_path = save_processed_google_trends_all_csv(_processed_frame(), output_dir)

    assert canonical_path == os.path.join(
        output_dir, "google_trends_all_elections_interest_long.csv"
    )
    assert os.path.exists(canonical_path)
