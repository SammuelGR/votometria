import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


def load_database_url() -> str:
    """
    Loads the database URL from the project environment.
    """
    load_dotenv(find_dotenv())
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Create a '.env' file in the monorepo root containing the DATABASE_URL key."
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def create_session():
    """
    Creates a SQLAlchemy session and ensures database objects used by the ETL exist.
    """
    engine = create_engine(load_database_url())
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()
