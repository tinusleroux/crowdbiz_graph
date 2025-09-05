-- Update network_status table with standardized departments
-- Run this in Supabase SQL Editor

-- Step 1: Update current_standardized_department from role table
UPDATE network_status 
SET current_standardized_department = role.standardized_department,
    current_department = role.dept,
    last_updated = NOW()
FROM role 
WHERE network_status.person_id = role.person_id 
  AND role.is_current = true
  AND role.standardized_department IS NOT NULL;

-- Step 2: Verify the update
SELECT 
    current_standardized_department,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM network_status), 2) as percentage
FROM network_status 
WHERE current_standardized_department IS NOT NULL
GROUP BY current_standardized_department 
ORDER BY count DESC;

-- Step 3: Show sample results
SELECT 
    full_name,
    current_job_title,
    current_organization,
    current_department,
    current_standardized_department
FROM network_status 
WHERE current_standardized_department IS NOT NULL
LIMIT 10;
