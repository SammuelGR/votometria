# Integração com o Google Sheets

O pipeline de dados publica os datasets **direto no Google Sheets** — uma aba por
dataset, sem CSV em disco e sem banco de dados. A planilha é o local oficial dos
dados, de onde um dashboard React pode consumir cada aba publicada como CSV.

A mecânica de autenticação e escrita fica em `scripts/core/sheets.py`
(`get_spreadsheet()` + `write_dataframe_to_tab()`), usada pelo pipeline em
`scripts/loaders/google_trends.py` e acionada por `python scripts/main.py`.

## Arquitetura medalhão (bronze / prata / ouro)

Os dados são organizados em **três planilhas separadas**, uma por camada,
configuradas no `.env` (`SHEET_ID_bronze`, `SHEET_ID_prata`, `SHEET_ID_ouro`).
A mesma service account (`GOOGLE_SERVICE_ACCOUNT_FILE`) precisa ter permissão de
**Editor** nas três.

| Camada | Estágio do pipeline | `.env`            | Conteúdo                                              |
| ------ | ------------------- | ----------------- | ----------------------------------------------------- |
| Bronze | extractors          | `SHEET_ID_bronze` | dados brutos (batches Trends, presidência TSE, mercados/preços Polymarket) |
| Prata  | transformers        | `SHEET_ID_prata`  | dados limpos/normalizados (Trends long rescalado, presidência por turno, probabilidades long) |
| Ouro   | loaders             | `SHEET_ID_ouro`   | dados finais consolidados — **consumidos pelo frontend e pela API** |

Abas por fonte (exemplos):

| Fonte         | Bronze                              | Prata                                        | Ouro                                             |
| ------------- | ----------------------------------- | -------------------------------------------- | ------------------------------------------------ |
| Google Trends | `raw_google_trends_<ano>_batch_NN`  | `proc_google_trends_<ano>_interest_long`     | `proc_google_trends_all_elections_interest_long` |
| TSE           | `raw_tse_presidency_<ano>`          | `proc_tse_<ano>_presidency_tN`               | `proc_tse_<ano>_votes_tN`, `..._state_dist_tN`, `..._comparison` |
| Polymarket    | `raw_polymarket_markets`, `raw_polymarket_price_history` | `proc_polymarket_probabilities_long` | `proc_polymarket_probabilities` |

O prefixo `raw_`/`proc_` das abas é mantido dentro de cada planilha.

A cada execução a aba correspondente é **limpa** e reescrita por completo
(cabeçalho + linhas), usando `value_input_option="RAW"` (os valores entram na
planilha exatamente como vêm do pipeline, sem conversão automática de
números/datas).

## Pré-requisitos

- Python com as dependências de `scripts/requirements.txt` instaladas
  (inclui `gspread`, `google-auth`, `pandas`, `python-dotenv`):

  ```bash
  pip install -r scripts/requirements.txt
  ```

## 1. Criar a service account

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/) e
   selecione (ou crie) um projeto.
2. Em **APIs e serviços → Biblioteca**, habilite a **Google Sheets API**.
3. Em **APIs e serviços → Credenciais → Criar credenciais → Conta de serviço**,
   crie a conta de serviço.
4. Na conta de serviço criada, aba **Chaves → Adicionar chave → Criar nova
   chave → JSON**. O download do arquivo `.json` é a credencial.
5. Guarde o JSON **fora do controle de versão**, por exemplo em
   `secrets/service_account.json` (a pasta `secrets/` está no `.gitignore`).

> O JSON contém uma chave privada. Nunca faça commit desse arquivo nem cole o
> conteúdo dele em chats, issues ou logs. Se vazar, **revogue a chave** no
> console e gere outra.

## 2. Compartilhar a planilha com o `client_email`

O JSON da service account contém um campo `client_email`, algo como
`minha-conta@meu-projeto.iam.gserviceaccount.com`.

Abra a planilha de destino no navegador, clique em **Compartilhar** e adicione
esse `client_email` com permissão de **Editor**. Sem esse passo o script recebe
um erro de permissão (`PermissionError` / `403`) ao tentar escrever.

## 3. Configurar o `.env`

Crie um arquivo `.env` na raiz do projeto (veja `.env.example`) com **uma ID por
camada**:

```dotenv
SHEET_ID_bronze=<id da planilha bronze>
SHEET_ID_prata=<id da planilha prata>
SHEET_ID_ouro=<id da planilha ouro>
GOOGLE_SERVICE_ACCOUNT_FILE=secrets/service_account.json
```

- `SHEET_ID_*`: o ID de cada planilha — o trecho longo da URL entre `/d/` e
  `/edit` (`https://docs.google.com/spreadsheets/d/<ID>/edit`).
- `GOOGLE_SERVICE_ACCOUNT_FILE`: caminho do JSON da chave (Editor nas três
  planilhas). Caminhos relativos são resolvidos a partir da raiz do projeto.
- Compartilhe as **três** planilhas com o `client_email` da service account.

O `.env` também está no `.gitignore` e não deve ser commitado.

## 4. Rodar o pipeline

A partir da pasta `scripts/`:

```bash
cd scripts
python main.py
```

O Google Trends roda junto dos demais pipelines e publica as abas `raw_*` e
`proc_*`. Saída esperada (exemplo):

```
-> 2018: 13 terms | 3 batches | 689 processed rows -> tab 'proc_google_trends_2018_interest_long'
...
-> Consolidated all elections: 1908 rows -> tab 'proc_google_trends_all_elections_interest_long'
```

### Falhas com mensagem clara

A abertura da planilha **falha cedo e com mensagem explicativa** quando:

- não há arquivo `.env` na raiz;
- `GOOGLE_SHEETS_ID` ou `GOOGLE_SERVICE_ACCOUNT_FILE` não estão definidos;
- o arquivo JSON da service account não existe no caminho informado.

Como o Google Trends é isolado em `main.py`, uma falha de configuração do Sheets
**não interrompe** os demais pipelines.

## 5. Consumir a camada ouro no frontend

O frontend consome **sempre a camada ouro**:

- **Google Trends**: lido direto da planilha ouro. Defina
  `VITE_GOOGLE_SHEETS_ID` (em `frontend/.env`) com o mesmo valor de
  `SHEET_ID_ouro`. A aba lida é `proc_google_trends_all_elections_interest_long`.
- **Market expectations (Polymarket)**: servido pela **API do backend**
  (`VITE_API_BASE_URL`), que agora lê a aba `proc_polymarket_probabilities` da
  planilha ouro (via gviz CSV, com cache de 5 min) em vez do PostgreSQL. O
  contrato da API é o mesmo, então o frontend não muda.

Para o dashboard/ backend lerem sem credenciais, **publique** a planilha ouro
(uma vez): no Google Sheets, **Arquivo → Compartilhar → Publicar na web**, ou
deixe-a acessível por link. Cada aba é exportada como CSV via:

```
https://docs.google.com/spreadsheets/d/<GOOGLE_SHEETS_ID>/gviz/tq?tqx=out:csv&sheet=<NOME_DA_ABA>
```

Exemplo no front-end (substitua o ID e o nome da aba conforme necessário):

```ts
const SHEET_ID = "175BnX6bAgzDqOECpcXhxiAtship5FQ0OS5-A8elnkY0";

function sheetCsvUrl(tabName: string): string {
  const params = new URLSearchParams({ tqx: "out:csv", sheet: tabName });
  return `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?${params}`;
}

async function fetchSheetCsv(tabName: string): Promise<string> {
  const response = await fetch(sheetCsvUrl(tabName));
  if (!response.ok) {
    throw new Error(`Falha ao buscar a aba '${tabName}': ${response.status}`);
  }
  return response.text();
}

// Uso (note o prefixo proc_ da aba):
const csv = await fetchSheetCsv("proc_google_trends_all_elections_interest_long");
// Faça o parse com PapaParse, d3-dsv, etc.
```

> O endpoint `gviz/tq?tqx=out:csv` exige que a planilha esteja acessível por
> link / publicada na web; caso contrário a requisição do navegador é bloqueada
> por falta de autenticação.
