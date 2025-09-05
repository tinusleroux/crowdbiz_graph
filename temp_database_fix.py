#!/usr/bin/env python3
"""
Temporary fix for database connection issues
This shows improved error handling for the database operations
"""

import time
import random
from typing import Dict, List, Optional, Any

def retry_database_operation(operation_func, max_retries=3, base_delay=1.0):
    """
    Retry database operations with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return operation_func()
        except Exception as e:
            if "Server disconnected" in str(e) or "connection" in str(e).lower():
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Database connection failed (attempt {attempt + 1}), retrying in {delay:.1f}s")
                    time.sleep(delay)
                    continue
            raise e
    
    raise Exception(f"Database operation failed after {max_retries} attempts")

def improved_enrich_person_data(db_manager, person):
    """
    Improved version of person enrichment with better error handling
    """
    def get_current_roles():
        return db_manager.client.table('role')\
            .select('job_title, dept, start_date, is_executive, organization!inner(name, org_type, sport, industry)')\
            .eq('person_id', person['id'])\
            .eq('is_current', True)\
            .order('start_date', desc=True)\
            .limit(5)\
            .execute()
    
    try:
        # Use retry logic for the database operation
        current_roles = retry_database_operation(get_current_roles, max_retries=2, base_delay=0.5)
        
        # Process the enriched data...
        enriched_person = person.copy()
        
        # Privacy filter
        sensitive_fields = ['email', 'embedding', 'company_domain']
        for field in sensitive_fields:
            enriched_person.pop(field, None)
        
        if current_roles.data:
            primary_role = current_roles.data[0]
            enriched_person.update({
                'job_title': primary_role.get('job_title'),
                'department': primary_role.get('dept'),
                'start_date': primary_role.get('start_date'),
                'is_executive': primary_role.get('is_executive', False),
                'current_roles_count': len(current_roles.data)
            })
            
            if primary_role.get('organization'):
                org = primary_role['organization']
                enriched_person.update({
                    'organization': org.get('name'),
                    'org_type': org.get('org_type'),
                    'sport': org.get('sport'),
                    'industry': org.get('industry')
                })
        
        return enriched_person
        
    except Exception as e:
        logger.warning(f"Could not enrich person {person.get('id')}: {e}")
        # Return the person with privacy filtering but without enrichment
        filtered_person = person.copy()
        sensitive_fields = ['email', 'embedding', 'company_domain']
        for field in sensitive_fields:
            filtered_person.pop(field, None)
        return filtered_person

print("This file shows improved error handling patterns for the database connection issues.")
print("The main improvements are:")
print("1. Retry logic with exponential backoff")
print("2. Better error classification (connection vs other errors)")
print("3. Graceful degradation when enrichment fails")
print("4. Reduced query complexity to avoid timeouts")
