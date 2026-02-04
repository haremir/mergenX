#!/bin/bash
# Harezmi Intelligence - Project Initialization Script
# Run this script to set up the development environment

echo "🚀 Initializing Harezmi Intelligence (Production SaaS Platform)"

# ============================================================================
# 1. Install UV Package Manager (if not installed)
# ============================================================================
echo -e "\n📦 Step 1: Installing UV package manager..."
pip install uv

# ============================================================================
# 2. Create Python Virtual Environment with UV
# ============================================================================
echo -e "\n🐍 Step 2: Creating virtual environment..."
uv venv .venv

# Activate virtual environment
source .venv/bin/activate

# ============================================================================
# 3. Sync Dependencies
# ============================================================================
echo -e "\n📚 Step 3: Installing dependencies..."
uv sync --all-groups

# ============================================================================
# 4. Create Environment File
# ============================================================================
echo -e "\n⚙️  Step 4: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file (configure it before running the app)"
fi

# ============================================================================
# 5. Initialize Docker Environment
# ============================================================================
echo -e "\n🐳 Step 5: Setting up Docker infrastructure..."
if command -v docker &> /dev/null; then
    echo "Starting Docker services (postgres, redis)..."
    docker compose -f infra/docker-compose.dev.yml up -d
    echo "✅ Docker services started"
else
    echo "⚠️  Docker not found. Install Docker and run:"
    echo "   docker compose -f infra/docker-compose.dev.yml up -d"
fi

# ============================================================================
# 6. Database Migrations (Placeholder)
# ============================================================================
echo -e "\n🗄️  Step 6: Database setup..."
echo "Run migrations when ready:"
echo "   alembic upgrade head"

# ============================================================================
# 7. Pre-commit Setup
# ============================================================================
echo -e "\n🔍 Step 7: Setting up pre-commit hooks..."
pre-commit install

# ============================================================================
# Final Instructions
# ============================================================================
echo -e "\n✨ Setup Complete!"
echo -e "\nNext steps:"
echo "1. Configure .env file with your settings"
echo "2. Run migrations: alembic upgrade head"
echo "3. Start API: uvicorn apps.api.main:app --reload"
echo "4. Open browser: http://localhost:8000/docs"
echo -e "\n📚 Documentation: http://localhost:8000/redoc"
