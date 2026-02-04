"""
Async SQLAlchemy database setup for PostgreSQL with PostGIS and pgvector.

This module provides:
- Async database engine configuration
- Session management for FastAPI dependency injection
- Base class for ORM models
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from core.config import settings


# ============================================================================
# Database Engine Configuration
# ============================================================================
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    # Use NullPool for testing or if you have connection issues
    # poolclass=NullPool,
)


# ============================================================================
# Async Session Factory
# ============================================================================
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================================================
# Declarative Base for ORM Models
# ============================================================================
class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    
    Usage:
        from core.database import Base
        
        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            email: Mapped[str] = mapped_column(String(255), unique=True)
    """
    pass


# ============================================================================
# FastAPI Dependency for Database Session
# ============================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.
    
    Usage in FastAPI endpoints:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session for the request lifecycle
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# Utility Functions
# ============================================================================
async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    WARNING: This should only be used in development.
    In production, use Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Dispose of the database engine and close all connections.
    Should be called on application shutdown.
    """
    await engine.dispose()
