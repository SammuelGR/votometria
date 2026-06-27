"""
Read-only audit: compare candidate search strings in a single Google Trends
request and report each term's mean/peak interest.

Because the request is a single ``build_payload`` call, all terms share the same
0–100 scale and are directly comparable. This is the tool to decide *which
spelling* of a name to collect — surname vs full name — since Google Trends
matches search strings literally and the public usually searches the shorter,
more common form (but the surname may also capture homonyms, so always check).

It does **not** touch the dashboard data, the spreadsheet or ``constants.py`` —
it only queries Google Trends and writes one summary CSV under
``scripts/audit_outputs/``.

Run from the ``scripts/`` directory. Examples:

    # 2022 Bolsonaro surname vs full name (default):
    python audit_term_comparison.py --name bolsonaro

    # 2018 Haddad surname vs full name (with the 2018 anchor for context):
    python audit_term_comparison.py --name haddad \\
        --timeframe "2018-01-01 2018-12-31" Bolsonaro Haddad "Fernando Haddad"
"""

import argparse
import sys

import pandas as pd

from constants import (
    GOOGLE_TRENDS_GEO,
    GOOGLE_TRENDS_HL,
    GOOGLE_TRENDS_TZ,
    PROJECT_ROOT,
)
from extractors.google_trends import fetch_interest_over_time_batch

DEFAULT_TERMS = ["Lula", "Bolsonaro", "Jair Bolsonaro"]
DEFAULT_TIMEFRAME = "2022-08-01 2022-10-31"
OUTPUT_DIR = PROJECT_ROOT / "scripts" / "audit_outputs"


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "terms",
        nargs="*",
        default=DEFAULT_TERMS,
        help="Search strings to compare (max 5). Defaults to the Bolsonaro case.",
    )
    parser.add_argument(
        "--timeframe",
        default=DEFAULT_TIMEFRAME,
        help=f"Google Trends timeframe. Default: '{DEFAULT_TIMEFRAME}'.",
    )
    parser.add_argument(
        "--name",
        default="custom",
        help="Slug used in the output filename term_comparison_<name>.csv.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    terms = args.terms

    print(
        f"Querying Google Trends to compare {terms} "
        f"(geo={GOOGLE_TRENDS_GEO}, timeframe='{args.timeframe}')..."
    )
    raw = fetch_interest_over_time_batch(
        terms=terms,
        timeframe=args.timeframe,
        geo=GOOGLE_TRENDS_GEO,
        hl=GOOGLE_TRENDS_HL,
        tz=GOOGLE_TRENDS_TZ,
    )

    if raw is None or raw.empty:
        print("Google Trends returned no data for the comparison window.")
        return 1

    interest = raw.drop(columns=[c for c in ["isPartial"] if c in raw.columns])
    means = interest[terms].mean()
    peaks = interest[terms].max()

    summary = (
        pd.DataFrame(
            {
                "term": terms,
                "mean_interest": [round(float(means[t]), 2) for t in terms],
                "peak_interest": [int(peaks[t]) for t in terms],
            }
        )
        .sort_values("mean_interest", ascending=False)
        .reset_index(drop=True)
    )

    print("\n== Term comparison (same request, same 0-100 scale) ==")
    for _, row in summary.iterrows():
        print(f"  {row['term']}: mean={row['mean_interest']} peak={row['peak_interest']}")

    top = summary.iloc[0]
    bottom = summary.iloc[-1]
    if bottom["mean_interest"] > 0:
        ratio = top["mean_interest"] / bottom["mean_interest"]
        print(
            f"\n  '{top['term']}' is {ratio:.1f}x the mean interest of "
            f"'{bottom['term']}' over {args.timeframe}."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"term_comparison_{args.name}.csv"
    summary.to_csv(path, index=False)
    print(f"\nWrote {path.relative_to(PROJECT_ROOT)}. No dashboard data was modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
