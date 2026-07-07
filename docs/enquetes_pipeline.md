# Pipeline de pesquisas eleitorais (enquetes)

Ingestão e normalização das pesquisas presidenciais extraídas da Wikipedia
(2018, 2022 e 2026) para a arquitetura medalhão do projeto (Google Sheets:
bronze / prata / ouro). Segue o mesmo padrão das demais fontes
(`google_trends`, `tse`, `polymarket`): `extractors → transformers → loaders`,
orquestrado em `pipelines/enquetes.py` e registrado em `scripts/main.py`.

## Origem dos dados

Cada eleição tem uma pasta com o wikitext bruto e a extração estruturada:

```
votometria/pesquisa-2018/  2018.txt  pesquisas_presidenciais_2018.csv  .xlsx
votometria/pesquisa-2022/  2022.txt  pesquisas_presidenciais_2022.csv  .xlsx
votometria/pesquisa-2026/  2026.txt  pesquisas_presidenciais_2026.csv  .xlsx
```

O pipeline **lê o CSV** de cada pasta (uma linha por candidato por pesquisa/
cenário, 22 colunas idênticas entre os anos). O `.txt` (wikitext) é a fonte
última e permanece rastreável pela coluna `linha_original_wikitext`, preservada
na bronze. **Os arquivos brutos nunca são alterados.**

## Camada Bronze — `raw_enquetes_<ano>`

Cópia auditável do CSV, com transformação mínima. Preserva todas as 22 colunas
originais e acrescenta linhagem:

`ano_eleicao`, `source_folder`, `source_file`, `ingestion_timestamp`,
`raw_row_number`, `hash_linha` (+ colunas originais).

- `hash_linha` = SHA-1 dos valores originais da linha (+ ano + arquivo). Depende
  só do dado, **não** do `ingestion_timestamp` → estável entre execuções.
- Idempotente: a aba é limpa e reescrita por completo a cada execução
  (`write_dataframe_to_tab`, `value_input_option="RAW"`).

## Camada Prata — `proc_enquetes_long`

Formato longo, uma linha por candidato por cenário. **Escopo Datafolha**: a
prata mantém apenas pesquisas cujo `instituto_pesquisa` contém "Datafolha"
(case-insensitive) — inclui `Datafolha`, `Globo/Datafolha`, `Folha/Datafolha`,
`Globo e Folha/Datafolha`. O bronze permanece completo (todos os institutos).
Colunas:

`pesquisa_id`, `cenario_id`, `ano_eleicao`, `mes_referencia`,
`instituto_pesquisa`, `contratante_pesquisa`, `data_referencia`,
`tamanho_amostra`, `margem_erro`, `nome_candidato`,
`nome_candidato_normalizado`, `partido`, `percentual_original`,
`percentual_numero`, `outros_original`, `outros_numero`,
`indecisos_absentos_original`, `indecisos_absentos_numero`, `fonte_titulo`,
`fonte_url`, `fonte_website`, `fonte_data_publicacao`, `fonte_data_acesso`,
`hash_linha_bronze`, `observacoes_normalizacao`.

Normalizações:

- **Percentuais**: `42%`→`42.0`, `38,3%`→`38.3`, `não pontuou`→`0.0` (original
  preservado), `N/A`/`{{N/A}}`/vazio/`-`→`NULL`. Ausência nunca vira zero.
- **Datas**: `data_referencia` (ISO) = data de fim da pesquisa quando
  interpretável, senão a de início; o ano vem da própria linha (coluna `ano`) ou
  da pasta. Data de início só com o dia (ex. `28`) herda mês/ano da data de fim
  (registrado em observação). O que não for seguro fica `NULL` com nota. As datas
  brutas de início/fim são usadas internamente para compor `data_referencia` e o
  `pesquisa_id`, mas não são materializadas como colunas.
- **Mês (2022)**: as linhas de 2022 trazem `mes` como trimestre
  (`1º/2º/3º trimestre`); `mes_referencia` é reescrito para o nome do mês
  correspondente à data de fim da pesquisa (ex. `29 Set` → `Setembro`),
  padronizando com os demais anos. A troca é registrada em
  `observacoes_normalizacao`.
- **Candidato**: `nome_candidato_normalizado` = minúsculas, sem acento, espaços
  colapsados. Candidatos distintos nunca são unidos; apelidos não viram nomes
  completos.
- **Partido**: preservado como informado (só caixa/espaços normalizados).
- **Instituto/Contratante**: `instituto_pesquisa` (limpo) e
  `contratante_pesquisa` (texto original) preservados.
- **Chaves determinísticas**:
  - `pesquisa_id` = `psq_` + SHA-1(`ano_eleicao|instituto|data_inicio|data_fim|tamanho_amostra|fonte_url`)[:12].
  - `cenario_id` = `<pesquisa_id>_cenario_N`.
- `hash_linha_bronze` liga cada linha da prata à sua origem na bronze.

## Camada Ouro

Tabelas orientadas ao consumo analítico (também restritas ao Datafolha, por
derivarem da prata). Incluem apenas linhas com candidato, `percentual_numero`
não-nulo e `data_referencia` válida (o restante permanece íntegro na prata).

- **`gold_pesquisas_candidato_temporal`** (principal): desempenho de cada
  candidato ao longo do tempo. Colunas: `ano_eleicao`, `data_referencia`,
  `instituto_pesquisa`, `pesquisa_id`, `cenario_id`, `nome_candidato`,
  `nome_candidato_normalizado`, `partido`, `percentual_numero`,
  `percentual_original`, `tamanho_amostra`, `margem_erro`, `fonte_url`,
  `fonte_website`.
- **`gold_pesquisas_ultima_por_candidato`**: última pesquisa por
  (`ano_eleicao`, `instituto_pesquisa`, `nome_candidato_normalizado`), pela
  maior `data_referencia`.
- **`gold_pesquisas_media_movel_candidato`**: média diária por candidato
  (`media_percentual_dia`, média entre institutos/cenários da mesma data) e
  **média móvel** de janela **3 datas** (`media_movel`, `NULL` quando há menos
  de 3 datas — nunca inventada). Coluna `janela_media_movel` documenta a regra.
- **`gold_pesquisas_comparativo_candidatos`**: pivô por cenário
  (`ano_eleicao`, `pesquisa_id`, `cenario_id`, `instituto_pesquisa`,
  `data_referencia`) × candidato normalizado (valor = `percentual_numero`).

## Como executar

Requer `.env` com `SHEET_ID_bronze/prata/ouro` + `GOOGLE_SERVICE_ACCOUNT_FILE`
(service account Editor nas três planilhas).

```bash
cd votometria/scripts
../.venv/bin/python main.py          # roda todas as fontes, incluindo enquetes
# ou apenas enquetes:
../.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from pipelines.enquetes import run_enquetes_pipeline; run_enquetes_pipeline()"
```

Rodar duas vezes **não duplica** dados (full-refresh + ids determinísticos).

## Como validar

As validações rodam junto com o pipeline e são publicadas na aba
`validacao_enquetes` (camada prata), além de impressas no log. Cobrem:
arquivos por ano, linhas na bronze, pesquisas/cenários distintos, candidatos
por ano, percentuais fora de 0–100, pesquisas sem instituto/data/`fonte_url`,
candidatos sem partido, duplicidades (`cenario_id`+candidato), e a linhagem
ouro→prata→bronze (registros órfãos).

Testes unitários (sem rede):

```bash
../.venv/bin/python -m pytest tests/test_enquetes_transformer.py -q
```

## Limitações conhecidas

- **`turno`** e **`tipo_cenario`** não existem no dado bruto e foram removidas
  da prata/ouro (eram sempre `NULL`). `source_file`/`source_folder` (redundantes
  com a lineage do bronze) e `data_inicio_pesquisa`/`data_fim_pesquisa` (não
  usadas na ouro) também saíram da prata.
- **Escopo Datafolha**: a prata e a ouro cobrem apenas pesquisas do instituto
  Datafolha; outros institutos ficam disponíveis só no bronze.
- **`ano_eleicao` vs ano da linha**: a pasta 2018 contém pesquisas hipotéticas
  de 2015–2017 e o resultado de 2014; `ano_eleicao=2018` (ciclo da tabela),
  mas `data_referencia` reflete a data real de cada linha.
- **Sem `fonte_url`** em 2 pesquisas (linhas de evento/resultado, ex. "Eleições
  de 2014", "Grupo 6Sigma") e **sem data** em 1 — sinalizadas, não descartadas.
- **`nome_candidato_normalizado`** cruza anos: `bolsonaro` = Jair (2018/2022 e
  cenários hipotéticos de 2026); `flavio` = Flávio (2026). Não há reconciliação
  de identidade entre anos.
- Como a fonte é Google Sheets, as queries SQL abaixo pressupõem carregar a aba
  em um motor SQL (DuckDB/Postgres) ou usar o equivalente em pandas.

## Exemplos de consultas

```sql
-- Evolução de um candidato
SELECT data_referencia, instituto_pesquisa, nome_candidato_normalizado, percentual_numero
FROM gold_pesquisas_candidato_temporal
WHERE ano_eleicao = 2026 AND nome_candidato_normalizado = 'lula'
ORDER BY data_referencia;

-- Comparação entre candidatos
SELECT data_referencia, instituto_pesquisa, nome_candidato_normalizado, percentual_numero
FROM gold_pesquisas_candidato_temporal
WHERE ano_eleicao = 2026 AND nome_candidato_normalizado IN ('lula','flavio')
ORDER BY data_referencia, nome_candidato_normalizado;

-- Desempenho por instituto
SELECT instituto_pesquisa, nome_candidato_normalizado, AVG(percentual_numero) AS media_percentual
FROM gold_pesquisas_candidato_temporal
WHERE ano_eleicao = 2026
GROUP BY instituto_pesquisa, nome_candidato_normalizado
ORDER BY instituto_pesquisa, media_percentual DESC;
```
