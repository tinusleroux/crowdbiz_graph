-- ================================================================
-- CrowdBiz Graph - Summary Tables for Performance Optimization
-- Copy and paste this entire script into Supabase SQL Editor
-- ================================================================

-- Step 1: Create network_status table (replaces complex person enrichment)
CREATE TABLE IF NOT EXISTS network_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    
    -- Basic Info (denormalized from person table)
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    linkedin_url TEXT,
    
    -- Current Role Info (denormalized from role + organization tables)
    current_job_title TEXT,
    current_organization TEXT,
    current_org_type TEXT CHECK (current_org_type IN ('Team','League','Brand','Agency','Vendor')),
    current_sport TEXT,
    current_industry TEXT,
    current_department TEXT,
    role_start_date DATE,
    is_executive BOOLEAN DEFAULT FALSE,
    
    -- Additional Metrics
    total_roles_count INTEGER DEFAULT 0,
    current_roles_count INTEGER DEFAULT 0,
    
    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one record per person
    CONSTRAINT uniq_network_status_person UNIQUE (person_id)
);

-- Step 2: Create organization_summary table (replaces complex org queries)
CREATE TABLE IF NOT EXISTS organization_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    
    -- Basic Info (denormalized from organization table)
    name TEXT NOT NULL,
    org_type TEXT CHECK (org_type IN ('Team','League','Brand','Agency','Vendor')),
    sport TEXT,
    industry TEXT,
    parent_org_name TEXT,
    
    -- Employee Metrics
    total_employees INTEGER DEFAULT 0,
    current_employees INTEGER DEFAULT 0,
    executive_count INTEGER DEFAULT 0,
    
    -- Department Breakdown (JSON for flexibility)
    departments JSONB DEFAULT '{}',
    
    -- Role Distribution
    role_distribution JSONB DEFAULT '{}',
    
    -- Recent Activity
    recent_hires_30d INTEGER DEFAULT 0,
    recent_departures_30d INTEGER DEFAULT 0,
    
    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one record per organization
    CONSTRAINT uniq_org_summary_org UNIQUE (org_id)
);

-- Step 3: Create indexes for performance
-- Indexes for network_status
CREATE INDEX IF NOT EXISTS network_status_name_idx ON network_status USING GIN (to_tsvector('simple', full_name));
CREATE INDEX IF NOT EXISTS network_status_org_idx ON network_status (current_organization);
CREATE INDEX IF NOT EXISTS network_status_org_type_idx ON network_status (current_org_type);
CREATE INDEX IF NOT EXISTS network_status_sport_idx ON network_status (current_sport);
CREATE INDEX IF NOT EXISTS network_status_executive_idx ON network_status (is_executive) WHERE is_executive = TRUE;
CREATE INDEX IF NOT EXISTS network_status_updated_idx ON network_status (last_updated);

-- Indexes for organization_summary
CREATE INDEX IF NOT EXISTS org_summary_name_idx ON organization_summary USING GIN (to_tsvector('simple', name));
CREATE INDEX IF NOT EXISTS org_summary_org_type_idx ON organization_summary (org_type);
CREATE INDEX IF NOT EXISTS org_summary_sport_idx ON organization_summary (sport);
CREATE INDEX IF NOT EXISTS org_summary_employees_idx ON organization_summary (current_employees);
CREATE INDEX IF NOT EXISTS org_summary_executive_idx ON organization_summary (executive_count);
CREATE INDEX IF NOT EXISTS org_summary_updated_idx ON organization_summary (last_updated);

-- Step 4: Populate network_status table with data
INSERT INTO network_status (
    person_id, full_name, first_name, last_name, linkedin_url,
    current_job_title, current_organization, current_org_type, 
    current_sport, current_industry, current_department, 
    role_start_date, is_executive, total_roles_count, current_roles_count
)
SELECT 
    p.id as person_id,
    p.full_name,
    p.first_name, 
    p.last_name,
    p.linkedin_url,
    
    -- Get primary current role (most recent start date)
    cr.job_title as current_job_title,
    co.name as current_organization,
    co.org_type as current_org_type,
    co.sport as current_sport,
    co.industry as current_industry,
    cr.dept as current_department,
    cr.start_date as role_start_date,
    COALESCE(cr.is_executive, FALSE) as is_executive,
    
    -- Role counts
    COALESCE(total_roles.count, 0) as total_roles_count,
    COALESCE(current_roles.count, 0) as current_roles_count
    
FROM person p

-- Get primary current role (most recent)
LEFT JOIN LATERAL (
    SELECT r.job_title, r.dept, r.start_date, r.is_executive, r.org_id
    FROM role r 
    WHERE r.person_id = p.id AND r.is_current = TRUE
    ORDER BY r.start_date DESC
    LIMIT 1
) cr ON TRUE

-- Get organization info for current role
LEFT JOIN organization co ON cr.org_id = co.id

-- Count total roles
LEFT JOIN LATERAL (
    SELECT COUNT(*) as count
    FROM role r
    WHERE r.person_id = p.id
) total_roles ON TRUE

-- Count current roles
LEFT JOIN LATERAL (
    SELECT COUNT(*) as count  
    FROM role r
    WHERE r.person_id = p.id AND r.is_current = TRUE
) current_roles ON TRUE

ON CONFLICT (person_id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    linkedin_url = EXCLUDED.linkedin_url,
    current_job_title = EXCLUDED.current_job_title,
    current_organization = EXCLUDED.current_organization,
    current_org_type = EXCLUDED.current_org_type,
    current_sport = EXCLUDED.current_sport,
    current_industry = EXCLUDED.current_industry,
    current_department = EXCLUDED.current_department,
    role_start_date = EXCLUDED.role_start_date,
    is_executive = EXCLUDED.is_executive,
    total_roles_count = EXCLUDED.total_roles_count,
    current_roles_count = EXCLUDED.current_roles_count,
    last_updated = NOW();

-- Step 5: Populate organization_summary table with data
INSERT INTO organization_summary (
    org_id, name, org_type, sport, industry, parent_org_name,
    total_employees, current_employees, executive_count,
    departments, role_distribution
)
SELECT 
    o.id as org_id,
    o.name,
    o.org_type,
    o.sport,
    o.industry,
    po.name as parent_org_name,
    
    -- Employee counts
    COALESCE(total_emp.count, 0) as total_employees,
    COALESCE(current_emp.count, 0) as current_employees, 
    COALESCE(exec_count.count, 0) as executive_count,
    
    -- Department breakdown
    COALESCE(dept_breakdown.departments, '{}') as departments,
    
    -- Role distribution  
    COALESCE(role_breakdown.roles, '{}') as role_distribution
    
FROM organization o

-- Parent organization name
LEFT JOIN organization po ON o.parent_org_id = po.id

-- Total employees (all time)
LEFT JOIN LATERAL (
    SELECT COUNT(DISTINCT person_id) as count
    FROM role r
    WHERE r.org_id = o.id
) total_emp ON TRUE

-- Current employees
LEFT JOIN LATERAL (
    SELECT COUNT(DISTINCT person_id) as count
    FROM role r  
    WHERE r.org_id = o.id AND r.is_current = TRUE
) current_emp ON TRUE

-- Executive count
LEFT JOIN LATERAL (
    SELECT COUNT(DISTINCT person_id) as count
    FROM role r
    WHERE r.org_id = o.id AND r.is_current = TRUE AND r.is_executive = TRUE  
) exec_count ON TRUE

-- Department breakdown
LEFT JOIN LATERAL (
    SELECT jsonb_object_agg(dept, count) as departments
    FROM (
        SELECT COALESCE(r.dept, 'Unknown') as dept, COUNT(*) as count
        FROM role r
        WHERE r.org_id = o.id AND r.is_current = TRUE
        GROUP BY r.dept
    ) dept_counts
) dept_breakdown ON TRUE

-- Role distribution
LEFT JOIN LATERAL (
    SELECT jsonb_object_agg(job_title, count) as roles
    FROM (
        SELECT r.job_title, COUNT(*) as count
        FROM role r
        WHERE r.org_id = o.id AND r.is_current = TRUE
        GROUP BY r.job_title
        ORDER BY count DESC
        LIMIT 20  -- Top 20 roles
    ) role_counts
) role_breakdown ON TRUE

ON CONFLICT (org_id) DO UPDATE SET
    name = EXCLUDED.name,
    org_type = EXCLUDED.org_type,
    sport = EXCLUDED.sport,
    industry = EXCLUDED.industry,
    parent_org_name = EXCLUDED.parent_org_name,
    total_employees = EXCLUDED.total_employees,
    current_employees = EXCLUDED.current_employees,
    executive_count = EXCLUDED.executive_count,
    departments = EXCLUDED.departments,
    role_distribution = EXCLUDED.role_distribution,
    last_updated = NOW();

-- Step 6: Create refresh functions for daily updates
CREATE OR REPLACE FUNCTION refresh_network_status()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
BEGIN
    -- Update existing records and insert new ones
    WITH updated_data AS (
        SELECT 
            p.id as person_id,
            p.full_name,
            p.first_name, 
            p.last_name,
            p.linkedin_url,
            cr.job_title as current_job_title,
            co.name as current_organization,
            co.org_type as current_org_type,
            co.sport as current_sport,
            co.industry as current_industry,
            cr.dept as current_department,
            cr.start_date as role_start_date,
            COALESCE(cr.is_executive, FALSE) as is_executive,
            COALESCE(total_roles.count, 0) as total_roles_count,
            COALESCE(current_roles.count, 0) as current_roles_count
        FROM person p
        LEFT JOIN LATERAL (
            SELECT r.job_title, r.dept, r.start_date, r.is_executive, r.org_id
            FROM role r 
            WHERE r.person_id = p.id AND r.is_current = TRUE
            ORDER BY r.start_date DESC
            LIMIT 1
        ) cr ON TRUE
        LEFT JOIN organization co ON cr.org_id = co.id
        LEFT JOIN LATERAL (
            SELECT COUNT(*) as count
            FROM role r
            WHERE r.person_id = p.id
        ) total_roles ON TRUE
        LEFT JOIN LATERAL (
            SELECT COUNT(*) as count  
            FROM role r
            WHERE r.person_id = p.id AND r.is_current = TRUE
        ) current_roles ON TRUE
    )
    INSERT INTO network_status (
        person_id, full_name, first_name, last_name, linkedin_url,
        current_job_title, current_organization, current_org_type, 
        current_sport, current_industry, current_department, 
        role_start_date, is_executive, total_roles_count, current_roles_count
    )
    SELECT * FROM updated_data
    ON CONFLICT (person_id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        linkedin_url = EXCLUDED.linkedin_url,
        current_job_title = EXCLUDED.current_job_title,
        current_organization = EXCLUDED.current_organization,
        current_org_type = EXCLUDED.current_org_type,
        current_sport = EXCLUDED.current_sport,
        current_industry = EXCLUDED.current_industry,
        current_department = EXCLUDED.current_department,
        role_start_date = EXCLUDED.role_start_date,
        is_executive = EXCLUDED.is_executive,
        total_roles_count = EXCLUDED.total_roles_count,
        current_roles_count = EXCLUDED.current_roles_count,
        last_updated = NOW();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_organization_summary()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
BEGIN
    WITH updated_data AS (
        SELECT 
            o.id as org_id,
            o.name,
            o.org_type,
            o.sport,
            o.industry,
            po.name as parent_org_name,
            COALESCE(total_emp.count, 0) as total_employees,
            COALESCE(current_emp.count, 0) as current_employees, 
            COALESCE(exec_count.count, 0) as executive_count,
            COALESCE(dept_breakdown.departments, '{}') as departments,
            COALESCE(role_breakdown.roles, '{}') as role_distribution
        FROM organization o
        LEFT JOIN organization po ON o.parent_org_id = po.id
        LEFT JOIN LATERAL (
            SELECT COUNT(DISTINCT person_id) as count
            FROM role r WHERE r.org_id = o.id
        ) total_emp ON TRUE
        LEFT JOIN LATERAL (
            SELECT COUNT(DISTINCT person_id) as count
            FROM role r WHERE r.org_id = o.id AND r.is_current = TRUE
        ) current_emp ON TRUE
        LEFT JOIN LATERAL (
            SELECT COUNT(DISTINCT person_id) as count
            FROM role r
            WHERE r.org_id = o.id AND r.is_current = TRUE AND r.is_executive = TRUE  
        ) exec_count ON TRUE
        LEFT JOIN LATERAL (
            SELECT jsonb_object_agg(dept, count) as departments
            FROM (
                SELECT COALESCE(r.dept, 'Unknown') as dept, COUNT(*) as count
                FROM role r
                WHERE r.org_id = o.id AND r.is_current = TRUE
                GROUP BY r.dept
            ) dept_counts
        ) dept_breakdown ON TRUE
        LEFT JOIN LATERAL (
            SELECT jsonb_object_agg(job_title, count) as roles
            FROM (
                SELECT r.job_title, COUNT(*) as count
                FROM role r
                WHERE r.org_id = o.id AND r.is_current = TRUE
                GROUP BY r.job_title
                ORDER BY count DESC
                LIMIT 20
            ) role_counts
        ) role_breakdown ON TRUE
    )
    INSERT INTO organization_summary (
        org_id, name, org_type, sport, industry, parent_org_name,
        total_employees, current_employees, executive_count,
        departments, role_distribution
    )
    SELECT * FROM updated_data
    ON CONFLICT (org_id) DO UPDATE SET
        name = EXCLUDED.name,
        org_type = EXCLUDED.org_type,
        sport = EXCLUDED.sport,
        industry = EXCLUDED.industry,
        parent_org_name = EXCLUDED.parent_org_name,
        total_employees = EXCLUDED.total_employees,
        current_employees = EXCLUDED.current_employees,
        executive_count = EXCLUDED.executive_count,
        departments = EXCLUDED.departments,
        role_distribution = EXCLUDED.role_distribution,
        last_updated = NOW();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Verify the tables were created and populated
SELECT 'network_status' as table_name, COUNT(*) as record_count FROM network_status
UNION ALL
SELECT 'organization_summary' as table_name, COUNT(*) as record_count FROM organization_summary;
