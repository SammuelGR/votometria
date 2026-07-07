"""
Reusable Google Sheets client and writer.

Used by data pipelines that publish datasets straight to a spreadsheet.
Configuration is read from the project ``.env`` file:

    GOOGLE_SHEETS_ID            ID of the destination spreadsheet.
    GOOGLE_SERVICE_ACCOUNT_FILE Path to the service account JSON key file.
"""

import os
from pathlib import Path

import pandas as pd
import gspread
from dotenv import find_dotenv, load_dotenv
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

from constants import PROJECT_ROOT

# Opening a spreadsheet by its key only requires the spreadsheets scope; the
# broader Drive scope is intentionally omitted so the service account stays
# least-privilege.
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def load_sheets_settings() -> tuple[str, Path]:
    """
    Reads and validates the Google Sheets configuration from the project
    ``.env`` file.

    Fails fast with an actionable message when the ``.env`` is absent, when a
    required variable is missing, or when the service account JSON does not
    exist on disk.
    """
    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        raise RuntimeError(
            "No '.env' file was found. Create one in the project root with the "
            "GOOGLE_SHEETS_ID and GOOGLE_SERVICE_ACCOUNT_FILE keys "
            "(see .env.example and docs/google_sheets_sync.md)."
        )

    load_dotenv(dotenv_path)

    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise RuntimeError(
            "GOOGLE_SHEETS_ID is not set. Add it to your '.env' file with the "
            "ID of the destination spreadsheet."
        )

    service_account_value = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_value:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_FILE is not set. Add it to your '.env' file "
            "pointing to the service account JSON key file."
        )

    # Allow relative paths in the .env; resolve them against the repo root so
    # the behaviour is the same no matter where the process is invoked from.
    service_account_file = Path(service_account_value)
    if not service_account_file.is_absolute():
        service_account_file = PROJECT_ROOT / service_account_file

    if not service_account_file.is_file():
        raise RuntimeError(
            "Service account JSON file was not found at "
            f"'{service_account_file}'. Check GOOGLE_SERVICE_ACCOUNT_FILE in "
            "your '.env' (the path may be relative to the project root)."
        )

    return sheets_id, service_account_file


def _resolve_service_account_file() -> Path:
    """
    Reads and validates ``GOOGLE_SERVICE_ACCOUNT_FILE`` (shared by every layer),
    resolving relative paths against the project root.
    """
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)

    service_account_value = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_value:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_FILE is not set. Add it to your '.env' file "
            "pointing to the service account JSON key file."
        )

    service_account_file = Path(service_account_value)
    if not service_account_file.is_absolute():
        service_account_file = PROJECT_ROOT / service_account_file

    if not service_account_file.is_file():
        raise RuntimeError(
            "Service account JSON file was not found at "
            f"'{service_account_file}'. Check GOOGLE_SERVICE_ACCOUNT_FILE in "
            "your '.env' (the path may be relative to the project root)."
        )

    return service_account_file


def open_spreadsheet(sheets_id: str, service_account_file: Path):
    """
    Authenticates with the service account and opens a spreadsheet by its ID.
    """
    credentials = Credentials.from_service_account_file(
        str(service_account_file), scopes=SHEETS_SCOPES
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(sheets_id)


def get_spreadsheet():
    """
    Convenience: loads the settings from the environment and opens the
    destination spreadsheet. Raises a clear ``RuntimeError`` when configuration
    is missing or invalid.
    """
    return open_spreadsheet(*load_sheets_settings())


# --- Medallion architecture (bronze / prata / ouro) -----------------------
#
# Each layer is a separate spreadsheet, configured in the ``.env`` file:
#
#     SHEET_ID_bronze   raw extractor output
#     SHEET_ID_prata    cleaned transformer output
#     SHEET_ID_ouro     final loader output (consumed by the frontend)
#
# The service account (GOOGLE_SERVICE_ACCOUNT_FILE) is shared across layers and
# must be granted Editor access on all three spreadsheets.

LAYER_SHEET_ENV = {
    "bronze": "SHEET_ID_bronze",
    "prata": "SHEET_ID_prata",
    "ouro": "SHEET_ID_ouro",
}

# Cache one open spreadsheet handle per layer so a pipeline run authenticates
# and opens each spreadsheet only once.
_LAYER_CACHE: dict[str, object] = {}


def load_layer_sheet_id(layer: str) -> str:
    """
    Reads the spreadsheet ID for a medallion layer from the environment.
    """
    if layer not in LAYER_SHEET_ENV:
        raise ValueError(
            f"Unknown layer '{layer}'. Expected one of {sorted(LAYER_SHEET_ENV)}."
        )

    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)

    env_key = LAYER_SHEET_ENV[layer]
    sheet_id = os.getenv(env_key)
    if not sheet_id:
        raise RuntimeError(
            f"{env_key} is not set. Add it to your '.env' file with the ID of "
            f"the '{layer}' spreadsheet (see docs/google_sheets_sync.md)."
        )
    return sheet_id


def get_layer_spreadsheet(layer: str):
    """
    Opens (and caches) the spreadsheet for a medallion layer: ``bronze``,
    ``prata`` or ``ouro``. Fails fast with a clear message when the layer's
    ``SHEET_ID_*`` variable or the service account JSON is missing.
    """
    if layer in _LAYER_CACHE:
        return _LAYER_CACHE[layer]

    spreadsheet = open_spreadsheet(load_layer_sheet_id(layer), _resolve_service_account_file())
    _LAYER_CACHE[layer] = spreadsheet
    return spreadsheet


def get_layer_spreadsheets(*layers: str) -> dict:
    """
    Opens several layers at once and returns a ``{layer: spreadsheet}`` mapping.
    Defaults to all three layers when called with no arguments.
    """
    if not layers:
        layers = ("bronze", "prata", "ouro")
    return {layer: get_layer_spreadsheet(layer) for layer in layers}


def _dataframe_to_values(df: pd.DataFrame) -> list[list[str]]:
    """
    Converts a DataFrame into a header + rows matrix of strings.

    Everything is emitted as text so values land in the sheet exactly as
    rendered by pandas (no implicit numeric/date coercion by Sheets), and
    missing cells become empty strings instead of the literal ``nan``/``NaT``.
    """
    header = [str(column) for column in df.columns]
    rendered = df.astype(str).where(df.notna(), "")
    return [header] + rendered.values.tolist()


def write_dataframe_to_tab(spreadsheet, title: str, df: pd.DataFrame) -> int:
    """
    Mirrors a DataFrame into the worksheet named ``title``, creating the tab
    when needed and fully replacing its contents otherwise (header + rows,
    ``value_input_option="RAW"``).

    Returns the number of data rows written (excluding the header).
    """
    values = _dataframe_to_values(df)
    num_rows = len(values)
    num_cols = len(values[0]) if values else 1

    try:
        worksheet = spreadsheet.worksheet(title)
        worksheet.clear()
    except WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=title, rows=max(num_rows, 1), cols=max(num_cols, 1)
        )

    # Guarantee the grid is large enough for the payload before writing; a
    # reused tab may be smaller than the new data.
    worksheet.resize(rows=max(num_rows, 1), cols=max(num_cols, 1))
    worksheet.update(range_name="A1", values=values, value_input_option="RAW")

    return max(num_rows - 1, 0)
