from datetime import datetime, timezone

from constants import POLYMARKET_SOURCE
from core.catalog import get_or_create_candidate_catalog_entry
from core.time_windows import calculate_incremental_start_timestamp
from extractors.polymarket import fetch_event_markets, fetch_price_history
from loaders.polymarket import get_latest_timestamps_by_market, save_probability_records
from transformers.polymarket import parse_markets, parse_price_history


def run_polymarket_pipeline(session) -> int:
    """
    Runs the Polymarket ETL pipeline.
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
    latest_timestamps = get_latest_timestamps_by_market(session)
    end_ts = int(datetime.now(timezone.utc).timestamp())
    total_saved = 0

    for market in markets:
        last_timestamp = latest_timestamps.get(market.market_id)
        start_ts = calculate_incremental_start_timestamp(last_timestamp)
        candidate = get_or_create_candidate_catalog_entry(
            session,
            source=POLYMARKET_SOURCE,
            source_key=market.market_id,
            raw_name=market.candidate_name,
            full_name=market.candidate_name,
        )

        try:
            history_points = fetch_price_history(
                token_id=market.yes_token_id,
                start_ts=start_ts,
                end_ts=end_ts if start_ts is not None else None,
            )
            records = parse_price_history(market, candidate.id, history_points)
        except Exception as exc:
            print(
                f"Error processing price history for market ID "
                f"{market.market_id} ({market.candidate_name}): {exc}"
            )
            continue

        saved_count = save_probability_records(session, records)
        total_saved += saved_count

        print(
            f"-> Candidate: {market.candidate_name} | "
            f"Fetched: {len(history_points)} | Saved: {saved_count} new records"
        )

    if total_saved > 0:
        session.commit()
        print(f"Success! {total_saved} historical probability records saved to the database.")
    else:
        print("No new probability records to save.")

    return total_saved
