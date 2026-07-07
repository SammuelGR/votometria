# Google Trends — Pipeline

Pipeline ETL que coleta o interesse de busca do Google Trends para candidatos
presidenciais brasileiros de **2018**, **2022** e da **eleição atual**, e o publica
**direto no Google Sheets** (uma aba por dataset, sem banco de dados e sem CSV em
disco). Usa coleta em **lotes com termo-âncora** para contornar o limite de ~5 termos
por consulta — ver `google_trends_metodologia.md`. A configuração e a mecânica do
Google Sheets estão em `google_sheets_sync.md`.

## Fluxo do pipeline

```
get_spreadsheet()                             [Setup]    → abre a planilha (lê .env)
Para cada grupo eleitoral (2018, 2022, current):
  build_trends_batches(terms, anchor)        → lotes de 1 âncora + até 4 candidatos
  Para cada lote:
    fetch_interest_over_time_batch(...)       [Extract]  → DataFrame wide
    save_raw_google_trends_batch(...)         [Load]     → aba raw_google_trends_{ano}_batch_NN
    transform_batch_interest_over_time(...)   [Transform]→ long com interest_raw
  rescale_batches_by_anchor(lotes, anchor)    [Transform]→ adiciona interest_scaled
  save_processed_google_trends_year(...)      [Load]     → aba proc_google_trends_{ano}_interest_long

Consolidar todos os anos:
  save_processed_google_trends_all(...)       [Load]     → aba proc_google_trends_all_elections_interest_long
  build_monthly_interest(consolidado)        [Transform]→ média mensal de interest_raw por (ano, termo)
  save_processed_google_trends_monthly(...)   [Load]     → aba proc_google_trends_all_elections_interest_monthly
```

A função de orquestração é `run_google_trends_pipeline()` em
`scripts/pipelines/google_trends.py`. É **independente do banco de dados** e **refaz a
janela completa** a cada execução. As abas são separadas por camada: `raw_*` para os
dados brutos e `proc_*` para os processados. A escrita reusa
`scripts/core/sheets.py` (autenticação + `write_dataframe_to_tab`).

Retorno (estrutura; números ilustrativos):

```python
{
    "source": "google_trends",
    "status": "success",
    "groups": {
        "2018":    {"terms_count": 13, "batches_count": 3, "processed_rows": 600, "processed_tab": "proc_google_trends_2018_interest_long"},
        "2022":    {"terms_count": 11, "batches_count": 3, "processed_rows": 520, "processed_tab": "proc_google_trends_2022_interest_long"},
        "current": {"terms_count": 0,  "batches_count": 0, "processed_rows": 0,   "processed_tab": None},
    },
    "all_processed_tab": "proc_google_trends_all_elections_interest_long",
    "all_processed_monthly_tab": "proc_google_trends_all_elections_interest_monthly",
}
```

Se `current["terms"]` estiver vazio, o pipeline **não quebra**: registra um aviso,
reporta o grupo com contagens zeradas e segue com 2018 e 2022. Falhas de coleta em um
lote são registradas e o pipeline continua com os demais.

## Abas geradas no Google Sheets

- Brutos: `raw_google_trends_{ano}_batch_{NN}`.
- Processados por ano: `proc_google_trends_{ano}_interest_long`.
- Consolidado: `proc_google_trends_all_elections_interest_long`.
- Consolidado mensal: `proc_google_trends_all_elections_interest_monthly` — uma
  linha por (`election_year`, `term`, mês), com `interest_mean` (média de
  `interest_raw` dentro do mês; nunca usa `interest_scaled`). Dedicada a
  cruzar com outras fontes já agregadas por mês (ex. pesquisas eleitorais,
  `gold_pesquisas_media_mensal_candidato`) sem ruído diário. Como a média é
  sempre dentro do próprio termo (nunca comparando termos entre si), a
  ressalva de "não comparar `interest_raw` entre lotes diferentes" não se
  aplica aqui.

A cada execução cada aba é limpa e reescrita (cabeçalho + linhas, `RAW`). Esquema das
colunas em `google_trends_dicionario_dados.md`. Detalhes de credenciais, `.env` e
consumo pelo React em `google_sheets_sync.md`.

## Dependências

Em `scripts/requirements.txt`: `pandas`, `pytrends`, `gspread`, `google-auth`,
`python-dotenv`.

```bash
cd scripts
pip install -r requirements.txt
```

## Como executar

Requer um `.env` configurado com `GOOGLE_SHEETS_ID` e `GOOGLE_SERVICE_ACCOUNT_FILE`
(ver `google_sheets_sync.md`). Depois:

```bash
cd scripts
python main.py
```

O Google Trends roda junto do pipeline da Polymarket; uma falha no Google Trends
(inclusive de configuração/credenciais do Sheets) **não interrompe** os demais
pipelines.

## Onde configurar

Tudo em `scripts/constants.py`, no dicionário `GOOGLE_TRENDS_ELECTION_GROUPS`:

| O que alterar                | Onde                                                        |
| ---------------------------- | ----------------------------------------------------------- |
| Candidatos de um ano         | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["terms"]`           |
| Possíveis candidatos atuais  | `GOOGLE_TRENDS_ELECTION_GROUPS["current"]["terms"]`         |
| Período/janela de um ano     | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["timeframe"]`       |
| Termo-âncora de um ano       | `GOOGLE_TRENDS_ELECTION_GROUPS["<ano>"]["anchor_term"]`     |
| Data mínima publicada (grupo `current`) | `GOOGLE_TRENDS_ELECTION_GROUPS["current"]["min_date"]` |
| Região                       | `GOOGLE_TRENDS_GEO`                                         |
| Idioma / fuso                | `GOOGLE_TRENDS_HL`, `GOOGLE_TRENDS_TZ`                      |
| Termos por consulta / lote   | `GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST`, `GOOGLE_TRENDS_TERMS_PER_BATCH` |
| Retry / backoff              | `GOOGLE_TRENDS_MAX_RETRIES`, `GOOGLE_TRENDS_BACKOFF_SECONDS` |

> Se o `anchor_term` não estiver presente na lista `terms`, ele será adicionado
> automaticamente no início de cada lote.
> A lista de candidatos atuais é configurável e **não** é definitiva — ver
> `google_trends_candidatos.md`.
> O grupo `current` usa `timeframe: "today 12-m"` (janela móvel dos últimos 12
> meses), que sempre inclui alguns meses do ano anterior ao ciclo eleitoral. Por
> isso `min_date` corta as linhas publicadas nas abas prata/ouro (`proc_*`) para
> a data configurada — as abas `raw_*` (bronze) continuam com a janela completa,
> sem corte, para auditoria.

## Uso futuro no dashboard React

O consolidado, publicado na aba `proc_google_trends_all_elections_interest_long`, foi
desenhado para consumo direto por um **dashboard React** comparando eleições (como ler
a aba como CSV: ver `google_sheets_sync.md`):

- Uma linha por (`date`, `term`, `election_year`) facilita séries temporais por
  candidato e filtros por ano.
- `interest_raw` para análises dentro do mesmo lote; `interest_scaled` para comparação
  aproximada entre candidatos do mesmo ano.
- **Nunca** comparar `interest_raw` entre lotes diferentes; **não** comparar
  `interest_scaled` entre anos diferentes sem sinalizar que as janelas são
  independentes (ver `google_trends_metodologia.md`).
- O gráfico "Atenção pública × pesquisa eleitoral" consome
  `proc_google_trends_all_elections_interest_monthly` (não o diário), cruzando
  por mês com `gold_pesquisas_media_mensal_candidato` (enquetes) — ambos já
  agregados por mês, então o eixo X do gráfico tem um tick por mês.
- Metadados (`geo`, `timeframe`, `source`, `batch_id`, `anchor_term`, `collected_at`)
  permitem exibir contexto e data de atualização sem consultar o backend.
