# 📚 Harezmi Intelligence - Documentation Index

Welcome to the Harezmi Intelligence documentation. This folder contains all project guides and references.

## 🚀 Quick Navigation

### For New Developers
1. **[Setup Guide](./SETUP.md)** - Complete setup instructions
2. **[Quick Reference](./QUICK_REFERENCE.md)** - Common commands at a glance
3. **[Shell Commands](./SHELL_COMMANDS.md)** - Exact commands to run

### For Architecture & Design
1. **[Architecture Guide](./ARCHITECTURE.md)** - Full system architecture
2. **[Implementation Summary](./IMPLEMENTATION.md)** - Technical details

### For Daily Development
1. **[Quick Reference](./QUICK_REFERENCE.md)** - All useful commands
2. **[Make Commands](./MAKE_COMMANDS.txt)** - Available make targets

---

## 📖 File Guide

| File | Purpose | Audience |
|------|---------|----------|
| **SETUP.md** | Installation & initial setup | New developers |
| **ARCHITECTURE.md** | System design & structure | Architects, senior devs |
| **QUICK_REFERENCE.md** | Commands & common tasks | All developers |
| **SHELL_COMMANDS.md** | Step-by-step shell commands | Setup assistance |
| **IMPLEMENTATION.md** | Technical implementation details | Developers |

---

## ⚡ Quick Start (5 Minutes)

### Windows
```powershell
.\setup-dev.ps1
```

### macOS/Linux
```bash
chmod +x setup-dev.sh && ./setup-dev.sh
```

Then:
```bash
docker compose -f infra/docker-compose.dev.yml up -d
uvicorn apps.api.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## 🛠️ Essential Commands

```bash
# Setup
uv venv .venv
source .venv/bin/activate
uv sync --all-groups

# Development
make dev              # Start API server
make up              # Start Docker services
make test            # Run tests
make lint            # Check code quality

# Database
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

## 📁 Project Structure

```
harezmi-intelligence/
├── docs/                    # This documentation folder
├── apps/                    # Application code
├── core/                    # Shared infrastructure
├── services/                # Business logic
├── infra/                   # Docker & deployment
├── tests/                   # Test suite
├── pyproject.toml           # Dependencies
├── Makefile                 # Commands
└── .env.example             # Configuration
```

---

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [PostGIS Manual](https://postgis.net)
- [pgvector GitHub](https://github.com/pgvector/pgvector)

---

**Version:** 1.0.0  
**Last Updated:** February 4, 2026
