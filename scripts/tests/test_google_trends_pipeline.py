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

    def fake_save_raw(df, output_dir, election_year, batch_id):
        saved["raw"].append((election_year, batch_id))
        return f"/fake/dados-brutos/google_trends_{election_year}_{batch_id}.csv"

    def fake_save_year(df, output_dir, election_year):
        saved["year"].append((election_year, len(df)))
        return f"/fake/dados-processados/google_trends_{election_year}_interest_long.csv"

    def fake_save_all(df, output_dir):
        saved["all"].append(len(df))
        return "/fake/dados-processados/google_trends_all_elections_interest_long.csv"

    monkeypatch.setattr(gt_pipeline, "GOOGLE_TRENDS_ELECTION_GROUPS", GROUPS)
    monkeypatch.setattr(gt_pipeline, "fetch_interest_over_time_batch", _fake_fetch)
    monkeypatch.setattr(gt_pipeline, "save_raw_google_trends_batch_csv", fake_save_raw)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_year_csv", fake_save_year)
    monkeypatch.setattr(gt_pipeline, "save_processed_google_trends_all_csv", fake_save_all)
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
    assert summary_2022["processed_path"].endswith("google_trends_2022_interest_long.csv")


def test_pipeline_skips_empty_current_group_without_breaking(monkeypatch):
    _patch_pipeline(monkeypatch)

    result = gt_pipeline.run_google_trends_pipeline()

    current = result["groups"]["current"]
    assert current["terms_count"] == 0
    assert current["batches_count"] == 0
    assert current["processed_rows"] == 0
    assert current["processed_path"] is None


def test_pipeline_writes_consolidated_file(monkeypatch):
    saved = _patch_pipeline(monkeypatch)

    result = gt_pipeline.run_google_trends_pipeline()

    assert result["all_processed_path"].endswith(
        "google_trends_all_elections_interest_long.csv"
    )
    assert len(saved["all"]) == 1
    # raw saved once per batch of the non-empty group
    assert saved["raw"] == [("2022", "batch_01"), ("2022", "batch_02")]
