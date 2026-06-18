import sys

from core.database import create_session
from pipelines.google_trends import run_google_trends_pipeline
from pipelines.polymarket import run_polymarket_pipeline


def main() -> int:
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

    # Google Trends is database-independent and writes CSV files. A failure here
    # must not break the rest of the execution, so it is isolated in its own block.
    try:
        result = run_google_trends_pipeline()
        print(result)
    except Exception as exc:
        print(f"Google Trends pipeline failure: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
