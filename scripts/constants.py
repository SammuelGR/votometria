from pathlib import Path

# Polymarket API configuration constants
POLYMARKET_ELECTION_EVENT_ID = "45915"
POLYMARKET_GAMMA_EVENT_URL = "https://gamma-api.polymarket.com/events/{event_id}"
POLYMARKET_PRICE_HISTORY_URL = "https://clob.polymarket.com/prices-history"
POLYMARKET_HISTORY_OVERLAP_SECONDS = 24 * 60 * 60
POLYMARKET_HISTORY_FIDELITY_MINUTES = 60

# Google Trends configuration constants
GOOGLE_TRENDS_GEO = "BR"
GOOGLE_TRENDS_HL = "pt-BR"
GOOGLE_TRENDS_TZ = 180
GOOGLE_TRENDS_SOURCE_NAME = "google_trends"
GOOGLE_TRENDS_MAX_RETRIES = 3
GOOGLE_TRENDS_BACKOFF_SECONDS = 2

# Google Trends only compares terms requested together and accepts ~5 terms per
# query. With more than 5 candidates per election we collect in batches of one
# anchor term + up to 4 candidates, then rescale the batches using the anchor.
GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST = 5
GOOGLE_TRENDS_TERMS_PER_BATCH = 4

# Per-election configuration. Each group has its own timeframe, anchor term and
# candidate list. The "current" list is intentionally configurable and must NOT
# be treated as a definitive ballot — edit it freely as the race evolves.
GOOGLE_TRENDS_ELECTION_GROUPS = {
    "2018": {
        "timeframe": "2018-01-01 2018-12-31",
        "anchor_term": "Jair Bolsonaro",
        "terms": [
            "Jair Bolsonaro",
            "Fernando Haddad",
            "Ciro Gomes",
            "Geraldo Alckmin",
            "Marina Silva",
            "João Amoêdo",
            "Henrique Meirelles",
            "Alvaro Dias",
            "Guilherme Boulos",
            "Cabo Daciolo",
            "Vera Lúcia",
            "João Goulart Filho",
            "Eymael",
        ],
    },
    "2022": {
        "timeframe": "2022-01-01 2022-12-31",
        "anchor_term": "Lula",
        "terms": [
            "Lula",
            "Jair Bolsonaro",
            "Simone Tebet",
            "Ciro Gomes",
            "Felipe d'Avila",
            "Soraya Thronicke",
            "Padre Kelmon",
            "Léo Péricles",
            "Sofia Manzano",
            "Vera Lúcia",
            "Eymael",
        ],
    },
    "current": {
        "timeframe": "today 12-m",
        "anchor_term": "Lula",
        # Search terms (not ballot names): party suffixes are intentionally
        # omitted because Google Trends matches search strings. "Lula" is used
        # for Luiz Inácio Lula da Silva and doubles as the anchor term.
        # Configurable list — not a definitive ballot.
        "terms": [
            "Lula",
            "Aldo Rebelo",
            "Augusto Cury",
            "Cabo Daciolo",
            "Edmilson Costa",
            "Flávio Bolsonaro",
            "Hertz Dias",
            "Renan Santos",
            "Romeu Zema",
            "Ronaldo Caiado",
            "Rui Costa Pimenta",
            "Samara Martins",
        ],
    },
}

# Output directories (anchored to the repo root, independent of the cwd)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = str(PROJECT_ROOT / "dados-brutos")
PROCESSED_DATA_DIR = str(PROJECT_ROOT / "dados-processados")
DOCS_DIR = str(PROJECT_ROOT / "docs")
