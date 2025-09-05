"""
Analytics Page
Business intelligence and data analytics dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ...services.analytics_service import get_analytics_service
from ...core.logger import get_logger

logger = get_logger("analytics_page")

def show_analytics():
    """Display the analytics page"""
    
    st.title("📊 Analytics Dashboard")
    
    st.markdown("""
    Explore insights and trends in your **sports industry professional network**.
    """)
    
    # Get analytics service
    analytics_service = get_analytics_service()
    
    try:
        # Analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏢 Organizations", "👥 People", "🔗 Network"])
        
        with tab1:
            show_overview_analytics(analytics_service)
        
        with tab2:
            show_organization_analytics(analytics_service)
        
        with tab3:
            show_people_analytics(analytics_service)
        
        with tab4:
            show_network_analytics(analytics_service)
    
    except Exception as e:
        logger.error(f"Analytics page error: {e}")
        st.error("Failed to load analytics data")
        st.error(str(e))

def show_overview_analytics(analytics_service):
    """Show overview analytics"""
    
    st.markdown("### 📊 System Overview")
    
    # Get basic analytics
    analytics = analytics_service.get_dashboard_analytics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total People", analytics.total_people)
    
    with col2:
        st.metric("Organizations", analytics.total_organizations)
    
    with col3:
        leagues_count = len(analytics.league_breakdown) if analytics.league_breakdown else 0
        st.metric("Leagues", leagues_count)
    
    with col4:
        network_density = analytics.total_people / max(1, analytics.total_organizations)
        st.metric("Network Density", f"{network_density:.1f}")
    
    # League distribution chart
    if analytics.league_breakdown:
        st.markdown("### 🏈 League Distribution")
        
        leagues = [item['league'] for item in analytics.league_breakdown if item['league']]
        counts = [item['count'] for item in analytics.league_breakdown if item['league']]
        
        if leagues and counts:
            fig = px.pie(values=counts, names=leagues, title="Organizations by League")
            st.plotly_chart(fig, use_container_width=True)

def show_organization_analytics(analytics_service):
    """Show organization analytics"""
    
    st.markdown("### 🏢 Organization Analytics")
    
    try:
        org_analytics = analytics_service.get_organization_analytics()
        
        if org_analytics.get('error'):
            st.error(f"Error loading organization analytics: {org_analytics['error']}")
            return
        
        # Basic stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Organizations", org_analytics.get('total_organizations', 0))
        
        with col2:
            basic_stats = org_analytics.get('basic_stats', {})
            st.metric("Total Leagues", basic_stats.get('total_leagues', 0))
        
        with col3:
            st.metric("Total States", basic_stats.get('total_states', 0))
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            # League breakdown
            league_breakdown = org_analytics.get('league_breakdown', [])
            if league_breakdown:
                st.markdown("#### League Distribution")
                leagues = [item['league'] for item in league_breakdown]
                counts = [item['count'] for item in league_breakdown]
                
                fig = px.bar(x=counts, y=leagues, orientation='h', 
                           title="Organizations by League")
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Geographic breakdown
            geographic_breakdown = org_analytics.get('geographic_breakdown', [])
            if geographic_breakdown:
                st.markdown("#### Geographic Distribution")
                states = [item['state'] for item in geographic_breakdown]
                counts = [item['count'] for item in geographic_breakdown]
                
                fig = px.bar(x=counts, y=states, orientation='h',
                           title="Organizations by State")
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Organization analytics error: {e}")
        st.error("Failed to load organization analytics")

def show_people_analytics(analytics_service):
    """Show people analytics"""
    
    st.markdown("### 👥 People Analytics")
    
    try:
        people_analytics = analytics_service.get_people_analytics()
        
        if people_analytics.get('error'):
            st.error(f"Error loading people analytics: {people_analytics['error']}")
            return
        
        # Basic stats
        basic_stats = people_analytics.get('basic_stats', {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total People", basic_stats.get('total_people', 0))
        
        with col2:
            st.metric("Unique Job Titles", basic_stats.get('total_job_titles', 0))
        
        with col3:
            st.metric("Organizations Represented", basic_stats.get('total_organizations_represented', 0))
        
        # Job titles breakdown
        job_title_breakdown = people_analytics.get('job_title_breakdown', [])
        if job_title_breakdown:
            st.markdown("#### Top Job Titles")
            
            titles = [item['job_title'] for item in job_title_breakdown[:15]]
            counts = [item['count'] for item in job_title_breakdown[:15]]
            
            fig = px.bar(x=counts, y=titles, orientation='h',
                       title="Most Common Job Titles")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Organization representation
        org_breakdown = people_analytics.get('organization_breakdown', [])
        if org_breakdown:
            st.markdown("#### Top Organizations by People Count")
            
            orgs = [item['organization'] for item in org_breakdown[:10]]
            counts = [item['count'] for item in org_breakdown[:10]]
            
            fig = px.bar(x=counts, y=orgs, orientation='h',
                       title="Organizations with Most People")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"People analytics error: {e}")
        st.error("Failed to load people analytics")

def show_network_analytics(analytics_service):
    """Show network analytics"""
    
    st.markdown("### 🔗 Network Analytics")
    
    try:
        network_analytics = analytics_service.get_network_analysis()
        
        if network_analytics.get('error'):
            st.error(f"Error loading network analytics: {network_analytics['error']}")
            return
        
        # Network stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Network Nodes", network_analytics.get('total_network_nodes', 0))
        
        with col2:
            st.metric("People Connections", network_analytics.get('total_people_connections', 0))
        
        with col3:
            st.metric("Organization Nodes", network_analytics.get('total_organization_nodes', 0))
        
        # Network density metrics
        network_density = network_analytics.get('network_density', {})
        if network_density:
            st.markdown("#### Network Density Metrics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg People per Org", f"{network_density.get('avg_people_per_organization', 0):.1f}")
            with col2:
                st.metric("Connected Organizations", network_density.get('organizations_with_people', 0))
            with col3:
                st.metric("Empty Organizations", network_density.get('empty_organizations', 0))
        
        # Top connected organizations
        top_connected = network_analytics.get('top_connected_organizations', [])
        if top_connected:
            st.markdown("#### Most Connected Organizations")
            
            orgs = [item['organization'] for item in top_connected[:15]]
            people_counts = [item['people_count'] for item in top_connected[:15]]
            
            fig = px.bar(x=people_counts, y=orgs, orientation='h',
                       title="Organizations by Connection Count")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Network analytics error: {e}")
        st.error("Failed to load network analytics")
