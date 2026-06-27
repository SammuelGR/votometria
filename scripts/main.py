import sys

from core.database import create_session
from pipelines.google_trends import run_google_trends_pipeline
from pipelines.polymarket import run_polymarket_pipeline
from pipelines.tse import run_tse_pipeline


def main() -> int:
    # Google Trends is database-independent and publishes straight to Google
    # Sheets. A failure here must not break the rest of the execution, so it is
    # isolated before the PostgreSQL-dependent pipelines.
    try:
        result = run_google_trends_pipeline()
        print(result)
    except Exception as exc:
        print(f"Google Trends pipeline failure: {exc}")

    try:
        run_tse_pipeline()
    except Exception as exc:
        print(f"TSE pipeline failure: {exc}")
        return 1

    print("Initiating connection to PostgreSQL...")

    try:
        session = create_session()
    except Exception as exc:
        print(f"Database connection failure: {exc}")
        return 1

    try:
        run_polymarket_pipeline(session)
    except Exception as exc:
        session.rollback()
        print(f"Polymarket pipeline failure: {exc}")
        return 1
    finally:
        session.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
