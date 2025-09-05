#!/usr/bin/env python3
"""
Analyze job titles at sports teams to suggest department categories
"""

import os
import sys
from collections import Counter
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_API_KEY')
    return create_client(url, key)

def analyze_team_job_titles():
    """Analyze job titles at organizations classified as Teams"""
    client = get_supabase_client()
    
    print("🔍 Analyzing Job Titles at Sports Teams")
    print("=" * 60)
    
    try:
        # Get all roles at Team organizations
        query = """
        SELECT DISTINCT
            r.job_title,
            r.dept,
            o.name as org_name,
            o.org_type,
            o.sport,
            COUNT(*) as count
        FROM role r
        JOIN organization o ON r.org_id = o.id
        WHERE o.org_type = 'Team' AND r.is_current = true
        GROUP BY r.job_title, r.dept, o.name, o.org_type, o.sport
        ORDER BY count DESC, r.job_title
        """
        
        # Use a raw SQL query through the PostgREST API
        response = client.postgrest.rpc('exec_sql', {'query': query}).execute()
        
        if not response.data:
            print("❌ No team data found or query failed")
            return
            
        team_roles = response.data
        
    except Exception as e:
        # Fallback: Get data through regular table queries
        print(f"Note: Using fallback method due to: {e}")
        
        # Get Team organizations
        teams_response = client.table('organization').select('*').eq('org_type', 'Team').execute()
        if not teams_response.data:
            print("❌ No Team organizations found")
            return
        
        teams = teams_response.data
        team_ids = [team['id'] for team in teams]
        
        # Get current roles at these teams
        roles_response = client.table('role').select('*, organization!inner(name, org_type, sport)').in_('org_id', team_ids).eq('is_current', True).execute()
        
        if not roles_response.data:
            print("❌ No current roles found at teams")
            return
            
        team_roles = roles_response.data
    
    print(f"✅ Found {len(team_roles)} current roles at Team organizations")
    
    # Analyze job titles
    job_titles = []
    departments = []
    org_names = set()
    sports = set()
    
    for role in team_roles:
        job_title = role.get('job_title', '').strip()
        dept = role.get('dept', '').strip() if role.get('dept') else None
        
        if isinstance(role.get('organization'), dict):
            org_name = role['organization'].get('name', '')
            sport = role['organization'].get('sport', '')
        else:
            org_name = role.get('org_name', '')
            sport = role.get('sport', '')
        
        if job_title:
            job_titles.append(job_title)
        if dept:
            departments.append(dept)
        if org_name:
            org_names.add(org_name)
        if sport:
            sports.add(sport)
    
    # Count frequency
    title_counts = Counter(job_titles)
    dept_counts = Counter(departments) if departments else Counter()
    
    print(f"\n📊 Analysis Summary:")
    print(f"   • {len(org_names)} Team organizations")
    print(f"   • {len(set(job_titles))} unique job titles")
    print(f"   • {len(set(departments))} existing departments")
    print(f"   • Sports: {', '.join(sports) if sports else 'Not specified'}")
    
    print(f"\n🏢 Team Organizations:")
    for org in sorted(org_names):
        print(f"   • {org}")
    
    print(f"\n🎯 Most Common Job Titles at Teams:")
    for title, count in title_counts.most_common(20):
        print(f"   • {title} ({count})")
    
    if dept_counts:
        print(f"\n📋 Current Departments at Teams:")
        for dept, count in dept_counts.most_common():
            print(f"   • {dept} ({count})")
    
    # Suggest department categorization based on job titles
    print(f"\n💡 Suggested Department Categories (based on job title analysis):")
    
    suggested_departments = analyze_and_suggest_departments(job_titles)
    
    for category, roles in suggested_departments.items():
        print(f"\n   🔹 {category}:")
        for role in sorted(set(roles))[:5]:  # Show top 5 examples
            print(f"      - {role}")
        if len(set(roles)) > 5:
            print(f"      ... and {len(set(roles)) - 5} more")

def analyze_and_suggest_departments(job_titles):
    """Analyze job titles and suggest department categories"""
    
    # Define department mapping based on common sports organization structure
    department_keywords = {
        "Sales & Partnerships": [
            "sales", "partnership", "sponsor", "corporate", "revenue", "account", "business development",
            "commercial", "marketing partnership", "corporate partnership"
        ],
        "Ticketing & Customer Service": [
            "ticket", "customer", "service", "box office", "season ticket", "premium services",
            "hospitality", "customer experience", "guest services"
        ],
        "Marketing & Communications": [
            "marketing", "communication", "brand", "content", "social media", "public relations",
            "pr", "digital", "creative", "advertising", "media relations", "community relations"
        ],
        "Fan Experience & Events": [
            "fan", "experience", "event", "game day", "entertainment", "fan engagement",
            "community", "outreach", "promotions", "activation", "fan services"
        ],
        "Operations & Facilities": [
            "operations", "facility", "maintenance", "security", "logistics", "stadium",
            "arena", "venue", "game operations", "facilities", "equipment"
        ],
        "Finance & Administration": [
            "finance", "accounting", "controller", "financial", "admin", "hr", "human resources",
            "payroll", "budget", "analyst", "coordinator", "assistant"
        ],
        "Baseball Operations": [
            "baseball operations", "player development", "scouting", "minor league",
            "farm system", "roster", "baseball", "player personnel"
        ],
        "Broadcasting & Media": [
            "broadcast", "media", "radio", "television", "tv", "production", "commentary",
            "announcer", "media relations", "digital media"
        ],
        "Technology & Analytics": [
            "technology", "it", "data", "analytics", "digital", "systems", "tech",
            "information technology", "data analyst", "software"
        ],
        "Legal & Compliance": [
            "legal", "counsel", "compliance", "risk", "contracts", "attorney", "lawyer"
        ]
    }
    
    # Categorize job titles
    categorized = {dept: [] for dept in department_keywords.keys()}
    uncategorized = []
    
    for title in job_titles:
        title_lower = title.lower()
        matched = False
        
        for dept, keywords in department_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                categorized[dept].append(title)
                matched = True
                break
        
        if not matched:
            uncategorized.append(title)
    
    # Add uncategorized section
    if uncategorized:
        categorized["Other/Uncategorized"] = uncategorized
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}

def main():
    """Main function"""
    try:
        analyze_team_job_titles()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
