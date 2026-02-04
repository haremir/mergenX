# Setup Guide - Harezmi Intelligence

## 🚀 Quick Start (5 Minutes)

### Automated Setup (Recommended)

**Windows:**
```powershell
.\setup-dev.ps1
```

**macOS/Linux:**
```bash
chmod +x setup-dev.sh && ./setup-dev.sh
```

Then start developing:
```bash
docker compose -f infra/docker-compose.dev.yml up -d
uvicorn apps.api.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## Manual Setup (8 Steps)

### 1. Install UV
```bash
pip install uv
```

### 2. Create Virtual Environment
```bash
uv venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
uv sync --all-groups
```

### 5. Configure Environment
```bash
cp .env.example .env
# Optional: edit .env with your values
```

### 6. Start Docker Services
```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

### 7. Verify Services
```bash
# Check all services are running
docker compose -f infra/docker-compose.dev.yml ps

# Test database
docker compose -f infra/docker-compose.dev.yml exec postgres pg_isready

# Test Redis
docker compose -f infra/docker-compose.dev.yml exec redis redis-cli ping
```

### 8. Start Development Server
```bash
uvicorn apps.api.main:app --reload
```

---

## Project Structure

```
harezmi-intelligence/
├── apps/                    # Application code
│   ├── api/                # FastAPI endpoints
│   └── dashboard/          # Streamlit dashboard
├── core/                    # Shared infrastructure
│   ├── config.py           # Pydantic Settings
│   ├── database.py         # SQLAlchemy async
│   └── security.py         # JWT & auth
├── services/                # Business logic
├── data_pipeline/           # Data processing
├── infra/                   # Docker & deployment
├── tests/                   # Test suite
├── pyproject.toml           # Dependencies
├── Makefile                 # Common commands
├── .env.example             # Configuration
└── docs/                    # Documentation
```

---

## Essential Files

| File | Purpose |
|------|---------|
| **pyproject.toml** | Dependencies & project config |
| **.env.example** | Environment template |
| **docker-compose.dev.yml** | Development services |
| **Makefile** | Development commands |
| **setup-dev.ps1** / **setup-dev.sh** | Automated setup scripts |

---

## Key Technologies

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL + PostGIS + pgvector** - Database
- **Redis** - Caching layer
- **Pydantic v2** - Data validation
- **Pytest** - Testing framework

---

## Common Commands

```bash
# Start development
make dev              # Start API server

# Docker
make up              # Start services
make down            # Stop services
make logs            # View logs

# Code quality
make lint            # Check code
make format          # Format code
make test            # Run tests

# Database
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

## Accessing the Application

- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

---

## Documentation

See [docs/README.md](../docs/README.md) for complete documentation:
- **ARCHITECTURE.md** - System design
- **QUICK_REFERENCE.md** - All commands
- **SHELL_COMMANDS.md** - Setup steps

---

## Next Steps

1. ✅ Setup complete
2. Create database models in `core/database.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "initial"`
4. Implement authentication in `core/security.py`
5. Create API endpoints in `apps/api/v1/`

---

**Version:** 1.0.0  
**Last Updated:** February 4, 2026
