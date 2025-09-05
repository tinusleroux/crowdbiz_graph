"""
Enhanced Database Manager - Using Summary Tables for Performance
This eliminates the complex joins that were causing "Server disconnected" errors
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from app.core.logger import get_logger

logger = get_logger("database_enhanced")

class EnhancedDatabaseManager:
    """
    Enhanced database manager using summary tables for better performance
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.client = db_manager.client
    
    def get_network_status(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """
        Get people data from the network_status summary table - NO JOINS REQUIRED!
        This replaces the complex enriched people query that was causing connection issues.
        """
        try:
            query = self.client.table('network_status').select('*')
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if value:
                        if key == 'name':
                            query = query.ilike('full_name', f'%{value}%')
                        elif key == 'organization':
                            query = query.ilike('current_organization', f'%{value}%')
                        elif key == 'org_type':
                            query = query.eq('current_org_type', value)
                        elif key == 'sport':
                            query = query.eq('current_sport', value)
                        elif key == 'is_executive':
                            query = query.eq('is_executive', value)
                        else:
                            query = query.eq(key, value)
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            # Order by name
            query = query.order('full_name')
            
            result = query.execute()
            return result.data if result else []
            
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return []
    
    def get_organization_summary(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """
        Get organization data from the organization_summary table - NO JOINS REQUIRED!
        """
        try:
            query = self.client.table('organization_summary').select('*')
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if value:
                        if key == 'name':
                            query = query.ilike('name', f'%{value}%')
                        else:
                            query = query.eq(key, value)
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            # Order by employee count (most employees first)
            query = query.order('current_employees', desc=True)
            
            result = query.execute()
            return result.data if result else []
            
        except Exception as e:
            logger.error(f"Failed to get organization summary: {e}")
            return []
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard statistics using summary tables - MUCH FASTER!
        """
        try:
            stats = {}
            
            # Count total people (from network_status table)
            people_count = self.client.table('network_status').select('*', count='exact').execute()
            stats['total_people'] = people_count.count if people_count else 0
            
            # Count total organizations (from organization_summary table)  
            org_count = self.client.table('organization_summary').select('*', count='exact').execute()
            stats['total_organizations'] = org_count.count if org_count else 0
            
            # Count executives (from network_status table)
            exec_count = self.client.table('network_status')\
                .select('*', count='exact')\
                .eq('is_executive', True)\
                .execute()
            stats['total_executives'] = exec_count.count if exec_count else 0
            
            # Count people with current roles
            employed_count = self.client.table('network_status')\
                .select('*', count='exact')\
                .not_.is_('current_organization', 'null')\
                .execute()
            stats['people_with_roles'] = employed_count.count if employed_count else 0
            
            # Get organization types distribution
            org_types = self.client.table('organization_summary')\
                .select('org_type')\
                .execute()
                
            if org_types and org_types.data:
                type_counts = {}
                for org in org_types.data:
                    org_type = org.get('org_type', 'Unknown')
                    type_counts[org_type] = type_counts.get(org_type, 0) + 1
                stats['organization_types'] = type_counts
            else:
                stats['organization_types'] = {}
            
            # Get sports distribution
            sports = self.client.table('organization_summary')\
                .select('sport')\
                .not_.is_('sport', 'null')\
                .execute()
                
            if sports and sports.data:
                sport_counts = {}
                for org in sports.data:
                    sport = org.get('sport', 'Unknown')
                    sport_counts[sport] = sport_counts.get(sport, 0) + 1
                stats['sports_distribution'] = sport_counts
            else:
                stats['sports_distribution'] = {}
                
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                'total_people': 0,
                'total_organizations': 0, 
                'total_executives': 0,
                'people_with_roles': 0,
                'organization_types': {},
                'sports_distribution': {}
            }
    
    def search_people(self, query: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Search people using the network_status table - MUCH FASTER!
        """
        if not query:
            return []
            
        try:
            # Search in network_status table (no joins needed!)
            result = self.client.table('network_status')\
                .select('*')\
                .or_(f"full_name.ilike.%{query}%,current_organization.ilike.%{query}%,current_job_title.ilike.%{query}%")\
                .limit(limit)\
                .offset(offset)\
                .order('full_name')\
                .execute()
                
            return result.data if result else []
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def refresh_summary_tables(self) -> Dict[str, int]:
        """
        Refresh both summary tables - call this daily or when data changes significantly
        """
        results = {}
        
        try:
            # Refresh network_status table
            network_result = self.client.rpc('refresh_network_status').execute()
            results['network_status'] = network_result.data if network_result else 0
            
            # Refresh organization_summary table  
            org_result = self.client.rpc('refresh_organization_summary').execute()
            results['organization_summary'] = org_result.data if org_result else 0
            
            logger.info(f"Summary tables refreshed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to refresh summary tables: {e}")
            return {'network_status': 0, 'organization_summary': 0}

# Usage example functions
def get_top_organizations_by_employees(enhanced_db, limit: int = 10) -> List[Dict]:
    """Get organizations with the most employees"""
    return enhanced_db.client.table('organization_summary')\
        .select('name, current_employees, executive_count, org_type, sport')\
        .order('current_employees', desc=True)\
        .limit(limit)\
        .execute().data

def get_executives_by_organization(enhanced_db, org_name: str = None) -> List[Dict]:
    """Get all executives, optionally filtered by organization"""
    query = enhanced_db.client.table('network_status')\
        .select('full_name, current_job_title, current_organization, current_org_type')\
        .eq('is_executive', True)
    
    if org_name:
        query = query.ilike('current_organization', f'%{org_name}%')
        
    return query.order('current_organization', 'full_name').execute().data

def get_organization_details(enhanced_db, org_name: str) -> Optional[Dict]:
    """Get detailed information about a specific organization"""  
    result = enhanced_db.client.table('organization_summary')\
        .select('*')\
        .ilike('name', f'%{org_name}%')\
        .limit(1)\
        .execute()
    
    return result.data[0] if result and result.data else None

print("Enhanced Database Manager created with summary tables support!")
print("Benefits:")
print("✅ No more complex joins")
print("✅ No more 'Server disconnected' errors")  
print("✅ Much faster dashboard loading")
print("✅ Simplified queries")
print("✅ Better caching opportunities")
