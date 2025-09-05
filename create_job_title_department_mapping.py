"""
Job Title Department Classification System
Creates a mapping table for job titles to standardized departments
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_database_manager
from app.core.logger import get_logger

logger = get_logger("job_title_departments")

# Department classification mapping based on job title keywords
DEPARTMENT_MAPPING = {
    'Sales & Partnerships': [
        'sales', 'partnership', 'corporate partnership', 'sponsor', 'business development',
        'account', 'client', 'revenue', 'commercial', 'corporate sales', 'premium sales',
        'season ticket', 'membership', 'corporate services', 'vip', 'suite', 'hospitality'
    ],
    'Marketing & Communications': [
        'marketing', 'communications', 'content', 'social media', 'brand', 'creative',
        'graphic design', 'public relations', 'pr', 'media relations', 'digital',
        'advertising', 'promotion', 'community relations', 'fan engagement', 'publicity'
    ],
    'Finance & Administration': [
        'finance', 'accounting', 'controller', 'cfo', 'treasurer', 'budget', 'financial',
        'hr', 'human resources', 'legal', 'compliance', 'administration', 'admin',
        'operations manager', 'business operations', 'executive assistant', 'office manager'
    ],
    'Stadium Operations & Facilities': [
        'stadium', 'facilities', 'maintenance', 'security', 'grounds', 'field',
        'building', 'operations', 'event operations', 'game day', 'facility',
        'groundskeeper', 'custodial', 'engineering'
    ],
    'Technology & Analytics': [
        'technology', 'it', 'data', 'analytics', 'digital', 'software', 'systems',
        'database', 'tech', 'information', 'analyst', 'developer', 'programmer'
    ],
    'Fan Experience & Events': [
        'fan experience', 'events', 'entertainment', 'guest services', 'customer service',
        'fan services', 'game presentation', 'promotions', 'activation', 'experience',
        'community', 'youth', 'education', 'outreach'
    ],
    'Ticketing & Operations': [
        'ticketing', 'box office', 'ticket', 'seating', 'concessions', 'merchandise',
        'retail', 'food service', 'vendor', 'procurement', 'purchasing'
    ],
    'Broadcasting & Media': [
        'broadcasting', 'media', 'production', 'video', 'audio', 'broadcast',
        'television', 'radio', 'streaming', 'content production', 'journalism',
        'reporter', 'announcer', 'producer'
    ]
}

def classify_job_title(job_title: str) -> str:
    """Classify a job title into one of the 8 standard departments"""
    if not job_title:
        return 'Other'
    
    job_title_lower = job_title.lower()
    
    # Check each department's keywords
    for department, keywords in DEPARTMENT_MAPPING.items():
        for keyword in keywords:
            if keyword in job_title_lower:
                return department
    
    # Special case handling
    if any(exec_word in job_title_lower for exec_word in ['ceo', 'president', 'owner', 'chairman', 'chief']):
        return 'Executive Leadership'
    
    return 'Other'

def create_job_title_department_table():
    """Create a table for job title to department mapping"""
    db = get_database_manager()
    
    if not db.is_connected():
        logger.error("Database not connected")
        return False
    
    try:
        # Get all unique job titles from the role table
        logger.info("Fetching all unique job titles...")
        job_titles_result = db.client.table('role')\
            .select('job_title')\
            .execute()
        
        if not job_titles_result.data:
            logger.error("No job titles found")
            return False
        
        # Get unique job titles
        unique_titles = list(set([
            row['job_title'] for row in job_titles_result.data 
            if row.get('job_title') and row['job_title'].strip()
        ]))
        
        logger.info(f"Found {len(unique_titles)} unique job titles")
        
        # Create job title department mappings
        job_title_mappings = []
        department_counts = {}
        
        for title in unique_titles:
            department = classify_job_title(title)
            department_counts[department] = department_counts.get(department, 0) + 1
            
            job_title_mappings.append({
                'job_title': title.strip(),
                'standardized_department': department,
                'created_at': 'now()'
            })
        
        # Log department distribution
        logger.info("Department classification results:")
        for dept, count in sorted(department_counts.items()):
            logger.info(f"  {dept}: {count} job titles")
        
        # Clear existing data from job_title_departments table (if it exists)
        try:
            db.client.table('job_title_departments').delete().neq('job_title', '').execute()
            logger.info("Cleared existing job_title_departments data")
        except Exception as e:
            logger.info(f"job_title_departments table may not exist: {e}")
        
        # Insert mappings in batches
        batch_size = 100
        logger.info(f"Inserting {len(job_title_mappings)} job title mappings...")
        
        for i in range(0, len(job_title_mappings), batch_size):
            batch = job_title_mappings[i:i + batch_size]
            try:
                result = db.client.table('job_title_departments').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} mappings")
            except Exception as e:
                logger.error(f"Failed to insert batch {i//batch_size + 1}: {e}")
                # Continue with next batch
        
        logger.info("✅ Job title department mapping table created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create job title department table: {e}")
        return False

def main():
    """Main function"""
    logger.info("🏗️ Creating Job Title Department Classification System...")
    
    success = create_job_title_department_table()
    
    if success:
        logger.info("✅ Job title department classification completed!")
        print("✅ Job title department classification completed!")
        print("\nNext steps:")
        print("1. Create the job_title_departments table in Supabase if it doesn't exist")
        print("2. Update queries to JOIN with this table instead of storing department in roles")
        print("3. Remove redundant department columns from role and network_status tables")
    else:
        logger.error("❌ Job title department classification failed")
        print("❌ Job title department classification failed - check logs")

if __name__ == "__main__":
    main()
