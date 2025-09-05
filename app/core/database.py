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
        """Search for people in the database"""
        if not query or not self.is_connected():
            return []
        
        try:
            # Use simple text search across name fields
            people_query = self.client.table('person').select('*')
            people_query = people_query.or_(
                f"full_name.ilike.%{query}%,"
                f"first_name.ilike.%{query}%,"
                f"last_name.ilike.%{query}%"
            )
            result = people_query.limit(limit).offset(offset).execute()
            
            return result.data if result else []
            
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
