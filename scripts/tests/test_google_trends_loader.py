import pandas as pd
from gspread.exceptions import WorksheetNotFound

from loaders.google_trends import (
    save_processed_google_trends_all,
    save_processed_google_trends_year,
    save_raw_google_trends_batch,
)


class FakeWorksheet:
    def __init__(self, title):
        self.title = title
        self.cleared = False
        self.resized_to = None
        self.update_call = None

    def clear(self):
        self.cleared = True

    def resize(self, rows, cols):
        self.resized_to = (rows, cols)

    def update(self, range_name, values, value_input_option):
        self.update_call = {
            "range_name": range_name,
            "values": values,
            "value_input_option": value_input_option,
        }


class FakeSpreadsheet:
    """Minimal stand-in for a gspread Spreadsheet capturing tab writes."""

    def __init__(self, existing_titles=()):
        self.tabs = {title: FakeWorksheet(title) for title in existing_titles}
        self.added_titles = []

    def worksheet(self, title):
        if title not in self.tabs:
            raise WorksheetNotFound(title)
        return self.tabs[title]

    def add_worksheet(self, title, rows, cols):
        worksheet = FakeWorksheet(title)
        self.tabs[title] = worksheet
        self.added_titles.append(title)
        return worksheet


def _processed_frame():
    return pd.DataFrame(
        {
            "date": ["2022-03-13"],
            "election_year": ["2022"],
            "term": ["Lula"],
            "interest_raw": [80],
            "interest_scaled": [80.0],
            "geo": ["BR"],
            "timeframe": ["2022-01-01 2022-12-31"],
            "source": ["google_trends"],
            "batch_id": ["batch_01"],
            "anchor_term": ["Lula"],
            "is_anchor": [True],
            "is_partial": [False],
            "collected_at": ["2026-06-18T20:00:00"],
        }
    )


def test_save_raw_batch_writes_prefixed_tab():
    spreadsheet = FakeSpreadsheet()
    index = pd.to_datetime(["2022-03-13"])
    index.name = "date"
    raw_df = pd.DataFrame({"Lula": [80], "isPartial": [False]}, index=index)

    title = save_raw_google_trends_batch(
        spreadsheet, raw_df, election_year="2022", batch_id="batch_01"
    )

    assert title == "raw_google_trends_2022_batch_01"
    assert title in spreadsheet.added_titles

    worksheet = spreadsheet.tabs[title]
    assert worksheet.update_call["value_input_option"] == "RAW"
    values = worksheet.update_call["values"]
    # Header promotes the date index to a "date" column; values are strings.
    assert values[0] == ["date", "Lula", "isPartial"]
    assert values[1] == ["2022-03-13", "80", "False"]


def test_save_processed_year_writes_prefixed_tab():
    spreadsheet = FakeSpreadsheet()

    title = save_processed_google_trends_year(
        spreadsheet, _processed_frame(), election_year="2022"
    )

    assert title == "proc_google_trends_2022_interest_long"
    worksheet = spreadsheet.tabs[title]
    assert worksheet.update_call["values"][0][:3] == ["date", "election_year", "term"]
    assert worksheet.update_call["values"][1][2] == "Lula"


def test_save_processed_all_writes_prefixed_tab():
    spreadsheet = FakeSpreadsheet()

    title = save_processed_google_trends_all(spreadsheet, _processed_frame())

    assert title == "proc_google_trends_all_elections_interest_long"
    assert title in spreadsheet.tabs


def test_existing_tab_is_cleared_and_reused():
    title = "proc_google_trends_2022_interest_long"
    spreadsheet = FakeSpreadsheet(existing_titles=[title])

    save_processed_google_trends_year(
        spreadsheet, _processed_frame(), election_year="2022"
    )

    worksheet = spreadsheet.tabs[title]
    assert worksheet.cleared is True
    # The tab already existed, so no new worksheet should be created.
    assert spreadsheet.added_titles == []
