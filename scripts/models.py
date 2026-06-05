from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PolymarketProbability(Base):
    """
    Represents the table of probabilities collected from Polymarket.
    Stores market state snapshots over time.
    """
    __tablename__ = 'polymarket_probabilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)  # Normalized value from 0.00 to 1.00 (based on the Yes token)
    timestamp = Column(DateTime, nullable=False)
    market_id = Column(String(255), nullable=False)   # Unique identifier of the token/market in Polymarket

    __table_args__ = (
        Index('idx_market_timestamp', 'market_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<PolymarketProbability(candidate='{self.candidate_name}', prob={self.probability}, time={self.timestamp})>"
