# Backend

This document defines stable backend architecture decisions for the project.

Product and domain module definitions are documented in `docs/modules.md`.

Database schema and persistence decisions are documented in `docs/database.md`.

## Stack

The backend uses:

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- python-dotenv
- pytest

## Application model

The backend is an HTTP API that serves processed analytical data to the frontend.

The backend reads persisted analytical data and exposes stable frontend-facing contracts.

Route paths are organized by product area and exposed under the `/api` prefix.

FastAPI provides interactive API documentation at `/docs` during development.

## Project structure

```text
backend/
  app/
    core/
    routers/
    schemas/
    services/
    main.py
    models.py
  tests/
```

Core configuration and database session helpers stay in `app/core`.

Route declarations stay in `app/routers`. `app/routers/api.py` owns the global `/api` prefix.

Response schemas stay in `app/schemas`.

Database read logic and response assembly stay in `app/services`.

## Configuration

The backend reads `DATABASE_URL` from the project environment.

## Testing

Run backend unit tests from inside `/backend`.

Use `python -m pytest tests`.
