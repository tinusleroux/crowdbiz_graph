-- Job Title Department Classification System
-- Run this in Supabase SQL Editor

-- Step 1: Create job_title_departments lookup table
CREATE TABLE IF NOT EXISTS job_title_departments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_title TEXT NOT NULL UNIQUE,
    standardized_department TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_job_title_departments_title ON job_title_departments(job_title);
CREATE INDEX IF NOT EXISTS idx_job_title_departments_dept ON job_title_departments(standardized_department);

-- Step 3: Remove redundant columns from role table
-- (Run these one by one, after confirming the lookup table works)
-- ALTER TABLE role DROP COLUMN IF EXISTS dept;
-- ALTER TABLE role DROP COLUMN IF EXISTS standardized_department;

-- Step 4: Update network_status to use lookup instead of stored values
-- (This will be done via application code)

-- Step 5: Create a view that shows roles with their departments via lookup
CREATE OR REPLACE VIEW v_roles_with_departments AS
SELECT 
    r.*,
    jtd.standardized_department,
    p.full_name,
    o.name as organization_name,
    o.org_type,
    o.sport
FROM role r
LEFT JOIN person p ON r.person_id = p.id
LEFT JOIN organization o ON r.org_id = o.id  
LEFT JOIN job_title_departments jtd ON r.job_title = jtd.job_title;

-- Step 6: Create a view for current roles with departments
CREATE OR REPLACE VIEW v_current_roles_with_departments AS
SELECT * FROM v_roles_with_departments 
WHERE is_current = true;

-- Step 7: Test query to see how many job titles will be classified
SELECT 
    CASE 
        WHEN r.job_title IS NULL THEN 'NULL job titles'
        ELSE 'Valid job titles'
    END as category,
    COUNT(DISTINCT r.job_title) as unique_titles,
    COUNT(*) as total_roles
FROM role r
WHERE r.is_current = true
GROUP BY 
    CASE 
        WHEN r.job_title IS NULL THEN 'NULL job titles'
        ELSE 'Valid job titles'
    END;

-- Step 8: Sample query showing the new architecture
SELECT 
    p.full_name,
    r.job_title,
    o.name as organization,
    COALESCE(jtd.standardized_department, 'Unclassified') as department
FROM role r
JOIN person p ON r.person_id = p.id
JOIN organization o ON r.org_id = o.id
LEFT JOIN job_title_departments jtd ON r.job_title = jtd.job_title
WHERE r.is_current = true
LIMIT 10;
