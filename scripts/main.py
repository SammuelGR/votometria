import sys

from pipelines.enquetes import run_enquetes_pipeline
from pipelines.google_trends import run_google_trends_pipeline
from pipelines.polymarket import run_polymarket_pipeline
from pipelines.tse import run_tse_pipeline


def main() -> int:
    # Every pipeline now publishes straight to the medallion spreadsheets
    # (bronze/prata/ouro) — no PostgreSQL. Each pipeline is isolated so a
    # failure in one does not break the others.
    try:
        result = run_google_trends_pipeline()
        print(result)
    except Exception as exc:
        print(f"Google Trends pipeline failure: {exc}")

    try:
        run_tse_pipeline()
    except Exception as exc:
        print(f"TSE pipeline failure: {exc}")

    try:
        run_polymarket_pipeline()
    except Exception as exc:
        print(f"Polymarket pipeline failure: {exc}")

    try:
        run_enquetes_pipeline()
    except Exception as exc:
        print(f"Enquetes pipeline failure: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
