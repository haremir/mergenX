"""
Example usage of the config and database modules.

This file demonstrates how to use the configuration and database
setup in a FastAPI application with async SQLAlchemy.
"""
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings
from core.database import Base, engine, get_db


# ============================================================================
# Example ORM Model
# ============================================================================
class User(Base):
    """Example User model using SQLAlchemy 2.0 syntax."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)


# ============================================================================
# FastAPI Application Setup
# ============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    # In production, use Alembic migrations instead
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"✅ {settings.PROJECT_NAME} started")
    print(f"🗄️  Database: {settings.DATABASE_URL}")
    print(f"📦 Redis: {settings.REDIS_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    await engine.dispose()
    print("👋 Application shutdown complete")


# ============================================================================
# Example API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get(f"{settings.API_V1_STR}/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all users.
    
    This demonstrates how to use the async database session
    with FastAPI dependency injection.
    """
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return users


@app.post(f"{settings.API_V1_STR}/users")
async def create_user(
    email: str,
    name: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.
    
    Demonstrates how to create and commit records
    using async SQLAlchemy.
    """
    user = User(email=email, name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ============================================================================
# Run with: uvicorn examples.usage_example:app --reload
# ============================================================================
