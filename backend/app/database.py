from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from app.config import settings

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def table_exists(table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()
