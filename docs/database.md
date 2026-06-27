# Database Schema & Conventions

This document outlines the PostgreSQL database schema, models, performance indices, and deduplication logic implemented by database-backed ingestion pipelines.

---

## 1. Current Database Model

The application uses SQLAlchemy to persist selected normalized analytical datasets to PostgreSQL.

Some integrations generate local analytical files instead of database tables. TSE historical election outputs are documented in `docs/tse-integration.md`.

### Table Name: `candidate_catalog`

The candidate catalog stores candidates as observed by each data source. ETL pipelines populate this table when a source candidate is first observed.

| Column Name       | SQLAlchemy Type               | Nullable | Description                                                   |
| :---------------- | :---------------------------- | :------- | :------------------------------------------------------------ |
| `id`              | `Integer` (PK, autoincrement) | No       | Database primary key.                                         |
| `source`          | `String(50)`                  | No       | Source identifier, such as `polymarket`.                      |
| `source_key`      | `String(255)`                 | No       | Source-specific candidate key.                                |
| `raw_name`        | `String(255)`                 | No       | Candidate name as received from the source.                   |
| `display_name`    | `String(255)`                 | No       | Candidate name used by the application.                       |
| `normalized_name` | `String(255)`                 | No       | Normalized candidate name used for matching and inspection.   |
| `full_name`       | `String(255)`                 | Yes      | Full candidate name when available.                           |

The `(source, source_key)` pair is unique.

### Table Name: `polymarket_probabilities`

| Column Name            | SQLAlchemy Type               | Nullable | Description                                                            |
| :--------------------- | :---------------------------- | :------- | :--------------------------------------------------------------------- |
| `id`                   | `Integer` (PK, autoincrement) | No       | Database primary key.                                                  |
| `candidate_catalog_id` | `Integer` (FK)                | No       | Reference to `candidate_catalog.id`.                                   |
| `candidate_name`       | `String(100)`                 | No       | Name of the candidate (extracted from `groupItemTitle`).               |
| `probability`          | `Float`                       | No       | Victory probability (from outcome price `'p'`, range: `0.0` - `1.0`).  |
| `timestamp`            | `DateTime`                    | No       | UTC timestamp of the hourly snapshot (converted from Unix epoch `'t'`). |
| `market_id`            | `String(255)`                 | No       | Unique identifier of the specific binary market in Polymarket.         |

### Performance Indexing

To support incremental ingestion and fast time-series queries, the database schema includes:

- **Composite Index**: `(market_id, timestamp)` (named `idx_market_timestamp`) to optimize timestamp lookups for each Polymarket market.
- **Composite Index**: `(candidate_catalog_id, timestamp)` (named `idx_polymarket_candidate_catalog_timestamp`) to optimize candidate time-series queries.
- **Catalog Index**: `normalized_name` (named `idx_candidate_catalog_normalized_name`) to support candidate catalog inspection and matching.

---

## 2. Incremental Ingestion & Deduplication

To avoid fetching the full Polymarket history on every run, the ETL pipeline derives the latest persisted timestamp per market before calling the CLOB history endpoint:

1. **Latest Timestamp Lookup**: The loader queries the latest known timestamp for each market:
   ```python
   session.query(
       PolymarketProbability.market_id,
       func.max(PolymarketProbability.timestamp),
   ).group_by(PolymarketProbability.market_id)
   ```
2. **Windowed API Request**: The pipeline converts that value into a CLOB `startTs` parameter, applies a 24-hour overlap to avoid missing late or boundary records, and requests hourly points with `fidelity=60`.
3. **Candidate Catalog Upsert**: For each parsed market, the pipeline ensures a corresponding `candidate_catalog` row exists for the Polymarket source.
4. **Targeted Duplicate Check**: Before inserting transformed records, the loader queries only the `(market_id, timestamp)` pairs present in the current batch.
5. **Transaction Commit**: Once all candidate histories are parsed and queued, a single transaction commit persists the batch to PostgreSQL.

---

## 3. Future Database Schema Expansion

To support the other data modules outlined in the project blueprint (`AGENTS.md`), future database designs should consider:

### A. Cross-Source Candidate Linking

The current `candidate_catalog` stores source-specific candidate entries. Future cross-source analyses may introduce a canonical candidate entity or linking field to relate entries that represent the same person across TSE, Polymarket, and Google Trends.

This should be added only where cross-source modules require it, such as Public Attention vs Market Expectations.
