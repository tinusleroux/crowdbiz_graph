-- Staging-First Architecture Migration
-- Implements the clean architecture from simplified_structure.txt

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For similarity matching

-- Import batch tracking table
CREATE TABLE IF NOT EXISTS import_batch (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL, -- csv, website, news, api
    file_path TEXT,
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    valid_records INTEGER DEFAULT 0,
    merged_records INTEGER DEFAULT 0,
    status TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'ready_to_merge')),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Person staging table (mirrors production + staging metadata)
CREATE TABLE IF NOT EXISTS person_staging (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Core person fields
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    email TEXT,
    linkedin_url TEXT,
    twitter_url TEXT,
    phone TEXT,
    title TEXT,
    company TEXT,
    department TEXT,
    location TEXT,
    
    -- Staging metadata
    import_batch_id UUID NOT NULL REFERENCES import_batch(id) ON DELETE CASCADE,
    import_source TEXT NOT NULL,
    import_timestamp TIMESTAMPTZ DEFAULT NOW(),
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid', 'merged')),
    validation_errors JSONB DEFAULT '[]',
    merge_candidate_id UUID, -- Link to potential production record
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    merge_decision TEXT CHECK (merge_decision IN ('new', 'update', 'skip', 'manual_review')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization staging table
CREATE TABLE IF NOT EXISTS organization_staging (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Core organization fields
    name TEXT NOT NULL,
    org_type TEXT CHECK (org_type IN ('Team','League','Brand','Agency','Vendor')),
    website TEXT,
    city TEXT,
    state TEXT,
    sport TEXT,
    league TEXT,
    parent_org_name TEXT, -- Will be resolved to parent_org_id during merge
    industry TEXT,
    is_active BOOLEAN DEFAULT true,
    
    -- Staging metadata
    import_batch_id UUID NOT NULL REFERENCES import_batch(id) ON DELETE CASCADE,
    import_source TEXT NOT NULL,
    import_timestamp TIMESTAMPTZ DEFAULT NOW(),
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid', 'merged')),
    validation_errors JSONB DEFAULT '[]',
    merge_candidate_id UUID, -- Link to potential production record
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    merge_decision TEXT CHECK (merge_decision IN ('new', 'update', 'skip', 'manual_review')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role staging table
CREATE TABLE IF NOT EXISTS role_staging (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- References to staging records
    person_staging_id UUID REFERENCES person_staging(id) ON DELETE CASCADE,
    organization_staging_id UUID REFERENCES organization_staging(id) ON DELETE CASCADE,
    
    -- Core role fields
    job_title TEXT NOT NULL,
    dept TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT true,
    is_executive BOOLEAN DEFAULT false,
    reports_to_title TEXT, -- Will be resolved during merge
    
    -- Staging metadata
    import_batch_id UUID NOT NULL REFERENCES import_batch(id) ON DELETE CASCADE,
    import_source TEXT NOT NULL,
    import_timestamp TIMESTAMPTZ DEFAULT NOW(),
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid', 'merged')),
    validation_errors JSONB DEFAULT '[]',
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    merge_decision TEXT CHECK (merge_decision IN ('new', 'update', 'skip', 'manual_review')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- News item staging table
CREATE TABLE IF NOT EXISTS news_item_staging (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Core news fields
    title TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMPTZ,
    article_text TEXT,
    author TEXT,
    source_name TEXT,
    
    -- Staging metadata
    import_batch_id UUID NOT NULL REFERENCES import_batch(id) ON DELETE CASCADE,
    import_source TEXT NOT NULL,
    import_timestamp TIMESTAMPTZ DEFAULT NOW(),
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid', 'merged')),
    validation_errors JSONB DEFAULT '[]',
    merge_candidate_id UUID, -- Link to potential production record
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    merge_decision TEXT CHECK (merge_decision IN ('new', 'update', 'skip', 'manual_review')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_import_batch_status ON import_batch(status);
CREATE INDEX IF NOT EXISTS idx_import_batch_source ON import_batch(source_name, source_type);

CREATE INDEX IF NOT EXISTS idx_person_staging_batch ON person_staging(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_person_staging_email ON person_staging(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_person_staging_status ON person_staging(validation_status);
CREATE INDEX IF NOT EXISTS idx_person_staging_merge ON person_staging(merge_candidate_id) WHERE merge_candidate_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_person_staging_name ON person_staging USING gin((first_name || ' ' || last_name) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_org_staging_batch ON organization_staging(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_org_staging_name ON organization_staging USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_org_staging_status ON organization_staging(validation_status);
CREATE INDEX IF NOT EXISTS idx_org_staging_merge ON organization_staging(merge_candidate_id) WHERE merge_candidate_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_role_staging_batch ON role_staging(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_role_staging_person ON role_staging(person_staging_id);
CREATE INDEX IF NOT EXISTS idx_role_staging_org ON role_staging(organization_staging_id);
CREATE INDEX IF NOT EXISTS idx_role_staging_current ON role_staging(is_current) WHERE is_current = true;

CREATE INDEX IF NOT EXISTS idx_news_staging_batch ON news_item_staging(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_news_staging_url ON news_item_staging(url) WHERE url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_news_staging_title ON news_item_staging USING gin(title gin_trgm_ops);

-- Functions for staging operations

-- Function to calculate name similarity
CREATE OR REPLACE FUNCTION calculate_person_similarity(
    staging_first TEXT,
    staging_last TEXT,
    prod_first TEXT,
    prod_last TEXT
) RETURNS DECIMAL(3,2) AS $$
BEGIN
    RETURN GREATEST(
        similarity(COALESCE(staging_first, ''), COALESCE(prod_first, '')),
        similarity(COALESCE(staging_last, ''), COALESCE(prod_last, '')),
        similarity(
            COALESCE(staging_first, '') || ' ' || COALESCE(staging_last, ''),
            COALESCE(prod_first, '') || ' ' || COALESCE(prod_last, '')
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Function to auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER trigger_person_staging_updated_at
    BEFORE UPDATE ON person_staging
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_org_staging_updated_at
    BEFORE UPDATE ON organization_staging
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_role_staging_updated_at
    BEFORE UPDATE ON role_staging
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_news_staging_updated_at
    BEFORE UPDATE ON news_item_staging
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE import_batch IS 'Tracks import operations and their status';
COMMENT ON TABLE person_staging IS 'Staging area for person records before validation and merge';
COMMENT ON TABLE organization_staging IS 'Staging area for organization records before validation and merge';
COMMENT ON TABLE role_staging IS 'Staging area for role relationships before validation and merge';
COMMENT ON TABLE news_item_staging IS 'Staging area for news articles before validation and merge';

COMMENT ON COLUMN person_staging.merge_candidate_id IS 'ID of potential matching record in production person table';
COMMENT ON COLUMN person_staging.confidence_score IS 'Confidence level (0.00-1.00) for merge candidate match';
COMMENT ON COLUMN person_staging.merge_decision IS 'Decision on how to handle this record during merge';
