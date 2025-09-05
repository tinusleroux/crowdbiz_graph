"""
Search Page
Professional network search functionality
"""

import streamlit as st
from typing import Dict, Any

from ...services.search_service import get_search_service
from ...core.logger import get_logger

logger = get_logger("search_page")

def show_search():
    """Display the search page"""
    
    st.title("🔍 Search Professional Network")
    
    st.markdown("""
    Search across our **privacy-first professional network** to discover connections in the sports industry.
    
    **What you can search for:**
    - 👤 **People**: Names, job titles, organizations
    - 🏢 **Organizations**: Team names, leagues, cities
    - 🔗 **Connections**: Professional relationships and networks
    """)
    
    # Get search service
    search_service = get_search_service()
    
    # Search input section
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter search terms:",
            placeholder="e.g., 'head coach', 'New York Giants', 'marketing director'",
            help="Search for people, organizations, job titles, or any professional information"
        )
    
    with col2:
        search_type = st.selectbox(
            "Search in:",
            ["All", "People", "Organizations"],
            help="Filter search results by type"
        )
    
    # Advanced search options
    with st.expander("🔧 Advanced Search Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**People Filters:**")
            job_title_filter = st.text_input("Job Title contains:")
            organization_filter = st.text_input("Organization contains:")
        
        with col2:
            st.markdown("**Organization Filters:**")
            league_filter = st.selectbox("League:", ["", "NFL", "NBA", "MLB", "NHL", "MLS", "Other"])
            city_filter = st.text_input("City contains:")
    
    # Search button and results
    if search_query or st.button("🔍 Search", type="primary"):
        if search_query:
            
            # Prepare search criteria
            search_criteria = {
                'query': search_query,
                'search_type': search_type.lower() if search_type != "All" else "all",
                'limit': 50,
                'offset': 0
            }
            
            # Add filters
            filters = {}
            if job_title_filter:
                filters['job_title'] = job_title_filter
            if organization_filter:
                filters['organization'] = organization_filter
            if league_filter:
                filters['league'] = league_filter
            if city_filter:
                filters['city'] = city_filter
            
            if filters:
                if search_type.lower() == "people":
                    search_criteria['person_filters'] = filters
                elif search_type.lower() == "organizations":
                    search_criteria['org_filters'] = filters
                else:
                    search_criteria['person_filters'] = {k: v for k, v in filters.items() 
                                                       if k in ['job_title', 'organization']}
                    search_criteria['org_filters'] = {k: v for k, v in filters.items() 
                                                    if k in ['league', 'city']}
            
            # Perform search
            with st.spinner("Searching professional network..."):
                try:
                    if filters:
                        results = search_service.advanced_search(search_criteria)
                    else:
                        results = search_service.search_all(
                            search_query, 
                            limit=50, 
                            offset=0
                        )
                    
                    # Display results
                    display_search_results(results, search_query)
                    
                except Exception as e:
                    logger.error(f"Search error: {e}")
                    st.error("Search failed. Please try again.")
                    st.error(str(e))
        else:
            st.warning("Please enter a search term")
    
    # Search suggestions
    if search_query and len(search_query) >= 2:
        try:
            suggestions = search_service.get_search_suggestions(search_query, limit=5)
            if suggestions:
                st.markdown("**💡 Suggestions:**")
                cols = st.columns(min(len(suggestions), 5))
                for i, suggestion in enumerate(suggestions):
                    with cols[i]:
                        if st.button(suggestion, key=f"suggestion_{i}"):
                            st.rerun()
        except Exception as e:
            logger.warning(f"Failed to get search suggestions: {e}")

def display_search_results(results, query: str):
    """Display search results in a user-friendly format"""
    
    if not results.results:
        st.info("No results found. Try different search terms or check your filters.")
        return
    
    # Results header
    st.markdown("---")
    st.markdown(f"### 📋 Search Results ({results.total} found)")
    st.caption(f"Search query: **{query}** | Type: **{results.search_type}**")
    
    # Group results by type
    people_results = [r for r in results.results if r.get('result_type') == 'person']
    org_results = [r for r in results.results if r.get('result_type') == 'organization']
    
    # Display people results
    if people_results:
        st.markdown(f"#### 👤 People ({len(people_results)})")
        
        for person in people_results:
            display_person_result(person)
    
    # Display organization results
    if org_results:
        st.markdown(f"#### 🏢 Organizations ({len(org_results)})")
        
        for org in org_results:
            display_organization_result(org)

def display_person_result(person: Dict[str, Any]):
    """Display a person search result"""
    
    with st.container():
        st.markdown('<div class="search-result">', unsafe_allow_html=True)
        
        # Person name and title
        name = person.get('full_name', 'Unknown')
        title = person.get('job_title', '')
        
        if title:
            st.markdown(f"**{name}** - *{title}*")
        else:
            st.markdown(f"**{name}**")
        
        # Organization and department
        col1, col2 = st.columns(2)
        
        with col1:
            if person.get('organization'):
                st.write(f"🏢 {person['organization']}")
            
            if person.get('department'):
                st.write(f"📋 {person['department']}")
        
        with col2:
            # LinkedIn profile if available
            if person.get('linkedin_url'):
                st.markdown(f"[🔗 LinkedIn Profile]({person['linkedin_url']})")
            
            # Created date
            if person.get('created_at'):
                st.caption(f"Added: {person['created_at']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_organization_result(org: Dict[str, Any]):
    """Display an organization search result"""
    
    with st.container():
        st.markdown('<div class="search-result">', unsafe_allow_html=True)
        
        # Organization name and league
        name = org.get('name', 'Unknown')
        league = org.get('league', '')
        
        if league:
            st.markdown(f"**{name}** - *{league}*")
        else:
            st.markdown(f"**{name}**")
        
        # Location and details
        col1, col2 = st.columns(2)
        
        with col1:
            # Location
            location_parts = []
            if org.get('city'):
                location_parts.append(org['city'])
            if org.get('state'):
                location_parts.append(org['state'])
            
            if location_parts:
                st.write(f"📍 {', '.join(location_parts)}")
            
            # Venue
            if org.get('venue'):
                st.write(f"🏟️ {org['venue']}")
        
        with col2:
            # Website
            if org.get('website'):
                st.markdown(f"[🌐 Website]({org['website']})")
            
            # Established year
            if org.get('established_year'):
                st.write(f"📅 Est. {org['established_year']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_search_tips():
    """Display search tips and help"""
    with st.expander("💡 Search Tips"):
        st.markdown("""
        **Search Tips:**
        
        - **Names**: Search for full names or partial names
        - **Job Titles**: Try "coach", "manager", "director", "president"
        - **Organizations**: Search team names, league names, or cities
        - **Wildcards**: Use partial terms for broader results
        
        **Examples:**
        - `Tom Brady` - Find specific person
        - `head coach NFL` - Find NFL head coaches
        - `New York` - Find people/orgs in New York
        - `marketing director` - Find marketing directors
        """)
