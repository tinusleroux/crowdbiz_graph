#!/usr/bin/env python3
"""
CrowdBiz Graph - Web Interface
==============================

Streamlit UI for the CrowdBiz Sports Industry Intelligence Platform.
Integrates with the existing FastAPI backend for data operations.
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Any
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
from dotenv import load_dotenv
import io
import uuid
import sys

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CrowdBiz Graph - Sports Industry Intelligence",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

supabase = init_supabase()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .search-result {
        border: 1px solid #ddd;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: #fafafa;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏈 CrowdBiz Graph")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard", "Search", "Import Contacts", "Import Articles", "Analytics", "Database Explorer"]
)

# Helper functions
def api_request(endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """Make API request to FastAPI backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please start the FastAPI server with: `python api.py`")
        return None
    except Exception as e:
        st.error(f"Request error: {e}")
        return None

def check_api_health():
    """Check if FastAPI server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_dashboard_stats():
    """Get dashboard statistics via API"""
    # Get basic counts from API endpoints
    people = api_request("/people", params={"limit": 1})
    orgs = api_request("/organizations", params={"limit": 1})
    
    # For more detailed stats, use direct Supabase queries if available
    if supabase:
        try:
            people_count = supabase.table("person").select("id", count="exact").execute().count
            org_count = supabase.table("organization").select("id", count="exact").execute().count
            role_count = supabase.table("role").select("id", count="exact").execute().count
            nfl_teams = supabase.table("organization").select("id", count="exact").eq("sport", "NFL").execute().count
            
            return {
                "total_people": people_count,
                "total_organizations": org_count,
                "total_roles": role_count,
                "nfl_teams": nfl_teams
            }
        except Exception as e:
            st.error(f"Error getting stats: {e}")
    
    return {"total_people": 0, "total_organizations": 0, "total_roles": 0, "nfl_teams": 0}

def search_database(query: str, search_type: str = "all"):
    """Search via API"""
    params = {"q": query, "limit": 50}
    if search_type != "all":
        params["type"] = search_type
    
    return api_request("/search", params=params)

# Check API connection
api_healthy = check_api_health()

if not api_healthy:
    st.error("🚨 **API Server Not Running**")
    st.markdown("""
    The CrowdBiz API server is not running. Please start it first:
    
    ```bash
    python api_simple.py
    ```
    
    Then refresh this page.
    """)
    st.stop()

# Main content based on selected page
if page == "Dashboard":
    st.markdown('<h1 class="main-header">🏈 CrowdBiz Graph Dashboard</h1>', unsafe_allow_html=True)
    
    # Get statistics
    stats = get_dashboard_stats()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total People", f"{stats['total_people']:,}")
    
    with col2:
        st.metric("Organizations", f"{stats['total_organizations']:,}")
    
    with col3:
        st.metric("Active Roles", f"{stats['total_roles']:,}")
    
    with col4:
        st.metric("NFL Teams", f"{stats['nfl_teams']:,}")
    
    st.markdown("---")
    
    # Recent activity via API
    st.subheader("📈 Recent Activity")
    
    try:
        # Get recent role changes via API
        recent_changes = api_request("/analytics/roles/changes", params={"days": 7})
        
        if recent_changes and recent_changes.get("changes"):
            changes_df = pd.DataFrame([
                {
                    "Person": change.get("person_name", "Unknown"),
                    "Organization": change.get("organization_name", "Unknown"),
                    "Title": change.get("title", ""),
                    "Department": change.get("department", ""),
                    "Date": change.get("created_at", "")[:10] if change.get("created_at") else ""
                }
                for change in recent_changes["changes"][:10]
            ])
            
            st.dataframe(changes_df, use_container_width=True)
        else:
            st.info("No recent activity found.")
    
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")
    
    # Quick search
    st.subheader("🔍 Quick Search")
    quick_search = st.text_input("Search for people, organizations, or roles...")
    
    if quick_search:
        search_results = search_database(quick_search)
        if search_results and search_results.get("results"):
            for result in search_results["results"][:5]:  # Show top 5 results
                with st.container():
                    st.markdown(f"**{result.get('type', 'Unknown').title()}**: {result.get('name', 'Unknown')}")
                    if result.get('linkedin_url'):
                        st.text(f"LinkedIn: {result['linkedin_url']}")
                    elif result.get('league'):
                        st.text(f"League: {result['league']}")
                    elif result.get('person_name'):
                        st.text(f"Person: {result['person_name']}")
                    st.markdown("---")

elif page == "Search":
    st.title("🔍 Advanced Search")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search query:", placeholder="Enter names, titles, organizations...")
    
    with col2:
        search_type = st.selectbox("Search in:", ["all", "person", "organization", "role"])
    
    if st.button("Search", type="primary") or search_query:
        if search_query:
            with st.spinner("Searching..."):
                search_results = search_database(search_query, search_type)
            
            if search_results and search_results.get("results"):
                results = search_results["results"]
                st.success(f"Found {len(results)} results")
                
                # Display results
                for i, result in enumerate(results):
                    result_type = result.get('type', 'Unknown').title()
                    result_name = result.get('name', 'Unknown')
                    
                    with st.expander(f"{result_type}: {result_name}", expanded=i < 3):
                        
                        if result_type.lower() == "person":
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Name:** {result.get('name', 'N/A')}")
                                # LinkedIn URL only (email/phone removed for privacy compliance)
                                if result.get('linkedin_url'):
                                    st.write(f"**LinkedIn:** {result.get('linkedin_url')}")
                            with col2:
                                st.write(f"**ID:** {result.get('id', 'N/A')}")
                                
                                # Get additional details via API
                                if result.get('id'):
                                    person_details = api_request(f"/people/{result['id']}")
                                    if person_details:
                                        # Show only public professional information
                                        if person_details.get('first_name') or person_details.get('last_name'):
                                            name_parts = []
                                            if person_details.get('first_name'):
                                                name_parts.append(person_details['first_name'])
                                            if person_details.get('last_name'):
                                                name_parts.append(person_details['last_name'])
                                            st.write(f"**Full Name:** {' '.join(name_parts)}")
                        
                        elif result_type.lower() == "organization":
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Name:** {result.get('name', 'N/A')}")
                                st.write(f"**League:** {result.get('league', 'N/A')}")
                            with col2:
                                st.write(f"**ID:** {result.get('id', 'N/A')}")
                                
                                # Get organization people count
                                if result.get('id'):
                                    org_people = api_request(f"/organizations/{result['id']}/people", params={"limit": 1})
                                    if org_people:
                                        st.write(f"**People Count:** {len(org_people)}")
                        
                        elif result_type.lower() == "role":
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Title:** {result.get('name', 'N/A')}")
                                st.write(f"**Person:** {result.get('person_name', 'N/A')}")
                            with col2:
                                st.write(f"**Organization:** {result.get('organization_name', 'N/A')}")
                                st.write(f"**ID:** {result.get('id', 'N/A')}")
            else:
                st.warning("No results found. Try a different search term.")

elif page == "Import Contacts":
    st.title("📥 Import Contacts")
    
    st.markdown("""
    Upload CSV files containing contact information. The system will automatically map columns and import via the API.
    
    **Supported columns:**
    - `full_name`, `first_name`, `last_name`
    - `linkedin_url`
    - `organization`, `job_title`, `department`
    
    *Note: Contact information (email/phone) is not supported as this database focuses on public professional data only.*
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            st.subheader("📋 File Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            st.subheader("🔧 Column Mapping")
            
            # Create column mapping interface
            available_columns = [""] + df.columns.tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Person Fields:**")
                full_name_col = st.selectbox("Full Name", available_columns)
                first_name_col = st.selectbox("First Name", available_columns)
                last_name_col = st.selectbox("Last Name", available_columns)
                # Email and phone fields removed - not supported for privacy compliance
            
            with col2:
                st.write("**Professional Fields:**")
                organization_col = st.selectbox("Organization", available_columns)
                job_title_col = st.selectbox("Job Title", available_columns)
                department_col = st.selectbox("Department", available_columns)
                linkedin_col = st.selectbox("LinkedIn URL", available_columns)
            
            # Import button
            if st.button("Import Contacts", type="primary"):
                with st.spinner("Importing contacts..."):
                    # Prepare contacts for bulk import
                    contacts = []
                    
                    for index, row in df.iterrows():
                        try:
                            # Prepare person data
                            contact = {}
                            
                            if full_name_col and pd.notna(row.get(full_name_col)):
                                contact['name'] = str(row[full_name_col]).strip()
                            elif first_name_col and last_name_col:
                                first = str(row.get(first_name_col, "")).strip()
                                last = str(row.get(last_name_col, "")).strip()
                                contact['name'] = f"{first} {last}".strip()
                                contact['first_name'] = first
                                contact['last_name'] = last
                            else:
                                continue  # Skip if no name
                            
                            # LinkedIn URL only (no email/phone for privacy compliance)
                            if linkedin_col and pd.notna(row.get(linkedin_col)):
                                contact['linkedin_url'] = str(row[linkedin_col]).strip()
                            
                            # Add organization and job title data
                            if organization_col and pd.notna(row.get(organization_col)):
                                contact['organization'] = str(row[organization_col]).strip()
                            
                            if job_title_col and pd.notna(row.get(job_title_col)):
                                contact['job_title'] = str(row[job_title_col]).strip()
                            
                            if department_col and pd.notna(row.get(department_col)):
                                contact['department'] = str(row[department_col]).strip()
                            
                            contacts.append(contact)
                            
                        except Exception as e:
                            st.error(f"Error preparing row {index + 1}: {e}")
                    
                    # Bulk import via API
                    if contacts:
                        import_data = {
                            "contacts": contacts,
                            "source": f"CSV Upload - {uploaded_file.name}"
                        }
                        
                        import_result = api_request("/import/contacts", method="POST", data=import_data)
                        
                        if import_result:
                            # Show detailed results
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("New Contacts", import_result.get('imported', 0))
                            with col2:
                                st.metric("Updated Contacts", import_result.get('updated', 0))
                            with col3:
                                st.metric("Total Processed", import_result.get('total', 0))
                            
                            if import_result.get('imported', 0) > 0 or import_result.get('updated', 0) > 0:
                                st.success(f"Import completed! ✅ {import_result.get('imported', 0)} new contacts created, {import_result.get('updated', 0)} contacts updated")
                            
                            if import_result.get('errors'):
                                st.warning(f"❌ {len(import_result['errors'])} errors occurred during import:")
                                for error in import_result['errors'][:10]:  # Show first 10 errors
                                    st.error(error)
                                if len(import_result['errors']) > 10:
                                    st.info(f"... and {len(import_result['errors']) - 10} more errors")
                        else:
                            st.error("Import failed. Please check your data and try again.")
                    else:
                        st.warning("No valid contacts found in the uploaded file.")
        
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

elif page == "Import Articles":
    st.title("📰 Import News Articles")
    
    st.markdown("""
    Import news articles and industry content. The system will extract key information and store it for analysis.
    
    **Supported formats:**
    - Text files (.txt)
    - Markdown files (.md)
    - CSV files with article data
    """)
    
    # Note: This would require additional API endpoints for article management
    st.info("📝 **Coming Soon**: Article import functionality will be available when article management endpoints are added to the API.")
    
    # File upload placeholder
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=['txt', 'md', 'csv'])
    
    if uploaded_files:
        st.warning("Article import endpoints are not yet implemented in the API. Please use the direct import scripts for now.")

elif page == "Analytics":
    st.title("📊 Analytics Dashboard")
    
    # Get analytics data via API
    try:
        org_stats = api_request("/analytics/organizations/stats")
        
        if org_stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Organizations by League")
                if org_stats.get("league_breakdown"):
                    league_data = org_stats["league_breakdown"]
                    leagues = [item['league'] for item in league_data if item['league']]
                    counts = [item['count'] for item in league_data if item['league']]
                    
                    if leagues and counts:
                        fig = px.pie(values=counts, names=leagues, title="League Distribution")
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("League Statistics")
                if org_stats.get("basic_stats"):
                    stats = org_stats["basic_stats"]
                    st.metric("Total Organizations", stats.get("total_organizations", 0))
                    st.metric("Total Leagues", stats.get("total_leagues", 0))
                    st.metric("Total States", stats.get("total_states", 0))
        
        # Role changes analysis
        st.subheader("Recent Role Changes")
        role_changes = api_request("/analytics/roles/changes", params={"days": 30})
        
        if role_changes and role_changes.get("changes"):
            changes_df = pd.DataFrame(role_changes["changes"])
            
            if not changes_df.empty:
                # Show summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Changes (30 days)", role_changes.get("total_changes", 0))
                with col2:
                    if "created_at" in changes_df.columns:
                        changes_df['date'] = pd.to_datetime(changes_df['created_at']).dt.date
                        daily_changes = changes_df['date'].value_counts().sort_index()
                        fig = px.line(x=daily_changes.index, y=daily_changes.values, title="Daily Role Changes")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Show recent changes table
                st.dataframe(changes_df[['person_name', 'organization_name', 'title', 'department']].head(10), 
                           use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

elif page == "Database Explorer":
    st.title("🗃️ Database Explorer")
    
    # Use API endpoints to explore data
    st.markdown("Explore your database through the API endpoints:")
    
    # Table selector
    tables = {
        "People": "/people",
        "Organizations": "/organizations", 
        "Search Results": "/search"
    }
    
    selected_table = st.selectbox("Select data to explore:", list(tables.keys()))
    
    # Query options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("Limit results:", min_value=1, max_value=1000, value=100)
    
    with col2:
        offset = st.number_input("Offset:", min_value=0, value=0)
    
    with col3:
        if st.button("Load Data", type="primary"):
            st.rerun()
    
    # Load and display data
    try:
        endpoint = tables[selected_table]
        params = {"limit": limit, "offset": offset}
        
        if selected_table == "Search Results":
            search_term = st.text_input("Enter search term:")
            if search_term:
                params["q"] = search_term
                response = api_request(endpoint, params=params)
                if response and response.get("results"):
                    df = pd.DataFrame(response["results"])
                else:
                    df = pd.DataFrame()
            else:
                st.info("Enter a search term to see results.")
                df = pd.DataFrame()
        else:
            response = api_request(endpoint, params=params)
            if response:
                df = pd.DataFrame(response)
            else:
                df = pd.DataFrame()
        
        if not df.empty:
            st.subheader(f"📋 {selected_table} ({len(df)} records)")
            
            # Show basic info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Records Shown", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            
            # Display data
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_table} data as CSV",
                data=csv,
                file_name=f"{selected_table.lower()}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        else:
            st.info(f"No data found for {selected_table}.")
    
    except Exception as e:
        st.error(f"Error loading {selected_table} data: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**CrowdBiz Graph v1.0**")
st.sidebar.markdown("Sports Industry Intelligence Platform")

if api_healthy:
    st.sidebar.success("✅ API Connected")
else:
    st.sidebar.error("❌ API Disconnected")

# API server status in sidebar
with st.sidebar:
    st.markdown("### 🔧 System Status")
    if api_healthy:
        st.success("FastAPI Server: Online")
    else:
        st.error("FastAPI Server: Offline")
        st.markdown("Start with: `python api.py`")
    
    if supabase:
        st.success("Supabase: Connected")
    else:
        st.warning("Supabase: Direct connection unavailable")
    
    st.info(f"Streamlit Python: {sys.executable}")
