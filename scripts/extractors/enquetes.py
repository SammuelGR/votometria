"""
Extractor for the electoral-polls (enquetes) source.

Reads the ``pesquisas_presidenciais_<ano>.csv`` files from each election folder
with no coercion (every value kept as raw text), so the bronze layer preserves
the original percentuais, datas, candidatos, partidos, institutos and fontes.
The raw files themselves are never modified.
"""

import pandas as pd

from constants_enquetes import ENQUETES_CSV_TEMPLATE, ENQUETES_FOLDERS


def extract_enquetes_raw() -> dict:
    """
    Returns ``{ano_eleicao: (source_folder, source_file, DataFrame)}`` for each
    election folder whose CSV exists. Missing files are skipped with a warning.
    """
    result = {}
    for ano, folder in ENQUETES_FOLDERS.items():
        filename = ENQUETES_CSV_TEMPLATE.format(ano=ano)
        path = folder / filename
        if not path.is_file():
            print(f"Warning: enquetes CSV not found: {path}")
            continue

        # dtype=str + keep_default_na=False -> nothing is turned into NaN; the
        # bronze layer stores exactly what is in the file.
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        result[ano] = (folder.name, filename, df)
        print(f"-> enquetes {ano}: {len(df)} raw rows from {folder.name}/{filename}")

    return result
