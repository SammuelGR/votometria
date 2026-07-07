import pandas as pd

from pipelines import google_trends as gt_pipeline

GROUPS = {
    "2022": {
        "timeframe": "2022-01-01 2022-12-31",
        "anchor_term": "Lula",
        "terms": ["Lula", "Jair Bolsonaro", "Simone Tebet", "Ciro Gomes", "Tebet2", "Tebet3"],
    },
    "current": {
        "timeframe": "today 12-m",
        "anchor_term": "Lula",
        "terms": [],
    },
}


def _fake_fetch(terms, timeframe, geo, hl, tz):
    """Returns a wide DataFrame with one column per requested term."""
    index = pd.to_datetime(["2022-03-13", "2022-03-20"])
    index.name = "date"
    data = {term: [50, 40] for term in terms}
    data["isPartial"] = [False, False]
    return pd.DataFrame(data, index=index)


def _patch_pipeline(monkeypatch):
    saved = {"raw": [], "year": [], "all": []}

    def fake_save_raw(spreadsheet, df, election_year, batch_id):
        saved["raw"].append((election_year, batch_id))
        return f"raw_google_trends_{election_year}_{batch_id}"

    def fake_save_year(spreadsheet, df, election_year):
        saved["year"].append((election_year, len(df)))
        return f"proc_google_trends_{election_year}_interest_long"

    def fake_save_all(spreadsheet, df):
        saved["all"].append(len(df))
        return "proc_google_trends_all_elections_interest_long"

    monkeypatch.setattr(gt_pipeline, "GOOGLE_TRENDS_ELECTION_GROUPS", GROUPS)
    monkeypatch.setattr(gt_pipeline, "fetch_interest_over_time_batch", _fake_fetch)
    # The spreadsheet objects are opaque to the pipeline; sentinels are enough.
    # raw -> bronze, rescaled -> prata, consolidated -> ouro.
    monkeypatch.setattr(
        gt_pipeline,
        "get_layer_spreadsheets",
        lambda *layers: {"bronze": object(), "prata": object(), "ouro": object()},
    )
    monkeypatch.setattr(gt_pipeline, "save_raw_google_trends_batch", fake_save_raw)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_year", fake_save_year)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_all", fake_save_all)
    return saved


def test_pipeline_returns_summary_for_each_group(monkeypatch):
    _patch_pipeline(monkeypatch)

    result = gt_pipeline.run_google_trends_pipeline()

    assert result["source"] == "google_trends"
    assert result["status"] == "success"
    assert set(result["groups"].keys()) == {"2022", "current"}

    summary_2022 = result["groups"]["2022"]
    # 6 terms, anchor "Lula" -> 5 candidates -> ceil(5/4) = 2 batches
    assert summary_2022["terms_count"] == 6
    assert summary_2022["batches_count"] == 2
    assert summary_2022["processed_rows"] > 0
    assert summary_2022["processed_tab"] == "proc_google_trends_2022_interest_long"


def test_pipeline_skips_empty_current_group_without_breaking(monkeypatch):
    _patch_pipeline(monkeypatch)

    result = gt_pipeline.run_google_trends_pipeline()

    current = result["groups"]["current"]
    assert current["terms_count"] == 0
    assert current["batches_count"] == 0
    assert current["processed_rows"] == 0
    assert current["processed_tab"] is None


def test_pipeline_writes_consolidated_file(monkeypatch):
    saved = _patch_pipeline(monkeypatch)

    result = gt_pipeline.run_google_trends_pipeline()

    assert result["all_processed_tab"] == "proc_google_trends_all_elections_interest_long"
    assert len(saved["all"]) == 1
    # raw saved once per batch of the non-empty group
    assert saved["raw"] == [("2022", "batch_01"), ("2022", "batch_02")]


GROUPS_WITH_MIN_DATE = {
    "2022": {
        "timeframe": "2022-01-01 2022-12-31",
        "anchor_term": "Lula",
        "terms": ["Lula", "Bolsonaro"],
    },
    "current": {
        "timeframe": "today 12-m",
        "anchor_term": "Lula",
        "terms": ["Lula", "Bolsonaro"],
        "min_date": "2026-01-01",
    },
}


def _fake_fetch_spanning_years(terms, timeframe, geo, hl, tz):
    """Returns a wide DataFrame with dates on both sides of 2026-01-01."""
    index = pd.to_datetime(["2025-11-01", "2025-12-15", "2026-01-01", "2026-02-01"])
    index.name = "date"
    data = {term: [10, 20, 30, 40] for term in terms}
    data["isPartial"] = [False, False, False, False]
    return pd.DataFrame(data, index=index)


def test_pipeline_filters_current_group_rows_before_min_date(monkeypatch):
    saved = {"raw": [], "year": [], "all": []}

    def fake_save_raw(spreadsheet, df, election_year, batch_id):
        saved["raw"].append((election_year, batch_id))
        return f"raw_google_trends_{election_year}_{batch_id}"

    def fake_save_year(spreadsheet, df, election_year):
        saved["year"].append((election_year, len(df)))
        return f"proc_google_trends_{election_year}_interest_long"

    def fake_save_all(spreadsheet, df):
        saved["all"].append(len(df))
        return "proc_google_trends_all_elections_interest_long"

    monkeypatch.setattr(gt_pipeline, "GOOGLE_TRENDS_ELECTION_GROUPS", GROUPS_WITH_MIN_DATE)
    monkeypatch.setattr(gt_pipeline, "fetch_interest_over_time_batch", _fake_fetch_spanning_years)
    monkeypatch.setattr(
        gt_pipeline,
        "get_layer_spreadsheets",
        lambda *layers: {"bronze": object(), "prata": object(), "ouro": object()},
    )
    monkeypatch.setattr(gt_pipeline, "save_raw_google_trends_batch", fake_save_raw)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_year", fake_save_year)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_all", fake_save_all)

    result = gt_pipeline.run_google_trends_pipeline()

    # "current" has min_date: only the 2 dates from 2026 survive, x 2 terms
    # (Lula, Bolsonaro) = 4 rows.
    current_summary = result["groups"]["current"]
    assert current_summary["processed_rows"] == 4
    assert ("current", 4) in saved["year"]

    # "2022" has no min_date: all 4 dates x 2 terms = 8 rows survive, unaffected.
    summary_2022 = result["groups"]["2022"]
    assert summary_2022["processed_rows"] == 8
    assert ("2022", 8) in saved["year"]
