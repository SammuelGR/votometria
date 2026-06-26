import re
import unicodedata

from sqlalchemy.orm import Session

from models import CandidateCatalog


def normalize_candidate_name(value: str) -> str:
    """
    Normalizes a candidate name for matching and catalog inspection.
    """
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
    lowered = without_accents.lower()
    without_punctuation = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", without_punctuation).strip()


def get_or_create_candidate_catalog_entry(
    session: Session,
    source: str,
    source_key: str,
    raw_name: str,
    full_name: str | None = None,
) -> CandidateCatalog:
    """
    Returns a candidate catalog entry, creating it when first observed by an ETL.
    """
    candidate = (
        session.query(CandidateCatalog)
        .filter_by(source=source, source_key=source_key)
        .one_or_none()
    )

    if candidate is not None:
        candidate.raw_name = raw_name
        if candidate.full_name is None and full_name is not None:
            candidate.full_name = full_name
        return candidate

    display_name = full_name or raw_name
    candidate = CandidateCatalog(
        source=source,
        source_key=source_key,
        raw_name=raw_name,
        display_name=display_name,
        normalized_name=normalize_candidate_name(display_name),
        full_name=full_name,
    )
    session.add(candidate)
    session.flush()

    return candidate
