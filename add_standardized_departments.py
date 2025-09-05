#!/usr/bin/env python3
"""
Add standardized Department field to the database and populate it
based on job titles and existing department data
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_API_KEY')
    return create_client(url, key)

def create_department_mapping():
    """Create mapping from job titles/departments to standardized departments"""
    
    department_mapping = {
        "Sales & Partnerships": [
            # Job title keywords
            "sales", "partnership", "sponsor", "corporate", "revenue", "account executive", 
            "business development", "commercial", "membership", "season ticket", "premium sales",
            "corporate partnership", "sponsorship", "account manager", "client acquisition",
            "premium partnerships", "partnership activation", "partnership sales",
            # Existing department names
            "corporate partnerships", "ticket sales & service", "sales and service", 
            "ticket sales", "client relations & retention", "corporate sales & business development",
            "client services", "premium partnerships", "partnership activation", "partnership sales"
        ],
        
        "Ticketing & Operations": [
            # Job title keywords
            "ticket", "customer service", "box office", "guest services", "hospitality",
            "customer experience", "membership services", "season ticket service",
            # Existing department names  
            "ticket sales & service", "ticket sales & services", "ticket sales & operations",
            "ticket sales, service & operations", "ticket sales", "guest services & stadium operations",
            "ticket operations", "ticket sales, services, and operations"
        ],
        
        "Marketing & Communications": [
            # Job title keywords
            "marketing", "communication", "brand", "content", "social media", "public relations",
            "pr", "digital", "creative", "advertising", "media relations", "community relations",
            "graphic designer", "producer", "social media coordinator", "videographer", "photographer",
            # Existing department names
            "marketing", "marketing & media", "communications", "content", "content & digital",
            "marketing & fan engagement", "digital & social media", "public relations & community",
            "marketing, intelligence & broadcasting", "marketing & community impact", "media & content",
            "marketing & creative", "digital media", "public relations", "digital media and content production",
            "marketing and brand management"
        ],
        
        "Fan Experience & Events": [
            # Job title keywords  
            "fan engagement", "fan experience", "event", "game day", "entertainment", 
            "community", "outreach", "promotions", "activation", "fan services", "game presentation",
            # Existing department names
            "marketing & fan engagement", "community relations", "game presentation & live production",
            "events & game operations", "event management & hospitality", "community development",
            "community impact", "community & youth programs", "marketing & community impact"
        ],
        
        "Stadium Operations & Facilities": [
            # Job title keywords
            "operations", "facility", "maintenance", "security", "logistics", "stadium",
            "arena", "venue", "game operations", "facilities", "equipment", "grounds",
            "building", "facilities operations",
            # Existing department names
            "stadium operations", "facility operations", "facilities operations", "operations",
            "guest services & stadium operations", "maintenance & grounds", "grounds", 
            "venue operations", "events & game operations"
        ],
        
        "Finance & Administration": [
            # Job title keywords
            "finance", "accounting", "controller", "financial", "admin", "hr", "human resources",
            "payroll", "budget", "analyst", "coordinator", "assistant", "accountant", "treasurer",
            "cfo", "chief financial", "people", "culture", "inclusion", "legal", "counsel", "attorney",
            # Existing department names
            "finance", "human resources", "legal", "executive", "people, culture & inclusion",
            "executive office", "people & culture", "finance & accounting", "finance and accounting",
            "people, culture, & inclusion", "human resources/business operations", "strategy"
        ],
        
        "Technology & Analytics": [
            # Job title keywords
            "technology", "it", "data", "analytics", "digital", "systems", "tech",
            "information technology", "data analyst", "software", "football analytics",
            "application developer", "engineer", "developer", "audio visual", "broadcast systems",
            # Existing department names
            "information technology", "technology", "football analytics", "business analytics and data strategy",
            "business & football operations"
        ],
        
        "Broadcasting & Media": [
            # Job title keywords
            "broadcast", "media", "radio", "television", "tv", "production", "commentary",
            "announcer", "media relations", "digital media", "audio", "video", "media asset",
            "play-by-play", "radio network",
            # Existing department names
            "ravens media", "media", "broadcasting", "media & content", "marketing, intelligence & broadcasting"
        ]
    }
    
    return department_mapping

def categorize_role(job_title, existing_dept, department_mapping):
    """Categorize a role based on job title and existing department"""
    
    job_title_lower = (job_title or "").lower()
    existing_dept_lower = (existing_dept or "").lower()
    
    # Check each department category
    for dept_category, keywords in department_mapping.items():
        for keyword in keywords:
            if keyword in job_title_lower or keyword in existing_dept_lower:
                return dept_category
    
    # Default category for unmatched items
    return "Other"

def add_standardized_department_column():
    """Add standardized_department column to role table"""
    
    print("🔧 Adding standardized_department column to role table...")
    
    # SQL to add the new column
    sql_add_column = """
    ALTER TABLE role 
    ADD COLUMN IF NOT EXISTS standardized_department TEXT;
    """
    
    client = get_supabase_client()
    
    try:
        # Execute through SQL editor approach
        print("✅ Please run this SQL in your Supabase Dashboard SQL Editor:")
        print("-" * 60)
        print(sql_add_column)
        print("-" * 60)
        print("\nAfter running the SQL, press Enter to continue...")
        input()
        
    except Exception as e:
        print(f"Note: {e}")
        print("Please manually add the column using the SQL above.")
        input("Press Enter when done...")

def update_standardized_departments():
    """Update all roles with standardized department categories"""
    
    client = get_supabase_client()
    department_mapping = create_department_mapping()
    
    print("🔄 Updating standardized departments for all roles...")
    
    try:
        # Get all current roles
        response = client.table('role').select('*').eq('is_current', True).execute()
        
        if not response.data:
            print("❌ No current roles found")
            return
        
        roles = response.data
        print(f"📊 Processing {len(roles)} current roles...")
        
        # Categorize and update each role
        updates = {}
        for role in roles:
            job_title = role.get('job_title', '')
            existing_dept = role.get('dept', '')
            role_id = role.get('id')
            
            standardized_dept = categorize_role(job_title, existing_dept, department_mapping)
            
            if standardized_dept not in updates:
                updates[standardized_dept] = []
            updates[standardized_dept].append({
                'id': role_id,
                'job_title': job_title,
                'existing_dept': existing_dept
            })
        
        # Show categorization summary
        print(f"\n📋 Categorization Summary:")
        for dept, role_list in updates.items():
            print(f"   🔹 {dept}: {len(role_list)} roles")
        
        print(f"\n🔄 Updating database...")
        
        # Update roles in batches by department
        updated_count = 0
        for dept_category, role_list in updates.items():
            
            # Update in smaller batches to avoid timeouts
            batch_size = 50
            for i in range(0, len(role_list), batch_size):
                batch = role_list[i:i + batch_size]
                
                for role_info in batch:
                    try:
                        client.table('role').update({
                            'standardized_department': dept_category
                        }).eq('id', role_info['id']).execute()
                        updated_count += 1
                        
                        if updated_count % 100 == 0:
                            print(f"   Updated {updated_count} roles...")
                            
                    except Exception as e:
                        print(f"   ❌ Failed to update role {role_info['id']}: {e}")
                        continue
        
        print(f"✅ Successfully updated {updated_count} roles")
        
        # Show sample results
        print(f"\n🔍 Sample categorization results:")
        for dept_category, role_list in list(updates.items())[:3]:  # Show first 3 categories
            print(f"\n   🔹 {dept_category}:")
            for role_info in role_list[:3]:  # Show first 3 examples
                print(f"      • {role_info['job_title']} (was: {role_info['existing_dept'] or 'N/A'})")
        
    except Exception as e:
        print(f"❌ Error updating departments: {e}")
        import traceback
        traceback.print_exc()

def update_summary_tables():
    """Update the summary tables to include the new standardized department"""
    
    print("🔄 Updating summary tables with standardized departments...")
    
    client = get_supabase_client()
    
    try:
        # Refresh network_status table
        client.rpc('refresh_network_status').execute()
        print("✅ Updated network_status table")
        
        # Refresh organization_summary table  
        client.rpc('refresh_organization_summary').execute()
        print("✅ Updated organization_summary table")
        
    except Exception as e:
        print(f"Note: Could not auto-refresh summary tables: {e}")
        print("Please manually refresh them using:")
        print("   SELECT refresh_network_status();")
        print("   SELECT refresh_organization_summary();")

def add_to_summary_tables():
    """Add standardized_department column to summary tables"""
    
    print("🔧 Adding standardized_department to summary tables...")
    
    sql_commands = """
    -- Add to network_status table
    ALTER TABLE network_status 
    ADD COLUMN IF NOT EXISTS current_standardized_department TEXT;
    
    -- Add to organization_summary table  
    ALTER TABLE organization_summary
    ADD COLUMN IF NOT EXISTS standardized_departments JSONB DEFAULT '{}';
    """
    
    print("✅ Please run this SQL in your Supabase Dashboard SQL Editor:")
    print("-" * 60)
    print(sql_commands)
    print("-" * 60)
    print("\nAfter running the SQL, press Enter to continue...")
    input()

def main():
    """Main function"""
    try:
        print("🏈 CrowdBiz Graph - Department Standardization")
        print("=" * 60)
        
        # Step 1: Add column to role table
        add_standardized_department_column()
        
        # Step 2: Update all current roles with standardized departments
        update_standardized_departments()
        
        # Step 3: Add columns to summary tables
        add_to_summary_tables()
        
        # Step 4: Update summary tables
        update_summary_tables()
        
        print(f"\n🎉 Department standardization complete!")
        print(f"✅ All current roles now have standardized department categories")
        print(f"✅ 8 main department categories implemented")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
