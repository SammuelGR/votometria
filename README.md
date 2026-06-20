# Votometria

Projeto da disciplina de Análise de Dados. O objetivo do Votometria é construir um painel analítico sobre eleições presidenciais brasileiras.

A arquitetura do projeto segue um modelo de monorepo estruturado para processamento e visualização:

- `/scripts`: Pipelines de extração, transformação e carga (ETL) em Python.
- `/backend` (Futuro): Camada de servidor API Python.
- `/frontend`: Visualização interativa desenvolvida em React + TypeScript.

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

## Ingestão de Dados da Polymarket

Esta etapa conecta à API pública da Polymarket para coletar as probabilidades da eleição de 2026, tratar os dados e salvá-los no banco **PostgreSQL** usando o ORM **SQLAlchemy**.

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

3. **Configurar as credenciais do banco**:
   - Crie uma cópia do arquivo `.env.example` na raiz do projeto e renomeie-a para `.env`.
   - Abra o arquivo `.env` e insira a string de conexão do seu banco de dados **PostgreSQL** na variável `DATABASE_URL`.

### Executando o Script

Com o ambiente virtual ativo e dentro da pasta `scripts`, execute:

```bash
python main.py
```

### Executando os Testes dos Scripts

Com o ambiente virtual ativo e dentro da pasta `scripts`, execute:

```bash
python -m pytest tests
```
