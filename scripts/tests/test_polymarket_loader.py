from tests.helpers import naive_utc_datetime, probability_record
from core.catalog import get_or_create_candidate_catalog_entry
from loaders.polymarket import get_latest_timestamps_by_market, save_probability_records
from models import PolymarketProbability


def create_candidate_catalog_entry(db_session, source_key="market-1", raw_name="Candidate A"):
    return get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key=source_key,
        raw_name=raw_name,
    )


def test_get_latest_timestamps_by_market_returns_latest_timestamp(db_session):
    candidate_a = create_candidate_catalog_entry(db_session)
    candidate_b = create_candidate_catalog_entry(
        db_session,
        source_key="market-2",
        raw_name="Candidate B",
    )
    db_session.add_all(
        [
            PolymarketProbability(
                candidate_catalog_id=candidate_a.id,
                market_id="market-1",
                candidate_name="Candidate A",
                probability=0.40,
                timestamp=naive_utc_datetime(2024, 1, 1, 10),
            ),
            PolymarketProbability(
                candidate_catalog_id=candidate_a.id,
                market_id="market-1",
                candidate_name="Candidate A",
                probability=0.42,
                timestamp=naive_utc_datetime(2024, 1, 1, 12),
            ),
            PolymarketProbability(
                candidate_catalog_id=candidate_b.id,
                market_id="market-2",
                candidate_name="Candidate B",
                probability=0.20,
                timestamp=naive_utc_datetime(2024, 1, 1, 8),
            ),
        ]
    )
    db_session.commit()

    latest_timestamps = get_latest_timestamps_by_market(db_session)

    assert latest_timestamps == {
        "market-1": naive_utc_datetime(2024, 1, 1, 12),
        "market-2": naive_utc_datetime(2024, 1, 1, 8),
    }


def test_save_probability_records_persists_new_records(db_session):
    candidate_a = create_candidate_catalog_entry(db_session)
    candidate_b = create_candidate_catalog_entry(
        db_session,
        source_key="market-2",
        raw_name="Candidate B",
    )
    records = [
        probability_record(
            market_id="market-1",
            candidate_catalog_id=candidate_a.id,
            hour=10,
        ),
        probability_record(
            market_id="market-2",
            candidate_catalog_id=candidate_b.id,
            candidate_name="Candidate B",
            hour=11,
        ),
    ]

    saved_count = save_probability_records(db_session, records)
    db_session.commit()

    saved_records = db_session.query(PolymarketProbability).all()
    assert saved_count == 2
    assert [(record.market_id, record.timestamp) for record in saved_records] == [
        ("market-1", naive_utc_datetime(2024, 1, 1, 10)),
        ("market-2", naive_utc_datetime(2024, 1, 1, 11)),
    ]


def test_save_probability_records_skips_records_already_saved_in_database(db_session):
    candidate = create_candidate_catalog_entry(db_session)
    already_saved_record = PolymarketProbability(
        candidate_catalog_id=candidate.id,
        market_id="market-1",
        candidate_name="Candidate A",
        probability=0.40,
        timestamp=naive_utc_datetime(2024, 1, 1, 10),
    )
    db_session.add(already_saved_record)
    db_session.commit()

    record_already_saved_in_database = probability_record(
        market_id="market-1",
        candidate_catalog_id=candidate.id,
        hour=10,
    )
    new_record = probability_record(
        market_id="market-1",
        candidate_catalog_id=candidate.id,
        hour=11,
    )

    saved_count = save_probability_records(
        db_session,
        [record_already_saved_in_database, new_record],
    )
    db_session.commit()

    saved_records = (
        db_session.query(PolymarketProbability)
        .order_by(PolymarketProbability.timestamp)
        .all()
    )
    assert saved_count == 1
    assert [(record.market_id, record.timestamp) for record in saved_records] == [
        ("market-1", naive_utc_datetime(2024, 1, 1, 10)),
        ("market-1", naive_utc_datetime(2024, 1, 1, 11)),
    ]


def test_save_probability_records_skips_duplicate_records_from_same_batch(db_session):
    candidate = create_candidate_catalog_entry(db_session)
    new_record = probability_record(
        market_id="market-1",
        candidate_catalog_id=candidate.id,
        hour=10,
    )
    same_record_repeated_in_batch = probability_record(
        market_id="market-1",
        candidate_catalog_id=candidate.id,
        hour=10,
    )

    saved_count = save_probability_records(
        db_session,
        [new_record, same_record_repeated_in_batch],
    )
    db_session.commit()

    saved_records = db_session.query(PolymarketProbability).all()
    assert saved_count == 1
    assert [(record.market_id, record.timestamp) for record in saved_records] == [
        ("market-1", naive_utc_datetime(2024, 1, 1, 10)),
    ]
