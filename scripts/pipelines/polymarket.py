from extractors.polymarket import fetch_event_markets, fetch_price_history
from loaders.polymarket_sheets import (
    save_raw_history_to_bronze,
    save_raw_markets_to_bronze,
    save_records_to_ouro,
    save_records_to_prata,
)
from transformers.polymarket import parse_markets, parse_price_history

from core.sheets import get_layer_spreadsheets


def _stable_candidate_catalog_ids(markets) -> dict:
    """
    Assigns a deterministic integer id per candidate (sorted by market_id) so
    the gold table has a stable ``candidate_catalog_id`` across runs without a
    database-backed catalog.
    """
    ordered_ids = sorted({market.market_id for market in markets})
    return {market_id: index for index, market_id in enumerate(ordered_ids, start=1)}


def run_polymarket_pipeline() -> int:
    """
    Runs the Polymarket ETL pipeline straight to the medallion spreadsheets
    (bronze/prata/ouro), with no database. The pipeline is stateless: the full
    price history is refetched and the tabs are fully rewritten on every run.

    Returns the number of probability records published to the gold layer.
    """
    markets_payload = fetch_event_markets()
    if not markets_payload:
        print("Warning: No markets found in the election event.")
        return 0

    markets = parse_markets(markets_payload)
    if not markets:
        print("Warning: No candidate markets were parsed from the election event.")
        return 0

    print(f"Processing {len(markets)} candidate markets from the election event...")

    layers = get_layer_spreadsheets("bronze", "prata", "ouro")

    # Extractor output -> bronze (raw markets).
    save_raw_markets_to_bronze(layers["bronze"], markets)

    catalog_ids = _stable_candidate_catalog_ids(markets)
    raw_history_rows: list[dict] = []
    all_records = []

    for market in markets:
        try:
            # Stateless full-history fetch (no incremental DB timestamps).
            history_points = fetch_price_history(token_id=market.yes_token_id)
        except Exception as exc:
            print(
                f"Error processing price history for market ID "
                f"{market.market_id} ({market.candidate_name}): {exc}"
            )
            continue

        for point in history_points:
            raw_history_rows.append(
                {
                    "market_id": market.market_id,
                    "candidate_name": market.candidate_name,
                    "t": point.get("t"),
                    "p": point.get("p"),
                }
            )

        records = parse_price_history(
            market, catalog_ids[market.market_id], history_points
        )
        all_records.extend(records)

        print(
            f"-> Candidate: {market.candidate_name} | "
            f"Fetched: {len(history_points)} points"
        )

    # Extractor output -> bronze (raw price history).
    save_raw_history_to_bronze(layers["bronze"], raw_history_rows)
    # Transformer output -> prata (parsed long records).
    save_records_to_prata(layers["prata"], all_records)
    # Loader output -> ouro (consolidated series; read by the backend API).
    save_records_to_ouro(layers["ouro"], all_records)

    print(
        f"Success! {len(all_records)} probability records published to "
        f"bronze/prata/ouro."
    )
    return len(all_records)
