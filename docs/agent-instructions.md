# Project Entry Point & Developer Guidelines

This document is the entry point for developers and AI coding agents working on the **Brazilian Presidential Election Analytical Dashboard** project.

Detailed product, frontend, database and integration decisions live in the dedicated documentation files listed below. When a specific document defines a topic, prefer that document over older or broader notes.

---

## Documentation map

- `docs/modules.md`
  Product and domain definition of the analytical modules.

- `docs/frontend-modules.md`
  Frontend representation of the analytical modules.

- `docs/frontend.md`
  Frontend stack, routing and interface language.

- `docs/database.md`
  Database schema and persistence decisions.

- `docs/polymarket-integration.md`
  Polymarket ETL and integration details.

## Reading guide

For frontend tasks, read:

- `docs/frontend.md`
- `docs/frontend-modules.md`
- `docs/modules.md`

For data modeling or backend tasks, read:

- `docs/modules.md`
- `docs/database.md`

For Polymarket tasks, read:

- `docs/polymarket-integration.md`
- `docs/database.md`
- `docs/modules.md`

## 1. Project Overview

The goal of this project is to build an analytical dashboard that consolidates public expectation, electoral data, public attention, and macroeconomic context for Brazilian Presidential Elections.

The application helps users answer two main focus questions:

1. **Who is concentrating public attention?**
2. **How does public attention and market expectation behave over time?**

---

## 2. Monorepo Architecture

This project is structured as a monorepo containing isolated modules:

- **/scripts**: Contains Python ETL pipelines organized by shared core utilities, extractors, transformers, loaders, pipelines, and database models.
- **/frontend**: Reserved for the web-based visualization frontend application (dashboard).
- **/docs**: Contains documentation schemas, specifications, and guidelines.

---

## 3. Data Integration & Quality Standards

When merging these sources, agents must implement the following data quality rules:

- **Name Standardization**: Normalize candidate names across different sources (e.g., aligning "Luiz Inácio Lula da Silva" vs "Lula" into a unified ID).
- **Temporal Alignment**: Resample daily/high-frequency series (like Polymarket) to a **weekly granularity** when comparing with lower-frequency public interest data (Google Trends).
- **Date Formats**: Enforce standard ISO `YYYY-MM-DD` formatting across all databases and datasets.
- **Data Types**: Ensure numerical metrics (like TSE vote counts stored as text strings) are parsed into integer or float columns during ingestion.
- **No Synthetic Data**: Always query real live data sources. Do not implement mock fallbacks or dummy data generators.

---

## 4. Coding Conventions

- **Strict English Policy**: All variables, database models, table/column names, prints, logs, docstrings, and code comments **must** be written in English.
- Frontend user-facing interface text is documented separately in `docs/frontend.md`.

---

## 5. Testing Guidelines

Testing is defined per monorepo module.

### `/scripts`

- Use `pytest`.
- Run tests from inside `/scripts` with `python -m pytest tests`.
- Keep script tests inside `/scripts/tests`.
- Unit tests must not call live APIs or production databases.
- Use `tests/conftest.py` for shared pytest fixtures.
- Use `tests/helpers.py` for small reusable factories and utilities.
- Loader tests may use SQLite in-memory databases when validating persistence behavior.
- Pipeline tests should mock extractors, transformers, and loaders to validate orchestration behavior.

---

## 6. KPI Thresholds & Update Frequencies

### Specific KPI Meta Targets

Analytical notifications and visualization logic use the following business thresholds:

- **Attention Concentration**: Triggered when the top 2 candidates by Share of Search aggregate **70% or more** of total attention in a given period.
- **Attention/Market Divergence**: Triggered when the difference between a candidate's Share of Search and their Polymarket win probability exceeds **10 percentage points**.
- **Relevant Event Impact**: Triggered when a candidate's search interest increases by **20% or more** in the window following a logged political event (e.g. debate or campaign announcement).

### Data Ingestion Frequencies

- **Polymarket Expectations**: Daily or every 4 hours.
- **Google Trends & Wikipedia Pageviews**: Weekly batches.
- **TSE Historical Votes**: Static historical load per election cycle.
- **Macroeconomic Indicators**: Weekly or monthly batches (aligned with indicator releases).
