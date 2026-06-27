# Votometria

Projeto da disciplina de Análise de Dados. O objetivo do Votometria é construir um painel analítico sobre eleições presidenciais brasileiras.

A arquitetura do projeto segue um modelo de monorepo estruturado para processamento e visualização:

- `/scripts`: Pipelines de extração, transformação e carga (ETL) em Python.
- `/backend`: API Python para servir dados analíticos processados ao frontend.
- `/frontend`: Visualização interativa desenvolvida em React + TypeScript.

---

## Configuração de Ambiente

Crie uma cópia do arquivo `.env.example` na raiz do projeto e renomeie-a para `.env`.

Variáveis de ambiente:

- `DATABASE_URL`: URL de conexão PostgreSQL. Preencha com a connection string do banco que será usado pelo projeto.
- `BACKEND_CORS_ORIGINS`: origens autorizadas a acessar o backend pelo browser. Preencha com URLs separadas por vírgula, por exemplo `http://localhost:5173,https://votometria.vercel.app`.

O frontend possui um arquivo de ambiente próprio em `/frontend`.

Crie uma cópia de `frontend/.env.example` como `frontend/.env`.

Variável de ambiente do frontend:

- `VITE_API_BASE_URL`: URL base da API backend, incluindo o prefixo `/api`.

---

## Frontend

O frontend usa Vite, React, TypeScript, Tailwind CSS, TanStack Query e Recharts.

Para instalar as dependências:

```bash
cd frontend
npm install
```

Para executar em desenvolvimento:

```bash
npm run dev
```

Para validar o módulo:

```bash
npm run format:check
npm run lint
npm run build
```

Mais detalhes estão em `frontend/README.md` e `docs/frontend.md`.

---

## Backend

O backend usa FastAPI e lê os dados processados do PostgreSQL.

Para instalar as dependências:

```bash
cd backend
python -m venv .venv
```

Ative o ambiente virtual conforme o seu terminal:

- **Windows (Git Bash)**: `source .venv/Scripts/activate`
- **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
- **Windows (CMD)**: `.venv\Scripts\activate`
- **Linux/macOS**: `source .venv/bin/activate`

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Para executar em desenvolvimento:

```bash
uvicorn app.main:app --reload
```

Para executar os testes unitários:

```bash
python -m pytest tests
```

Mais detalhes estão em `backend/README.md` e `docs/backend.md`.

---

## Scripts

Os scripts concentram os pipelines de extração, transformação e carga (ETL) do projeto.

Os pipelines podem persistir dados no PostgreSQL ou gerar arquivos locais, de acordo com a natureza de cada integração.

### Pré-requisitos

- Python 3.8 ou superior
- Pip

### Instalação e Configuração

1. **Criar e ativar o ambiente virtual (venv)**:

   ```bash
   cd scripts
   python -m venv .venv
   ```

   Ative o ambiente virtual conforme o seu terminal:
   - **Windows (Git Bash)**: `source .venv/Scripts/activate`
   - **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
   - **Windows (CMD)**: `.venv\Scripts\activate`
   - **Linux/macOS**: `source .venv/bin/activate`

2. **Instalar as dependências**:

   ```bash
   python -m pip install -r requirements.txt
   ```

### Executando os pipelines

Com o ambiente virtual ativo e dentro da pasta `scripts`, execute:

```bash
python main.py
```

Mais detalhes sobre integrações específicas estão em `docs/polymarket-integration.md` e `docs/tse-integration.md`.

### Executando os Testes dos Scripts

Com o ambiente virtual ativo e dentro da pasta `scripts`, execute:

```bash
python -m pytest tests
```

---

## Ingestão de Dados do Google Trends

O pipeline do Google Trends coleta o interesse de busca dos candidatos e publica
os dados **direto no Google Sheets** (abas `raw_*` e `proc_*`), sem CSV em disco e
sem banco de dados. Roda junto do `python main.py` (uma falha aqui não interrompe
os demais pipelines).

Requer, no `.env`, além do `DATABASE_URL`:

- `GOOGLE_SHEETS_ID`: ID da planilha de destino.
- `GOOGLE_SERVICE_ACCOUNT_FILE`: caminho do JSON da service account.

Passo a passo de credenciais, configuração e consumo pelo frontend em
`docs/google_sheets_sync.md`.

## Deploy

| Módulo   | Host   | URL                             |
| -------- | ------ | ------------------------------- |
| Frontend | Vercel | https://votometria.vercel.app   |
| Backend  | Render | https://votometria.onrender.com |
