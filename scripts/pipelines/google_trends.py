from datetime import datetime

import pandas as pd

from constants import (
    GOOGLE_TRENDS_ELECTION_GROUPS,
    GOOGLE_TRENDS_GEO,
    GOOGLE_TRENDS_HL,
    GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST,
    GOOGLE_TRENDS_SOURCE_NAME,
    GOOGLE_TRENDS_TZ,
)
from core.sheets import get_layer_spreadsheets
from extractors.google_trends import (
    build_trends_batches,
    fetch_interest_over_time_batch,
)
from loaders.google_trends import (
    save_processed_google_trends_all,
    save_processed_google_trends_year,
    save_raw_google_trends_batch,
)
from transformers.google_trends import (
    rescale_batches_by_anchor,
    transform_batch_interest_over_time,
)


def _process_election_group(
    election_year: str, config: dict, collected_at: datetime, layers: dict
):
    """
    Collects, transforms and rescales every batch of a single election group,
    publishing raw batches to the bronze layer and the consolidated (rescaled)
    year dataset to the prata (silver) layer.

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
        "processed_tab": None,
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

        # Extractor output -> bronze layer.
        save_raw_google_trends_batch(layers["bronze"], raw_df, election_year, batch_id)

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

    # Transformer output (rescaled long) -> prata (silver) layer.
    year_df = rescale_batches_by_anchor(batch_long_dfs, anchor_term)
    processed_tab = save_processed_google_trends_year(
        layers["prata"], year_df, election_year
    )

    print(
        f"-> {election_year}: {len(terms)} terms | {len(batches)} batches | "
        f"{len(year_df)} processed rows -> tab '{processed_tab}'"
    )

    summary = {
        "terms_count": len(terms),
        "batches_count": len(batches),
        "processed_rows": len(year_df),
        "processed_tab": processed_tab,
    }
    return year_df, summary


def run_google_trends_pipeline() -> dict:
    """
    Runs the Google Trends ETL pipeline across all configured election groups.

    For each year the candidates are split into anchor-based batches, every batch
    is fetched and published raw, transformed to long format and rescaled by the
    anchor term. A consolidated dataset is published per year plus one combining
    all years. Results are published straight to the Google Sheets spreadsheet
    (``raw_*`` and ``proc_*`` tabs) — never to the database and never to CSV on
    disk. An empty election group (e.g. an unset "current" list) is skipped
    without breaking the run. The full window is refetched on every execution
    because Google Trends renormalizes values per requested window.
    """
    collected_at = datetime.now()

    # Open the three medallion spreadsheets once up front; this also fails fast
    # with a clear message when the .env / service account configuration is
    # missing. raw -> bronze, rescaled long -> prata, consolidated -> ouro.
    layers = get_layer_spreadsheets("bronze", "prata", "ouro")

    groups_summary = {}
    year_dfs = []

    for election_year, config in GOOGLE_TRENDS_ELECTION_GROUPS.items():
        year_df, summary = _process_election_group(
            election_year, config, collected_at, layers
        )
        groups_summary[election_year] = summary
        if year_df is not None and not year_df.empty:
            year_dfs.append(year_df)

    all_processed_tab = None
    if year_dfs:
        all_df = pd.concat(year_dfs, ignore_index=True)
        # Loader output (consolidated) -> ouro (gold) layer; read by the frontend.
        all_processed_tab = save_processed_google_trends_all(layers["ouro"], all_df)
        print(
            f"-> Consolidated all elections: {len(all_df)} rows -> "
            f"tab '{all_processed_tab}'"
        )
    else:
        print("Warning: no election group produced data; consolidated tab not written.")

    return {
        "source": GOOGLE_TRENDS_SOURCE_NAME,
        "status": "success",
        "groups": groups_summary,
        "all_processed_tab": all_processed_tab,
    }
