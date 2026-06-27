# Dashboards de Google Trends (Atenção Pública e Share of Search)

Este documento descreve os dois dashboards baseados em Google Trends no frontend:
**Atenção Pública** (série temporal) e **Share of Search** (distribuição). Eles aparecem
em `/current-election` (ano `current`) e em `/historical-elections` (2018 e 2022),
respeitando a divisão de rotas definida em `docs/frontend.md`.

## Fonte de dados

Os dados vêm da aba consolidada `proc_google_trends_all_elections_interest_long` do
Google Sheets, lida pelo navegador via export CSV público
(`gviz/tq?tqx=out:csv`). É preciso:

- a planilha **publicada / compartilhada por link**;
- `VITE_GOOGLE_SHEETS_ID` definido em `frontend/.env` (veja `frontend/.env.example`).

O fetch e o parse ficam em `src/services/sheets.ts` e `src/services/googleTrends.ts`;
o cache em `src/fetchers/hooks/useGoogleTrends.ts` (TanStack Query).

## `interest_raw` × `interest_scaled`

- **`interest_raw`**: índice 0–100 original do Google Trends **dentro de um lote**.
  Comparável apenas no mesmo lote e data.
- **`interest_scaled`**: valor reescalado pelo **termo-âncora** do ano, tornando os
  candidatos **do mesmo ano** aproximadamente comparáveis mesmo vindos de lotes
  diferentes. É **nulo** quando o âncora vale 0 na data (não inventamos valor).

O índice é **relativo e reescalado**. **Nunca** comparar valores entre anos diferentes —
são janelas temporais independentes, com escalas não equivalentes. Os dashboards usam
`interest_scaled` por padrão e oferecem alternância para `interest_raw`.

## Eventos são hipóteses, não causalidade

A base de eventos vive em `src/data/electionEvents.ts` (módulo tipado, versionado).
Os eventos aparecem como **linhas verticais** no gráfico de Atenção Pública e, quando
um pico está próximo de um evento (janela de ±7 dias), o tooltip mostra o evento como
**contexto** — com o texto "evento próximo (contexto, não causa)". Em nenhum momento
afirmamos que o evento causou o pico; é uma **hipótese explicativa** a ser verificada.

### Detecção de picos

Um ponto é considerado pico quando seu valor é pelo menos **20% maior** que o ponto
anterior disponível **e** maior que o próximo (`src/utils/trends.ts`, `detectPeaks`).
Pontos `is_partial` (período ainda em formação) são **ignorados** na detecção e marcados
de forma distinta no gráfico.

### Como atualizar os eventos

Edite `ELECTION_EVENTS` em `src/data/electionEvents.ts`. Cada evento tem:
`date`, `electionYear` (`'2018' | '2022' | 'current'`), `title`, `type`,
`relatedTerms`, `description`, `impact`. Mantenha as datas no formato `YYYY-MM-DD`.
Os eventos de 2026 são pré-campanha (ver `EVENTS_DISCLAIMER_2026`) e devem ser
revisados conforme a corrida evolui.

## Cálculo do Share of Search

Para o período selecionado:

```
share(candidato) = média de interesse do candidato / soma das médias de todos os selecionados
```

Usamos **média** (não soma) porque o índice já é relativo e os períodos podem ter
tamanhos diferentes (`src/utils/trends.ts`, `shareOfSearch`). O período é um filtro
próprio do módulo (decisão de produto que diverge de `docs/frontend-modules.md:57`,
que sugere derivar o intervalo do Brush do gráfico). O cálculo **ignora pontos
`is_partial`** (relevante só para o ano `current`).

O Dash 3 usa `interest_scaled` por padrão e oferece **alternância para `interest_raw`**
(igual ao Dash 1). O modo `interest_raw` serve de **auditoria** quando os candidatos
selecionados estão no **mesmo lote** (ex.: Lula e Bolsonaro em 2022, ambos no
`batch_01`): nesse caso `raw` e `scaled` coincidem e a comparação é direta.

> **Atenção ao termo de busca.** O Share depende fortemente da string coletada. Usar
> `Jair Bolsonaro` (nome completo) em vez de `Bolsonaro` inflava o Share de Lula para
> ~92%. Ver `docs/auditoria_google_trends_importacao.md` e
> `docs/google_trends_metodologia.md`.

### KPI de concentração

`Concentração Top 2` = soma dos dois maiores shares. Classificação:

- **≥ 70%**: alta concentração;
- **50%–69%**: concentração moderada;
- **< 50%**: atenção distribuída.

## Limitações metodológicas

- Google Trends é **índice relativo**, não volume absoluto de buscas.
- A reescala por âncora aproxima candidatos do **mesmo ano**; comparações entre anos
  não são válidas.
- Termos de busca casam strings (ex.: usamos `Lula`, não "Luiz Inácio Lula da Silva").
- Pontos `is_partial` representam períodos incompletos e podem mudar em coletas futuras.
