import sys

# from core.database import create_session
# from pipelines.polymarket import run_polymarket_pipeline
from pipelines.tse import run_tse_pipeline


def main() -> int:
    # print("Initiating connection to PostgreSQL...")

    # try:
    #     session = create_session()
    # except Exception as exc:
    #     print(f"Database connection failure: {exc}")
    #     return 1

    # try:
    #     run_polymarket_pipeline(session)
    # except Exception as exc:
    #     session.rollback()
    #     print(f"Polymarket pipeline failure: {exc}")
    #     return 1
    

    try:
        print("\n--- Running TSE Pipeline ---")
        run_tse_pipeline()
    except Exception as exc:
        # session.rollback()
        print(f"TSE pipeline failure: {exc}")
        return 1

    finally:
        # session.close()

        return 0


if __name__ == "__main__":
    sys.exit(main())
