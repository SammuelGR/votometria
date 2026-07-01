import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    load_dotenv(find_dotenv())
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Create a '.env' file in the monorepo root containing the DATABASE_URL key."
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return Settings(
        database_url=database_url,
        cors_origins=get_cors_origins(),
    )


def get_ouro_sheet_id() -> str:
    """
    ID of the gold (ouro) spreadsheet that the API reads for market expectations.
    """
    load_dotenv(find_dotenv())
    sheet_id = os.getenv("SHEET_ID_ouro")

    if not sheet_id:
        raise RuntimeError(
            "SHEET_ID_ouro environment variable is not set. Add it to the '.env' "
            "file with the ID of the gold spreadsheet."
        )

    return sheet_id


def get_cors_origins() -> tuple[str, ...]:
    load_dotenv(find_dotenv())

    return _parse_csv_env(
        os.getenv("BACKEND_CORS_ORIGINS"),
        default=(
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ),
    )


def _parse_csv_env(value: str | None, *, default: tuple[str, ...]) -> tuple[str, ...]:
    if not value:
        return default

    return tuple(item.strip() for item in value.split(",") if item.strip())
