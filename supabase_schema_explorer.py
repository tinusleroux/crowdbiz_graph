#!/usr/bin/env python3
"""
Script to get schema info from Supabase using the REST API and available system functions
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_API_KEY')
    
    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_API_KEY")
        return None
    
    return create_client(url, key)

def get_table_list(client):
    """Get list of tables using introspection endpoint"""
    try:
        # Use the PostgREST API to query pg_tables system view
        response = client.postgrest.from_("pg_tables").select("tablename").eq("schemaname", "public").execute()
        return [row['tablename'] for row in response.data]
    except Exception as e:
        print(f"Error getting table list: {e}")
        return []

def get_table_columns(client, table_name):
    """Get columns for a table using information_schema"""
    try:
        # Query information_schema through the API
        response = client.postgrest.rpc("get_table_columns", {"table_name": table_name}).execute()
        return response.data
    except Exception as e:
        print(f"Could not get columns for {table_name}: {e}")
        return []

def test_table_access(client, table_name):
    """Test if we can access a table and get its row count"""
    try:
        # Get total count
        response = client.table(table_name).select("*", count="exact").limit(0).execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        print(f"Could not access table {table_name}: {e}")
        return None

def get_accessible_tables(client):
    """Get tables that we can actually access"""
    # Known tables from your migration files
    known_tables = [
        'person', 'organization', 'role', 'source', 'news_item',
        'import_batch', 'person_staging', 'organization_staging', 
        'role_staging', 'news_item_staging', 'network_status', 
        'organization_summary'
    ]
    
    accessible_tables = []
    
    for table in known_tables:
        count = test_table_access(client, table)
        if count is not None:
            accessible_tables.append({
                'name': table,
                'count': count
            })
        else:
            print(f"⚠️  Table '{table}' not accessible or doesn't exist")
    
    return accessible_tables

def sample_table_data(client, table_name, limit=3):
    """Get sample data from a table"""
    try:
        response = client.table(table_name).select("*").limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Could not sample {table_name}: {e}")
        return []

def print_live_schema_analysis(client):
    """Print analysis of the live schema"""
    print("=" * 80)
    print("🏈 CrowdBiz Graph - Live Schema Analysis (via Supabase REST API)")
    print("=" * 80)
    
    # Get accessible tables
    print("\n📊 Analyzing accessible tables...")
    tables = get_accessible_tables(client)
    
    if not tables:
        print("❌ No accessible tables found")
        return
    
    print(f"\n✅ Found {len(tables)} accessible tables:")
    
    total_records = 0
    for table in tables:
        count = table['count']
        total_records += count
        print(f"   📋 {table['name']}: {count:,} records")
    
    print(f"\n📈 Total records across all tables: {total_records:,}")
    
    # Show sample data from key tables
    print(f"\n🔍 Sample Data from Key Tables:")
    
    key_tables = ['person', 'organization', 'role', 'network_status', 'organization_summary']
    
    for table_info in tables:
        table_name = table_info['name']
        if table_name in key_tables and table_info['count'] > 0:
            print(f"\n   🗃️  {table_name.upper()} (showing first 3 records)")
            sample_data = sample_table_data(client, table_name, 3)
            
            if sample_data:
                # Show column names
                columns = list(sample_data[0].keys())
                print(f"      Columns: {', '.join(columns)}")
                
                # Show sample rows
                for i, row in enumerate(sample_data, 1):
                    print(f"      Row {i}:")
                    for col, val in row.items():
                        # Truncate long values
                        if val is not None:
                            val_str = str(val)
                            if len(val_str) > 50:
                                val_str = val_str[:47] + "..."
                        else:
                            val_str = "NULL"
                        print(f"        {col}: {val_str}")
    
    # Show staging tables status
    staging_tables = [t for t in tables if 'staging' in t['name']]
    if staging_tables:
        print(f"\n📥 Staging Tables (Import Pipeline):")
        for table in staging_tables:
            print(f"   • {table['name']}: {table['count']} records")
    
    # Show summary tables status  
    summary_tables = [t for t in tables if t['name'] in ['network_status', 'organization_summary']]
    if summary_tables:
        print(f"\n⚡ Performance Summary Tables:")
        for table in summary_tables:
            print(f"   • {table['name']}: {table['count']} records")

def main():
    """Main function"""
    print("🔧 CrowdBiz Graph - Supabase Schema Explorer")
    print("=" * 50)
    
    try:
        print("\n🔌 Connecting to Supabase...")
        client = get_supabase_client()
        
        if not client:
            return
        
        print("✅ Connected to Supabase!")
        
        # Test basic connectivity
        print("\n🧪 Testing connection...")
        test_response = client.table('person').select("count", count="exact").limit(0).execute()
        if test_response:
            print(f"✅ API connection successful!")
        
        # Analyze the schema
        print_live_schema_analysis(client)
        
        print(f"\n✅ Schema analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
