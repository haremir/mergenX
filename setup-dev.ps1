#!/usr/bin/env pwsh
# Harezmi Intelligence - Project Initialization Script
# Run this script to set up the development environment

Write-Host "🚀 Initializing Harezmi Intelligence (Production SaaS Platform)" -ForegroundColor Cyan

# ============================================================================
# 1. Install UV Package Manager (if not installed)
# ============================================================================
Write-Host "`n📦 Step 1: Installing UV package manager..." -ForegroundColor Yellow
pip install uv

# ============================================================================
# 2. Create Python Virtual Environment with UV
# ============================================================================
Write-Host "`n🐍 Step 2: Creating virtual environment..." -ForegroundColor Yellow
uv venv .venv

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# ============================================================================
# 3. Sync Dependencies
# ============================================================================
Write-Host "`n📚 Step 3: Installing dependencies..." -ForegroundColor Yellow
uv sync --all-groups

# ============================================================================
# 4. Create Environment File
# ============================================================================
Write-Host "`n⚙️  Step 4: Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file (configure it before running the app)" -ForegroundColor Green
}

# ============================================================================
# 5. Initialize Docker Environment
# ============================================================================
Write-Host "`n🐳 Step 5: Setting up Docker infrastructure..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Starting Docker services (postgres, redis)..." -ForegroundColor Cyan
    docker compose -f infra/docker-compose.dev.yml up -d
    Write-Host "✅ Docker services started" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker not found. Install Docker Desktop and run:" -ForegroundColor Yellow
    Write-Host "   docker compose -f infra/docker-compose.dev.yml up -d" -ForegroundColor Gray
}

# ============================================================================
# 6. Database Migrations (Placeholder)
# ============================================================================
Write-Host "`n🗄️  Step 6: Database setup..." -ForegroundColor Yellow
Write-Host "Run migrations when ready:" -ForegroundColor Cyan
Write-Host "   alembic upgrade head" -ForegroundColor Gray

# ============================================================================
# 7. Pre-commit Setup
# ============================================================================
Write-Host "`n🔍 Step 7: Setting up pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

# ============================================================================
# Final Instructions
# ============================================================================
Write-Host "`n✨ Setup Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Configure .env file with your settings" -ForegroundColor Gray
Write-Host "2. Run migrations: alembic upgrade head" -ForegroundColor Gray
Write-Host "3. Start API: uvicorn apps.api.main:app --reload" -ForegroundColor Gray
Write-Host "4. Open browser: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "`n📚 Documentation: http://localhost:8000/redoc" -ForegroundColor Cyan
