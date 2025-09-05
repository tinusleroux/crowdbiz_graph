"""
Sidebar Component
Navigation and system status display
"""

import streamlit as st
import sys
from datetime import datetime

from ...core.database import get_database_manager
from ...core.config import get_config
from ...core.logger import get_logger

logger = get_logger("sidebar")

def render_sidebar() -> str:
    """
    Render the main sidebar navigation
    
    Returns:
        str: Selected page name
    """
    
    st.sidebar.title("🏈 CrowdBiz Graph")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "Dashboard", 
            "Search", 
            "Import Contacts", 
            "Import Articles", 
            "Analytics", 
            "Database Explorer"
        ]
    )
    
    # System status section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System Status")
    
    # Database connection status
    db_manager = get_database_manager()
    if db_manager.is_connected():
        st.sidebar.success("✅ Database: Connected")
    else:
        st.sidebar.error("❌ Database: Disconnected")
    
    # Configuration status
    config = get_config()
    is_valid, _ = config.validate()
    if is_valid:
        st.sidebar.success("✅ Config: Valid")
    else:
        st.sidebar.error("❌ Config: Issues")
    
    # Debug info (if in debug mode)
    if config.debug:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🐛 Debug Info")
        st.sidebar.info(f"Python: {sys.executable}")
        
        # Session info
        if 'start_time' in st.session_state:
            uptime = datetime.now() - st.session_state.start_time
            st.sidebar.info(f"Uptime: {uptime.total_seconds():.0f}s")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**CrowdBiz Graph v1.0**")
    st.sidebar.markdown("Sports Industry Intelligence Platform")
    
    # Quick stats in sidebar
    try:
        stats = db_manager.get_dashboard_stats()
        if stats:
            st.sidebar.markdown("### 📊 Quick Stats")
            st.sidebar.metric("People", stats.get('total_people', 0))
            st.sidebar.metric("Organizations", stats.get('total_organizations', 0))
    except Exception as e:
        logger.error(f"Error loading sidebar stats: {e}")
    
    return page

def render_status_indicators():
    """Render system status indicators"""
    col1, col2, col3 = st.sidebar.columns(3)
    
    # Database status
    db_manager = get_database_manager()
    with col1:
        if db_manager.is_connected():
            st.success("DB")
        else:
            st.error("DB")
    
    # Config status
    config = get_config()
    with col2:
        is_valid, _ = config.validate()
        if is_valid:
            st.success("CFG")
        else:
            st.error("CFG")
    
    # App status
    with col3:
        st.success("APP")
