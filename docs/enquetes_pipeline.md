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

Formato longo, uma linha por candidato por cenário. **Todos os institutos**:
diferente de versões anteriores deste pipeline, a prata **não** filtra por
instituto — mantém toda pesquisa presente no bronze, com `instituto_pesquisa`
preservado por linha. O recorte por instituto (quando necessário) acontece
**dentro de `build_gold()`**, tabela por tabela — ver "Camada Ouro" abaixo.
Essa mudança existe para que a agregação mensal multi-institucional
(`gold_pesquisas_media_mensal_candidato`) tenha acesso a todo o universo de
pesquisas, e não fique limitada às lacunas de um único instituto.

**Escopo do ciclo 2018**: a prata mantém apenas pesquisas do ciclo
`ano_eleicao = 2018` cuja `data_referencia` esteja efetivamente em 2018 — a
pasta `pesquisa-2018` também traz pesquisas hipotéticas pré-corrida de
2015–2017 (e um resultado de 2014), que ficam de fora da prata/ouro
(permanecem íntegras no bronze). Linhas sem `data_referencia` interpretável
não são descartadas por essa regra (já ficam fora de toda tabela ouro pelo
filtro existente de `data_referencia != ""`). Os ciclos 2022 e 2026 não têm
esse desvio (100% das linhas já caem dentro do próprio ano do ciclo). O
bronze permanece completo (todos os institutos e anos). Colunas:

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

Tabelas orientadas ao consumo analítico. Incluem apenas linhas com candidato,
`percentual_numero` não-nulo e `data_referencia` válida (o restante permanece
íntegro na prata). **Quatro das cinco tabelas são restritas ao Datafolha**
(filtro aplicado dentro de `build_gold()`, não mais herdado da prata — ver
acima); a exceção é `gold_pesquisas_media_mensal_candidato`, que é
deliberadamente multi-institucional:

- **`gold_pesquisas_candidato_temporal`** (principal, só Datafolha):
  desempenho de cada candidato ao longo do tempo. Colunas: `ano_eleicao`,
  `data_referencia`, `instituto_pesquisa`, `pesquisa_id`, `cenario_id`,
  `nome_candidato`, `nome_candidato_normalizado`, `partido`,
  `percentual_numero`, `percentual_original`, `tamanho_amostra`,
  `margem_erro`, `fonte_url`, `fonte_website`.
- **`gold_pesquisas_ultima_por_candidato`** (só Datafolha): última pesquisa por
  (`ano_eleicao`, `instituto_pesquisa`, `nome_candidato_normalizado`), pela
  maior `data_referencia`.
- **`gold_pesquisas_media_movel_candidato`** (só Datafolha): média diária por
  candidato (`media_percentual_dia`, média entre cenários da mesma data) e
  **média móvel** de janela **3 datas** (`media_movel`, `NULL` quando há menos
  de 3 datas — nunca inventada). Coluna `janela_media_movel` documenta a regra.
- **`gold_pesquisas_comparativo_candidatos`** (só Datafolha): pivô por cenário
  (`ano_eleicao`, `pesquisa_id`, `cenario_id`, `instituto_pesquisa`,
  `data_referencia`) × candidato normalizado (valor = `percentual_numero`).
- **`gold_pesquisas_media_mensal_candidato`** (**multi-institucional**):
  tabela dedicada a **gráficos temporais** — uma linha por (`ano_eleicao`,
  `nome_candidato_normalizado`, mês), pronta para consumo direto sem
  agregação adicional no frontend. Colunas: `ano_eleicao`, `data_referencia`
  (primeiro dia do mês agregado, ISO, ex. `2026-06-01` — garante ordenação
  cronológica), `mes_referencia` (nome do mês em português),
  `nome_candidato_normalizado`, `percentual_agregado`. O mês é agrupado pelo
  ano-mês **real** derivado de `data_referencia` (não pelo nome de
  `mes_referencia` isolado nem por `ano_eleicao`), para não misturar, por
  exemplo, "Setembro" de anos civis diferentes dentro do mesmo ciclo
  eleitoral (a pasta 2018 também carrega linhas hipotéticas de 2014–2017).
  - **Por que multi-institucional**: restrito só ao Datafolha, o instituto
    tem lacunas de mês reais em todo ciclo (ex. 2018 só cobria 3 dos 10
    meses do próprio ano de 2018). Nenhum instituto isolado cobre 100% dos
    meses em nenhum ciclo, e o instituto mais completo muda de ciclo para
    ciclo — trocar de instituto não elimina as lacunas nem preserva
    comparabilidade entre ciclos. Agregando **todos os institutos** por mês,
    hoje (2026-07-06) os três ciclos ficam com cobertura mensal completa
    dentro da própria janela de coleta (2018: 10/10 meses, 2022: 10/10,
    2026: 6/6 até o mês corrente).
  - **Peso da média**: `percentual_agregado` é a **média ponderada por
    `tamanho_amostra`** (tamanho da amostra da pesquisa, parseado a partir do
    texto bruto — aceita separador de milhar em ponto ou espaço; parseável em
    ~99,6% das linhas de todos os institutos). Quando nenhuma pesquisa do mês
    tem `tamanho_amostra` parseável (placeholder `–`), usa-se **média
    aritmética simples** como *fallback* documentado para aquele mês — o
    peso nunca é inventado.
  - **Trade-off metodológico ("house effect")**: institutos diferentes usam
    metodologias diferentes (amostragem, formulação de pergunta, tratamento
    de indecisos). Misturar institutos numa mesma média ganha cobertura
    mensal completa, mas perde a garantia de que cada ponto do mês vem de uma
    única metodologia consistente — um viés sistemático de um instituto pode
    deslocar a média de um mês em relação a outro que teve mais peso de um
    instituto diferente. As tabelas Datafolha-only acima continuam
    disponíveis para quem precisar de uma série de metodologia única.
  - **Limitação herdada**: pesquisas com múltiplos cenários (`cenario_id`,
    ex. "com fulano" vs. "sem fulano") compartilham o mesmo `tamanho_amostra`
    da pesquisa original, então cada cenário pesa o total da amostra
    independentemente — mesmo efeito que `gold_pesquisas_media_movel_candidato`
    já tem via média simples por cenário; não é uma distorção nova desta
    tabela.

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
- **Escopo Datafolha por tabela**: só `gold_pesquisas_candidato_temporal`,
  `_ultima_por_candidato`, `_media_movel_candidato` e `_comparativo_candidatos`
  são restritas ao Datafolha (filtro aplicado dentro de `build_gold()`). A
  prata e `gold_pesquisas_media_mensal_candidato` cobrem todos os institutos.
- **`nome_candidato_normalizado` entre institutos**: não há reconciliação de
  grafias entre institutos diferentes (o mesmo candidato pode, em tese,
  aparecer com uma grafia ligeiramente diferente em outro instituto e virar
  um "candidato" distinto em `gold_pesquisas_media_mensal_candidato`); a
  normalização (minúsculas, sem acento, espaços colapsados) reduz esse risco
  mas não garante identidade entre fontes.
- **`ano_eleicao` vs ano da linha**: a pasta 2018 contém pesquisas hipotéticas
  de 2015–2017 e o resultado de 2014, além das pesquisas do próprio ano de
  2018. Diferente dos outros ciclos, a prata **descarta** as linhas do ciclo
  2018 cuja `data_referencia` não caia em 2018 (486 de 765 linhas antes do
  filtro) — o restante do pipeline (2022, 2026) não precisa dessa regra
  porque já não tem esse desvio nos dados reais. As linhas descartadas
  continuam íntegras no bronze (`raw_enquetes_2018`).
- **`nome_candidato_normalizado`** cruza anos: `bolsonaro` = Jair (2018/2022 e
  cenários hipotéticos de 2026); `flavio` = Flávio (2026). Não há reconciliação
  de identidade entre anos.
- **Reconciliação Haddad/2018 (só na camada ouro)**: antes de Haddad ser
  confirmado como candidato do PT (após a impugnação de Lula pelo TSE), alguns
  institutos pesquisaram cenários hipotéticos que o citam indiretamente —
  `"Haddad, apoiado por Lula"` e `"algum candidato apoiado por Lula"`. Dentro
  de `build_gold()`, essas duas linhas (só para `ano_eleicao = 2018`) são
  fundidas em `nome_candidato`/`nome_candidato_normalizado = "Haddad"/"haddad"`
  antes de qualquer tabela ouro ser montada, então elas entram no cálculo
  agregado de Haddad em todas as tabelas (incluindo `gold_pesquisas_media_mensal_candidato`)
  em vez de aparecerem como candidatos à parte. A prata (`proc_enquetes_long`)
  preserva os rótulos originais e distintos, para auditoria. `"Lula"` (a
  candidatura real, antes da impugnação) não é afetado por essa fusão.
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

-- Gráfico temporal mensal (pronto para consumo direto, sem agregação no frontend)
SELECT data_referencia, nome_candidato_normalizado, percentual_agregado
FROM gold_pesquisas_media_mensal_candidato
WHERE ano_eleicao = 2026
ORDER BY data_referencia, nome_candidato_normalizado;
```
