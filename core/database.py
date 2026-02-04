"""
PostgreSQL ve SQLAlchemy bağlantıları
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Veritabanı konfigürasyonu
DATABASE_URL = "postgresql://user:password@localhost/mergenx"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Veritabanı oturumu al"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
