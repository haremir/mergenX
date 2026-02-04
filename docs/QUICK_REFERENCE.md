# Harezmi Intelligence - Quick Reference & Commands

## 🚀 Initialization Commands

### Step 1: Install UV (Global)
```bash
pip install uv
```

### Step 2: Create Virtual Environment
```bash
uv venv .venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash):**
```bash
source .venv/bin/activate
```

### Step 4: Install All Dependencies
```bash
uv sync --all-groups
```

### Step 5: Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### Step 6: Start Docker Services
```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

### Step 7: Verify Database Connection
```bash
# Install psql client if needed
psql postgresql://harezmi:harezmi_dev_password@localhost:5432/harezmi_dev
```

---

## 🐳 Docker Commands

### Start Services
```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

### Stop Services
```bash
docker compose -f infra/docker-compose.dev.yml down
```

### View Logs
```bash
# All services
docker compose -f infra/docker-compose.dev.yml logs -f

# Specific service
docker compose -f infra/docker-compose.dev.yml logs -f postgres
docker compose -f infra/docker-compose.dev.yml logs -f redis
```

### Reset Database (Remove Volumes)
```bash
docker compose -f infra/docker-compose.dev.yml down -v
```

### Check Service Status
```bash
docker compose -f infra/docker-compose.dev.yml ps
```

### Execute Commands in Container
```bash
# PostgreSQL shell
docker compose -f infra/docker-compose.dev.yml exec postgres psql -U harezmi -d harezmi_dev

# Redis shell
docker compose -f infra/docker-compose.dev.yml exec redis redis-cli
```

---

## 🚀 FastAPI Server

### Development Mode (Auto-reload)
```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Custom Port
```bash
uvicorn apps.api.main:app --reload --port 3000
```

### Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 📦 Dependency Management

### Add New Dependency
```bash
uv pip install package-name
```

### Add Development Dependency
```bash
uv pip install --extra dev package-name
```

### Update Locked Dependencies
```bash
uv lock --upgrade
```

### View Installed Packages
```bash
uv pip list
```

### Create Requirements File
```bash
uv pip freeze > requirements.txt
```

---

## 🗄️ Database Migrations (Alembic)

### Initialize Alembic (one-time)
```bash
alembic init migrations
```

### Create New Migration
```bash
alembic revision --autogenerate -m "add_users_table"
```

### Apply Migrations to Database
```bash
alembic upgrade head
```

### Rollback One Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

### Show Current Revision
```bash
alembic current
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=apps --cov=core --cov=services --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_api.py
```

### Run Specific Test Function
```bash
pytest tests/test_api.py::test_health_check
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Output Capture Disabled
```bash
pytest -s
```

### Run Async Tests
```bash
pytest --asyncio-mode=auto
```

---

## 🔍 Code Quality

### Lint Code (Ruff)
```bash
# Check
ruff check .

# Fix issues automatically
ruff check . --fix
```

### Format Code (Black)
```bash
# Format
black . --line-length 100

# Check without formatting
black . --check --line-length 100
```

### Type Checking (MyPy)
```bash
mypy apps core services --ignore-missing-imports
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

### All in One
```bash
# Format + Lint + Type Check
black . --line-length 100 && ruff check . --fix && mypy apps core services --ignore-missing-imports
```

---

## 📊 Database Connection Examples

### PostgreSQL with psql
```bash
psql postgresql://harezmi:harezmi_dev_password@localhost:5432/harezmi_dev
```

### Using Python (asyncpg)
```python
import asyncpg

async def connect():
    conn = await asyncpg.connect(
        user='harezmi',
        password='harezmi_dev_password',
        database='harezmi_dev',
        host='localhost'
    )
    return conn
```

### Using SQLAlchemy
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://harezmi:harezmi_dev_password@localhost/harezmi_dev"
)
```

---

## 🔐 Security & Authentication

### Generate Secret Key (for .env)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Hash Password Manually
```bash
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt']); print(pwd_context.hash('password'))"
```

---

## 📝 Git Commands

### Initialize Repository (if needed)
```bash
git init
git add .
git commit -m "Initial commit: Harezmi Intelligence"
git branch -M main
git remote add origin https://github.com/haremir/mergenX.git
git push -u origin main
```

### Check Status
```bash
git status
```

### Make a Commit
```bash
git add .
git commit -m "feat: add feature description"
git push
```

---

## 🛠️ Make Commands

### Show Available Commands
```bash
make help
```

### Install Dependencies
```bash
make install
```

### Start Development Server
```bash
make dev
```

### Docker Services
```bash
make up      # Start
make down    # Stop
make logs    # View logs
```

### Code Quality
```bash
make lint    # Lint code
make format  # Format code
make test    # Run tests
```

### Database
```bash
make migrate              # Apply migrations
make migrate-create       # Create new migration
```

### Cleanup
```bash
make clean   # Remove cache, venv, etc.
```

---

## 💡 Useful Tips

### List Python Packages with Versions
```bash
uv pip list
```

### Check Python Version
```bash
python --version
```

### Verify Virtual Environment
```bash
which python  # macOS/Linux
where python  # Windows
```

### Clear Python Cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

### View Environment Variables
```bash
cat .env  # Or set | grep VAR_NAME on Windows
```

### Test Database Connection
```bash
# PostgreSQL
docker compose -f infra/docker-compose.dev.yml exec postgres pg_isready

# Redis
docker compose -f infra/docker-compose.dev.yml exec redis redis-cli ping
```

---

**Last Updated:** February 4, 2026  
**Version:** 1.0.0
