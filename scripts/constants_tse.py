import os

## =================================================================
## TSE EXTRACTION CONSTANTS (PRESIDENCY 2018 AND 2022)
## =================================================================

# 1. Source ZIP URLs from the TSE Open Data repository
URL_TSE_PRESIDENCY_2018 = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip"
URL_TSE_PRESIDENCY_2022 = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip"
URL_TSE_ELECTORATE_2018 = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2018.zip"
URL_TSE_ELECTORATE_2022 = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2022.zip"

# 2. Target files inside the ZIP archives (focusing on national/presidency scope)
# This avoids loading governor, senator, and other non-presidential data.
TARGET_CSV_PRESIDENCY_2018 = "votacao_candidato_munzona_2018_BR.csv"
TARGET_CSV_PRESIDENCY_2022 = "votacao_candidato_munzona_2022_BR.csv"
TARGET_CSV_ELECTORATE_2018 = "perfil_eleitorado_2018.csv"
TARGET_CSV_ELECTORATE_2022 = "perfil_eleitorado_2022.csv"

# 3. Read/write settings
CSV_ENCODING = "latin-1"
CSV_SEPARATOR = ";"

# 4. Local directory setup
# Uses relative paths so the project works on any team member's machine.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Columns for transforming and cleaning the data, focusing on the most relevant fields for analysis.
INTEREST_COLUMNS_PRESIDENCY = [
    "NR_TURNO", 
    "SG_UF",
    "NM_URNA_CANDIDATO", 
    "SG_PARTIDO", 
    "NM_PARTIDO",
    "QT_VOTOS_NOMINAIS",
    "DS_SIT_TOT_TURNO"
]

INTEREST_COLUMNS_ELECTORATE = [
    "SG_UF",
    "CD_MUNICIPIO",
    "NR_ZONA",
    "DS_FAIXA_ETARIA",
    "QT_ELEITORES_PERFIL"
]