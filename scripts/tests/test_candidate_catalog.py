from core.catalog import get_or_create_candidate_catalog_entry, normalize_candidate_name
from models import CandidateCatalog


def test_normalize_candidate_name_returns_lowercase_ascii_without_extra_spacing():
    normalized_name = normalize_candidate_name("  Luiz Inácio   Lula da Silva!!! ")

    assert normalized_name == "luiz inacio lula da silva"


def test_get_or_create_candidate_catalog_entry_creates_candidate(db_session):
    candidate = get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key="market-1",
        raw_name="Luiz Inácio Lula da Silva",
    )
    db_session.commit()

    saved_candidate = db_session.query(CandidateCatalog).one()
    assert candidate.id == saved_candidate.id
    assert saved_candidate.source == "polymarket"
    assert saved_candidate.source_key == "market-1"
    assert saved_candidate.raw_name == "Luiz Inácio Lula da Silva"
    assert saved_candidate.display_name == "Luiz Inácio Lula da Silva"
    assert saved_candidate.normalized_name == "luiz inacio lula da silva"


def test_get_or_create_candidate_catalog_entry_reuses_existing_candidate(db_session):
    first_candidate = get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key="market-1",
        raw_name="Luiz Inácio Lula da Silva",
    )
    second_candidate = get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key="market-1",
        raw_name="Luiz Inácio Lula da Silva",
    )
    db_session.commit()

    assert first_candidate.id == second_candidate.id
    assert db_session.query(CandidateCatalog).count() == 1


def test_get_or_create_candidate_catalog_entry_preserves_manual_display_name(db_session):
    candidate = get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key="market-1",
        raw_name="Luiz Inácio Lula da Silva",
    )
    candidate.display_name = "Lula"
    candidate.normalized_name = normalize_candidate_name(candidate.display_name)
    db_session.commit()

    same_candidate = get_or_create_candidate_catalog_entry(
        db_session,
        source="polymarket",
        source_key="market-1",
        raw_name="Luiz Inácio Lula da Silva",
    )
    db_session.commit()

    assert same_candidate.display_name == "Lula"
    assert same_candidate.normalized_name == "lula"
