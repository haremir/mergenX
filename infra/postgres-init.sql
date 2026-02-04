-- Initialize PostgreSQL extensions for Harezmi Intelligence
-- This script runs when the container starts for the first time

-- Enable PostGIS for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable pgvector for vector/embedding operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable JSON/JSONB functions
CREATE EXTENSION IF NOT EXISTS jsonb_utils;

-- Create schema for application
CREATE SCHEMA IF NOT EXISTS app;

-- Set search path
ALTER ROLE harezmi SET search_path TO app, public;
