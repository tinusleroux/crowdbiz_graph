"""
Refresh Summary Tables Script
Updates the network_status and organization_summary materialized views
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_database_manager
from app.core.logger import get_logger

logger = get_logger("refresh_summary_tables")

def refresh_network_status():
    """Refresh the network_status summary table"""
    db = get_database_manager()
    
    if not db.is_connected():
        logger.error("Database not connected")
        return False
    
    try:
        # Delete existing data
        logger.info("Clearing existing network_status data...")
        delete_result = db.client.table('network_status').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        logger.info(f"Deleted {len(delete_result.data) if delete_result.data else 0} existing records")
        
        # Get all persons with their current roles
        logger.info("Fetching current role data...")
        
        # Get people with current roles - simpler approach
        people_with_roles = db.client.table('person')\
            .select('id, full_name, first_name, last_name, linkedin_url, created_at')\
            .execute()
        
        logger.info(f"Found {len(people_with_roles.data) if people_with_roles.data else 0} total people")
        
        # Transform data for network_status table
        network_status_records = []
        for person in people_with_roles.data:
            # Get current roles for this person
            current_roles = db.client.table('role')\
                .select('job_title, dept, standardized_department, start_date, is_executive, organization!inner(name, org_type, sport, industry)')\
                .eq('person_id', person['id'])\
                .eq('is_current', True)\
                .execute()
            
            if not current_roles.data:
                continue  # Skip people with no current roles
            
            # Handle multiple current roles - take the first one as primary
            role = current_roles.data[0]
            org = role.get('organization', {})
            
            record = {
                'person_id': person['id'],
                'full_name': person.get('full_name'),
                'first_name': person.get('first_name'),
                'last_name': person.get('last_name'),
                'linkedin_url': person.get('linkedin_url'),
                'current_job_title': role.get('job_title'),
                'current_department': role.get('dept'),
                'current_standardized_department': role.get('standardized_department'),
                'current_organization': org.get('name'),
                'current_org_type': org.get('org_type'),
                'current_sport': org.get('sport'),
                'current_industry': org.get('industry'),
                'is_executive': role.get('is_executive', False),
                'role_start_date': role.get('start_date'),
                'current_roles_count': len(current_roles.data),
                'created_at': person.get('created_at'),
                'last_updated': 'now()'
            }
            network_status_records.append(record)
        
        # Get total roles count for each person
        logger.info("Getting total roles count...")
        for record in network_status_records:
            total_roles = db.client.table('role')\
                .select('id', count='exact')\
                .eq('person_id', record['person_id'])\
                .execute()
            record['total_roles_count'] = total_roles.count if total_roles else 0
        
        # Insert new records in batches
        batch_size = 100
        logger.info(f"Inserting {len(network_status_records)} records in batches of {batch_size}...")
        
        for i in range(0, len(network_status_records), batch_size):
            batch = network_status_records[i:i + batch_size]
            result = db.client.table('network_status').insert(batch).execute()
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        logger.info("✅ network_status table refreshed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to refresh network_status: {e}")
        return False

def refresh_organization_summary():
    """Refresh the organization_summary table"""
    db = get_database_manager()
    
    if not db.is_connected():
        logger.error("Database not connected")
        return False
    
    try:
        # Delete existing data
        logger.info("Clearing existing organization_summary data...")
        delete_result = db.client.table('organization_summary').delete().neq('org_id', '00000000-0000-0000-0000-000000000000').execute()
        logger.info(f"Deleted {len(delete_result.data) if delete_result.data else 0} existing records")
        
        # Get all organizations
        logger.info("Fetching organization data...")
        organizations = db.client.table('organization').select('*').execute()
        
        if not organizations.data:
            logger.warning("No organizations found")
            return False
        
        logger.info(f"Found {len(organizations.data)} organizations")
        
        # Create summary records
        summary_records = []
        for org in organizations.data:
            # Get current employees
            current_employees = db.client.table('role')\
                .select('person_id, is_executive')\
                .eq('org_id', org['id'])\
                .eq('is_current', True)\
                .execute()
            
            # Get total historical employees
            total_employees = db.client.table('role')\
                .select('person_id', count='exact')\
                .eq('org_id', org['id'])\
                .execute()
            
            # Count executives
            executive_count = len([emp for emp in current_employees.data if emp.get('is_executive')]) if current_employees.data else 0
            
            # Get parent organization name
            parent_org_name = None
            if org.get('parent_org_id'):
                parent_org = db.client.table('organization')\
                    .select('name')\
                    .eq('id', org['parent_org_id'])\
                    .single()\
                    .execute()
                parent_org_name = parent_org.data.get('name') if parent_org.data else None
            
            record = {
                'org_id': org['id'],
                'name': org.get('name'),
                'org_type': org.get('org_type'),
                'sport': org.get('sport'),
                'industry': org.get('industry'),
                'is_active': org.get('is_active', True),
                'parent_org_id': org.get('parent_org_id'),
                'parent_org_name': parent_org_name,
                'current_employees': len(current_employees.data) if current_employees.data else 0,
                'total_employees': total_employees.count if total_employees else 0,
                'executive_count': executive_count,
                'last_updated': 'now()'
            }
            summary_records.append(record)
        
        # Insert new records in batches
        batch_size = 50
        logger.info(f"Inserting {len(summary_records)} organization summary records...")
        
        for i in range(0, len(summary_records), batch_size):
            batch = summary_records[i:i + batch_size]
            result = db.client.table('organization_summary').insert(batch).execute()
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        logger.info("✅ organization_summary table refreshed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to refresh organization_summary: {e}")
        return False

def main():
    """Main function to refresh all summary tables"""
    logger.info("🔄 Starting summary table refresh...")
    
    # Refresh network_status
    logger.info("📊 Refreshing network_status table...")
    network_success = refresh_network_status()
    
    # Refresh organization_summary
    logger.info("🏢 Refreshing organization_summary table...")
    org_success = refresh_organization_summary()
    
    if network_success and org_success:
        logger.info("✅ All summary tables refreshed successfully!")
        print("✅ Summary tables refresh completed successfully!")
    else:
        logger.error("❌ Some summary table refreshes failed")
        print("❌ Summary table refresh had errors - check logs")

if __name__ == "__main__":
    main()
