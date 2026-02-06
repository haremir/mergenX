# -*- coding: utf-8 -*-
import sys
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

# 1. Import project components
from core.database import Base
from core.config import settings
from core.models import * 

config = context.config

# 2. Database URL conversion for sync psycopg (Windows compatible)
if hasattr(settings.DATABASE_URL, 'unicode_string'):
    db_url = settings.DATABASE_URL.unicode_string()
else:
    db_url = str(settings.DATABASE_URL)

# Convert asyncpg -> psycopg (sync) for Alembic
db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
db_url = db_url.replace("localhost", "127.0.0.1")
db_url = db_url.replace(":5432/", ":5433/")  # Use port 5433 for Docker container

config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 4. Filter to ignore PostGIS system tables
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and name not in target_metadata.tables:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode with sync psycopg."""
    
    # Create engine directly (bypass alembic.ini for clean URL handling)
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()
    
    connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()