# Google Trends — Candidatos e Termos-Âncora

Lista dos candidatos coletados por ano eleitoral e o termo-âncora de cada ano. A
configuração canônica fica em `GOOGLE_TRENDS_ELECTION_GROUPS` em
`scripts/constants.py`; este documento explica e justifica as escolhas.

> Os termos são strings de busca enviadas ao Google Trends, não entidades oficiais.
> Pequenas variações de grafia mudam os resultados.

## Critério de escolha do termo-âncora

O termo-âncora aparece em **todos os lotes** de um ano e é usado para reescalar os
lotes a uma base comparável. Um bom âncora tem **interesse de busca alto e estável ao
longo de toda a janela**, reduzindo a chance de valores zero (que impedem a reescala —
ver `google_trends_metodologia.md`). Por isso escolhemos um candidato de **alta
notoriedade** em cada ano.

## 2018

- **Termo-âncora:** `Jair Bolsonaro` (candidato de alta notoriedade durante toda a
  campanha de 2018; presente em todos os lotes).
- **Janela:** `2018-01-01 2018-12-31`.
- **Candidatos:**
  Jair Bolsonaro, Fernando Haddad, Ciro Gomes, Geraldo Alckmin, Marina Silva,
  João Amoêdo, Henrique Meirelles, Alvaro Dias, Guilherme Boulos, Cabo Daciolo,
  Vera Lúcia, João Goulart Filho, Eymael.

## 2022

- **Termo-âncora:** `Lula` (alta e estável notoriedade ao longo de 2022).
- **Janela:** `2022-01-01 2022-12-31`.
- **Candidatos:**
  Lula, Jair Bolsonaro, Simone Tebet, Ciro Gomes, Felipe d'Avila, Soraya Thronicke,
  Padre Kelmon, Léo Péricles, Sofia Manzano, Vera Lúcia, Eymael.

## Eleição atual (`current`)

- **Termo-âncora:** `Lula` (maior notoriedade entre os nomes da corrida atual).
- **Janela:** `today 12-m` (últimos 12 meses, móvel).
- **Candidatos (termo de busca → nome/partido):**

  | Termo de busca       | Candidato / partido               |
  | -------------------- | --------------------------------- |
  | `Lula`               | Luiz Inácio Lula da Silva (PT)    |
  | `Aldo Rebelo`        | Aldo Rebelo (DC)                  |
  | `Augusto Cury`       | Augusto Cury (Avante)             |
  | `Cabo Daciolo`       | Cabo Daciolo (Mobiliza)           |
  | `Edmilson Costa`     | Edmilson Costa (PCB)              |
  | `Flávio Bolsonaro`   | Flávio Bolsonaro (PL)             |
  | `Hertz Dias`         | Hertz Dias (PSTU)                 |
  | `Renan Santos`       | Renan Santos (Missão)             |
  | `Romeu Zema`         | Romeu Zema (Novo)                 |
  | `Ronaldo Caiado`     | Ronaldo Caiado (PSD)              |
  | `Rui Costa Pimenta`  | Rui Costa Pimenta (PCO)           |
  | `Samara Martins`     | Samara Martins (UP)               |

> **Decisão de termo de busca:** os sufixos de partido foram **omitidos** de
> propósito — o Google Trends casa strings de busca, e "Nome (Partido)" praticamente
> não é pesquisado, o que zeraria a série. Para Luiz Inácio Lula da Silva usamos
> `Lula`, que também é o termo-âncora.

> ⚠️ A lista de candidatos da eleição atual **não é definitiva** e deve ser editada
> conforme a corrida evolui. Se a esvaziar, o pipeline ignora o grupo `current` sem
> erro. Ao editá-la, **mantenha o termo-âncora na própria lista** e confirme que ele
> tem interesse alto e estável na janela.

## Observações sobre comparabilidade

- A reescala torna os candidatos **do mesmo ano** aproximadamente comparáveis.
- **Não** compare valores entre anos diferentes sem deixar claro que são janelas
  temporais independentes (escalas não equivalentes).
- Candidatos que aparecem em mais de um ano (ex.: Ciro Gomes, Vera Lúcia, Eymael,
  Jair Bolsonaro, Lula) têm uma série por ano, cada uma na escala do seu próprio ano.
