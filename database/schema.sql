CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY,
    source TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    external_id TEXT,
    gr_no TEXT,
    title TEXT NOT NULL,
    decision_date DATE,
    justice TEXT,
    ponencia TEXT,
    division TEXT,
    category TEXT,
    full_text TEXT NOT NULL,
    clean_text TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    scraped_at TIMESTAMPTZ,
    parsed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cases_gr_no ON cases(gr_no);
CREATE INDEX IF NOT EXISTS idx_cases_decision_date ON cases(decision_date);
CREATE INDEX IF NOT EXISTS idx_cases_category ON cases(category);

CREATE TABLE IF NOT EXISTS case_chunks (
    id UUID PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    section_label TEXT,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(case_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id UUID PRIMARY KEY,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    records_in INTEGER NOT NULL DEFAULT 0,
    records_out INTEGER NOT NULL DEFAULT 0,
    error_log TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS retrieval_logs (
    id UUID PRIMARY KEY,
    query TEXT NOT NULL,
    retrieved_case_ids JSONB NOT NULL,
    retrieved_chunk_ids JSONB NOT NULL,
    latency_ms INTEGER NOT NULL,
    model_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
