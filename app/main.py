"""
Main Streamlit Application Entry Point
Orchestrates the entire CrowdBiz Graph application
"""

import streamlit as st
import sys
from datetime import datetime

# Import UI components
from app.ui.components.sidebar import render_sidebar
from app.ui.pages.dashboard import show_dashboard
from app.ui.pages.search import show_search
from app.ui.pages.import_contacts import show_import_contacts
from app.ui.pages.import_articles import show_import_articles
from app.ui.pages.analytics import show_analytics
from app.ui.pages.database_explorer import show_database_explorer

# Import core services
from app.core.config import get_config
from app.core.database import get_database_manager
from app.core.logger import get_logger

# Configure logger
logger = get_logger("main_app")

def initialize_app():
    """Initialize the Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="CrowdBiz Graph - Sports Industry Intelligence",
        page_icon="🏈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
    
    # Initialize session state
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.start_time = datetime.now()
        logger.info("CrowdBiz Graph application initialized")
    
    # Validate configuration
    config = get_config()
    is_valid, errors = config.validate()
    
    if not is_valid:
        st.error("Configuration Error")
        st.error("Please check your environment variables:")
        for error in errors:
            st.error(f"• {error}")
        st.stop()
    
    # Check database connection
    db_manager = get_database_manager()
    if not db_manager.is_connected():
        st.error("Database Connection Failed")
        st.error("Cannot connect to Supabase. Please check your database configuration.")
        st.info("Make sure SUPABASE_URL and SUPABASE_API_KEY are set correctly.")
        st.stop()
    
    logger.info("App initialization completed successfully")

def main():
    """Main application entry point"""
    try:
        # Initialize the application
        initialize_app()
        
        # Render sidebar and get selected page
        selected_page = render_sidebar()
        
        # Route to the appropriate page
        if selected_page == "Dashboard":
            show_dashboard()
        elif selected_page == "Search":
            show_search()
        elif selected_page == "Import Contacts":
            show_import_contacts()
        elif selected_page == "Import Articles":
            show_import_articles()
        elif selected_page == "Analytics":
            show_analytics()
        elif selected_page == "Database Explorer":
            show_database_explorer()
        else:
            # Default to dashboard
            show_dashboard()
    
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
