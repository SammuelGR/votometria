import sys

from core.database import create_session
from pipelines.enquetes import run_enquetes_pipeline
from pipelines.google_trends import run_google_trends_pipeline
from pipelines.polymarket import run_polymarket_pipeline
from pipelines.tse import run_tse_pipeline


def main() -> int:
    # Google Trends, TSE and enquetes publish straight to Google Sheets and need
    # no database; Polymarket still runs against PostgreSQL. Each pipeline is
    # isolated so a failure in one does not break the others.
    try:
        result = run_google_trends_pipeline()
        print(result)
    except Exception as exc:
        print(f"Google Trends pipeline failure: {exc}")

    try:
        run_tse_pipeline()
    except Exception as exc:
        print(f"TSE pipeline failure: {exc}")

    # Polymarket is the only PostgreSQL-dependent pipeline, so it manages its own
    # session and is skipped (without aborting the run) if the DB is unreachable.
    print("Initiating connection to PostgreSQL...")
    try:
        session = create_session()
    except Exception as exc:
        print(f"Database connection failure: {exc}")
        session = None

    if session is not None:
        try:
            run_polymarket_pipeline(session)
        except Exception as exc:
            session.rollback()
            print(f"Polymarket pipeline failure: {exc}")
        finally:
            session.close()

    try:
        run_enquetes_pipeline()
    except Exception as exc:
        print(f"Enquetes pipeline failure: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
