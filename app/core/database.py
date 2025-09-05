"""
Database operations and connection management
Centralized Supabase client and database utilities
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st

from .config import get_config
from .logger import get_logger

# Load environment variables
load_dotenv()
logger = get_logger("database")

class DatabaseManager:
    """Centralized database operations manager"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        config = get_config()
        
        if not config.database.validate():
            logger.error("Database configuration invalid - missing URL or API key")
            return
        
        try:
            self.client = create_client(
                config.database.url,
                config.database.api_key
            )
            logger.info("Database client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database client: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if database connection is available"""
        return self.client is not None
    
    def safe_query(self, table: str, operation: str, **kwargs) -> Optional[Any]:
        """Safely execute database queries with error handling"""
        if not self.is_connected():
            logger.error("Database client not available")
            return None
        
        try:
            if operation == "select":
                query = self.client.table(table).select("*")
                
                # Apply filters if provided
                if "filters" in kwargs:
                    for key, value in kwargs["filters"].items():
                        if value is not None:
                            query = query.ilike(key, f"%{value}%")
                
                # Apply limit and offset
                if "limit" in kwargs:
                    query = query.limit(kwargs["limit"])
                if "offset" in kwargs:
                    query = query.offset(kwargs["offset"])
                
                # Apply ordering
                if "order_by" in kwargs:
                    query = query.order(kwargs["order_by"])
                
                result = query.execute()
                return result.data if result else []
                
            elif operation == "insert":
                result = self.client.table(table).insert(kwargs["data"]).execute()
                return result.data if result else None
                
            elif operation == "update":
                query = self.client.table(table).update(kwargs["data"])
                if "filters" in kwargs:
                    for key, value in kwargs["filters"].items():
                        query = query.eq(key, value)
                result = query.execute()
                return result.data if result else None
                
            elif operation == "delete":
                query = self.client.table(table)
                if "filters" in kwargs:
                    for key, value in kwargs["filters"].items():
                        query = query.eq(key, value)
                result = query.execute()
                return result.data if result else None
                
            elif operation == "count":
                result = self.client.table(table).select("*", count="exact").execute()
                return result.count if result else 0
                
        except Exception as e:
            logger.error(f"Database query failed - table: {table}, operation: {operation}, error: {e}")
            return None
    
    def search_people(self, query: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Search for people in the database with their organization info"""
        if not query or not self.is_connected():
            return []
        
        try:
            # First get people matching the search
            people_query = self.client.table('person').select('*')
            people_query = people_query.or_(
                f"full_name.ilike.%{query}%,"
                f"first_name.ilike.%{query}%,"
                f"last_name.ilike.%{query}%"
            )
            people_result = people_query.limit(limit).offset(offset).execute()
            
            if not people_result.data:
                return []
            
            # Enhance each person with their current role/organization info
            enhanced_people = []
            for person in people_result.data:
                try:
                    # Get current roles for this person using the materialized view
                    current_roles = self.client.table('v_role_current')\
                        .select('job_title, dept, organization!inner(name, org_type, sport)')\
                        .eq('person_id', person['id'])\
                        .execute()
                    
                    # Add organization info to person record
                    if current_roles.data:
                        role = current_roles.data[0]  # Take first current role
                        person['job_title'] = role.get('job_title')
                        person['department'] = role.get('dept')
                        if role.get('organization'):
                            org = role['organization']
                            person['organization'] = org.get('name')
                            person['org_type'] = org.get('org_type')
                            person['sport'] = org.get('sport')
                    
                    enhanced_people.append(person)
                    
                except Exception as role_error:
                    logger.warning(f"Could not get role info for person {person.get('id')}: {role_error}")
                    # Still include the person even without role info
                    enhanced_people.append(person)
            
            return enhanced_people
            
        except Exception as e:
            logger.error(f"People search failed: {e}")
            return []
    
    def search_organizations(self, query: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Search for organizations in the database"""
        if not query or not self.is_connected():
            return []
        
        try:
            org_query = self.client.table('organization').select('*')
            org_query = org_query.or_(
                f"name.ilike.%{query}%,"
                f"org_type.ilike.%{query}%,"
                f"sport.ilike.%{query}%"
            )
            result = org_query.limit(limit).offset(offset).execute()
            
            return result.data if result else []
            
        except Exception as e:
            logger.error(f"Organization search failed: {e}")
            return []
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        if not self.is_connected():
            return {}
        
        try:
            stats = {}
            
            # Count people
            people_count = self.safe_query('person', 'count')
            stats['total_people'] = people_count or 0
            
            # Count organizations
            org_count = self.safe_query('organization', 'count')
            stats['total_organizations'] = org_count or 0
            
            # Get organization type breakdown
            orgs = self.safe_query('organization', 'select')
            if orgs:
                org_type_counts = {}
                for org in orgs:
                    org_type = org.get('org_type', 'Unknown')
                    org_type_counts[org_type] = org_type_counts.get(org_type, 0) + 1
                stats['org_type_breakdown'] = [
                    {'org_type': k, 'count': v} 
                    for k, v in org_type_counts.items()
                ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {}

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

@st.cache_resource
def get_database_manager() -> DatabaseManager:
    """Get or create the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_supabase_client() -> Optional[Client]:
    """Get the Supabase client from the database manager"""
    db_manager = get_database_manager()
    return db_manager.client if db_manager else None

# Convenience functions for common operations
def search_database(query: str, search_type: str = "all", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Search the database with unified results"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return {"results": [], "total": 0, "error": "Database not connected"}
    
    try:
        results = []
        
        if search_type in ["all", "people"]:
            people_results = db_manager.search_people(query, limit, offset)
            for person in people_results:
                person['result_type'] = 'person'
                results.append(person)
        
        if search_type in ["all", "organizations"]:
            org_results = db_manager.search_organizations(query, limit, offset)
            for org in org_results:
                org['result_type'] = 'organization'
                results.append(org)
        
        return {
            "results": results[:limit],  # Ensure we don't exceed limit
            "total": len(results),
            "query": query,
            "search_type": search_type
        }
        
    except Exception as e:
        logger.error(f"Database search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}

def get_table_data(table: str, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
    """Get data from a specific table"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return []
    
    return db_manager.safe_query(
        table, 
        "select",
        limit=limit,
        offset=offset,
        filters=filters or {}
    ) or []

def get_enriched_people_data(limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
    """Get people data enriched with their current organizations and roles"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return []
    
    try:
        # Get people with their current roles and organizations using is_current flag
        people = db_manager.safe_query('person', 'select', limit=limit*2, offset=offset)
        
        if not people:
            return []
        
        enriched_people = []
        for person in people:
            try:
                # Get current roles for this person using is_current flag (more efficient)
                current_roles = db_manager.client.table('role')\
                    .select('job_title, dept, start_date, is_executive, organization!inner(name, org_type, sport, industry)')\
                    .eq('person_id', person['id'])\
                    .eq('is_current', True)\
                    .order('start_date', desc=True)\
                    .execute()
                
                # Create enriched person record with privacy filtering
                enriched_person = person.copy()
                
                # Privacy filter: Remove email and other sensitive fields
                sensitive_fields = ['email', 'embedding', 'company_domain']
                for field in sensitive_fields:
                    enriched_person.pop(field, None)
                
                if current_roles.data:
                    # Add primary role info (most recent)
                    primary_role = current_roles.data[0]
                    enriched_person['job_title'] = primary_role.get('job_title')
                    enriched_person['department'] = primary_role.get('dept')
                    enriched_person['start_date'] = primary_role.get('start_date')
                    enriched_person['is_executive'] = primary_role.get('is_executive', False)
                    
                    if primary_role.get('organization'):
                        org = primary_role['organization']
                        enriched_person['organization'] = org.get('name')
                        enriched_person['org_type'] = org.get('org_type')
                        enriched_person['sport'] = org.get('sport')
                        enriched_person['industry'] = org.get('industry')
                    
                    # Add count of total current roles
                    enriched_person['current_roles_count'] = len(current_roles.data)
                    
                    # Add multiple roles info if applicable
                    if len(current_roles.data) > 1:
                        enriched_person['additional_roles'] = f"+{len(current_roles.data)-1} more"
                else:
                    # Person with no current roles
                    enriched_person['job_title'] = None
                    enriched_person['organization'] = None
                    enriched_person['org_type'] = None
                    enriched_person['sport'] = None
                    enriched_person['industry'] = None
                    enriched_person['department'] = None
                    enriched_person['start_date'] = None
                    enriched_person['current_roles_count'] = 0
                    enriched_person['is_executive'] = False
                
                enriched_people.append(enriched_person)
                
            except Exception as role_error:
                logger.warning(f"Could not enrich person {person.get('id')}: {role_error}")
                # Include person without enrichment but with privacy filtering
                filtered_person = person.copy()
                sensitive_fields = ['email', 'embedding', 'company_domain']
                for field in sensitive_fields:
                    filtered_person.pop(field, None)
                enriched_people.append(filtered_person)
        
        return enriched_people[:limit]  # Respect the limit
        
    except Exception as e:
        logger.error(f"Failed to get enriched people data: {e}")
        return []

def get_enriched_organization_data(limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
    """Get organization data enriched with current employee counts and roles"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return []
    
    try:
        organizations = db_manager.safe_query('organization', 'select', limit=limit, offset=offset)
        
        if not organizations:
            return []
        
        enriched_orgs = []
        for org in organizations:
            try:
                # Get current employees/roles for this organization using is_current flag
                current_roles = db_manager.client.table('role')\
                    .select('person_id, job_title, is_executive, person!inner(full_name, first_name, last_name, linkedin_url)')\
                    .eq('org_id', org['id'])\
                    .eq('is_current', True)\
                    .order('is_executive', desc=True)\
                    .order('job_title')\
                    .execute()
                
                # Create enriched organization record
                enriched_org = org.copy()
                
                if current_roles.data:
                    enriched_org['current_people_count'] = len(current_roles.data)
                    
                    # Count executives vs non-executives
                    executives = [role for role in current_roles.data if role.get('is_executive')]
                    enriched_org['executive_count'] = len(executives)
                    enriched_org['non_executive_count'] = len(current_roles.data) - len(executives)
                    
                    # Add sample employees (top 3)
                    sample_employees = []
                    for role in current_roles.data[:3]:
                        if role.get('person'):
                            person = role['person']
                            employee_info = {
                                'name': person.get('full_name', f"{person.get('first_name', '')} {person.get('last_name', '')}").strip(),
                                'title': role.get('job_title'),
                                'is_executive': role.get('is_executive', False)
                            }
                            sample_employees.append(employee_info)
                    
                    enriched_org['sample_employees'] = sample_employees
                    
                    if len(current_roles.data) > 3:
                        enriched_org['additional_employees'] = f"+{len(current_roles.data)-3} more"
                    
                    # Get unique job titles
                    job_titles = list(set([role.get('job_title') for role in current_roles.data if role.get('job_title')]))
                    enriched_org['unique_job_titles'] = len(job_titles)
                    enriched_org['active_job_titles'] = ', '.join(job_titles[:3])
                    if len(job_titles) > 3:
                        enriched_org['active_job_titles'] += f' +{len(job_titles)-3} more'
                    
                    # Add key people names with executive indicator
                    key_people = []
                    for role in current_roles.data[:3]:
                        if role.get('person'):
                            name = role['person'].get('full_name', '')
                            if role.get('is_executive'):
                                name += ' (Executive)'
                            key_people.append(name)
                    enriched_org['key_people'] = ', '.join(key_people)
                    
                else:
                    # Organization with no current employees
                    enriched_org['current_people_count'] = 0
                    enriched_org['executive_count'] = 0
                    enriched_org['non_executive_count'] = 0
                    enriched_org['sample_employees'] = []
                    enriched_org['unique_job_titles'] = 0
                    enriched_org['active_job_titles'] = None
                    enriched_org['key_people'] = None
                
                enriched_orgs.append(enriched_org)
                
            except Exception as org_error:
                logger.warning(f"Could not enrich organization {org.get('id')}: {org_error}")
                enriched_orgs.append(org)
        
        return enriched_orgs
        
    except Exception as e:
        logger.error(f"Failed to get enriched organization data: {e}")
        return []

def insert_data(table: str, data: Dict) -> Optional[Dict]:
    """Insert data into a table"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return None
    
    return db_manager.safe_query(table, "insert", data=data)

def update_data(table: str, data: Dict, filters: Dict) -> Optional[Dict]:
    """Update data in a table"""
    db_manager = get_database_manager()
    
    if not db_manager.is_connected():
        return None
    
    return db_manager.safe_query(table, "update", data=data, filters=filters)
