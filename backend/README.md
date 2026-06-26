# Backend

FastAPI backend for Votometria.

## Requirements

- Python 3.11 or newer
- PostgreSQL database configured through `DATABASE_URL` in the project `.env` file
- Backend CORS origins configured through `BACKEND_CORS_ORIGINS` in the project `.env` file

## Installation

```bash
python -m venv .venv
```

Activate the virtual environment according to your terminal:

- **Windows (Git Bash)**: `source .venv/Scripts/activate`
- **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
- **Windows (CMD)**: `.venv\Scripts\activate`
- **Linux/macOS**: `source .venv/bin/activate`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Development

With the virtual environment active and inside `/backend`, run:

```bash
uvicorn app.main:app --reload
```

The interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## Unit Tests

With the virtual environment active and inside `/backend`, run:

```bash
python -m pytest tests
```

## Deployment

The backend is hosted on Render.

Production URL: `https://votometria.onrender.com`
