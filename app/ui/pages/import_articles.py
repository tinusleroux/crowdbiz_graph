"""
Import Articles Page
Coming soon - article and press release import functionality
"""

import streamlit as st

def show_import_articles():
    """Display the import articles page"""
    
    st.title("📰 Import News Articles")
    
    st.markdown("""
    Import news articles and industry content. The system will extract key information and store it for analysis.
    
    **Supported formats:**
    - Text files (.txt)
    - Markdown files (.md)  
    - CSV files with article data
    """)
    
    # Coming soon notice
    st.info("📝 **Coming Soon**: Article import functionality will be available when article management endpoints are added to the API.")
    
    # File upload placeholder
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=['txt', 'md', 'csv'])
    
    if uploaded_files:
        st.warning("Article import endpoints are not yet implemented in the API. Please use the direct import scripts for now.")
    
    # Future features preview
    with st.expander("🔮 Planned Features"):
        st.markdown("""
        **Planned Article Import Features:**
        
        - 📰 **Press Release Processing**: Automatic extraction of key information
        - 🔗 **URL Import**: Direct import from news websites
        - 📊 **Content Analysis**: Extract people, organizations, and key events
        - 🏷️ **Auto-Tagging**: Automatic categorization and tagging
        - 📅 **Timeline Integration**: Connect articles to professional timelines
        - 🔍 **Search Integration**: Make articles searchable within the platform
        """)
