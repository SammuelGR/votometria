import os

## =================================================================
## TSE EXTRACTION CONSTANTS (PRESIDENCY 2018 AND 2022)
## =================================================================

# Source ZIP URLs from the TSE Open Data repository
URL_TSE_PRESIDENCY_2018 = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip"
URL_TSE_PRESIDENCY_2022 = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip"
URL_TSE_ELECTORATE_2018 = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2018.zip"
URL_TSE_ELECTORATE_2022 = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2022.zip"

# Target files inside the ZIP archives
TARGET_CSV_PRESIDENCY_2018 = "votacao_candidato_munzona_2018_BR.csv"
TARGET_CSV_PRESIDENCY_2022 = "votacao_candidato_munzona_2022_BR.csv"
TARGET_CSV_ELECTORATE_2018 = "perfil_eleitorado_2018.csv"
TARGET_CSV_ELECTORATE_2022 = "perfil_eleitorado_2022.csv"

# Target files after extraction and transformation
OUTPUT_CSV_PRESIDENCY_2018 = "parsed_presidencia_2018.csv"
OUTPUT_CSV_PRESIDENCY_2022 = "parsed_presidencia_2022.csv"

# Transformed tables for analysis
OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2018 = "votos_candidatos_turno_1_2018.csv"
OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2018 = "votos_candidatos_turno_2_2018.csv"
OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2018 = "distribuicao_estado_turno_1_2018.csv"
OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2018 = "distribuicao_estado_turno_2_2018.csv"
OUTPUT_CSV_COMPARACAO_TURNOS_2018 = "comparacao_turnos_2018.csv"

OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2022 = "votos_candidatos_turno_1_2022.csv"
OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2022 = "votos_candidatos_turno_2_2022.csv"
OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2022 = "distribuicao_estado_turno_1_2022.csv"
OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2022 = "distribuicao_estado_turno_2_2022.csv"
OUTPUT_CSV_COMPARACAO_TURNOS_2022 = "comparacao_turnos_2022.csv"

# Read/write settings
CSV_ENCODING = "latin-1"
CSV_SEPARATOR = ";"

# Local directory setup
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