# TSE Data Integration

This document is intended as a practical reference for developers and coding agents working on the TSE ingestion flow. It explains the configuration, source files, execution strategy, local output layout, and processing logic used to generate historical election data for the dashboard.

---

## 1. Source Files

The TSE pipeline downloads public ZIP archives from the TSE open data repository.

Current presidential vote sources:

- `votacao_candidato_munzona_2018.zip`
- `votacao_candidato_munzona_2022.zip`

Current voter profile sources:

- `perfil_eleitorado_2018.zip`
- `perfil_eleitorado_2022.zip`

The extractor stores only the target CSV files from each ZIP archive.

Target raw CSV files:

- `votacao_candidato_munzona_2018_BR.csv`
- `votacao_candidato_munzona_2022_BR.csv`
- `perfil_eleitorado_2018.csv`
- `perfil_eleitorado_2022.csv`

---

## 2. Local Output Layout

The TSE integration is file-based and keeps generated artifacts inside the scripts module.

```text
scripts/data/
  raw/
  parsed_tse/
  tables/
```

- `scripts/data/raw`: raw CSV files extracted from TSE ZIP archives.
- `scripts/data/parsed_tse`: cleaned intermediate CSV files.
- `scripts/data/tables`: final aggregated CSV tables used for historical election analysis.

Files under `scripts/data` are generated locally and are not versioned.

---

## 3. Execution

Run the scripts entrypoint from inside `/scripts`:

```bash
python main.py
```

The TSE pipeline runs from `scripts/main.py` through `scripts/pipelines/tse.py`.

The first execution may take longer because the TSE source files are large. When a target raw CSV already exists in `scripts/data/raw`, the extractor skips that download.

To run only the TSE pipeline during development:

```bash
python -c "from pipelines.tse import run_tse_pipeline; run_tse_pipeline()"
```

---

## 4. Processing Scope

The current TSE pipeline processes presidential election data for:

- 2018
- 2022

The transformed presidency dataset keeps the following columns:

- `NR_TURNO`
- `SG_UF`
- `NM_URNA_CANDIDATO`
- `SG_PARTIDO`
- `NM_PARTIDO`
- `QT_VOTOS_NOMINAIS`
- `DS_SIT_TOT_TURNO`

The transformed voter profile dataset keeps the following columns:

- `SG_UF`
- `CD_MUNICIPIO`
- `NR_ZONA`
- `DS_FAIXA_ETARIA`
- `QT_ELEITORES_PERFIL`

Vote and voter count fields are parsed as numeric values during transformation.

---

## 5. Generated Tables

The load stage writes aggregated CSV tables to `scripts/data/tables`.

Generated 2018 tables:

- `votos_candidatos_turno_1_2018.csv`
- `votos_candidatos_turno_2_2018.csv`
- `distribuicao_estado_turno_1_2018.csv`
- `distribuicao_estado_turno_2_2018.csv`
- `comparacao_turnos_2018.csv`

Generated 2022 tables:

- `votos_candidatos_turno_1_2022.csv`
- `votos_candidatos_turno_2_2022.csv`
- `distribuicao_estado_turno_1_2022.csv`
- `distribuicao_estado_turno_2_2022.csv`
- `comparacao_turnos_2022.csv`

Table purposes:

- Candidate vote totals by round.
- State-level vote distribution by round.
- First-round versus second-round comparison for runoff candidates.

---

## 6. Scripts Architecture

The TSE integration follows the project ETL layout:

- `scripts/constants_tse.py`: Defines TSE source URLs, target filenames, selected columns, encoding, separator, and local output directories.
- `scripts/extractors/tse.py`: Downloads TSE ZIP archives and extracts target raw CSV files into `scripts/data/raw`.
- `scripts/transformers/tse.py`: Loads raw CSV files, selects relevant columns, cleans records, and writes parsed CSV files into `scripts/data/parsed_tse`.
- `scripts/loaders/tse_sheets.py`: Publishes the parsed election data and derived vote tables to Google Sheets for frontend use.
- `scripts/pipelines/tse.py`: Orchestrates extraction, transformation, and Google Sheets publication.
- `scripts/main.py`: Runs the integrated scripts entrypoint.

---

## 7. Operational Notes

- The TSE source files are large, so the first execution can be slow.
- The extractor currently prints start and completion messages, but does not show download progress.
- If a download is interrupted, remove the incomplete raw file before running the pipeline again.
- If direct browser download is more reliable in a local environment, place the extracted target CSV file in `scripts/data/raw` using the expected filename.
- The Google Sheets publication step is the main integration point for the dashboard, so changes in worksheet names or column structure should be reflected in the frontend parser as well.
- The generated CSV tables are intentionally local artifacts and should not be committed.
