"""
Database Explorer Page
Direct database table exploration and data export
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from ...core.database import get_table_data, get_database_manager
from ...core.logger import get_logger

logger = get_logger("database_explorer_page")

def show_database_explorer():
    """Display the database explorer page"""
    
    st.title("🗃️ Database Explorer")
    
    st.markdown("""
    Explore your database tables directly. View, search, and export data from the CrowdBiz Graph database.
    """)
    
    # Table selector
    st.markdown("### 📊 Select Table to Explore")
    
    tables = {
        "People": "people",
        "Organizations": "organizations"
    }
    
    selected_table_name = st.selectbox("Select data to explore:", list(tables.keys()))
    selected_table = tables[selected_table_name]
    
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
        with st.spinner(f"Loading {selected_table_name} data..."):
            data = get_table_data(selected_table, limit=limit, offset=offset)
        
        if data:
            display_table_data(data, selected_table_name, selected_table)
        else:
            st.info(f"No {selected_table_name.lower()} data found.")
    
    except Exception as e:
        logger.error(f"Error loading {selected_table} data: {e}")
        st.error(f"Error loading {selected_table_name} data: {e}")

def display_table_data(data, table_name, table_id):
    """Display table data with statistics and export options"""
    
    df = pd.DataFrame(data)
    
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
