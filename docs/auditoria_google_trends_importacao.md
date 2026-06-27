# Auditoria da importação Google Trends → Google Sheets → Dashboard

> Auditoria executada em 2026-06-21. Motivo: o dashboard de 2022 exibia **Lula ~92% /
> Jair Bolsonaro ~8%** no Share of Search, comportamento suspeito. As planilhas do
> Google Sheets haviam sido apagadas; esta auditoria refez a importação e investigou a
> causa.

## Diagnóstico (resumo executivo)

- **O Share de 2022 estava, sim, inflado** — mas a causa **não** era duplicação do
  termo-âncora nem erro de fórmula no frontend. A causa era a **escolha do termo de
  busca**: `"Jair Bolsonaro"` (nome completo) em vez de `"Bolsonaro"` (sobrenome).
- O Google Trends casa **strings de busca**. Em uma coleta isolada (mesma requisição,
  mesma escala 0–100, ago–out/2022) a média de interesse foi:
  **Lula 12.6 · Bolsonaro 15.1 · "Jair Bolsonaro" 0.9**. Ou seja, `"Bolsonaro"` teve
  **16,7×** mais interesse que `"Jair Bolsonaro"`.
- Isso reproduz exatamente o número observado: `Lula 12.6 / (12.6 + 0.9) ≈ **93%**` —
  o "92/8" era um artefato do termo, não do pipeline.
- **Correção aplicada:** trocar o termo para `"Bolsonaro"` em 2022 e 2018 (e o
  `anchor_term` de 2018) em `scripts/constants.py`, e **recoletar**. Após a correção, o
  Share de 2022 entre os dois principais ficou **Lula 44,5% / Bolsonaro 55,5%**
  (realista).
- **Mesma correção em 2018 para Haddad:** o termo `"Fernando Haddad"` (nome completo)
  tinha **~7,7×** menos busca que `"Haddad"` (sobrenome). Trocado para `"Haddad"` e
  recoletado.
- **Não houve duplicação** por `election_year+date+term` (0 chaves duplicadas), **nem
  nulos/valores fora de escala** no dataset reimportado. O `interest_scaled` e o
  cálculo de Share of Search (média, não soma) já estavam **corretos**.
- **Onde estava o erro:** na **coleta** (configuração de termos), não no Google Sheets
  e não no frontend.

| Métrica 2022 (Lula vs Bolsonaro) | Antes (`"Jair Bolsonaro"`) | Depois (`"Bolsonaro"`) |
| --- | --- | --- |
| Share Lula | ~92% | 44,5% |
| Share Bolsonaro | ~8% | 55,5% |

---

## 1. Mapa da arquitetura atual

**Atenção:** a arquitetura **mudou** em relação ao que o prompt de auditoria assumia.
O projeto **não usa mais arquivos CSV em disco**. As pastas `dados-brutos/` e
`dados-processados/` estão no `.gitignore` e **não existem** — o pipeline **publica
direto no Google Sheets**.

**Pipeline de coleta (Python, `analise-eleicoes/scripts/`):**

| Etapa | Arquivo | Função principal |
| --- | --- | --- |
| Configuração | `constants.py` | `GOOGLE_TRENDS_ELECTION_GROUPS` (termos, âncora, timeframe por ano) |
| Coleta (extract) | `extractors/google_trends.py` | `build_trends_batches`, `fetch_interest_over_time_batch` (pytrends) |
| Transformação | `transformers/google_trends.py` | `transform_batch_interest_over_time`, `rescale_batches_by_anchor` |
| Carga (Sheets) | `loaders/google_trends.py` + `core/sheets.py` | `save_processed_*`, `write_dataframe_to_tab` (gspread) |
| Orquestração | `pipelines/google_trends.py` | `run_google_trends_pipeline` |

**Abas geradas no Google Sheets:**

- `raw_google_trends_{ano}_batch_{NN}` — lotes brutos (formato largo).
- `proc_google_trends_{ano}_interest_long` — consolidado por ano (formato longo).
- `proc_google_trends_all_elections_interest_long` — **consolidado de todos os anos**
  (esta é a aba consumida pelo frontend).

**Frontend (React + Vite, `analise-eleicoes/frontend/src/`):**

| Responsabilidade | Arquivo |
| --- | --- |
| Lê a aba do Sheets (gviz CSV público) | `services/sheets.ts` (`sheetCsvUrl`, `fetchSheetCsv`, `parseCsv`) |
| Tipa/converte os dados | `services/googleTrends.ts` (`TRENDS_TAB`, `mapRow`) |
| Cache | `hooks/useGoogleTrends.ts` (TanStack Query) |
| Dash 1 — Atenção pública | `components/modules/PublicAttentionModule.tsx` + `charts/AttentionTimelineChart.tsx` |
| Dash 3 — Share of Search | `components/modules/ShareOfSearchModule.tsx` + `charts/ShareOfSearchChart.tsx` |
| Cálculos | `utils/trends.ts` (`filterByYear`, `meanInterest`, `shareOfSearch`, `detectPeaks`) |

O frontend lê a aba via `https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet=...`
(`VITE_GOOGLE_SHEETS_ID` em `frontend/.env`).

---

## 2. Auditoria dos CSVs locais

**Não há CSVs locais.** A "fonte principal" é a aba
`proc_google_trends_all_elections_interest_long` no Google Sheets. O script de
auditoria (`scripts/audit_google_trends_import.py`) lê essa aba **direto do Sheet** via
service account (somente leitura).

**Colunas esperadas — todas presentes (13/13):** `date`, `election_year`, `term`,
`interest_raw`, `interest_scaled`, `geo`, `timeframe`, `source`, `batch_id`,
`anchor_term`, `is_anchor`, `is_partial`, `collected_at`.

**Contagens (dataset reimportado em 2026-06-21):**

- Total: **1973** linhas.
- Por ano: **2018 → 742 · 2022 → 583 · current → 648**.
- Por termo/ano: `scripts/audit_outputs/linhas_por_termo_ano.csv` (53 linhas por termo
  em cada ano = 53 semanas; consistente).

**Nulos e valores fora de escala** (`nulls_and_invalid_values.csv`): **zero** em todas
as checagens — `null_date`, `null_election_year`, `null_term`, `null_interest_raw`,
`null_interest_scaled`, `interest_raw_below_0`, `interest_raw_above_100`,
`interest_scaled_below_0`, `interest_scaled_above_120` = **0**.

---

## 3. Auditoria de duplicatas e termo-âncora

Chave `election_year + date + term`: **0 chaves duplicadas**
(`scripts/audit_outputs/duplicatas_por_termo.csv` está vazio).

- **Top termos duplicados:** nenhum.
- **Duplicatas por ano:** nenhuma.
- **Batches por termo** (`batches_por_termo.csv`): **nenhum** termo aparece em mais de
  um batch no dataset processado.

**Por quê não há duplicação?** O transformer já remove o âncora dos lotes auxiliares
(`transformers/google_trends.py:148-152`): no dataset consolidado o âncora (Lula em
2022, Bolsonaro em 2018) é mantido **apenas a partir do `batch_01`**. Logo, a hipótese
de "Lula contado em vários batches" **não se confirma** — a deduplicação ocorre na
origem.

---

## 4. Auditoria do termo-âncora e uso no dashboard

`scripts/audit_outputs/anchor_usage_by_year.csv`:

| Ano | Âncora configurada | Termos com `is_anchor=true` | Só a âncora certa marcada? | Batches da âncora no processado | Datas com âncora duplicada |
| --- | --- | --- | --- | --- | --- |
| 2018 | Bolsonaro | Bolsonaro | Sim | batch_01 | 0 |
| 2022 | Lula | Lula | Sim | batch_01 | 0 |
| current | Lula | Lula | Sim | batch_01 | 0 |

- Apenas o termo-âncora correto está marcado como `is_anchor`.
- No dataset processado, o âncora aparece **somente no `batch_01`** (uma vez por data).
- **Coluna `use_in_dashboard` não é necessária.** Ela faria sentido se anchors
  auxiliares entrassem no dataset analítico — mas eles são removidos na transformação.
  Criar a coluna seria redundante. (Decisão registrada na seção 12.)

---

## 5. Auditoria da reescala por termo-âncora (`interest_scaled`)

Fórmula (`rescale_batches_by_anchor`):

```
fator = valor_ancora_batch_base(data) / valor_ancora_batch_atual(data)
interest_scaled = interest_raw * fator         # batch_01: fator = 1 (scaled = raw)
```

Validações:

- Reescala feita **por ano** e **por data** ✔.
- **Divisão por zero / âncora ausente** → `interest_scaled` fica **nulo (NaN)**, com
  `interest_raw` preservado ✔ (coberto por `tests/test_google_trends_rescale.py`).
- `interest_raw` sempre preservado ✔.
- Anchors auxiliares removidos após a reescala ✔.

**2022 — raw vs scaled por termo** (`share_2022_atual_vs_deduplicado.csv`): Lula e
Bolsonaro estão no `batch_01`, então `mean_scaled == mean_raw` para os dois
(12.62 e 10.11). Candidatos de batches auxiliares têm pequenas diferenças por causa da
reescala (ex.: Padre Kelmon raw 0.30 → scaled 0.23). Nenhuma anomalia.

---

## 6. Auditoria da sincronização com Google Sheets

O upload é feito por `core/sheets.py::write_dataframe_to_tab` (via `gspread`):

- Uma aba por dataset; `proc_*` (processado) e `raw_*` (bruto) ficam **visivelmente
  separados** por prefixo.
- A aba é **limpa** (`worksheet.clear()`) e o grid é redimensionado antes de escrever —
  sem resíduo de execuções anteriores.
- Cabeçalho escrito corretamente; todos os 13 campos preservados.
- Valores escritos como texto (`value_input_option="RAW"`), `NaN`/`NaT` viram célula
  vazia (não a string `"nan"`).
- **Não há versões timestampadas** de abas; o nome é estável e fixo, então o frontend
  sempre lê a mesma aba.
- **Sem truncamento de nome de aba** (nomes < 100 chars).

**Conferência local × Sheets** (após reimportação): pipeline reportou 1973 linhas
processadas no total; a leitura de auditoria via gspread leu **1973 linhas** na aba
`proc_google_trends_all_elections_interest_long`, com **13 colunas**. Batem.

> Observação: o pipeline reescreve a janela completa a cada execução (o índice do
> Google Trends é renormalizado por janela), então a sincronização é sempre um
> *full refresh* — não incremental.

---

## 7. Auditoria do consumo no frontend

`utils/trends.ts` + `services/googleTrends.ts`:

1. Lê a aba **processada** correta (`proc_google_trends_all_elections_interest_long`) ✔.
2. Usa o **processado**, não o bruto ✔.
3. Filtra `election_year` corretamente (`filterByYear`) ✔.
4. Converte `interest_raw`/`interest_scaled` para número (`parseNumber` /
   `parseNullableNumber`, tratando `''`/`nan`/`none` como nulo) ✔.
5. `is_partial`: **não** era filtrado no Share of Search (corrigido — ver seção 9).
6. `use_in_dashboard`: coluna não existe e não é necessária (seção 4).
7. Deduplicação por `election_year+date+term`: não há duplicatas a remover; além disso o
   `shareOfSearch` agrega por **média por termo**, o que já é idempotente ao número de
   linhas.
8. Usa `interest_scaled` por padrão ✔.
9. Alternância raw/scaled: existia no Dash 1; **adicionada também ao Dash 3** (seção 9).
10. Modo de auditoria por `interest_raw` para candidatos do mesmo batch: agora possível
    no Dash 3 via a alternância adicionada.

---

## 8. Auditoria do Dash 1 — Atenção pública

`PublicAttentionModule.tsx` + `AttentionTimelineChart.tsx`:

- Eixo X = `date`; eixo Y = `interest_scaled` por padrão, com alternância para
  `interest_raw` (`SegmentedControl`) ✔.
- Série = `term`; filtra por `election_year` e por candidatos selecionados ✔.
- Eventos como linhas verticais; tooltip mostra "evento próximo (contexto, não causa)"
  — **sem afirmar causalidade** ✔.
- `is_partial` ignorado na detecção de picos (`detectPeaks`) ✔.

**2022 (Lula × Bolsonaro):** ambos no `batch_01`, então `interest_raw` é diretamente
comparável. Médias no ano: Bolsonaro 12.62 · Lula 10.11. No batch comum, raw e scaled
coincidem — a comparação é direta e legítima.

---

## 9. Auditoria do Dash 3 — Share of Search

Fórmula (`utils/trends.ts::shareOfSearch`), **já correta**:

```
share(candidato) = média_interesse(candidato) / Σ médias dos candidatos selecionados
```

- Usa **média** (não soma) ✔.
- Denominador = soma das médias **apenas dos candidatos selecionados** ✔.
- Filtra por ano, período e termos selecionados ✔.
- Não havia dupla contagem do âncora (dataset sem duplicatas).

**Ajustes aplicados:**
- Adicionada **alternância raw/scaled** (antes `METRIC` era fixo em `interestScaled`),
  permitindo o modo de auditoria por `interest_raw` para candidatos do mesmo batch.
- `shareOfSearch` passa a **ignorar `is_partial`** no escopo do cálculo (afeta o ano
  `current`, cujo último ponto pode estar incompleto).

**Comparação 2022 (Share of Search)** — `share_2022_atual_vs_deduplicado.csv`:

| Termo | Share scaled (todos selecionados) | Share scaled (deduplicado) | Share raw |
| --- | --- | --- | --- |
| Bolsonaro | 52,76% | 52,76% | 52,55% |
| Lula | 42,27% | 42,27% | 42,11% |
| Simone Tebet | 1,89% | 1,89% | 1,89% |
| Ciro Gomes | 1,58% | 1,58% | 1,57% |
| Padre Kelmon | 0,98% | 0,98% | 1,26% |
| demais | < 0,5% | — | — |

- **Atual == deduplicado** (não há duplicatas).
- **Lula vs Bolsonaro apenas (par):** Lula 44,5% / Bolsonaro 55,5% (scaled == raw,
  mesmo batch).
- O denominador inclui **apenas os candidatos selecionados** (decisão de produto).

---

## 10. Auditoria dos termos pesquisados

- 2022 originalmente usava `"Lula"` e **`"Jair Bolsonaro"`**.
- O termo `"Jair Bolsonaro"` **subestima drasticamente** o interesse de busca: o público
  busca `"Bolsonaro"`. Coleta isolada (`term_comparison_bolsonaro.csv`, ago–out/2022,
  mesma requisição):

| Termo | Média | Pico |
| --- | --- | --- |
| Lula | 12,6 | 100 |
| Bolsonaro | 15,11 | 97 |
| **Jair Bolsonaro** | **0,9** | **9** |

- `"Bolsonaro"` = **16,7×** `"Jair Bolsonaro"`. Esse é o gerador do "92/8".
- **Mesmo problema em 2018 com Haddad.** Coleta isolada (`term_comparison_haddad.csv`,
  2018, mesma requisição): `Bolsonaro` 17,3 · `Lula` 9,2 · **`Haddad` 2,9** ·
  **`Fernando Haddad` 0,4**. O sobrenome teve **~7,7×** mais interesse que o nome
  completo — `Fernando Haddad` subestimava fortemente o candidato.
- **Ações tomadas (decisão do usuário):** trocar para `"Bolsonaro"` (2022 e 2018) e
  `"Haddad"` (2018) e recoletar. O script `scripts/audit_term_comparison.py` (somente
  leitura, parametrizável) fica disponível para reauditar qualquer termo sem mexer no
  dataset do dashboard.

---

## 11. Scripts auxiliares de auditoria

Criados (somente leitura, não alteram dados originais):

- **`scripts/audit_google_trends_import.py`** — lê a aba `proc_*` direto do Google
  Sheets e gera, em `scripts/audit_outputs/`:
  `duplicatas_por_termo.csv`, `linhas_por_termo_ano.csv`, `batches_por_termo.csv`,
  `share_2022_atual_vs_deduplicado.csv`, `anchor_usage_by_year.csv`,
  `nulls_and_invalid_values.csv`. Resumo também impresso no terminal.
- **`scripts/audit_term_comparison.py`** — compara strings de busca na mesma requisição
  (mesma escala 0–100) e gera `term_comparison_<name>.csv`. Usado para
  Lula/Bolsonaro/Jair Bolsonaro (`term_comparison_bolsonaro.csv`) e para
  Haddad/Fernando Haddad (`term_comparison_haddad.csv`).
- **`scripts/audit_term_bolsonaro_comparison.py`** — versão específica do caso Bolsonaro
  (mantida por conveniência; `audit_term_comparison.py` a substitui de forma genérica).

Execução (a partir de `scripts/`, com a venv ativa):

```
python audit_google_trends_import.py
python audit_term_comparison.py --name bolsonaro
python audit_term_comparison.py --name haddad \
    --timeframe "2018-01-01 2018-12-31" Bolsonaro Haddad "Fernando Haddad" Lula
```

---

## 12. Correção opcional (NÃO necessária)

O prompt previa `scripts/fix_google_trends_dashboard_dataset.py` + um CSV
`..._dashboard.csv` **apenas se** a auditoria confirmasse duplicação ou uso indevido do
âncora.

**A auditoria descartou ambos:** 0 duplicatas, âncora apenas no `batch_01`. Portanto, o
script corretivo **não foi criado** — não há o que deduplicar e a coluna
`use_in_dashboard` seria redundante. A correção real foi na **origem** (termo de busca +
recoleta), preservando toda a metodologia de reescala existente.

---

## 13. Documentação metodológica

Atualizada em `docs/google_trends_metodologia.md`:

- Exemplo dos lotes de 2022 corrigido para `"Bolsonaro"`.
- Nova seção **"Termo textual × entidade/tópico"** e o **risco `"Jair Bolsonaro"` ×
  `"Bolsonaro"`** (com os números desta auditoria).
- **Checklist antes de usar dados no dashboard**.

Também alinhados: `docs/google_trends_candidatos.md`,
`docs/google_trends_dicionario_dados.md` e `docs/dashboard_google_trends.md`.

---

## 14. Diagnóstico final

- **Os dados estão consistentes?** Sim, após a reimportação (0 duplicatas, 0 nulos,
  0 valores fora de escala).
- **Há duplicação de âncora?** Não — o transformer já deduplica na origem.
- **O Share de 2022 estava inflado?** Sim, mas **por causa do termo** `"Jair Bolsonaro"`,
  não por duplicação nem fórmula.
- **O problema estava no CSV, no Google Sheets ou no frontend?** Em **nenhum** dos três —
  estava na **coleta** (configuração do termo de busca).
- **Correções necessárias:** trocar o termo para `"Bolsonaro"` (feito) + recoletar
  (feito). Ajustes menores de robustez no Dash 3 (toggle raw/scaled, ignorar
  `is_partial`).

---

## 15. Critérios de aceite

| Critério | Status |
| --- | --- |
| Relatório em `docs/auditoria_google_trends_importacao.md` | ✔ (este arquivo) |
| Duplicatas por `election_year+date+term` identificadas/descartadas | ✔ descartadas (0) |
| Confirmar se o âncora inflava o Share | ✔ não inflava (problema era o termo) |
| Comparação do Share de 2022 antes × depois | ✔ 92/8 → 44,5/55,5 |
| Verificação do cálculo no frontend | ✔ correto (média), com melhorias menores |
| Verificação do que vai ao Google Sheets | ✔ 1973 linhas × 13 colunas, full refresh |
| Recomendação raw vs scaled | ✔ scaled por padrão; raw para mesmo batch (toggle) |
| Orientação "Lula" × "Bolsonaro" × "Jair Bolsonaro" | ✔ usar "Bolsonaro" |
| Nenhum dado original sobrescrito sem backup | ✔ (dados regenerados; scripts read-only) |
| Dashboard passa a usar dados corrigidos / justificativa | ✔ aba recoletada com termo correto |
