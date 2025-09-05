"""
Database Explorer Page
Direct database table exploration and data export
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from ...core.database import get_table_data, get_database_manager, get_enriched_people_data, get_enriched_organization_data
from ...core.logger import get_logger

logger = get_logger("database_explorer_page")

def show_database_explorer():
    """Display the database explorer page"""
    
    st.title("🗃️ Database Explorer")
    
    st.markdown("""
    Explore your database with **enriched views** showing the relationships between people, organizations, and roles that make CrowdBiz Graph valuable.
    """)
    
    # View selector
    st.markdown("### 📊 Select Data View")
    
    views = {
        "People (with Organizations & Roles)": "enriched_people", 
        "Organizations (with People & Roles)": "enriched_organizations",
        "Raw People Table": "person",
        "Raw Organizations Table": "organization", 
        "Roles Table": "role",
        "Sources Table": "source"
    }
    
    selected_view_name = st.selectbox("Select data to explore:", list(views.keys()))
    selected_view = views[selected_view_name]
    
    # Show description of selected view
    view_descriptions = {
        "person": "� **Raw people data** - Individual profiles with personal information",
        "organization": "🏢 **Raw organization data** - Teams, leagues, and companies in sports",
        "role": "💼 **Raw role/position data** - Job positions and professional relationships",
        "source": "� **Data source tracking** - Import sources and data provenance",
        "v_role_current": "� **Current roles view** - Pre-computed current professional positions",
        "enriched_people": "� **People with their organizations and job titles** - The core value of CrowdBiz Graph showing professional connections with executive indicators",
        "enriched_organizations": "🏢 **Organizations with their people and roles** - Comprehensive organization profiles with employee counts, executive breakdowns, and active role summaries"
    }
    
    if selected_view in view_descriptions:
        st.info(view_descriptions[selected_view])
    
    # Query options
    st.markdown("### 🔧 Query Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("Limit results:", min_value=1, max_value=1000, value=100)
    
    with col2:
        offset = st.number_input("Offset:", min_value=0, value=0)
    
    with col3:
        if st.button("🔄 Load Data", type="primary"):
            st.rerun()
    
    # Load and display data
    try:
        with st.spinner(f"Loading {selected_view_name} data..."):
            # Use appropriate data loader based on view type
            if selected_view == "enriched_people":
                data = get_enriched_people_data(limit=limit, offset=offset)
            elif selected_view == "enriched_organizations":
                data = get_enriched_organization_data(limit=limit, offset=offset)
            else:
                # Raw table data
                data = get_table_data(selected_view, limit=limit, offset=offset)
        
        if data:
            display_table_data(data, selected_view_name, selected_view)
        else:
            st.info(f"No {selected_view_name.lower()} data found.")
    
    except Exception as e:
        logger.error(f"Error loading {selected_view} data: {e}")
        st.error(f"Error loading {selected_view_name} data: {e}")

def display_enriched_view_summary(df, table_name, table_id):
    """Display special summary for enriched views highlighting key relationships"""
    
    if table_id == "enriched_people":
        st.markdown("### 🔗 Professional Network Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            people_with_orgs = len(df[df['organization'].notna()])
            st.metric("👥 People with Organizations", people_with_orgs)
        
        with col2:
            executives = len(df[df.get('is_executive', False) == True])
            st.metric("⭐ Executives", executives)
        
        with col3:
            people_with_titles = len(df[df['job_title'].notna()])
            st.metric("🎯 People with Job Titles", people_with_titles)
        
        with col4:
            avg_roles = df['current_roles_count'].mean() if 'current_roles_count' in df.columns else 0
            st.metric("📊 Avg Current Roles", f"{avg_roles:.1f}")
        
        # Show top organizations and executive breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            if 'organization' in df.columns and not df['organization'].isna().all():
                st.markdown("**🏢 Top Organizations by People Count:**")
                org_counts = df['organization'].value_counts().head(5)
                for org, count in org_counts.items():
                    if pd.notna(org):
                        exec_count = len(df[(df['organization'] == org) & (df.get('is_executive', False) == True)])
                        exec_indicator = f" (⭐ {exec_count} execs)" if exec_count > 0 else ""
                        st.write(f"• **{org}**: {count} people{exec_indicator}")
        
        with col2:
            if 'industry' in df.columns and not df['industry'].isna().all():
                st.markdown("**🏭 Top Industries:**")
                industry_counts = df['industry'].value_counts().head(5)
                for industry, count in industry_counts.items():
                    if pd.notna(industry):
                        st.write(f"• **{industry}**: {count} people")
    
    elif table_id == "enriched_organizations":
        st.markdown("### 🏢 Organization Network Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_people = df['current_people_count'].sum() if 'current_people_count' in df.columns else 0
            st.metric("👥 Total People", total_people)
        
        with col2:
            total_execs = df['executive_count'].sum() if 'executive_count' in df.columns else 0
            st.metric("⭐ Total Executives", total_execs)
        
        with col3:
            avg_people = df['current_people_count'].mean() if 'current_people_count' in df.columns else 0
            st.metric("📊 Avg People/Org", f"{avg_people:.1f}")
        
        with col4:
            orgs_with_people = len(df[df['current_people_count'] > 0]) if 'current_people_count' in df.columns else 0
            st.metric("🏢 Active Organizations", orgs_with_people)
        
        # Show largest organizations with executive breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            if 'current_people_count' in df.columns:
                st.markdown("**👥 Largest Organizations:**")
                top_orgs = df.nlargest(5, 'current_people_count')[['name', 'current_people_count', 'executive_count', 'org_type']]
                for _, org in top_orgs.iterrows():
                    if org['current_people_count'] > 0:
                        org_type = f" ({org['org_type']})" if pd.notna(org['org_type']) else ""
                        exec_info = f" (⭐ {org.get('executive_count', 0)} execs)" if org.get('executive_count', 0) > 0 else ""
                        st.write(f"• **{org['name']}**{org_type}: {org['current_people_count']} people{exec_info}")
        
        with col2:
            if 'executive_count' in df.columns:
                st.markdown("**⭐ Organizations with Most Executives:**")
                exec_orgs = df[df['executive_count'] > 0].nlargest(5, 'executive_count')[['name', 'executive_count', 'current_people_count']]
                for _, org in exec_orgs.iterrows():
                    total = org.get('current_people_count', 0)
                    execs = org.get('executive_count', 0)
                    ratio = f" ({execs}/{total})" if total > 0 else ""
                    st.write(f"• **{org['name']}**: ⭐ {execs} executives{ratio}")

def reorder_dataframe_columns(df, priority_cols):
    """Reorder dataframe columns to show priority columns first"""
    if df.empty:
        return df
    
    # Get existing columns that are in priority list
    existing_priority = [col for col in priority_cols if col in df.columns]
    
    # Get remaining columns not in priority list
    remaining_cols = [col for col in df.columns if col not in priority_cols]
    
    # Combine them
    new_order = existing_priority + remaining_cols
    
    return df[new_order]

def display_table_data(data, table_name, table_id):
    """Display table data with statistics and export options"""
    
    df = pd.DataFrame(data)
    
    # Special handling for enriched views
    if "enriched" in table_id:
        display_enriched_view_summary(df, table_name, table_id)
    
    # Data summary
    st.markdown(f"### 📋 {table_name} Data ({len(df)} records)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Records Shown", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        # Calculate data freshness if created_at exists
        if 'created_at' in df.columns:
            try:
                df['created_at'] = pd.to_datetime(df['created_at'])
                latest_record = df['created_at'].max()
                days_since = (datetime.now() - latest_record).days
                st.metric("Days Since Latest", days_since)
            except:
                st.metric("Data Status", "Active")
        else:
            st.metric("Data Status", "Active")
    
    # Search functionality
    st.markdown("### 🔍 Search and Filter")
    
    search_term = st.text_input("Search in data:", placeholder="Enter search term...")
    
    # Apply search filter if provided
    display_df = df
    if search_term:
        # Search across all text columns
        text_columns = df.select_dtypes(include=['object']).columns
        mask = df[text_columns].astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        display_df = df[mask]
        
        if len(display_df) < len(df):
            st.info(f"Filtered to {len(display_df)} records containing '{search_term}'")
    
    # Column selector
    if len(df.columns) > 10:
        st.markdown("### 📊 Column Selector")
        selected_columns = st.multiselect(
            "Select columns to display:",
            df.columns.tolist(),
            default=df.columns.tolist()[:10]  # Show first 10 columns by default
        )
        
        if selected_columns:
            display_df = display_df[selected_columns]
    
    # Display data
    st.markdown("### 📑 Data Table")
    
    # Reorder columns for enriched views to show most important first
    if table_id == "enriched_people":
        priority_cols = ['full_name', 'job_title', 'organization', 'is_executive', 'org_type', 'sport', 'industry', 'department', 'current_roles_count', 'start_date']
        display_df = reorder_dataframe_columns(display_df, priority_cols)
    elif table_id == "enriched_organizations": 
        priority_cols = ['name', 'current_people_count', 'executive_count', 'non_executive_count', 'org_type', 'sport', 'industry', 'is_active', 'active_job_titles', 'key_people']
        display_df = reorder_dataframe_columns(display_df, priority_cols)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Export options
    st.markdown("### 📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label=f"📄 Download {table_name} as CSV",
            data=csv_data,
            file_name=f"{table_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        json_data = display_df.to_json(orient='records', indent=2)
        st.download_button(
            label=f"📄 Download {table_name} as JSON",
            data=json_data,
            file_name=f"{table_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Data statistics
    if st.checkbox("📊 Show Data Statistics"):
        show_data_statistics(display_df, table_name)

def show_data_statistics(df, table_name):
    """Show detailed statistics about the data"""
    
    st.markdown(f"### 📊 {table_name} Statistics")
    
    # Basic statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Info")
        st.write(f"**Total Records:** {len(df)}")
        st.write(f"**Columns:** {len(df.columns)}")
        st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Missing data analysis
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            st.write("**Missing Data:**")
            for col, missing_count in missing_data.items():
                if missing_count > 0:
                    percentage = (missing_count / len(df)) * 100
                    st.write(f"  • {col}: {missing_count} ({percentage:.1f}%)")
        else:
            st.write("**Missing Data:** None")
    
    with col2:
        st.markdown("#### Data Types")
        data_types = df.dtypes.value_counts()
        for dtype, count in data_types.items():
            st.write(f"**{dtype}:** {count} columns")
        
        # Unique values analysis
        st.markdown("#### Unique Values")
        for col in df.columns[:5]:  # Show first 5 columns
            unique_count = df[col].nunique()
            total_count = len(df)
            uniqueness = (unique_count / total_count) * 100
            st.write(f"**{col}:** {unique_count}/{total_count} ({uniqueness:.1f}% unique)")
    
    # Column-specific statistics
    if st.checkbox("🔍 Detailed Column Analysis"):
        selected_column = st.selectbox("Select column for detailed analysis:", df.columns)
        
        if selected_column:
            col_data = df[selected_column]
            
            st.markdown(f"#### Analysis: {selected_column}")
            
            # Basic stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Values", len(col_data))
            with col2:
                st.metric("Unique Values", col_data.nunique())
            with col3:
                st.metric("Missing Values", col_data.isnull().sum())
            
            # Most common values
            if col_data.dtype == 'object':
                st.markdown("**Most Common Values:**")
                value_counts = col_data.value_counts().head(10)
                for value, count in value_counts.items():
                    percentage = (count / len(col_data)) * 100
                    st.write(f"• {value}: {count} ({percentage:.1f}%)")
            else:
                # Numeric statistics
                st.markdown("**Numeric Statistics:**")
                st.write(col_data.describe())
