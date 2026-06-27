from pathlib import Path

# Polymarket API configuration constants
POLYMARKET_SOURCE = "polymarket"
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
        "anchor_term": "Bolsonaro",
        # "Lula" entra logo após a âncora para cair no batch_01 junto de Haddad e
        # Ciro: foi o pré-candidato dominante até a impugnação pelo TSE (31/08/2018),
        # com Haddad herdando sua base (11/09/2018). Mantê-lo é essencial para ler a
        # transferência de atenção. A âncora é "Bolsonaro" (alto e estável o ano todo,
        # evitando interest_scaled nulo no fim de 2018). Usamos o sobrenome "Bolsonaro",
        # e não o nome completo "Jair Bolsonaro", porque o Google Trends casa strings de
        # busca e o público busca esmagadoramente "Bolsonaro"; o nome completo subestima
        # fortemente o interesse (ver docs/google_trends_metodologia.md). Pela mesma
        # razão usamos "Haddad" (e não "Fernando Haddad"): auditoria de 2018 mostrou
        # "Haddad" com ~7,7x mais interesse de busca que o nome completo.
        "terms": [
            "Bolsonaro",
            "Lula",
            "Haddad",
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
        # "Bolsonaro" (sobrenome) em vez de "Jair Bolsonaro": o Google Trends casa
        # strings de busca e o público busca muito mais "Bolsonaro". Usar o nome
        # completo subestimava drasticamente o interesse e inflava o Share de Lula
        # (ver docs/auditoria_google_trends_importacao.md e a metodologia).
        "terms": [
            "Lula",
            "Bolsonaro",
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
        #
        # "Bolsonaro" (sobrenome) é um termo de ATENÇÃO PÚBLICA agregada da
        # família/marca (Jair, Flávio, Eduardo, Michelle...), não um candidato
        # específico. Fica logo após a âncora para cair no batch_01 e ser
        # diretamente comparável a "Lula". Atenção: no Share of Search, "Bolsonaro"
        # e "Flávio Bolsonaro" se sobrepõem (as buscas por Flávio também contêm
        # "Bolsonaro") — não selecionar os dois juntos para não contar em dobro.
        "terms": [
            "Lula",
            "Bolsonaro",
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

# Repo root (anchored independently of the cwd). Used to resolve relative paths
# such as the service account file in the Google Sheets configuration.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = str(PROJECT_ROOT / "docs")
