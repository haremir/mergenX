# Shell Commands - Harezmi Intelligence Initialization

## Step-by-Step Initialization Commands

### 1️⃣ Install UV Package Manager (Global - One Time)
```bash
pip install uv
```

### 2️⃣ Create Python Virtual Environment
```bash
uv venv .venv
```

### 3️⃣ Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash):**
```bash
source .venv/bin/activate
```

### 4️⃣ Install All Dependencies
```bash
uv sync --all-groups
```

Output should show:
```
Resolved 47 packages in Xs
Downloaded 47 packages in Xs
Installed 47 packages in Xs
```

### 5️⃣ Copy Environment Template
```bash
cp .env.example .env
```

### 6️⃣ Start Docker Services
```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

Expected output:
```
[+] Running 2/2
 ✔ Container harezmi-postgres-dev  Started
 ✔ Container harezmi-redis-dev     Started
```

### 7️⃣ Verify Database Connection
```bash
psql postgresql://harezmi:harezmi_dev_password@localhost:5432/harezmi_dev
```

Or using Docker:
```bash
docker compose -f infra/docker-compose.dev.yml exec postgres psql -U harezmi -d harezmi_dev
```

### 8️⃣ Start Development Server
```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Started server process [12345]
Waiting for application startup.
Application startup complete.
```

---

## Automated Setup (Single Command)

### Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup-dev.ps1
```

### macOS/Linux (Bash):
```bash
chmod +x setup-dev.sh && ./setup-dev.sh
```

---

## Common Workflows

### Run API Server
```bash
uvicorn apps.api.main:app --reload
```

### Run Tests
```bash
pytest tests/ -v --cov=apps --cov=core --cov=services
```

### Format Code
```bash
black . --line-length 100
```

### Lint Code
```bash
ruff check . --fix
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "your_migration_name"

# Apply migrations
alembic upgrade head
```

### Stop Docker Services
```bash
docker compose -f infra/docker-compose.dev.yml down
```

### View Docker Logs
```bash
docker compose -f infra/docker-compose.dev.yml logs -f
```

---

## Using Make (If Available)

```bash
make help              # Show all commands
make install           # Install dependencies
make dev              # Start API server
make up               # Start Docker services
make down             # Stop Docker services
make test             # Run tests
make lint             # Lint code
make format           # Format code
make clean            # Clean cache files
```

---

## Troubleshooting

### If `uv` command not found:
```bash
pip install uv
```

### If Docker not running:
```bash
# Windows: Start Docker Desktop from Applications
# macOS: Start Docker from Applications
# Linux: sudo systemctl start docker
```

### If PostgreSQL connection fails:
```bash
# Check if Docker container is running
docker compose -f infra/docker-compose.dev.yml ps

# Check Docker logs
docker compose -f infra/docker-compose.dev.yml logs postgres

# Restart services
docker compose -f infra/docker-compose.dev.yml restart
```

### If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000

# Or use a different port
uvicorn apps.api.main:app --reload --port 8001
```

---

## Verification Commands

### Check Python Version
```bash
python --version
# Expected: Python 3.11+ (recommended 3.12 or 3.13)
```

### Verify Virtual Environment
```bash
which python  # macOS/Linux
where python  # Windows
# Should show path to .venv/bin/python or .venv\Scripts\python.exe
```

### List Installed Packages
```bash
uv pip list
```

### Check Database Connection
```bash
# PostgreSQL
psql postgresql://harezmi:harezmi_dev_password@localhost:5432/harezmi_dev -c "SELECT 1"

# Or with Docker
docker compose -f infra/docker-compose.dev.yml exec postgres pg_isready
```

### Check Redis Connection
```bash
redis-cli ping
# Expected output: PONG

# Or with Docker
docker compose -f infra/docker-compose.dev.yml exec redis redis-cli ping
```

### Verify FastAPI is Running
```bash
curl http://localhost:8000/docs
# or open in browser: http://localhost:8000/docs
```

---

## Quick Reference: Most Important Commands

```bash
# Setup (do once)
uv venv .venv
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows
uv sync --all-groups
cp .env.example .env

# Daily development
docker compose -f infra/docker-compose.dev.yml up -d  # Start services
uvicorn apps.api.main:app --reload  # Start API
pytest tests/  # Run tests

# Cleanup
docker compose -f infra/docker-compose.dev.yml down  # Stop services
```

---

**Version:** 1.0.0  
**Last Updated:** February 4, 2026
