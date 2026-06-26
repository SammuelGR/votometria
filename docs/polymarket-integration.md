# Polymarket API Integration

This document explains the configuration, endpoints, and logic used to fetch election data from Polymarket.

---

## 1. Target Event

- **Event ID**: `45915`
- **Slug**: `brazil-presidential-election`
- **Gamma API Event Endpoint**: `https://gamma-api.polymarket.com/events/45915`
  - Returns metadata for the event and a list of associated `markets`.

---

## 2. Market & Candidate Selection

- **Candidate Names**: Extracted from the `groupItemTitle` field of each market in the event payload (e.g., "Luiz Inácio Lula da Silva", "Michelle Bolsonaro").
- **Filtering Placeholder Markets**: Any market with a candidate name containing `"person "` or `"another person"` (case-insensitive) is skipped as it represents placeholder slots.
- **Token Resolution**:
  - Each binary market contains a `clobTokenIds` list (represented as a JSON-encoded string or array).
  - The **first token ID (index `0`)** corresponds to the `"Yes"` outcome (victory probability).

---

## 3. Historical Price Extraction

- **CLOB History Endpoint**: `https://clob.polymarket.com/prices-history`
- **Query Parameters**:
  - `market`: The `"Yes"` token ID (resolved from `clobTokenIds[0]`).
  - `fidelity`: `60` minutes. The project stores hourly Polymarket snapshots.
  - `startTs`: Unix timestamp used for incremental updates when previous data exists.
  - `endTs`: Current Unix timestamp at execution time.
  - `interval`: `"max"` is used only when no previous timestamp exists for that market.
- **Response Format**:
  - The API returns a list of data point dictionaries:
    ```json
    [
      {
        "t": 1777795203,
        "p": 0.0015
      },
      ...
    ]
    ```
  - `t`: Unix epoch timestamp in seconds.
  - `p`: Probability of the candidate winning (normalized between `0.0` and `1.0`).

---

## 4. Ingestion & Execution Strategy

- **Update Frequency**: Polymarket data changes rapidly. The pipeline is designed to be executed on a scheduled trigger **daily** or **every 4 hours** to capture fresh snapshots.
- **Candidate Catalog**: Each parsed market is associated with a `candidate_catalog` entry using the Polymarket source and market ID.
- **Incremental Runs**: The ETL pipeline queries the latest persisted timestamp per `market_id`, applies a 24-hour safety overlap, and requests only the needed CLOB history window using `startTs`, `endTs`, and `fidelity=60`.
- **Deduplication**: The loader checks only the `(market_id, timestamp)` pairs from the current batch before inserting records.

---

## 5. Scripts Architecture

The Polymarket integration follows a modular ETL layout:

- `scripts/extractors/polymarket.py`: Calls Polymarket APIs and returns raw payloads.
- `scripts/core/catalog.py`: Provides candidate catalog helpers shared by ETL pipelines.
- `scripts/transformers/polymarket.py`: Parses markets, resolves `"Yes"` token IDs, filters placeholders, and converts price history points into internal records.
- `scripts/loaders/polymarket.py`: Reads existing database state and persists new probability records.
- `scripts/pipelines/polymarket.py`: Orchestrates the full extraction, transformation, incremental window calculation, and loading flow.
- `scripts/main.py`: Entry point for running the current ETL pipeline.
