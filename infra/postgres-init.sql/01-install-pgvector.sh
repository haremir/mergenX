#!/bin/bash
# PostgreSQL initialization script for pgvector extension

set -e

echo "Installing pgvector extension..."

# Install pgvector package
apt-get update
apt-get install -y postgresql-15-pgvector

echo "pgvector installed successfully"

# Create extensions in the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

echo "Extensions created successfully"
