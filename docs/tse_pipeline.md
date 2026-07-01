# TSE Data Pipeline Documentation

This document describes the current TSE ETL flow used to ingest presidential election results and voter profile data from the Tribunal Superior Eleitoral, clean them, and publish analysis-ready tables to Google Sheets for the dashboard.

---

## 1. Scope

The pipeline currently covers:

- presidential election results for 2018 and 2022
- voter profile datasets for 2018 and 2022
- publication of processed tables into Google Sheets for frontend consumption

The implementation is organized as a standard ETL flow:

1. extraction
2. transformation
3. load to Google Sheets

---

## 2. Extraction

The extractor downloads public ZIP archives from the official TSE open data repository and keeps only the target CSV files required for analysis.

### Source files

Presidential vote sources:

- `votacao_candidato_munzona_2018.zip`
- `votacao_candidato_munzona_2022.zip`

Voter profile sources:

- `perfil_eleitorado_2018.zip`
- `perfil_eleitorado_2022.zip`

### Extracted raw files

The extractor writes the relevant CSV files to `scripts/data/raw`:

- `votacao_candidato_munzona_2018_BR.csv`
- `votacao_candidato_munzona_2022_BR.csv`
- `perfil_eleitorado_2018.csv`
- `perfil_eleitorado_2022.csv`

The implementation lives in `scripts/extractors/tse.py` and is orchestrated by `scripts/pipelines/tse.py`.

---

## 3. Transformation

The transformation layer loads the raw CSVs, selects the relevant columns, cleans them, and saves analysis-ready files to disk.

### Presidency transformation

The presidency workflow uses the columns defined in `scripts/constants_tse.py`:

- `NR_TURNO`
- `SG_UF`
- `NM_URNA_CANDIDATO`
- `SG_PARTIDO`
- `NM_PARTIDO`
- `QT_VOTOS_NOMINAIS`
- `DS_SIT_TOT_TURNO`

The cleaning steps include:

- removing rows with null values in critical fields
- trimming whitespace from text fields
- dropping duplicate rows
- filtering out negative vote counts

The transformed outputs are written to:

- `scripts/data/parsed_tse/parsed_presidencia_2018.csv`
- `scripts/data/parsed_tse/parsed_presidencia_2022.csv`

### Voter profile transformation

The voter profile workflow keeps the following columns:

- `SG_UF`
- `CD_MUNICIPIO`
- `NR_ZONA`
- `DS_FAIXA_ETARIA`
- `QT_ELEITORES_PERFIL`

The transformed outputs are written to:

- `scripts/data/parsed_tse/parsed_eleitorado_2018.csv`
- `scripts/data/parsed_tse/parsed_eleitorado_2022.csv`

The transformation logic is implemented in `scripts/transformers/tse.py`.

---

## 4. Load to Google Sheets

The current load stage publishes the transformed data to Google Sheets instead of relying only on local CSV tables.

### Worksheets written

For each election year, the loader creates the following sheets:

- `raw_tse_presidency_{year}`: the parsed presidency source data
- `proc_tse_{year}_votes_t1`: candidate vote totals for round 1
- `proc_tse_{year}_votes_t2`: candidate vote totals for round 2
- `proc_tse_{year}_state_dist_t1`: state-level vote distribution for round 1
- `proc_tse_{year}_state_dist_t2`: state-level vote distribution for round 2
- `proc_tse_{year}_comparison`: comparison between rounds for runoff candidates

The loader implementation is in `scripts/loaders/tse_sheets.py`.

### Frontend consumption

The React frontend reads the processed vote totals from the worksheets named:

- `proc_tse_{year}_votes_t1`
- `proc_tse_{year}_votes_t2`

This is handled by `frontend/src/services/tseVotes.ts`, which parses the Google Sheets CSV, normalizes vote counts, and feeds the chart component that renders valid-vote results.

---

## 5. Pipeline orchestration

The orchestration entrypoint is `scripts/pipelines/tse.py`.

The pipeline runs in three phases:

1. extraction of presidency and electorate ZIP files
2. transformation of raw CSVs into cleaned parsed datasets
3. load of the processed tables into Google Sheets

The loader currently attempts both election years and reports warnings if any phase fails.

---

## 6. Execution

From the `scripts` directory, run:

```bash
python main.py
```

For a focused run of the TSE pipeline only:

```bash
python -c "from pipelines.tse import run_tse_pipeline; run_tse_pipeline()"
```

---

## 7. Configuration

Most pipeline settings are centralized in `scripts/constants_tse.py`, including:

- source URLs
- target filenames inside ZIP archives
- CSV encoding and separator
- local output directories
- selected columns for transformation

This keeps the ETL logic consistent across extraction, transformation, and loading.

---

## 8. Notes

- The first execution can take longer because the TSE source files are large.
- The pipeline is designed to be resilient to missing or partially downloaded inputs by logging warnings instead of failing immediately.
- The frontend chart uses the processed vote tables and applies the same color pattern as the other dashboard modules: the top two candidates are highlighted, and the remainder use a neutral tone.

- Presidential 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip
- Presidential 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip
- Electorate 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2018.zip
- Electorate 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2022.zip

Existing project modules:
- `scripts/extractors/tse.py`
- `scripts/transformers/tse.py`
- `scripts/pipelines/tse.py`
- `scripts/constants_tse.py`
