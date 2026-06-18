# Google Trends — Pipeline

Pipeline ETL que coleta o interesse de busca do Google Trends para candidatos
presidenciais brasileiros de **2018**, **2022** e da **eleição atual**, e o persiste
em arquivos CSV (sem banco de dados). Usa coleta em **lotes com termo-âncora** para
contornar o limite de ~5 termos por consulta — ver `google_trends_metodologia.md`.

## Fluxo do pipeline

```
Para cada grupo eleitoral (2018, 2022, current):
  build_trends_batches(terms, anchor)        → lotes de 1 âncora + até 4 candidatos
  Para cada lote:
    fetch_interest_over_time_batch(...)       [Extract]  → DataFrame wide
    save_raw_google_trends_batch_csv(...)     [Load]     → /dados-brutos/...batch_NN.csv
    transform_batch_interest_over_time(...)   [Transform]→ long com interest_raw
  rescale_batches_by_anchor(lotes, anchor)    [Transform]→ adiciona interest_scaled
  save_processed_google_trends_year_csv(...)  [Load]     → /dados-processados/{ano}_interest_long.csv

Consolidar todos os anos:
  save_processed_google_trends_all_csv(...)   [Load]     → google_trends_all_elections_interest_long.csv
```

A função de orquestração é `run_google_trends_pipeline()` em
`scripts/pipelines/google_trends.py`. É **independente do banco de dados** e **refaz a
janela completa** a cada execução.

Retorno (estrutura; números ilustrativos):

```python
{
    "source": "google_trends",
    "status": "success",
    "groups": {
        "2018":    {"terms_count": 13, "batches_count": 3, "processed_rows": 600, "processed_path": ".../google_trends_2018_interest_long.csv"},
        "2022":    {"terms_count": 11, "batches_count": 3, "processed_rows": 520, "processed_path": ".../google_trends_2022_interest_long.csv"},
        "current": {"terms_count": 0,  "batches_count": 0, "processed_rows": 0,   "processed_path": None},
    },
    "all_processed_path": ".../google_trends_all_elections_interest_long.csv",
}
```

Se `current["terms"]` estiver vazio, o pipeline **não quebra**: registra um aviso,
reporta o grupo com contagens zeradas e segue com 2018 e 2022. Falhas de coleta em um
lote são registradas e o pipeline continua com os demais.

## Arquivos gerados

- Brutos: `dados-brutos/google_trends_{ano}_batch_{NN}.csv` (+ cópia timestampada).
- Processados por ano: `dados-processados/google_trends_{ano}_interest_long.csv` (+ timestampada).
- Consolidado: `dados-processados/google_trends_all_elections_interest_long.csv` (+ timestampada).

As pastas ficam na **raiz do repositório** (mesmo nível de `docs/`); os caminhos são
resolvidos via `Path(__file__)` em `constants.py`. Esquema das colunas em
`google_trends_dicionario_dados.md`.

## Dependências

Em `scripts/requirements.txt`: `pandas`, `pytrends`.

```bash
cd scripts
pip install -r requirements.txt
```

## Como executar

```bash
cd scripts
python main.py
```

O Google Trends roda junto do pipeline da Polymarket; uma falha no Google Trends
**não interrompe** os demais pipelines.

## Onde configurar

Tudo em `scripts/constants.py`, no dicionário `GOOGLE_TRENDS_ELECTION_GROUPS`:

| O que alterar                | Onde                                                        |
| ---------------------------- | ----------------------------------------------------------- |
| Candidatos de um ano         | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["terms"]`           |
| Possíveis candidatos atuais  | `GOOGLE_TRENDS_ELECTION_GROUPS["current"]["terms"]`         |
| Período/janela de um ano     | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["timeframe"]`       |
| Termo-âncora de um ano       | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["anchor_term"]`     |
| Região                       | `GOOGLE_TRENDS_GEO`                                         |
| Idioma / fuso                | `GOOGLE_TRENDS_HL`, `GOOGLE_TRENDS_TZ`                      |
| Termos por consulta / lote   | `GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST`, `GOOGLE_TRENDS_TERMS_PER_BATCH` |
| Retry / backoff              | `GOOGLE_TRENDS_MAX_RETRIES`, `GOOGLE_TRENDS_BACKOFF_SECONDS` |

> O `anchor_term` de um ano **deve** estar presente na lista `terms` daquele ano.
> A lista de candidatos atuais é configurável e **não** é definitiva — ver
> `google_trends_candidatos.md`.

## Uso futuro no dashboard React

O consolidado `dados-processados/google_trends_all_elections_interest_long.csv` foi
desenhado para consumo direto por um **dashboard React** comparando eleições:

- Uma linha por (`date`, `term`, `election_year`) facilita séries temporais por
  candidato e filtros por ano.
- `interest_raw` para análises dentro do mesmo lote; `interest_scaled` para comparação
  aproximada entre candidatos do mesmo ano.
- **Nunca** comparar `interest_raw` entre lotes diferentes; **não** comparar
  `interest_scaled` entre anos diferentes sem sinalizar que as janelas são
  independentes (ver `google_trends_metodologia.md`).
- Metadados (`geo`, `timeframe`, `source`, `batch_id`, `anchor_term`, `collected_at`)
  permitem exibir contexto e data de atualização sem consultar o backend.
