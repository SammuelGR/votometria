"""
Read-only audit of the Google Trends dataset that the pipeline publishes to
Google Sheets.

It reads the consolidated processed tab straight from the spreadsheet (using the
same service-account client the pipeline uses), runs a set of consistency checks
and writes summary CSVs under ``scripts/audit_outputs/``. It **never** mutates
the spreadsheet, the source data or any pipeline artifact — it is strictly
read-only.

Run from the ``scripts/`` directory so the local packages resolve:

    python audit_google_trends_import.py

Requires the same ``.env`` configuration as the pipeline
(``GOOGLE_SHEETS_ID`` + ``GOOGLE_SERVICE_ACCOUNT_FILE``).
"""

import sys

import pandas as pd

from constants import GOOGLE_TRENDS_ELECTION_GROUPS, PROJECT_ROOT
from core.sheets import get_spreadsheet

PROCESSED_TAB = "proc_google_trends_all_elections_interest_long"
OUTPUT_DIR = PROJECT_ROOT / "scripts" / "audit_outputs"

EXPECTED_COLUMNS = [
    "date",
    "election_year",
    "term",
    "interest_raw",
    "interest_scaled",
    "geo",
    "timeframe",
    "source",
    "batch_id",
    "anchor_term",
    "is_anchor",
    "is_partial",
    "collected_at",
]

# Key that must be unique for the dataset the dashboard consumes.
DEDUP_KEY = ["election_year", "date", "term"]


def _to_bool(series: pd.Series) -> pd.Series:
    """Coerces a string/boolean column ('True'/'False'/'') to real booleans."""
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


def load_processed_tab() -> pd.DataFrame:
    """
    Reads the consolidated processed worksheet into a typed DataFrame.

    Values are read as text and coerced here so the audit behaves the same
    whether Sheets/gspread numericises cells or keeps them as strings.
    """
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(PROCESSED_TAB)
    records = worksheet.get_all_records(default_blank="")
    df = pd.DataFrame(records)

    if df.empty:
        return df

    # Make every expected column present (missing ones surface in the report).
    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    df["election_year"] = df["election_year"].astype(str).str.strip()
    df["term"] = df["term"].astype(str).str.strip()
    df["date"] = df["date"].astype(str).str.strip()
    df["batch_id"] = df["batch_id"].astype(str).str.strip()
    df["anchor_term"] = df["anchor_term"].astype(str).str.strip()
    df["interest_raw"] = pd.to_numeric(df["interest_raw"], errors="coerce")
    df["interest_scaled"] = pd.to_numeric(df["interest_scaled"], errors="coerce")
    df["is_anchor"] = _to_bool(df["is_anchor"])
    df["is_partial"] = _to_bool(df["is_partial"])
    return df


def write_csv(df: pd.DataFrame, name: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(PROJECT_ROOT)} ({len(df)} rows)")


def audit_columns(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    print("\n== Columns ==")
    print(f"  expected present: {len(EXPECTED_COLUMNS) - len(missing)}/{len(EXPECTED_COLUMNS)}")
    if missing:
        print(f"  MISSING columns: {missing}")
    if extra:
        print(f"  extra columns:   {extra}")


def audit_counts(df: pd.DataFrame) -> None:
    print("\n== Row counts ==")
    print(f"  total rows: {len(df)}")
    print("  rows per election_year:")
    for year, count in df.groupby("election_year").size().items():
        print(f"    {year}: {count}")

    per_year_term = (
        df.groupby(["election_year", "term"]).size().reset_index(name="rows")
        .sort_values(["election_year", "rows"], ascending=[True, False])
    )
    write_csv(per_year_term, "linhas_por_termo_ano.csv")


def audit_batches(df: pd.DataFrame) -> None:
    print("\n== Batches per term ==")
    grouped = (
        df.groupby(["election_year", "term"])["batch_id"]
        .agg(lambda s: ",".join(sorted(set(s))))
        .reset_index(name="batches")
    )
    grouped["n_batches"] = grouped["batches"].str.count(",") + 1
    grouped = grouped.sort_values(["election_year", "n_batches"], ascending=[True, False])
    write_csv(grouped, "batches_por_termo.csv")

    multi = grouped[grouped["n_batches"] > 1]
    if multi.empty:
        print("  no term appears in more than one batch in the processed tab (expected).")
    else:
        print("  terms spanning multiple batches (anchor dedup keeps only batch_01):")
        for _, row in multi.iterrows():
            print(f"    {row['election_year']} {row['term']}: {row['batches']}")


def audit_anchor_usage(df: pd.DataFrame) -> None:
    print("\n== Anchor usage by year ==")
    rows = []
    for year, config in GOOGLE_TRENDS_ELECTION_GROUPS.items():
        year_df = df[df["election_year"] == str(year)]
        if year_df.empty:
            continue
        configured_anchor = config["anchor_term"]
        flagged = sorted(year_df.loc[year_df["is_anchor"], "term"].unique().tolist())
        anchor_df = year_df[year_df["term"] == configured_anchor]
        anchor_batches = sorted(set(anchor_df["batch_id"]))
        # The anchor must not repeat per date in the processed (dedup'd) tab.
        anchor_dupe_dates = int(anchor_df.duplicated(subset=["date"]).sum())
        rows.append(
            {
                "election_year": str(year),
                "configured_anchor": configured_anchor,
                "terms_flagged_is_anchor": ",".join(flagged),
                "only_configured_anchor_flagged": flagged == [configured_anchor] or flagged == [],
                "anchor_batches_in_processed": ",".join(anchor_batches),
                "anchor_duplicate_dates": anchor_dupe_dates,
            }
        )
        print(
            f"  {year}: anchor='{configured_anchor}' | flagged={flagged} | "
            f"anchor batches={anchor_batches} | duplicate anchor dates={anchor_dupe_dates}"
        )
    write_csv(pd.DataFrame(rows), "anchor_usage_by_year.csv")


def audit_duplicates(df: pd.DataFrame) -> None:
    print("\n== Duplicates by election_year+date+term ==")
    grouped = df.groupby(DEDUP_KEY).size().reset_index(name="count")
    dupes = grouped[grouped["count"] > 1].sort_values("count", ascending=False)
    print(f"  duplicate (year,date,term) keys: {len(dupes)}")

    per_term = (
        dupes.groupby("term")["count"].sum().reset_index(name="duplicate_rows")
        .sort_values("duplicate_rows", ascending=False)
    )
    per_year = (
        dupes.groupby("election_year")["count"].sum().reset_index(name="duplicate_rows")
        .sort_values("duplicate_rows", ascending=False)
    )
    if not per_term.empty:
        print("  top duplicated terms:")
        for _, row in per_term.head(20).iterrows():
            print(f"    {row['term']}: {row['duplicate_rows']}")
        print("  duplicates per year:")
        for _, row in per_year.iterrows():
            print(f"    {row['election_year']}: {row['duplicate_rows']}")

    write_csv(dupes, "duplicatas_por_termo.csv")


def audit_nulls_and_invalid(df: pd.DataFrame) -> None:
    print("\n== Nulls and out-of-range values ==")
    checks = []

    def add(metric: str, value: int) -> None:
        checks.append({"metric": metric, "value": int(value)})
        print(f"  {metric}: {int(value)}")

    for column in ["date", "election_year", "term", "interest_raw", "interest_scaled"]:
        nulls = df[column].isna().sum()
        if df[column].dtype == object:
            nulls += (df[column].astype(str).str.strip() == "").sum()
        add(f"null_{column}", nulls)

    add("interest_raw_below_0", (df["interest_raw"] < 0).sum())
    add("interest_raw_above_100", (df["interest_raw"] > 100).sum())
    add("interest_scaled_below_0", (df["interest_scaled"] < 0).sum())
    add("interest_scaled_above_120", (df["interest_scaled"] > 120).sum())

    write_csv(pd.DataFrame(checks), "nulls_and_invalid_values.csv")


def _shares(means: pd.Series) -> pd.Series:
    total = means.sum()
    return (means / total * 100) if total > 0 else means * 0


def audit_share_2022(df: pd.DataFrame) -> None:
    print("\n== Share of Search 2022 (atual vs deduplicado) ==")
    year_df = df[df["election_year"] == "2022"]
    if year_df.empty:
        print("  no 2022 data found; skipping.")
        write_csv(pd.DataFrame(), "share_2022_atual_vs_deduplicado.csv")
        return

    dedup_df = year_df.drop_duplicates(subset=DEDUP_KEY)

    mean_scaled_atual = year_df.groupby("term")["interest_scaled"].mean()
    mean_scaled_dedup = dedup_df.groupby("term")["interest_scaled"].mean()
    mean_raw_atual = year_df.groupby("term")["interest_raw"].mean()

    out = pd.DataFrame(
        {
            "term": mean_scaled_atual.index,
            "rows": year_df.groupby("term").size().reindex(mean_scaled_atual.index).values,
            "mean_scaled_atual": mean_scaled_atual.round(2).values,
            "share_scaled_atual_pct": _shares(mean_scaled_atual).round(2).values,
            "mean_scaled_dedup": mean_scaled_dedup.reindex(mean_scaled_atual.index).round(2).values,
            "share_scaled_dedup_pct": _shares(mean_scaled_dedup.reindex(mean_scaled_atual.index)).round(2).values,
            "mean_raw_atual": mean_raw_atual.reindex(mean_scaled_atual.index).round(2).values,
            "share_raw_atual_pct": _shares(mean_raw_atual.reindex(mean_scaled_atual.index)).round(2).values,
        }
    ).sort_values("share_scaled_atual_pct", ascending=False)
    write_csv(out, "share_2022_atual_vs_deduplicado.csv")

    # Headline metric: Lula vs Bolsonaro pairwise (both live in batch_01).
    pair = ["Lula", "Bolsonaro"]
    pair_present = [t for t in pair if t in mean_scaled_atual.index]
    if len(pair_present) == 2:
        pair_scaled = _shares(mean_scaled_atual[pair_present])
        pair_raw = _shares(mean_raw_atual[pair_present])
        print("  Lula vs Bolsonaro (only these two selected):")
        for term in pair_present:
            print(
                f"    {term}: scaled {pair_scaled[term]:.1f}% | raw {pair_raw[term]:.1f}%"
            )
    else:
        print(f"  pairwise Lula vs Bolsonaro unavailable; present terms: {pair_present}")


def main() -> int:
    print(f"Reading processed tab '{PROCESSED_TAB}' from Google Sheets...")
    df = load_processed_tab()
    if df.empty:
        print(
            "The processed tab is empty or missing. Run the Google Trends pipeline "
            "first to repopulate the spreadsheet, then re-run this audit."
        )
        return 1

    audit_columns(df)
    audit_counts(df)
    audit_batches(df)
    audit_anchor_usage(df)
    audit_duplicates(df)
    audit_nulls_and_invalid(df)
    audit_share_2022(df)

    print("\nAudit complete. Outputs in scripts/audit_outputs/. No data was modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
