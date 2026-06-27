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

- **Termo-âncora:** `Bolsonaro` (candidato de alta notoriedade durante toda a
  campanha de 2018; presente em todos os lotes). Usamos o **sobrenome** `Bolsonaro`,
  não o nome completo `Jair Bolsonaro` — ver a ressalva abaixo.
- **Janela:** `2018-01-01 2018-12-31`.
- **Candidatos:**
  Bolsonaro, Lula, Haddad, Ciro Gomes, Geraldo Alckmin, Marina Silva,
  João Amoêdo, Henrique Meirelles, Alvaro Dias, Guilherme Boulos, Cabo Daciolo,
  Vera Lúcia, João Goulart Filho, Eymael.
  Usamos `Haddad` (sobrenome), não `Fernando Haddad` — ver a ressalva sobre termos
  abaixo.

## 2022

- **Termo-âncora:** `Lula` (alta e estável notoriedade ao longo de 2022).
- **Janela:** `2022-01-01 2022-12-31`.
- **Candidatos:**
  Lula, Bolsonaro, Simone Tebet, Ciro Gomes, Felipe d'Avila, Soraya Thronicke,
  Padre Kelmon, Léo Péricles, Sofia Manzano, Vera Lúcia, Eymael.

> ⚠️ **`Bolsonaro` × `Jair Bolsonaro`.** Originalmente 2022/2018 usavam o termo
> `Jair Bolsonaro`. Uma auditoria (ago–out/2022, mesma requisição) mostrou que o nome
> completo tem **~16,7× menos** interesse de busca que o sobrenome (`Jair Bolsonaro` ≈
> 0,9 vs `Bolsonaro` ≈ 15,1 de média). Isso inflava artificialmente o Share de Search
> de Lula (chegava a ~92% × ~8%). Trocando para `Bolsonaro`, o Share de 2022 entre os
> dois principais passou para ~44,5% (Lula) × ~55,5% (Bolsonaro). Detalhes em
> `auditoria_google_trends_importacao.md`.
>
> O mesmo vale para **`Haddad` × `Fernando Haddad`** em 2018: o sobrenome teve
> **~7,7×** mais interesse de busca que o nome completo (`Haddad` ≈ 2,9 vs
> `Fernando Haddad` ≈ 0,4 de média). Por isso 2018 usa `Haddad`. Para auditar
> qualquer termo, use `scripts/audit_term_comparison.py`.

## Eleição atual (`current`)

- **Termo-âncora:** `Lula` (maior notoriedade entre os nomes da corrida atual).
- **Janela:** `today 12-m` (últimos 12 meses, móvel).
- **Candidatos (termo de busca → nome/partido):**

  | Termo de busca       | Candidato / partido               |
  | -------------------- | --------------------------------- |
  | `Lula`               | Luiz Inácio Lula da Silva (PT)    |
  | `Bolsonaro`          | Atenção agregada à família/marca Bolsonaro (não é um candidato) |
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

> **`Bolsonaro` na eleição atual.** Incluímos o sobrenome `Bolsonaro` como sinal de
> **atenção pública agregada** à família/marca — Jair Bolsonaro segue altíssimo em
> buscas mesmo inelegível, e o termo captura também Flávio, Eduardo e Michelle. É ótimo
> para o Dash 1 (Atenção pública). ⚠️ **No Dash 3 (Share of Search), não selecione
> `Bolsonaro` e `Flávio Bolsonaro` juntos**: as buscas por "Flávio Bolsonaro" também
> contêm "Bolsonaro", então somá-los conta a atenção em dobro. Escolha um dos dois
> conforme a leitura desejada (agregado vs. candidato específico).

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
