# Integração com o Google Sheets

O pipeline de dados publica os datasets **direto no Google Sheets** — uma aba por
dataset, sem CSV em disco e sem banco de dados. A planilha é o local oficial dos
dados, de onde um dashboard React pode consumir cada aba publicada como CSV.

A mecânica de autenticação e escrita fica em `scripts/core/sheets.py`
(`get_spreadsheet()` + `write_dataframe_to_tab()`), usada pelo pipeline em
`scripts/loaders/google_trends.py` e acionada por `python scripts/main.py`.

## Separação por camada (prefixos das abas)

As abas são prefixadas para manter dados brutos e processados visivelmente
separados:

| Camada                | Prefixo  | Exemplos de aba                                      |
| --------------------- | -------- | ---------------------------------------------------- |
| Brutos (batches)      | `raw_`   | `raw_google_trends_2018_batch_01`                    |
| Processados (long)    | `proc_`  | `proc_google_trends_2022_interest_long`              |
| Consolidado           | `proc_`  | `proc_google_trends_all_elections_interest_long`     |

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

Crie um arquivo `.env` na raiz do projeto (veja `.env.example`) com:

```dotenv
GOOGLE_SHEETS_ID=175BnX6bAgzDqOECpcXhxiAtship5FQ0OS5-A8elnkY0
GOOGLE_SERVICE_ACCOUNT_FILE=secrets/service_account.json
```

- `GOOGLE_SHEETS_ID`: o ID da planilha — o trecho longo da URL entre `/d/` e
  `/edit` (`https://docs.google.com/spreadsheets/d/<ID>/edit`).
- `GOOGLE_SERVICE_ACCOUNT_FILE`: caminho do JSON da chave. Caminhos relativos
  são resolvidos a partir da raiz do projeto.

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

## 5. Consumir uma aba publicada como CSV no React

Para o dashboard ler os dados sem credenciais, **publique** a aba (uma vez por
planilha): no Google Sheets, **Arquivo → Compartilhar → Publicar na web**, ou
deixe a planilha acessível por link. Cada aba pode ser exportada como CSV via:

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
