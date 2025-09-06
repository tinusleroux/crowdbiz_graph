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
    """Refresh the network_status summary table efficiently."""
    db = get_database_manager()
    
    if not db.is_connected():
        logger.error("Database not connected")
        return False
    
    try:
        # 1. Clear existing data
        logger.info("Clearing existing network_status data...")
        db.client.table('network_status').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        # 2. Fetch all necessary data in bulk
        logger.info("Fetching all current roles with person and organization data...")
        
        roles_response = db.client.table('role') \
            .select('job_title, dept, standardized_department, start_date, is_executive, person:person_id(*), organization(*)') \
            .eq('is_current', True) \
            .execute()
            
        if not roles_response.data:
            logger.warning("No current roles found. Network status will be empty.")
            return True

        roles_data = roles_response.data
        logger.info(f"Found {len(roles_data)} current roles to process.")

        # 3. Get total role counts for all people efficiently
        logger.info("Fetching total role counts for all people...")
        all_roles_response = db.client.table('role').select('person_id', count='exact').execute()
        
        total_roles_counts = {}
        if all_roles_response.data:
            # This is a workaround since PostgREST doesn't support GROUP BY directly
            from collections import Counter
            person_ids = [role['person_id'] for role in all_roles_response.data]
            total_roles_counts = Counter(person_ids)

        # 4. Process data in memory
        network_status_records = []
        
        # Group roles by person to handle multiple current roles
        person_roles = {}
        for role in roles_data:
            if not role.get('person'):
                continue
            person_id = role['person']['id']
            if person_id not in person_roles:
                person_roles[person_id] = []
            person_roles[person_id].append(role)

        for person_id, roles in person_roles.items():
            primary_role = roles[0]  # Take the first role as the primary one
            person = primary_role.get('person')
            organization = primary_role.get('organization')

            if not person or not organization:
                continue  # Skip if data is incomplete

            record = {
                'person_id': person['id'],
                'full_name': person.get('full_name'),
                'first_name': person.get('first_name'),
                'last_name': person.get('last_name'),
                'linkedin_url': person.get('linkedin_url'),
                'current_job_title': primary_role.get('job_title'),
                'current_department': primary_role.get('dept'),
                'current_standardized_department': primary_role.get('standardized_department'),
                'current_organization': organization.get('name'),
                'current_org_type': organization.get('org_type'),
                'current_sport': organization.get('sport'),
                'current_industry': organization.get('industry'),
                'is_executive': primary_role.get('is_executive', False),
                'role_start_date': primary_role.get('start_date'),
                'current_roles_count': len(roles),
                'total_roles_count': total_roles_counts.get(person_id, 0),
                'created_at': person.get('created_at'),
                'last_updated': 'now()'
            }
            network_status_records.append(record)

        # 5. Insert new records in batches
        if network_status_records:
            batch_size = 200  # Increased batch size for efficiency
            logger.info(f"Inserting {len(network_status_records)} records in batches of {batch_size}...")
            
            for i in range(0, len(network_status_records), batch_size):
                batch = network_status_records[i:i + batch_size]
                db.client.table('network_status').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        logger.info("✅ network_status table refreshed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to refresh network_status: {e}", exc_info=True)
        return False

def refresh_organization_summary():
    """Refresh the organization_summary table efficiently."""
    db = get_database_manager()
    
    if not db.is_connected():
        logger.error("Database not connected")
        return False
    
    try:
        # 1. Clear existing data
        logger.info("Clearing existing organization_summary data...")
        db.client.table('organization_summary').delete().neq('org_id', '00000000-0000-0000-0000-000000000000').execute()
        
        # 2. Fetch all necessary data in bulk
        logger.info("Fetching all organizations and roles in bulk...")
        orgs_response = db.client.table('organization').select('*').execute()
        roles_response = db.client.table('role').select('org_id, is_current, is_executive').execute()

        if not orgs_response.data:
            logger.warning("No organizations found.")
            return True
            
        organizations = orgs_response.data
        roles = roles_response.data
        logger.info(f"Found {len(organizations)} organizations and {len(roles)} roles to process.")

        # 3. Process data in memory
        org_map = {org['id']: org for org in organizations}
        parent_org_names = {org['id']: org.get('name') for org in organizations}

        from collections import defaultdict
        current_employees = defaultdict(int)
        total_employees = defaultdict(int)
        executive_count = defaultdict(int)

        for role in roles:
            org_id = role['org_id']
            total_employees[org_id] += 1
            if role['is_current']:
                current_employees[org_id] += 1
                if role['is_executive']:
                    executive_count[org_id] += 1

        # 4. Create summary records
        summary_records = []
        for org_id, org_data in org_map.items():
            parent_org_id = org_data.get('parent_org_id')
            record = {
                'org_id': org_id,
                'name': org_data.get('name'),
                'org_type': org_data.get('org_type'),
                'sport': org_data.get('sport'),
                'industry': org_data.get('industry'),
                'is_active': org_data.get('is_active', True),
                'parent_org_id': parent_org_id,
                'parent_org_name': parent_org_names.get(parent_org_id),
                'current_employees': current_employees[org_id],
                'total_employees': total_employees[org_id],
                'executive_count': executive_count[org_id],
                'last_updated': 'now()'
            }
            summary_records.append(record)
        
        # 5. Insert new records in batches
        if summary_records:
            batch_size = 100
            logger.info(f"Inserting {len(summary_records)} organization summary records...")
            
            for i in range(0, len(summary_records), batch_size):
                batch = summary_records[i:i + batch_size]
                db.client.table('organization_summary').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        logger.info("✅ organization_summary table refreshed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to refresh organization_summary: {e}", exc_info=True)
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
