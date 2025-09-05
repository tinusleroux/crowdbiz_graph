#!/usr/bin/env python3
"""
Script to connect to Supabase and pull the live database schema
"""

import os
import sys
import psycopg2
from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def get_postgres_connection():
    """Get a direct PostgreSQL connection for schema queries"""
    # Try DATABASE_URL first
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    
    if db_url:
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

def execute_query(conn, query: str, params=None):
    """Execute a SQL query and return results"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Query failed: {e}")
        return []

def get_tables(conn):
    """Get all tables in the public schema"""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
    """
    result = execute_query(conn, query)
    return [row['table_name'] for row in result]

def get_table_info(conn, table_name):
    """Get detailed information about a table"""
    # Get columns
    columns_query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = %s
    ORDER BY ordinal_position
    """
    columns = execute_query(conn, columns_query, (table_name,))
    
    # Get constraints
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
    constraints = execute_query(conn, constraints_query, (table_name,))
    
    # Get record count
    count_query = f"SELECT COUNT(*) as count FROM \"{table_name}\""
    count_result = execute_query(conn, count_query)
    record_count = count_result[0]['count'] if count_result else 0
    
    return {
        'name': table_name,
        'columns': columns,
        'constraints': constraints,
        'record_count': record_count
    }

def get_views(conn):
    """Get all views"""
    query = """
    SELECT table_name
    FROM information_schema.views 
    WHERE table_schema = 'public'
    ORDER BY table_name
    """
    result = execute_query(conn, query)
    return [row['table_name'] for row in result]

def get_functions(conn):
    """Get all functions"""
    query = """
    SELECT routine_name, routine_type
    FROM information_schema.routines 
    WHERE routine_schema = 'public'
    AND routine_type = 'FUNCTION'
    ORDER BY routine_name
    """
    return execute_query(conn, query)

def print_schema(conn):
    """Print the complete database schema"""
    print("=" * 80)
    print("🏈 CrowdBiz Graph - Live Database Schema from Supabase")
    print("=" * 80)
    
    # Test connection
    version_result = execute_query(conn, "SELECT version();")
    if version_result:
        version = version_result[0]['version']
        print(f"✅ PostgreSQL Version: {version.split(',')[0]}")
    
    # Get schema objects
    tables = get_tables(conn)
    views = get_views(conn)
    functions = get_functions(conn)
    
    print(f"\n📊 Schema Summary:")
    print(f"   Tables: {len(tables)}")
    print(f"   Views: {len(views)}")
    print(f"   Functions: {len(functions)}")
    
    # Print detailed table information
    print(f"\n📋 Tables Detail:")
    for table_name in tables:
        info = get_table_info(conn, table_name)
        print(f"\n🗃️  {table_name.upper()} ({info['record_count']:,} records)")
        
        # Columns
        print("   Columns:")
        for col in info['columns']:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"     • {col['column_name']} {col['data_type']} {nullable}{default}")
        
        # Constraints
        if info['constraints']:
            print("   Constraints:")
            for const in info['constraints']:
                if const['constraint_type'] == 'PRIMARY KEY':
                    print(f"     🔑 PK: {const['column_name']}")
                elif const['constraint_type'] == 'FOREIGN KEY':
                    print(f"     🔗 FK: {const['column_name']} → {const['foreign_table_name']}.{const['foreign_column_name']}")
                elif const['constraint_type'] == 'UNIQUE':
                    print(f"     🎯 UNIQUE: {const['column_name']}")
                elif const['constraint_type'] == 'CHECK':
                    print(f"     ✅ CHECK: {const['constraint_name']}")
    
    # Print views
    if views:
        print(f"\n👁️  Views:")
        for view in views:
            print(f"   • {view}")
    
    # Print functions
    if functions:
        print(f"\n⚙️  Functions:")
        for func in functions:
            print(f"   • {func['routine_name']}() [{func['routine_type']}]")

def main():
    """Main function"""
    print("🔧 CrowdBiz Graph Schema Explorer")
    print("=" * 50)
    
    try:
        print("\n🔌 Connecting to PostgreSQL...")
        conn = get_postgres_connection()
        
        if not conn:
            print("❌ Could not establish connection")
            return
        
        print("✅ Connected successfully!")
        
        # Print the schema
        print_schema(conn)
        
        # Close connection
        conn.close()
        print(f"\n✅ Schema exploration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
