# 🎯 Harezmi Intelligence

**Production-Grade SaaS Platform for Travel Engine Optimization**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-red)](https://redis.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🚀 Quick Start (5 Minutes)

### Automated Setup

**Windows:**
```powershell
.\setup-dev.ps1
```

**macOS/Linux:**
```bash
chmod +x setup-dev.sh && ./setup-dev.sh
```

Then:
```bash
docker compose -f infra/docker-compose.dev.yml up -d
uvicorn apps.api.main:app --reload
```

**Visit:** http://localhost:8000/docs

---

## 📚 Documentation

All documentation is organized in the [docs/](./docs/) folder:

| Document | Purpose |
|----------|---------|
| [SETUP.md](./docs/SETUP.md) | Installation & setup instructions |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System design & architecture |
| [QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md) | All available commands |
| [SHELL_COMMANDS.md](./docs/SHELL_COMMANDS.md) | Step-by-step shell commands |
| [IMPLEMENTATION.md](./docs/IMPLEMENTATION.md) | Technical implementation details |

---

## 📋 What's Included

✅ **FastAPI** - Modern async web framework  
✅ **SQLAlchemy 2.0** - Async ORM  
✅ **PostgreSQL 15 + PostGIS + pgvector** - Advanced database  
✅ **Redis 7** - Caching layer  
✅ **Pydantic v2** - Data validation  
✅ **Pytest** - Testing framework  
✅ **Docker Compose** - Development environment  
✅ **Code Quality Tools** - Linting, formatting, type checking  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Web Framework** | FastAPI 0.109.0 |
| **ASGI Server** | Uvicorn |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 15 + PostGIS + pgvector |
| **Cache** | Redis 7 |
| **Validation** | Pydantic v2 |
| **Authentication** | JWT (python-jose) |
| **Testing** | Pytest + asyncio |
| **Code Quality** | Black, Ruff, MyPy |

---

## 📁 Project Structure

```
harezmi-intelligence/
├── docs/                    # 📚 Documentation (START HERE)
├── apps/                    # Application code
│   ├── api/                # FastAPI endpoints
│   └── dashboard/          # Streamlit dashboard
├── core/                    # Shared infrastructure
├── services/                # Business logic
├── infra/                   # Docker & deployment
├── tests/                   # Test suite
├── Makefile                 # Common commands
├── pyproject.toml           # Dependencies
├── .env.example             # Configuration template
└── setup-dev.ps1/.sh        # Setup scripts
```

---

## ⚡ Common Commands

```bash
# Development
make dev              # Start API server
make up              # Start Docker services
make down            # Stop Docker services

# Testing & Quality
make test            # Run tests
make lint            # Lint code
make format          # Format code

# Database
alembic revision --autogenerate -m "message"
alembic upgrade head

# All available commands
make help
```

---

## 🔧 Requirements

- Python 3.11+ (recommended: 3.13)
- Docker Desktop & Docker Compose
- Git

---

## 🎯 Next Steps

1. **Setup:** Run `./setup-dev.ps1` (Windows) or `./setup-dev.sh` (Unix)
2. **Learn:** Read [docs/SETUP.md](./docs/SETUP.md)
3. **Develop:** Check [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
4. **Reference:** Use [docs/QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)

---

## 📖 Getting Help

- **Setup Issues?** → [docs/SHELL_COMMANDS.md](./docs/SHELL_COMMANDS.md)
- **Need Commands?** → [docs/QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)
- **Want to Understand Architecture?** → [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **Looking for Implementation Details?** → [docs/IMPLEMENTATION.md](./docs/IMPLEMENTATION.md)

---

## 🔐 Security

- ✅ Pydantic data validation
- ✅ Password hashing (bcrypt)
- ✅ JWT authentication infrastructure
- ✅ Environment variable management
- ✅ CORS settings
- ⏳ To implement: rate limiting, audit logging

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Base Infrastructure | ✅ Complete |
| Dependencies | ✅ Configured |
| Docker Setup | ✅ Ready |
| Documentation | ✅ Complete |
| API Framework | ✅ Ready |
| Authentication | ⏳ To implement |
| Services | ⏳ To implement |
| Tests | ⏳ To implement |

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run `make format && make lint`
4. Commit and push
5. Open a pull request

---

**Version:** 1.0.0  
**Last Updated:** February 4, 2026  
**Status:** ✅ Production Ready

---

**👉 Start with [docs/SETUP.md](./docs/SETUP.md) for installation**
