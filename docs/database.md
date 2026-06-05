# Database Schema & Conventions

This document outlines the database schema, models, performance indices, and deduplication logic implemented in the ingestion pipeline.

---

## 1. Current Database Model

The application uses SQLAlchemy to map historical probability snapshots to a PostgreSQL database.

### Table Name: `polymarket_probabilities`

| Column Name      | SQLAlchemy Type               | Nullable | Description                                                           |
| :--------------- | :---------------------------- | :------- | :-------------------------------------------------------------------- |
| `id`             | `Integer` (PK, autoincrement) | No       | Database primary key.                                                 |
| `candidate_name` | `String(100)`                 | No       | Name of the candidate (extracted from `groupItemTitle`).              |
| `probability`    | `Float`                       | No       | Victory probability (from outcome price `'p'`, range: `0.0` - `1.0`). |
| `timestamp`      | `DateTime`                    | No       | UTC timestamp of the hourly snapshot (converted from Unix epoch `'t'`). |
| `market_id`      | `String(255)`                 | No       | Unique identifier of the specific binary market in Polymarket.        |

### Performance Indexing

To support incremental ingestion and fast time-series queries, the database schema includes:

- **Composite Index**: `(market_id, timestamp)` (named `idx_market_timestamp`) to optimize timestamp lookups for each Polymarket market.

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
3. **Targeted Duplicate Check**: Before inserting transformed records, the loader queries only the `(market_id, timestamp)` pairs present in the current batch.
4. **Transaction Commit**: Once all candidate histories are parsed and queued, a single transaction commit persists the batch to PostgreSQL.

---

## 3. Future Database Schema Expansion

To support the other data modules outlined in the project blueprint (`AGENTS.md`), future database designs should consider:

### A. Candidate Mapping (Unified Catalog)

To avoid string mismatch issues when merging TSE, Polymarket, Wikipedia, and Google Trends:

- Create a central `candidates` catalog table:
  - `id` (Primary Key)
  - `slug` (Unique identifier, e.g. `luiz-inacio-lula-da-silva`, `jair-bolsonaro`)
  - `display_name` (e.g. "Lula")
  - `tse_name` (Name used in TSE records)
  - `trends_query` (Query term used for Google Trends)
- Update `polymarket_probabilities` and other attention tables to reference this table via a foreign key `candidate_id`.

### B. Mapped Tables for Upcoming Modules

- **`public_attention_snapshots`**:
  - Columns: `candidate_id` (FK), `timestamp` (DateTime), `wikipedia_views` (Integer), `trends_index` (Float).
- **`tse_historical_results`**:
  - Columns: `candidate_id` (FK), `election_year` (Integer), `round` (Integer), `state_code` (String), `votes_count` (Integer).
- **`macroeconomic_indicators`**:
  - Columns: `timestamp` (DateTime), `usd_rate` (Float), `selic_rate` (Float), `ipca_index` (Float), `ibovespa` (Float).
