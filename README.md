# Votometria

Projeto da disciplina de Análise de Dados. O objetivo do Votometria é construir um painel analítico sobre eleições presidenciais brasileiras.

A arquitetura do projeto segue um modelo de monorepo estruturado para processamento e visualização:

- `/scripts`: Pipelines de extração, transformação e carga (ETL) em Python.
- `/backend`: API Python para servir dados analíticos processados ao frontend.
- `/frontend`: Visualização interativa desenvolvida em React + TypeScript.

---

## Configuração de Ambiente

Crie uma cópia do arquivo `.env.example` na raiz do projeto e renomeie-a para `.env`.

Variáveis usadas atualmente:

- `DATABASE_URL`: URL de conexão PostgreSQL. Preencha com a connection string do banco que será usado pelo projeto.
- `BACKEND_CORS_ORIGINS`: origens autorizadas a acessar o backend pelo browser. Preencha com URLs separadas por vírgula, por exemplo `http://localhost:5173,https://votometria.vercel.app`.

---

## Frontend

O frontend usa Vite, React, TypeScript e Tailwind CSS.

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

Os dados processados são persistidos no PostgreSQL para consumo posterior pelo backend e pelo frontend.

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

### Executando os Testes dos Scripts

Com o ambiente virtual ativo e dentro da pasta `scripts`, execute:

```bash
python -m pytest tests
```
