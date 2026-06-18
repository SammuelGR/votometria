from datetime import datetime

import pandas as pd

from constants import (
    GOOGLE_TRENDS_ELECTION_GROUPS,
    GOOGLE_TRENDS_GEO,
    GOOGLE_TRENDS_HL,
    GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST,
    GOOGLE_TRENDS_SOURCE_NAME,
    GOOGLE_TRENDS_TZ,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from extractors.google_trends import (
    build_trends_batches,
    fetch_interest_over_time_batch,
)
from loaders.google_trends import (
    save_processed_google_trends_all_csv,
    save_processed_google_trends_year_csv,
    save_raw_google_trends_batch_csv,
)
from transformers.google_trends import (
    rescale_batches_by_anchor,
    transform_batch_interest_over_time,
)


def _process_election_group(election_year: str, config: dict, collected_at: datetime):
    """
    Collects, transforms and rescales every batch of a single election group.

    Returns a tuple ``(year_df, summary)`` where ``year_df`` is the consolidated,
    rescaled long DataFrame (or ``None`` when there is nothing to collect).
    """
    terms = config.get("terms") or []
    anchor_term = config["anchor_term"]
    timeframe = config["timeframe"]

    empty_summary = {
        "terms_count": len(terms),
        "batches_count": 0,
        "processed_rows": 0,
        "processed_path": None,
    }

    if not terms:
        print(f"Warning: election group '{election_year}' has no terms; skipping.")
        return None, empty_summary

    batches = build_trends_batches(
        terms, anchor_term, GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST
    )
    if not batches:
        print(
            f"Warning: election group '{election_year}' produced no batches "
            f"(no candidates besides the anchor); skipping."
        )
        return None, empty_summary

    batch_long_dfs = []
    for index, batch_terms in enumerate(batches, start=1):
        batch_id = f"batch_{index:02d}"

        try:
            raw_df = fetch_interest_over_time_batch(
                terms=batch_terms,
                timeframe=timeframe,
                geo=GOOGLE_TRENDS_GEO,
                hl=GOOGLE_TRENDS_HL,
                tz=GOOGLE_TRENDS_TZ,
            )
        except Exception as exc:
            print(
                f"Error fetching {election_year} {batch_id} "
                f"({batch_terms}): {exc}"
            )
            continue

        save_raw_google_trends_batch_csv(raw_df, RAW_DATA_DIR, election_year, batch_id)

        long_df = transform_batch_interest_over_time(
            raw_df,
            election_year=election_year,
            batch_id=batch_id,
            anchor_term=anchor_term,
            geo=GOOGLE_TRENDS_GEO,
            timeframe=timeframe,
            collected_at=collected_at,
        )
        batch_long_dfs.append(long_df)

    if not batch_long_dfs:
        print(f"Warning: election group '{election_year}' yielded no data; skipping.")
        return None, {**empty_summary, "batches_count": len(batches)}

    year_df = rescale_batches_by_anchor(batch_long_dfs, anchor_term)
    processed_path = save_processed_google_trends_year_csv(
        year_df, PROCESSED_DATA_DIR, election_year
    )

    print(
        f"-> {election_year}: {len(terms)} terms | {len(batches)} batches | "
        f"{len(year_df)} processed rows"
    )

    summary = {
        "terms_count": len(terms),
        "batches_count": len(batches),
        "processed_rows": len(year_df),
        "processed_path": processed_path,
    }
    return year_df, summary


def run_google_trends_pipeline() -> dict:
    """
    Runs the Google Trends ETL pipeline across all configured election groups.

    For each year the candidates are split into anchor-based batches, every batch
    is fetched and saved raw, transformed to long format and rescaled by the
    anchor term. A consolidated CSV is written per year plus one combining all
    years. Results are persisted to CSV files only — never to the database. An
    empty election group (e.g. an unset "current" list) is skipped without
    breaking the run. The full window is refetched on every execution because
    Google Trends renormalizes values per requested window.
    """
    collected_at = datetime.now()

    groups_summary = {}
    year_dfs = []

    for election_year, config in GOOGLE_TRENDS_ELECTION_GROUPS.items():
        year_df, summary = _process_election_group(
            election_year, config, collected_at
        )
        groups_summary[election_year] = summary
        if year_df is not None and not year_df.empty:
            year_dfs.append(year_df)

    all_processed_path = None
    if year_dfs:
        all_df = pd.concat(year_dfs, ignore_index=True)
        all_processed_path = save_processed_google_trends_all_csv(
            all_df, PROCESSED_DATA_DIR
        )
        print(
            f"-> Consolidated all elections: {len(all_df)} rows -> {all_processed_path}"
        )
    else:
        print("Warning: no election group produced data; consolidated file not written.")

    return {
        "source": GOOGLE_TRENDS_SOURCE_NAME,
        "status": "success",
        "groups": groups_summary,
        "all_processed_path": all_processed_path,
    }
