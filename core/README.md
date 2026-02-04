# Core Module - Configuration & Database

This module contains the core infrastructure for Harezmi Intelligence:
- Configuration management with Pydantic Settings
- Async SQLAlchemy database setup
- Security utilities

## 📁 Files

| File | Purpose |
|------|---------|
| `config.py` | Application settings using Pydantic Settings |
| `database.py` | Async SQLAlchemy engine and session management |
| `security.py` | JWT authentication and password hashing |
| `usage_example.py` | Example usage with FastAPI |

---

## 🔧 Configuration (`config.py`)

### Features
- ✅ Case-sensitive environment variables
- ✅ Pydantic v2 validation
- ✅ Type-safe settings with Field descriptions
- ✅ PostgreSQL, Redis, and API configuration
- ✅ Feature flags and external service keys

### Usage

```python
from core.config import settings

# Access settings
print(settings.DATABASE_URL)
print(settings.PROJECT_NAME)
print(settings.API_V1_STR)
```

### Environment Variables

All settings can be configured via environment variables. See `.env.example` for full list.

**Key variables:**
- `DATABASE_URL` - PostgreSQL async connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret (generate with `secrets.token_urlsafe(32)`)
- `GROQ_API_KEY` - Groq API key for LLM services

---

## 🗄️ Database (`database.py`)

### Features
- ✅ Async SQLAlchemy 2.0 with asyncpg driver
- ✅ Connection pooling with health checks (`pool_pre_ping=True`)
- ✅ FastAPI dependency injection ready
- ✅ Automatic session management (commit/rollback)
- ✅ PostGIS and pgvector support

### Usage

#### 1. Define Models

```python
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
```

#### 2. Use in FastAPI Endpoints

```python
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

#### 3. Manual Session Usage

```python
from core.database import AsyncSessionLocal

async def some_function():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
```

### Database Initialization

**Development:**
```python
from core.database import init_db

# Create all tables (development only)
await init_db()
```

**Production:**
Use Alembic migrations:
```bash
# Create migration
alembic revision --autogenerate -m "create users table"

# Apply migrations
alembic upgrade head
```

---

## 🔐 Security Utilities (`security.py`)

**To be implemented:**
- JWT token creation and validation
- Password hashing with bcrypt
- OAuth2 password bearer scheme

---

## 📝 Connection Pool Configuration

The database engine is configured with optimal pool settings:

```python
pool_pre_ping=True        # Check connections before use
pool_size=20              # Base pool size
max_overflow=10           # Additional connections allowed
pool_timeout=30           # Timeout waiting for connection
pool_recycle=3600         # Recycle connections after 1 hour
```

**Environment variables:**
- `DB_POOL_SIZE` - Base pool size (default: 20)
- `DB_MAX_OVERFLOW` - Max overflow (default: 10)
- `DB_POOL_TIMEOUT` - Timeout in seconds (default: 30)
- `DB_POOL_RECYCLE` - Recycle time in seconds (default: 3600)
- `DB_ECHO` - Echo SQL queries for debugging (default: false)

---

## 🚀 Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure database URL:**
   ```bash
   # .env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   ```

3. **Import and use:**
   ```python
   from core.config import settings
   from core.database import get_db, Base
   ```

4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

---

## 🧪 Testing

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from core.database import Base

@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "postgresql+asyncpg://user:pass@localhost/test_db",
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

---

## 📚 References

- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [asyncpg](https://github.com/MagicStack/asyncpg)

---

**Version:** 1.0.0  
**Last Updated:** February 5, 2026
