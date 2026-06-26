# TSE Data Pipeline Documentation

## Overview

The TSE pipeline is responsible for extracting and transforming Brazilian election data from the Tribunal Superior Eleitoral (TSE). It is implemented to support presidential election analysis and is architected to accept future expansion for voter profile data.

This pipeline processes:
- Presidential election results for 2018 and 2022
- Voter profile data as a future domain, with a planned structural boundary already defined in the codebase

The architecture follows a standard ETL flow:
1. Extraction
2. Transformation
3. Pipeline orchestration and storage

The target output is parsed data in `data/parsed_tse`, with year-specific files generated for presidency data.

## Data Extraction (`extractors/tse`)

### Purpose

The extraction layer downloads raw TSE datasets from official open data sources and extracts only the target CSV files required for analysis.

### Source Data

The pipeline uses official TSE open data URLs for both presidential and electorate datasets:
- Presidential 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip
- Presidential 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip
- Electorate 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2018.zip
- Electorate 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2022.zip

### Implementation

The extraction module is located in `scripts/extractors/tse.py`.
It includes:
- `download_and_extract_tse(url_zip, target_filename)`
  - downloads a ZIP archive using streaming download
  - extracts only the required CSV file to `data/raw`
  - skips extraction if the target file already exists
  - cleans up temporary ZIP files after extraction
- `extract_presidency_data()`
  - orchestrates extraction of presidential files for 2018 and 2022
- `extract_voter_profile_data()`
  - orchestrates extraction of electorate files for 2018 and 2022

### Raw Data Structure

Raw CSV files are stored in `data/raw`.
The extraction layer focuses on national-level presidential CSV files only, avoiding governor, senator, or other non-presidential data.

The targeted raw filenames are:
- `votacao_candidato_munzona_2018_BR.csv`
- `votacao_candidato_munzona_2022_BR.csv`
- `perfil_eleitorado_2018.csv`
- `perfil_eleitorado_2022.csv`

### Extraction Responsibilities

The extractors are responsible for:
- fetching data from the TSE open data repository
- validating HTTP responses and download success
- extracting only the relevant CSV files from ZIP archives
- writing raw files to `data/raw`
- avoiding repeated downloads when source files already exist locally

## Data Transformation (`transformers/tse`)

### Purpose

The transformation layer takes raw CSV input from `data/raw` and produces cleaned, analysis-ready datasets.
This layer is designed to enforce column selection, clean text fields, remove invalid records, and preserve only the required presidential data.

### Mandatory use of `INTEREST_COLUMNS_PRESIDENCY`

Transformation must use the columns defined in `constants_tse.INTEREST_COLUMNS_PRESIDENCY`:
- `NR_TURNO`
- `SG_UF`
- `NM_URNA_CANDIDATO`
- `SG_PARTIDO`
- `NM_PARTIDO`
- `QT_VOTOS_NOMINAIS`
- `DS_SIT_TOT_TURNO`

This list defines the only columns that are persisted for presidential analysis.

### Transformation Steps for Presidency Data

The transformation module is located in `scripts/transformers/tse.py`.
It includes the following responsibilities:
- `load_presidency_csv(csv_filename)`
  - loads the raw CSV from `data/raw`
  - uses `latin-1` encoding and `;` separator
- `select_interest_columns(df)`
  - selects only the columns defined in `INTEREST_COLUMNS_PRESIDENCY`
  - preserves column order and warns if expected columns are missing
- `clean_presidency_data(df)`
  - removes rows with null values in critical columns
  - strips whitespace from text fields
  - removes duplicate rows
  - filters out rows with negative vote counts
- `transform_presidency_year(csv_filename, year)`
  - applies loading, selection, and cleaning for a single year
- `save_presidency_data(df, year, format="csv")`
  - saves the cleaned DataFrame to `data/parsed_tse`
  - writes year-specific filenames for 2018 and 2022

### Separation of Domains

The module keeps a clear separation between presidency transformations and electorate transformations.
Current implementation fully supports presidency data. Electorate processing is not yet implemented, but the file contains a future-ready structure with documented TODO functions:
- `load_voter_profile_csv()`
- `select_voter_profile_columns()`
- `clean_voter_profile_data()`
- `transform_voter_profile_data()`
- `save_voter_profile_data()`
- `run_voter_profile_transformation()`

### Justification for Separation

Keeping presidency and electorate logic separated enables:
- easier maintenance of each domain
- independent evolution of data models
- future addition of new data types without breaking existing presidency processing
- clearer architectural boundaries inside the same TSE module

## Pipeline Orchestration (`pipelines/tse.py`)

### Purpose

The pipeline orchestrator coordinates extraction and transformation in a single end-to-end flow.
It runs the raw data ingestion first, then cleans and persists parsed results.

### Execution Flow

The orchestration is implemented in `scripts/pipelines/tse.py`.
The steps are:
1. `extract_presidency_data()`
2. `extract_voter_profile_data()`
3. `run_presidency_transformation()`

The pipeline is intentionally linear:
- extraction must happen before transformation
- transformation depends on extracted raw files in `data/raw`
- load depends on parsed presidency CSVs in `data/parsed_tse`
- persistence writes aggregated tables to `data/tables`

### Responsibility of Each Stage

Extraction stage:
- download and extract official TSE CSV files
- save raw files in `data/raw`

Transformation stage:
- load raw CSVs
- select only relevant columns
- clean and standardize data
- save parsed outputs by election year

Pipeline stage:
- orchestrate stage order
- guard against failure if extraction or transformation fails
- report success and file generation status

### Persistence

Transformed data is written to `data/parsed_tse`.
The pipeline currently persists only presidency datasets, while voter profile persistence is prepared in the architecture.

## Output Datasets

### Generated Presidency Datasets

The pipeline generates year-specific presidency datasets:
- `data/parsed_tse/parsed_presidencia_2018.csv`
- `data/parsed_tse/parsed_presidencia_2022.csv`

Each file contains only the columns defined by `INTEREST_COLUMNS_PRESIDENCY`, cleaned and standardized for analysis.

### Future Electorate Dataset

The documentation and architecture reserve a place for a future dataset named:
- `parsed_eleitorado`

This dataset is not yet implemented, but the pipeline structure is prepared to support its addition.

### Output Format and Conventions

Current output format:
- CSV
- encoding: `latin-1`
- separator: `;`

Naming convention:
- `parsed_presidencia_<year>.csv`
- stored in `data/parsed_tse`

The year suffix clarifies the election cycle and keeps files isolated by cycle.

## Constants and Configuration (`constants_tse`)

### Role of `constants_tse`

The `constants_tse` module centralizes pipeline configuration for:
- source URLs
- target filenames inside ZIP archives
- CSV encoding and separator
- local raw data directory path
- column selection for transformation

This centralized approach avoids hardcoding values in multiple modules and improves maintainability.

### Importance of `INTEREST_COLUMNS_PRESIDENCY`

`INTEREST_COLUMNS_PRESIDENCY` defines the exact schema that the transformation layer persists.
Using this constant ensures:
- only relevant columns are kept
- transformations remain consistent across years
- future schema changes are explicit and controlled

### Safely Evolving Columns

To add or change columns safely:
1. Update `INTEREST_COLUMNS_PRESIDENCY` in `scripts/constants_tse.py`
2. Verify that raw CSV files include the new columns
3. Confirm `select_interest_columns()` preserves the updated set
4. Adjust downstream analysis expectations for the new column schema

This strategy keeps the transformation layer stable while allowing controlled schema evolution.

## Extensibility

### Adding New Elections

The pipeline can be extended to additional election cycles by:
- defining new source URLs and target filenames in `constants_tse`
- adding new extraction targets in `extractors/tse.py`
- adding new year-specific transformation calls in `transformers/tse.py`
- preserving the existing ETL orchestration in `pipelines/tse.py`

### Adding Electorate Data

The current architecture supports adding electorate transformation without structural refactor:
- the extractor already downloads electorate files
- the transformer module contains a future-ready TODO section for electorate processing
- the pipeline can later invoke `run_voter_profile_transformation()` alongside `run_presidency_transformation()`

This separation ensures new domain logic does not interfere with the existing presidency flow.

### Maintenance and Scalability

Best practices for this pipeline:
- keep extraction URLs and target filenames in `constants_tse`
- use year-specific output names for parsed data
- avoid mixing raw data loading with transformation rules
- preserve domain boundaries between presidency and electorate
- keep pipeline orchestration simple and explicit

## References

Official TSE data URLs used by the project:
- Presidential 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip
- Presidential 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip
- Electorate 2018: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2018.zip
- Electorate 2022: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2022.zip

Existing project modules:
- `scripts/extractors/tse.py`
- `scripts/transformers/tse.py`
- `scripts/pipelines/tse.py`
- `scripts/constants_tse.py`
