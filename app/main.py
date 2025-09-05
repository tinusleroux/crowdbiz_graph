"""
Main Streamlit Application Entry Point - Simplified UI
Single page application using high-performance summary tables
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
from typing import Optional

# Add the parent directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core services
from app.core.config import get_config
from app.core.database import get_database_manager
from app.core.logger import get_logger

# Configure logger
logger = get_logger("main_app")

def initialize_app():
    """Initialize the Streamlit application"""
    
    # Page configuration - no sidebar
    st.set_page_config(
        page_title="CrowdBiz Graph - Sports Industry Intelligence",
        page_icon="🏈",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for clean, professional design
    st.markdown("""
    <style>
        /* Hide sidebar */
        .css-1d391kg {
            display: none;
        }
        
        /* Clean header styling */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0A66C2;
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #495057;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #0A66C2;
            color: white;
        }
        
        /* Table styling */
        .dataframe {
            border: none !important;
        }
        
        .dataframe th {
            background-color: #f8f9fa !important;
            color: #495057 !important;
            font-weight: 600 !important;
            border: 1px solid #dee2e6 !important;
        }
        
        .dataframe td {
            border: 1px solid #dee2e6 !important;
            padding: 0.75rem !important;
        }
        
        /* Clickable names styling */
        .clickable-name {
            color: #0A66C2;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
        }
        
        .clickable-name:hover {
            text-decoration: underline;
            color: #004182;
        }
        
        /* Filter section styling */
        .filter-section {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border: 1px solid #dee2e6;
        }
        
        /* Profile card styling */
        .profile-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Back button styling */
        .back-button {
            background-color: #6c757d;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        /* Hide streamlit branding */
        .stApp > header {
            visibility: hidden;
        }
        
        div.block-container {
            padding-top: 1rem;
        }
        
        /* Search and filter inputs */
        .stTextInput > div > div > input {
            border-radius: 6px;
            border: 1px solid #ced4da;
        }
        
        .stSelectbox > div > div > select {
            border-radius: 6px;
            border: 1px solid #ced4da;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for navigation
    if 'view' not in st.session_state:
        st.session_state.view = 'home'
    if 'selected_person_id' not in st.session_state:
        st.session_state.selected_person_id = None
    if 'selected_org_id' not in st.session_state:
        st.session_state.selected_org_id = None
    
    # Initialize app state
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.start_time = datetime.now()
        logger.info("CrowdBiz Graph simplified application initialized")
    
    # Validate configuration
    config = get_config()
    is_valid, errors = config.validate()
    
    if not is_valid:
        st.error("⚠️ Configuration Error")
        st.error("Please check your environment variables:")
        for error in errors:
            st.error(f"• {error}")
        st.stop()
    
    # Check database connection
    db_manager = get_database_manager()
    if not db_manager.is_connected():
        st.error("❌ Database Connection Failed")
        st.error("Cannot connect to Supabase. Please check your database configuration.")
        st.info("Make sure SUPABASE_URL and SUPABASE_API_KEY are set correctly.")
        st.stop()
    
    logger.info("Simplified app initialization completed successfully")

@st.cache_data(ttl=300)
def get_network_status_data(search_term: str = "", org_type_filter: str = "", sport_filter: str = "", executive_filter: str = ""):
    """Get network status data with filters - using summary table"""
    try:
        db_manager = get_database_manager()
        query = db_manager.client.table('network_status').select('*')
        
        # Apply filters
        if search_term:
            query = query.or_(f"full_name.ilike.%{search_term}%,current_organization.ilike.%{search_term}%,current_job_title.ilike.%{search_term}%")
        
        if org_type_filter and org_type_filter != "All":
            query = query.eq('current_org_type', org_type_filter)
            
        if sport_filter and sport_filter != "All":
            query = query.eq('current_sport', sport_filter)
            
        if executive_filter == "Executives Only":
            query = query.eq('is_executive', True)
        elif executive_filter == "Non-Executives Only":
            query = query.eq('is_executive', False)
        
        result = query.order('full_name').limit(1000).execute()
        
        # Enhance data with department lookup
        if result.data:
            enhanced_data = []
            for row in result.data:
                enhanced_row = row.copy()
                enhanced_row['department'] = get_department_for_job_title(enhanced_row.get('current_job_title'))
                enhanced_data.append(enhanced_row)
            return enhanced_data
        
        return result.data if result else []
        
    except Exception as e:
        logger.error(f"Failed to get network status data: {e}")
        st.error(f"Error loading network data: {e}")
        return []

@st.cache_data(ttl=600)
def get_department_for_job_title(job_title: str) -> str:
    """Get department for a job title using the lookup table"""
    if not job_title:
        return 'Other'
    
    try:
        db_manager = get_database_manager()
        result = db_manager.client.table('job_title_departments')\
            .select('standardized_department')\
            .eq('job_title', job_title)\
            .single()\
            .execute()
        
        if result.data:
            return result.data['standardized_department']
        else:
            return 'Other'
            
    except Exception as e:
        logger.warning(f"Could not get department for job title '{job_title}': {e}")
        return 'Other'

@st.cache_data(ttl=300)
def get_organization_summary_data(search_term: str = "", org_type_filter: str = "", sport_filter: str = ""):
    """Get organization summary data with filters"""
    try:
        db_manager = get_database_manager()
        query = db_manager.client.table('organization_summary').select('*')
        
        # Apply filters
        if search_term:
            query = query.ilike('name', f'%{search_term}%')
        
        if org_type_filter and org_type_filter != "All":
            query = query.eq('org_type', org_type_filter)
            
        if sport_filter and sport_filter != "All":
            query = query.eq('sport', sport_filter)
        
        result = query.order('current_employees', desc=True).limit(1000).execute()
        return result.data if result else []
        
    except Exception as e:
        logger.error(f"Failed to get organization data: {e}")
        st.error(f"Error loading organization data: {e}")
        return []

def get_person_details(person_id: str):
    """Get detailed person information"""
    try:
        db_manager = get_database_manager()
        
        # Get person basic info
        person_result = db_manager.client.table('network_status')\
            .select('*')\
            .eq('person_id', person_id)\
            .single()\
            .execute()
        
        person_data = person_result.data if person_result else None
        
        # Get all roles for this person (historical)
        roles_result = db_manager.client.table('role')\
            .select('*, organization!inner(name, org_type, sport)')\
            .eq('person_id', person_id)\
            .order('start_date', desc=True)\
            .execute()
        
        roles_data = roles_result.data if roles_result else []
        
        return person_data, roles_data
        
    except Exception as e:
        logger.error(f"Failed to get person details: {e}")
        return None, []

def get_organization_details(org_id: str):
    """Get detailed organization information and staff"""
    try:
        db_manager = get_database_manager()
        
        # Get organization summary
        org_result = db_manager.client.table('organization_summary')\
            .select('*')\
            .eq('org_id', org_id)\
            .single()\
            .execute()
        
        org_data = org_result.data if org_result else None
        
        # Get staff for this organization
        staff_result = db_manager.client.table('network_status')\
            .select('*')\
            .eq('current_organization', org_data.get('name') if org_data else '')\
            .order('is_executive', desc=True)\
            .order('full_name')\
            .execute()
        
        staff_data = staff_result.data if staff_result else []
        
        return org_data, staff_data
        
    except Exception as e:
        logger.error(f"Failed to get organization details: {e}")
        return None, []

def show_home_view():
    """Main home view with network and organization tables"""
    
    st.markdown('<h1 class="main-header">🏈 CrowdBiz Graph</h1>', unsafe_allow_html=True)
    st.markdown("### Sports Industry Professional Network")
    
    # Create tabs for the two main tables
    tab1, tab2 = st.tabs(["👥 Professionals Network", "🏢 Organizations"])
    
    with tab1:
        st.subheader("Professional Network")
        
        # Filters for network table
        with st.container():
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                search_people = st.text_input("🔍 Search professionals", placeholder="Search by name, organization, or job title...", key="search_people")
            
            with col2:
                org_types = ["All", "Team", "League", "Brand", "Agency", "Vendor"]
                org_type_filter = st.selectbox("Organization Type", org_types, key="org_type_people")
            
            with col3:
                sports = ["All", "Football", "Basketball", "Baseball", "Soccer", "Hockey", "Other"]
                sport_filter = st.selectbox("Sport", sports, key="sport_people")
            
            with col4:
                exec_options = ["All", "Executives Only", "Non-Executives Only"]
                exec_filter = st.selectbox("Executive Level", exec_options, key="exec_people")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Get and display network data
        network_data = get_network_status_data(search_people, org_type_filter, sport_filter, exec_filter)
        
        if network_data:
            df_network = pd.DataFrame(network_data)
            
            # Format display columns
            display_columns = {
                'full_name': 'Name',
                'current_job_title': 'Job Title',
                'current_organization': 'Organization',
                'current_org_type': 'Org Type',
                'current_sport': 'Sport',
                'department': 'Department'
            }
            
            # Filter available columns
            available_cols = [col for col in display_columns.keys() if col in df_network.columns]
            df_display = df_network[available_cols].copy()
            df_display.rename(columns=display_columns, inplace=True)
            
            # Fill null values
            df_display = df_display.fillna('')
            
            st.markdown(f"**{len(df_display):,} professionals found**")
            
            # Display table with selection capability
            event = st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Job Title": st.column_config.TextColumn("Job Title", width="medium"),
                    "Organization": st.column_config.TextColumn("Organization", width="medium"),
                }
            )
            
            # Handle row selection for person details
            if len(event.selection["rows"]) > 0:
                selected_row = event.selection["rows"][0]
                selected_person = network_data[selected_row]
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"Selected: **{selected_person.get('full_name', 'Unknown')}** - {selected_person.get('current_job_title', 'No title')}")
                with col2:
                    if st.button("👤 View Profile", type="primary"):
                        st.session_state.view = 'person'
                        st.session_state.selected_person_id = selected_person.get('person_id')
                        st.rerun()
                
        else:
            st.info("No professional data found. Please check your filters or database connection.")
    
    with tab2:
        st.subheader("Organizations")
        
        # Filters for organization table
        with st.container():
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_orgs = st.text_input("🔍 Search organizations", placeholder="Search by organization name...", key="search_orgs")
            
            with col2:
                org_types_org = ["All", "Team", "League", "Brand", "Agency", "Vendor"]
                org_type_filter_org = st.selectbox("Organization Type", org_types_org, key="org_type_orgs")
            
            with col3:
                sports_org = ["All", "Football", "Basketball", "Baseball", "Soccer", "Hockey", "Other"]
                sport_filter_org = st.selectbox("Sport", sports_org, key="sport_orgs")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Get and display organization data
        org_data = get_organization_summary_data(search_orgs, org_type_filter_org, sport_filter_org)
        
        if org_data:
            df_org = pd.DataFrame(org_data)
            
            # Format display columns
            org_display_columns = {
                'name': 'Organization',
                'org_type': 'Type',
                'sport': 'Sport',
                'current_employees': 'Current Staff',
                'executive_count': 'Executives',
                'total_employees': 'Total Ever',
                'parent_org_name': 'Parent Organization'
            }
            
            # Filter available columns
            available_org_cols = [col for col in org_display_columns.keys() if col in df_org.columns]
            df_org_display = df_org[available_org_cols].copy()
            df_org_display.rename(columns=org_display_columns, inplace=True)
            
            # Fill null values
            df_org_display = df_org_display.fillna('')
            
            st.markdown(f"**{len(df_org_display):,} organizations found**")
            
            # Display table with selection capability
            event = st.dataframe(
                df_org_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "Organization": st.column_config.TextColumn("Organization", width="large"),
                    "Current Staff": st.column_config.NumberColumn("Current Staff", format="%d"),
                    "Executives": st.column_config.NumberColumn("Executives", format="%d"),
                    "Total Ever": st.column_config.NumberColumn("Total Ever", format="%d"),
                }
            )
            
            # Handle row selection for organization details
            if len(event.selection["rows"]) > 0:
                selected_row = event.selection["rows"][0]
                selected_org = org_data[selected_row]
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"Selected: **{selected_org.get('name', 'Unknown')}** ({selected_org.get('org_type', 'Unknown')} - {selected_org.get('sport', 'N/A')})")
                with col2:
                    if st.button("🏢 View Organization", type="primary"):
                        st.session_state.view = 'organization'
                        st.session_state.selected_org_id = selected_org.get('org_id')
                        st.rerun()
                
        else:
            st.info("No organization data found. Please check your filters or database connection.")

def show_person_view(person_id: str):
    """Individual person detail view"""
    
    # Back button
    if st.button("← Back to Network", type="secondary", key="back_from_person"):
        st.session_state.view = 'home'
        st.session_state.selected_person_id = None
        st.rerun()
    
    person_data, roles_data = get_person_details(person_id)
    
    if not person_data:
        st.error("Person not found")
        return
    
    # Person header
    st.markdown(f'<div class="profile-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"# {person_data.get('full_name', 'Unknown')}")
        
        if person_data.get('current_job_title'):
            st.markdown(f"**{person_data['current_job_title']}**")
        
        if person_data.get('current_organization'):
            st.markdown(f"📍 {person_data['current_organization']}")
        
        if person_data.get('is_executive'):
            st.markdown("👔 **Executive Level**")
    
    with col2:
        st.metric("Current Roles", person_data.get('current_roles_count', 0))
        st.metric("Total Career Roles", person_data.get('total_roles_count', 0))
        
        if person_data.get('linkedin_url'):
            st.markdown(f"[LinkedIn Profile]({person_data['linkedin_url']})")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Career history
    if roles_data:
        st.subheader("Career History")
        
        for role in roles_data:
            with st.expander(f"{role.get('job_title', 'Unknown Role')} at {role.get('organization', {}).get('name', 'Unknown Org')}", expanded=True):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Position:**")
                    st.write(role.get('job_title', 'N/A'))
                    
                    if role.get('dept'):
                        st.write("**Department:**")
                        st.write(role['dept'])
                
                with col2:
                    st.write("**Organization:**")
                    org_info = role.get('organization', {})
                    st.write(org_info.get('name', 'N/A'))
                    
                    if org_info.get('org_type'):
                        st.write("**Type:**")
                        st.write(org_info['org_type'])
                
                with col3:
                    st.write("**Period:**")
                    start_date = role.get('start_date', 'Unknown')
                    end_date = role.get('end_date', 'Present')
                    st.write(f"{start_date} - {end_date}")
                    
                    if role.get('is_executive'):
                        st.write("👔 **Executive Role**")

def show_organization_view(org_id: str):
    """Individual organization detail view"""
    
    # Back button
    if st.button("← Back to Organizations", type="secondary", key="back_from_org"):
        st.session_state.view = 'home'
        st.session_state.selected_org_id = None
        st.rerun()
    
    org_data, staff_data = get_organization_details(org_id)
    
    if not org_data:
        st.error("Organization not found")
        return
    
    # Organization header
    st.markdown(f'<div class="profile-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"# {org_data.get('name', 'Unknown Organization')}")
        
        if org_data.get('org_type'):
            st.markdown(f"**Type:** {org_data['org_type']}")
        
        if org_data.get('sport'):
            st.markdown(f"🏈 **Sport:** {org_data['sport']}")
        
        if org_data.get('parent_org_name'):
            st.markdown(f"**Parent Organization:** {org_data['parent_org_name']}")
    
    with col2:
        st.metric("Current Staff", org_data.get('current_employees', 0))
        st.metric("Executives", org_data.get('executive_count', 0))
        st.metric("Total Historical", org_data.get('total_employees', 0))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Staff listing
    if staff_data:
        st.subheader(f"Current Staff ({len(staff_data)})")
        
        # Create staff dataframe
        df_staff = pd.DataFrame(staff_data)
        
        staff_columns = {
            'full_name': 'Name',
            'current_job_title': 'Job Title',
            'current_department': 'Department',
            'is_executive': 'Executive',
            'role_start_date': 'Start Date'
        }
        
        available_staff_cols = [col for col in staff_columns.keys() if col in df_staff.columns]
        df_staff_display = df_staff[available_staff_cols].copy()
        df_staff_display.rename(columns=staff_columns, inplace=True)
        
        # Format executive column
        if 'Executive' in df_staff_display.columns:
            df_staff_display['Executive'] = df_staff_display['Executive'].map({True: '✅ Yes', False: '❌ No'})
        
        df_staff_display = df_staff_display.fillna('')
        
        st.dataframe(
            df_staff_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Job Title": st.column_config.TextColumn("Job Title", width="medium"),
            }
        )
    else:
        st.info("No current staff data available")

def main():
    """Main application entry point - simplified single page"""
    try:
        # Initialize the application
        initialize_app()
        
        # Route based on current view state
        if st.session_state.view == 'person' and st.session_state.selected_person_id:
            show_person_view(st.session_state.selected_person_id)
        elif st.session_state.view == 'organization' and st.session_state.selected_org_id:
            show_organization_view(st.session_state.selected_org_id)
        else:
            # Default home view
            show_home_view()
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred")
        st.error(str(e))
        
        # Show debug info in development
        config = get_config()
        if config.debug:
            st.exception(e)

if __name__ == "__main__":
    main()
