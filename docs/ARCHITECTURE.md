# Harezmi Intelligence - Architecture & Setup Guide

## 📋 Project Overview

**Harezmi Intelligence** is a production-grade SaaS platform for travel engine optimization. This document provides a complete guide to the project architecture, setup, and deployment.

**Original Project:** MergenX (Prototype)  
**Production Platform:** Harezmi Intelligence v1.0.0  
**Tech Stack:** FastAPI, PostgreSQL+PostGIS, Redis, SQLAlchemy (async), Pydantic v2

---

## 🏗️ Architecture

### Hexagonal/Modular Architecture

```
harezmi-intelligence/
├── apps/                          # Application entry points
│   ├── api/                       # FastAPI application
│   │   ├── main.py               # API entry point
│   │   └── v1/                   # API v1 routes
│   │       ├── search.py         # Search endpoints
│   │       └── tenants.py        # Multi-tenant endpoints
│   └── dashboard/                # Streamlit dashboard
│
├── core/                          # Shared infrastructure
│   ├── config.py                 # Settings & configuration (pydantic-settings)
│   ├── database.py               # SQLAlchemy async engine & session
│   └── security.py               # JWT, password hashing, auth utilities
│
├── services/                      # Business logic & domain models
│   ├── ai/                        # AI/ML services
│   ├── engine/                    # Core search engine logic
│   ├── geo/                       # Geospatial queries (PostGIS)
│   └── providers/                 # External provider integrations
│
├── data_pipeline/                 # Data processing & updates
│   ├── price_updater.py          # Real-time price synchronization
│   └── sync_hotels.py            # Hotel inventory sync
│
├── infra/                         # Infrastructure & deployment
│   ├── docker-compose.dev.yml    # Development services
│   ├── postgres-init.sql         # PostgreSQL initialization (PostGIS, pgvector)
│   └── Dockerfile                 # Application container
│
├── tests/                         # Test suite
│   ├── conftest.py               # pytest configuration & fixtures
│   └── ...                        # Unit, integration tests
│
├── pyproject.toml                 # uv workspace & dependencies
├── Makefile                       # Development commands
├── setup-dev.sh / setup-dev.ps1  # Initialization scripts
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+ (recommended: 3.12 or 3.13)
- Docker Desktop & Docker Compose
- Git

### Option 1: Automated Setup (Recommended)

#### Windows (PowerShell):
```powershell
.\setup-dev.ps1
```

#### macOS/Linux (Bash):
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

### Option 2: Manual Setup

#### Step 1: Install UV Package Manager
```bash
pip install uv
```

#### Step 2: Create Virtual Environment
```bash
uv venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

#### Step 3: Install Dependencies
```bash
uv sync --all-groups
```

#### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Step 5: Start Docker Services
```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

#### Step 6: Verify Database Connection
```bash
psql postgresql://harezmi:harezmi_dev_password@localhost:5432/harezmi_dev
```

---

## 📦 Dependency Management

### Dependencies Added

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | 0.109.0 | Web framework |
| **uvicorn[standard]** | 0.27.0 | ASGI server |
| **sqlalchemy[asyncio]** | 2.0.23 | ORM (async) |
| **alembic** | 1.13.1 | Database migrations |
| **pydantic** | 2.6.3 | Data validation |
| **pydantic-settings** | 2.2.1 | Configuration management |
| **asyncpg** | 0.29.0 | PostgreSQL async driver |
| **geoalchemy2** | 0.14.1 | PostGIS integration |
| **pgvector** | 0.2.1 | Vector/embedding support |
| **python-jose[cryptography]** | 3.3.0 | JWT tokens |
| **passlib[bcrypt]** | 1.7.4 | Password hashing |

### Dev Dependencies

```
pytest, pytest-asyncio, pytest-cov
black, ruff, mypy
pre-commit
ipython
```

### Using UV

```bash
# Add a new dependency
uv pip install package-name

# Add dev dependency
uv pip install --extra dev package-name

# Sync all dependencies
uv sync --all-groups

# Upgrade all packages
uv lock --upgrade
```

---

## 🐳 Docker Infrastructure

### Services (docker-compose.dev.yml)

#### PostgreSQL 15 with PostGIS + pgvector
- **Image:** postgis/postgis:15-3.4
- **Port:** 5432
- **Extensions:**
  - `postgis` - Geospatial queries
  - `vector` - Vector embeddings
  - `uuid-ossp` - UUID generation
  - `jsonb_utils` - JSON operations
- **Data Volume:** `postgres_data_dev`
- **Init Script:** `postgres-init.sql`

#### Redis 7 (Alpine)
- **Image:** redis:7-alpine
- **Port:** 6379
- **Data Volume:** `redis_data_dev`
- **Features:** AOF persistence enabled

### Docker Compose Commands

```bash
# Start services
docker compose -f infra/docker-compose.dev.yml up -d

# Stop services
docker compose -f infra/docker-compose.dev.yml down

# View logs
docker compose -f infra/docker-compose.dev.yml logs -f

# Remove volumes (reset databases)
docker compose -f infra/docker-compose.dev.yml down -v

# Rebuild services
docker compose -f infra/docker-compose.dev.yml up -d --build
```

---

## ⚙️ Environment Configuration (.env)

### Critical Settings

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256

# API
API_PORT=8000
DEBUG=true  # Set to false in production
```

**⚠️ IMPORTANT:** Never commit `.env` to version control. Use `.env.example` as template.

---

## 🧪 Development Workflow

### Available Make Commands

```bash
make help              # Show all commands
make install           # Install dependencies
make dev              # Start API server (with hot reload)
make up               # Start Docker services
make down             # Stop Docker services
make migrate          # Run database migrations
make test             # Run tests with coverage
make lint             # Run linter (ruff)
make format           # Format code (black)
make clean            # Remove cache files
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "add_users_table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=core --cov=services

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run async tests
pytest --asyncio-mode=auto
```

### Code Quality

```bash
# Lint code
ruff check . --fix

# Format code
black . --line-length 100

# Type checking
mypy apps core services

# Pre-commit hooks
pre-commit run --all-files
```

---

## 🚀 Running the Application

### Development Mode (Hot Reload)

```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points

- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **API Health:** http://localhost:8000/health
- **Redis:** localhost:6379
- **PostgreSQL:** localhost:5432

---

## 🔐 Security Best Practices

1. **Environment Variables:** Never commit sensitive data
2. **Database:** Use strong passwords in production
3. **Secret Key:** Generate a strong SECRET_KEY for production
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
4. **CORS:** Restrict CORS origins in production
5. **JWT Tokens:** Set appropriate token expiration times
6. **Password Hashing:** Use bcrypt with appropriate cost factor

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Base Infrastructure | ✅ Complete | uv, Docker, settings configured |
| Database Setup | ✅ Complete | PostgreSQL + PostGIS + pgvector |
| API Framework | ✅ Ready | FastAPI configured |
| Authentication | ⏳ Pending | Implement JWT auth in core/security.py |
| Services | ⏳ Pending | Implement business logic |
| Tests | ⏳ Pending | Add unit & integration tests |
| Documentation | ⏳ Pending | Generate API docs |

---

## 🔗 Related Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [PostGIS Documentation](https://postgis.net)
- [pgvector](https://github.com/pgvector/pgvector)

---

## 📧 Support

For issues or questions, refer to the architecture decisions in this document and the inline code comments throughout the project.

**Last Updated:** February 4, 2026  
**Version:** 1.0.0
