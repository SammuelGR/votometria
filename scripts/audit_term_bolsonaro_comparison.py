"""
Optional, read-only audit: does the search string change the result?

Collects a single Google Trends batch comparing the three candidate strings
``Lula``, ``Bolsonaro`` and ``Jair Bolsonaro`` in the same request (so they are
directly comparable on the same 0–100 scale) over the final stretch of the 2022
campaign, and reports the mean interest of each.

This is the quantitative evidence behind switching the configured 2022/2018 term
from ``"Jair Bolsonaro"`` to ``"Bolsonaro"``: the full name is searched far less
than the surname, which deflated Bolsonaro's Share of Search.

It does **not** touch the dashboard data, the spreadsheet or ``constants.py`` —
it only queries Google Trends and writes one summary CSV under
``scripts/audit_outputs/``.

Run from the ``scripts/`` directory:

    python audit_term_bolsonaro_comparison.py
"""

import sys

import pandas as pd

from constants import (
    GOOGLE_TRENDS_GEO,
    GOOGLE_TRENDS_HL,
    GOOGLE_TRENDS_TZ,
    PROJECT_ROOT,
)
from extractors.google_trends import fetch_interest_over_time_batch

TERMS = ["Lula", "Bolsonaro", "Jair Bolsonaro"]
TIMEFRAME = "2022-08-01 2022-10-31"
OUTPUT_DIR = PROJECT_ROOT / "scripts" / "audit_outputs"
OUTPUT_NAME = "term_comparison_bolsonaro.csv"


def main() -> int:
    print(
        f"Querying Google Trends to compare {TERMS} "
        f"(geo={GOOGLE_TRENDS_GEO}, timeframe='{TIMEFRAME}')..."
    )
    raw = fetch_interest_over_time_batch(
        terms=TERMS,
        timeframe=TIMEFRAME,
        geo=GOOGLE_TRENDS_GEO,
        hl=GOOGLE_TRENDS_HL,
        tz=GOOGLE_TRENDS_TZ,
    )

    if raw is None or raw.empty:
        print("Google Trends returned no data for the comparison window.")
        return 1

    interest = raw.drop(columns=[c for c in ["isPartial"] if c in raw.columns])
    means = interest[TERMS].mean()
    peaks = interest[TERMS].max()

    summary = pd.DataFrame(
        {
            "term": TERMS,
            "mean_interest": [round(float(means[t]), 2) for t in TERMS],
            "peak_interest": [int(peaks[t]) for t in TERMS],
        }
    )

    print("\n== Term comparison (same request, same 0-100 scale) ==")
    for _, row in summary.iterrows():
        print(f"  {row['term']}: mean={row['mean_interest']} peak={row['peak_interest']}")

    bolso = float(means["Bolsonaro"]) or 0.0
    jair = float(means["Jair Bolsonaro"]) or 0.0
    if jair > 0:
        print(
            f"\n  'Bolsonaro' is {bolso / jair:.1f}x the mean interest of "
            f"'Jair Bolsonaro' over {TIMEFRAME}."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / OUTPUT_NAME
    summary.to_csv(path, index=False)
    print(f"\nWrote {path.relative_to(PROJECT_ROOT)}. No dashboard data was modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
