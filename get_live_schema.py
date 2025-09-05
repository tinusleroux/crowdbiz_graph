#!/usr/bin/env python3
"""
Script to connect to Supabase and pull the live database schema
Uses the same connection pattern as the CrowdBiz Graph application
"""

import os
import sys
import psycopg2
from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import get_config
from app.core.database import get_database_manager

def get_postgres_connection():
    """Get a direct PostgreSQL connection for schema queries"""
    config = get_config()
    
    # Parse the DATABASE_URL to get connection parameters
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    
    if db_url:
        # Use the full DATABASE_URL
        try:
            return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Failed to connect with DATABASE_URL: {e}")
    
    # Fallback to individual parameters
    try:
        return psycopg2.connect(
            host=os.getenv('SUPABASE_HOST', 'aws-0-us-east-1.pooler.supabase.com'),
            port=int(os.getenv('SUPABASE_PORT', '6543')),
            database=os.getenv('SUPABASE_DB_NAME', 'postgres'),
            user=os.getenv('SUPABASE_USER', 'postgres.bmabudpcmfizqxuifiqf'),
            password=os.getenv('SUPABASE_PASSWORD', os.getenv('SUPABASE_DATABASE_PASSWORD')),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        print(f"Failed to connect with individual parameters: {e}")
        return None

def execute_sql_query(conn, query: str, params=None) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"SQL query failed: {e}")
        return []

def get_table_schema(conn, table_name: str) -> Dict[str, Any]:
    """Get detailed schema information for a specific table"""
    try:
        # Get column information
        columns_query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """
        
        columns = execute_sql_query(conn, columns_query, (table_name,))
        
        # Get constraints information
        constraints_query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_schema = 'public' AND tc.table_name = %s
        """
        
        constraints = execute_sql_query(conn, constraints_query, (table_name,))
        
        # Get indexes information
        indexes_query = """
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename = %s
        """
        
        indexes = execute_sql_query(conn, indexes_query, (table_name,))
        
        return {
            'table_name': table_name,
            'columns': columns,
            'constraints': constraints,
            'indexes': indexes
        }
        
    except Exception as e:
        print(f"Error getting schema for table {table_name}: {e}")
        return {'table_name': table_name, 'error': str(e)}

def get_all_tables(conn) -> List[str]:
    """Get list of all user tables in the public schema"""
    try:
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        result = execute_sql_query(conn, query)
        return [row['table_name'] for row in result]
        
    except Exception as e:
        print(f"Error getting table list: {e}")
        return []

def get_views(conn) -> List[Dict[str, Any]]:
    """Get list of all views"""
    try:
        query = """
        SELECT 
            table_name,
            view_definition
        FROM information_schema.views 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        
        return execute_sql_query(conn, query)
        
    except Exception as e:
        print(f"Error getting views: {e}")
        return []

def get_functions(conn) -> List[Dict[str, Any]]:
    """Get list of all functions"""
    try:
        query = """
        SELECT 
            routine_name,
            routine_type,
            data_type AS return_type,
            routine_definition
        FROM information_schema.routines 
        WHERE routine_schema = 'public'
        AND routine_type = 'FUNCTION'
        ORDER BY routine_name
        """
        
        return execute_sql_query(conn, query)
        
    except Exception as e:
        print(f"Error getting functions: {e}")
        return []

def get_table_count(conn, table_name: str) -> int:
    """Get record count for a table"""
    try:
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = execute_sql_query(conn, query)
        return result[0]['count'] if result else 0
    except Exception as e:
        print(f"Error counting records in {table_name}: {e}")
        return 0

def print_schema_summary(conn):
    """Print a comprehensive schema summary"""
    print("=" * 80)
    print("🏈 CrowdBiz Graph - Live Database Schema")
    print("=" * 80)
    
    # Get basic stats
    try:
        tables = get_all_tables(conn)
        views = get_views(conn)
        functions = get_functions(conn)
        
        print(f"\n📊 Schema Overview:")
        print(f"   Tables: {len(tables)}")
        print(f"   Views: {len(views)}")
        print(f"   Functions: {len(functions)}")
        
        # Show table details
        print(f"\n📋 Tables:")
        for table_name in tables:
            schema = get_table_schema(conn, table_name)
            if 'error' in schema:
                print(f"   ❌ {table_name} - Error: {schema['error']}")
                continue
                
            columns = schema.get('columns', [])
            constraints = schema.get('constraints', [])
            indexes = schema.get('indexes', [])
            
            print(f"\n   🗃️  {table_name.upper()}")
            print(f"      Columns: {len(columns)}")
            
            # Show columns
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"        • {col['column_name']} {col['data_type']} {nullable}{default}")
            
            # Show constraints
            if constraints:
                print(f"      Constraints:")
                for const in constraints:
                    if const['constraint_type'] == 'PRIMARY KEY':
                        print(f"        🔑 PK: {const['column_name']}")
                    elif const['constraint_type'] == 'FOREIGN KEY':
                        print(f"        🔗 FK: {const['column_name']} → {const['foreign_table_name']}.{const['foreign_column_name']}")
                    elif const['constraint_type'] == 'UNIQUE':
                        print(f"        🎯 UNIQUE: {const['column_name']}")
                    elif const['constraint_type'] == 'CHECK':
                        print(f"        ✅ CHECK: {const['constraint_name']}")
            
            # Show indexes
            if indexes:
                print(f"      Indexes: {len(indexes)}")
                for idx in indexes:
                    print(f"        📇 {idx['indexname']}")
        
        # Show views
        if views:
            print(f"\n👁️  Views:")
            for view in views:
                print(f"   • {view['table_name']}")
        
        # Show functions
        if functions:
            print(f"\n⚙️  Functions:")
            for func in functions:
                print(f"   • {func['routine_name']}() → {func['return_type']}")
        
        # Get record counts for each table
        print(f"\n📈 Record Counts:")
        for table_name in tables:
            count = get_table_count(conn, table_name)
            print(f"   {table_name}: {count:,} records")
        
    except Exception as e:
        print(f"Error in schema summary: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to connect and display schema"""
    print("🔧 CrowdBiz Graph Schema Explorer")
    print("=" * 50)
    
    # Load configuration
    config = get_config()
    print(f"Database URL: {config.database.url[:50]}...")
    print(f"Has API Key: {'✅' if config.database.api_key else '❌'}")
    
    # Validate config
    is_valid, errors = config.validate()
    if not is_valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"   • {error}")
        return
    
    print("✅ Configuration validated")
    
    # First try to test Supabase REST API connection
    try:
        print("\n🧪 Testing Supabase REST API connection...")
        db = get_database_manager()
        if db.is_connected():
            print("✅ Supabase REST API connected successfully")
        else:
            print("❌ Supabase REST API connection failed")
    except Exception as e:
        print(f"❌ Supabase REST API connection error: {e}")
    
    # Now try direct PostgreSQL connection for schema
    try:
        print("\n🔌 Connecting to PostgreSQL directly for schema...")
        conn = get_postgres_connection()
        
        if not conn:
            print("❌ Could not establish PostgreSQL connection")
            return
        
        # Test connection with a simple query
        print("🧪 Testing PostgreSQL connection...")
        test_result = execute_sql_query(conn, "SELECT version();")
        if test_result:
            version = test_result[0]['version']
            print(f"✅ Connected! PostgreSQL version: {version[:60]}...")
        
        # Print the full schema
        print_schema_summary(conn)
        
        print(f"\n✅ Schema analysis complete!")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
