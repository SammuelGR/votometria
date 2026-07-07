"""
Electoral-polls (enquetes) ETL pipeline.

Reads the parsed Wikipedia poll CSVs from ``pesquisa-<ano>/`` and publishes them
across the medallion layers:

    extractors  -> bronze (raw rows + lineage)
    transformers-> prata  (normalized long table)
    loaders     -> ouro   (analytical candidate/time tables)

The pipeline is idempotent (full-refresh tabs, deterministic ids) and never
mutates the raw source files.
"""

from datetime import datetime

import pandas as pd

from core.sheets import get_layer_spreadsheets
from extractors.enquetes import extract_enquetes_raw
from loaders.enquetes_sheets import save_bronze, save_gold, save_prata, save_validation
from transformers.enquetes import build_gold, to_bronze, to_prata
from validators.enquetes import run_validations


def run_enquetes_pipeline() -> dict:
    print("Starting enquetes (electoral polls) ETL pipeline...")
    ingestion_ts = datetime.now()

    layers = get_layer_spreadsheets("bronze", "prata", "ouro")

    # --- Phase 1: Extraction -> bronze ---
    print("\n--- Phase 1: Extraction (bronze) ---")
    raw = extract_enquetes_raw()
    if not raw:
        print("No enquetes CSV files were found; nothing to process.")
        return {"status": "empty"}

    bronze_by_year = {}
    for ano, (source_folder, source_file, df) in raw.items():
        bronze = to_bronze(df, ano, source_folder, source_file, ingestion_ts)
        bronze_by_year[ano] = bronze
        tab = save_bronze(layers["bronze"], bronze, ano)
        print(f"-> bronze {ano}: {len(bronze)} rows -> tab '{tab}'")

    bronze_all = pd.concat(bronze_by_year.values(), ignore_index=True)

    # --- Phase 2: Transformation -> prata ---
    print("\n--- Phase 2: Transformation (prata) ---")
    prata = to_prata(bronze_all)
    save_prata(layers["prata"], prata)
    print(
        f"-> prata: {len(prata)} rows | "
        f"{prata['pesquisa_id'].nunique()} pesquisas | "
        f"{prata['cenario_id'].nunique()} cenários -> tab 'proc_enquetes_long'"
    )

    # --- Phase 3: Load -> ouro ---
    print("\n--- Phase 3: Load (ouro) ---")
    gold = build_gold(prata)
    written = save_gold(layers["ouro"], gold)
    for title in written:
        key = title.replace("gold_pesquisas_", "")
        print(f"-> ouro: tab '{title}' published")

    # --- Validations ---
    print("\n--- Validations ---")
    validation_df, headline = run_validations(bronze_by_year, prata, gold)
    save_validation(layers["prata"], validation_df)
    for _, row in validation_df.iterrows():
        print(f"   [{row['severidade']}] {row['verificacao']}: {row['resultado']}")

    print(
        f"\nSuccess! enquetes pipeline: bronze={headline['total_bronze']} | "
        f"prata={headline['linhas_prata']} | gold_temporal={headline['linhas_gold_temporal']} | "
        f"erros={headline['erros']} | avisos={headline['avisos']}"
    )
    return headline
