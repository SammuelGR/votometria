from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CandidateCatalog(Base):
    """
    Represents a candidate as observed in a data source.
    """
    __tablename__ = "candidate_catalog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    source_key = Column(String(255), nullable=False)
    raw_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "source_key", name="uq_candidate_catalog_source_key"),
        Index("idx_candidate_catalog_normalized_name", "normalized_name"),
    )

    def __repr__(self):
        return (
            f"<CandidateCatalog(source='{self.source}', source_key='{self.source_key}', "
            f"display_name='{self.display_name}')>"
        )


class PolymarketProbability(Base):
    """
    Represents the table of probabilities collected from Polymarket.
    Stores market state snapshots over time.
    """
    __tablename__ = "polymarket_probabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_catalog_id = Column(Integer, ForeignKey("candidate_catalog.id"), nullable=False)
    candidate_name = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    market_id = Column(String(255), nullable=False)

    candidate_catalog = relationship("CandidateCatalog")

    __table_args__ = (
        Index("idx_market_timestamp", "market_id", "timestamp"),
        Index("idx_polymarket_candidate_catalog_timestamp", "candidate_catalog_id", "timestamp"),
    )

    def __repr__(self):
        return f"<PolymarketProbability(candidate='{self.candidate_name}', prob={self.probability}, time={self.timestamp})>"
