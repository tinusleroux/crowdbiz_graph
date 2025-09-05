"""
Sidebar Component
Navigation menu with buttons
"""

import streamlit as st

from ...core.logger import get_logger

logger = get_logger("sidebar")

def render_sidebar() -> str:
    """
    Render the main sidebar navigation
    
    Returns:
        str: Selected page name
    """
    
    # Initialize selected page in session state
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard"
    
    st.sidebar.title("🏈 CrowdBiz Graph")
    st.sidebar.markdown("---")
    
    # Navigation menu buttons
    pages = [
        ("🏠", "Dashboard"),
        ("🔍", "Search"), 
        ("📥", "Import Contacts"),
        ("📰", "Import Articles"),
        ("📊", "Analytics"),
        ("🗄️", "Database Explorer")
    ]
    
    for icon, page_name in pages:
        if st.sidebar.button(f"{icon} {page_name}", 
                           use_container_width=True,
                           type="primary" if st.session_state.selected_page == page_name else "secondary"):
            st.session_state.selected_page = page_name
            st.rerun()
    
    page = st.session_state.selected_page
    
    return page
