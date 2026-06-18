# Google Trends — Dicionário de Dados

Documentação dos arquivos CSV gerados pelo pipeline do Google Trends.

Os arquivos canônicos são sobrescritos a cada execução. A cada execução também é
gravada uma cópia com sufixo de timestamp (`_YYYYMMDD_HHMMSS`) para rastreabilidade
(essas cópias não são versionadas no git).

---

## 1. Dados brutos (por ano e lote)

**Arquivos:** `dados-brutos/google_trends_{ano}_batch_{NN}.csv`
**Cópia timestampada:** `dados-brutos/google_trends_{ano}_batch_{NN}_YYYYMMDD_HHMMSS.csv`

Exemplos: `google_trends_2018_batch_01.csv`, `google_trends_2022_batch_03.csv`,
`google_trends_current_batch_01.csv`.

Formato **wide**, o mais próximo possível do retorno do `pytrends`. O índice de data
é promovido a coluna `date`; há uma coluna por termo do lote (incluindo o âncora) e a
coluna `isPartial` do Google é preservada.

| Campo       | Tipo    | Descrição                                                   | Exemplo          |
| ----------- | ------- | ----------------------------------------------------------- | ---------------- |
| `date`      | data    | Ponto temporal da série                                     | `2022-03-13`     |
| `<termo_1>` | inteiro | Índice de interesse (0–100) do 1º termo do lote (o âncora)  | `80`             |
| `<termo_2>` | inteiro | Índice de interesse (0–100) do 2º termo do lote             | `45`             |
| `...`       | inteiro | Demais termos do lote (até 5 colunas de termos no total)    | `12`             |
| `isPartial` | boolean | Indica se o ponto ainda é parcial (período em andamento)    | `False`          |

> As colunas de termos variam por lote, conforme `GOOGLE_TRENDS_ELECTION_GROUPS`.

Exemplo:

```csv
date,Lula,Jair Bolsonaro,Simone Tebet,Ciro Gomes,Felipe d'Avila,isPartial
2022-03-13,80,70,10,8,3,False
```

---

## 2. Dados processados

### 2.1 Por ano

**Arquivos:** `dados-processados/google_trends_{ano}_interest_long.csv`
**Cópia timestampada:** `..._YYYYMMDD_HHMMSS.csv`

Exemplos: `google_trends_2018_interest_long.csv`, `google_trends_2022_interest_long.csv`,
`google_trends_current_interest_long.csv`.

### 2.2 Consolidado geral

**Arquivo:** `dados-processados/google_trends_all_elections_interest_long.csv`

Une os arquivos por ano em um único CSV (mesmo esquema de colunas).

Ambos usam o formato **long/tidy**: uma linha por (`date`, `term`), com os valores
bruto e reescalado e os metadados de coleta. Pronto para consumo em React, pandas ou
ferramentas de BI.

| Campo             | Tipo            | Descrição                                                        | Exemplo               |
| ----------------- | --------------- | ---------------------------------------------------------------- | --------------------- |
| `date`            | string ISO date | Data do ponto temporal (`YYYY-MM-DD`)                            | `2022-03-13`          |
| `election_year`   | string          | Ano eleitoral: `2018`, `2022` ou `current`                       | `2022`                |
| `term`            | string          | Termo pesquisado no Google Trends                                | `Simone Tebet`        |
| `interest_raw`    | inteiro         | Valor original do Google Trends **dentro do lote** (0–100)       | `10`                  |
| `interest_scaled` | float (nulável) | Valor ajustado pelo termo-âncora; vazio se não pôde reescalar    | `20.0`                |
| `geo`             | string          | Região da busca                                                  | `BR`                  |
| `timeframe`       | string          | Janela temporal pesquisada                                       | `2022-01-01 2022-12-31` |
| `source`          | string          | Valor fixo identificando a fonte                                 | `google_trends`       |
| `batch_id`        | string          | Identificador do lote dentro do ano                              | `batch_02`            |
| `anchor_term`     | string          | Termo usado como âncora naquele ano                              | `Lula`                |
| `is_anchor`       | boolean         | Indica se a linha é do termo-âncora                              | `False`               |
| `is_partial`      | boolean         | Indica se o ponto ainda é parcial                                | `False`               |
| `collected_at`    | string ISO 8601 | Timestamp da execução do pipeline                                | `2026-06-18T20:00:00` |

Exemplo:

```csv
date,election_year,term,interest_raw,interest_scaled,geo,timeframe,source,batch_id,anchor_term,is_anchor,is_partial,collected_at
2018-01-07,2018,Fernando Haddad,32,28.5,BR,2018-01-01 2018-12-31,google_trends,batch_01,Jair Bolsonaro,False,False,2026-06-18T20:00:00
2022-03-13,2022,Lula,80,80.0,BR,2022-01-01 2022-12-31,google_trends,batch_01,Lula,True,False,2026-06-18T20:00:00
```

### Observações

- **`interest_raw`** é sempre preservado (auditoria) e é um inteiro de 0 a 100.
- **`interest_scaled`** pode ser **vazio (nulo)** quando o termo-âncora vale 0 ou está
  ausente naquela data (não foi possível reescalar — ver `google_trends_metodologia.md`).
- Para o **lote base** (`batch_01`), `interest_scaled == interest_raw`.
- O termo-âncora aparece **apenas** com `batch_id = batch_01` (deduplicado dos demais lotes).
- `is_partial = True` indica período mais recente ainda em formação — tratar com cautela.
- `date` está em formato ISO (`YYYY-MM-DD`).
