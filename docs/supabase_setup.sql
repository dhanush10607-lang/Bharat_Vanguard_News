-- ============================================================
--  TruthLens AI — Supabase Initial Setup SQL
--  Run this in Supabase Dashboard → SQL Editor BEFORE
--  running Alembic migrations.
--
--  This enables the required PostgreSQL extensions that
--  are available on Supabase's free tier.
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for semantic embeddings
-- (Supabase free tier includes this)
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable trigram similarity for full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enable btree_gin for combined indexes
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================
--  Create GIN index for full-text search on articles
--  (Run AFTER Alembic creates the articles table)
-- ============================================================
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS articles_fts_idx
--     ON articles USING gin(to_tsvector('english', title || ' ' || coalesce(description, '')));

-- ============================================================
--  Create HNSW index for vector similarity search
--  (Run AFTER Alembic creates the article_embeddings table)
-- ============================================================
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS embeddings_hnsw_idx
--     ON article_embeddings USING hnsw (vector vector_cosine_ops)
--     WITH (m = 16, ef_construction = 64);

-- Verify extensions are enabled
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('uuid-ossp', 'vector', 'pg_trgm', 'btree_gin');
