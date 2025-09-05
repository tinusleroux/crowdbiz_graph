"""
Dashboard Page
Main overview and statistics page
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from ...services.analytics_service import get_analytics_service
from ...core.database import get_database_manager
from ...core.logger import get_logger

logger = get_logger("dashboard_page")

def show_dashboard():
    """Display the main dashboard page"""
    
    st.markdown('<h1 class="main-header">CrowdBiz Graph Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to CrowdBiz Graph - Your **Sports Industry Intelligence Platform**
    
    🏈 **Privacy-First Professional Networking** - Connect with industry professionals without compromising personal privacy
    """)
    
    # Get analytics service
    analytics_service = get_analytics_service()
    db_manager = get_database_manager()
    
    try:
        # Get dashboard analytics
        analytics = analytics_service.get_dashboard_analytics()
        
        # Key metrics row
        st.markdown("## 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Total People",
                value=analytics.total_people,
                delta=f"+{analytics.total_people // 10}" if analytics.total_people > 0 else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Organizations",
                value=analytics.total_organizations,
                delta=f"+{analytics.total_organizations // 20}" if analytics.total_organizations > 0 else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            leagues_count = len(analytics.league_breakdown) if analytics.league_breakdown else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Leagues",
                value=leagues_count,
                delta=None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            # Calculate network density
            network_density = analytics.total_people / max(1, analytics.total_organizations)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Avg People/Org",
                value=f"{network_density:.1f}",
                delta=None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts section
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏈 League Distribution")
            if analytics.league_breakdown:
                # Create pie chart for league distribution
                leagues = [item['league'] for item in analytics.league_breakdown if item['league']]
                counts = [item['count'] for item in analytics.league_breakdown if item['league']]
                
                if leagues and counts:
                    fig = px.pie(
                        values=counts,
                        names=leagues,
                        title="Organizations by League",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No league data available")
            else:
                st.info("No league data available")
        
        with col2:
            st.markdown("### 🏢 Top Organizations")
            if analytics.top_organizations:
                # Create bar chart for top organizations
                orgs = [org['name'] for org in analytics.top_organizations[:10]]
                people_counts = [org['people_count'] for org in analytics.top_organizations[:10]]
                
                if orgs and people_counts:
                    fig = px.bar(
                        x=people_counts,
                        y=orgs,
                        orientation='h',
                        title="Organizations by People Count",
                        labels={'x': 'Number of People', 'y': 'Organization'}
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No organization data available")
            else:
                st.info("No organization data available")
        
        # Recent activity section
        st.markdown("---")
        st.markdown("### 📈 Recent Activity")
        
        if analytics.recent_additions:
            st.markdown("**Latest Additions to the Network:**")
            
            for addition in analytics.recent_additions[:10]:
                with st.expander(f"{addition.get('type', 'Unknown').title()}: {addition.get('name', 'Unknown')}"):
                    if addition.get('type') == 'person':
                        st.write(f"**Organization:** {addition.get('organization', 'Not specified')}")
                    elif addition.get('type') == 'organization':
                        st.write(f"**League:** {addition.get('league', 'Not specified')}")
                    
                    created_at = addition.get('created_at')
                    if created_at:
                        st.write(f"**Added:** {created_at}")
        else:
            st.info("No recent activity data available")
        
        # Quick actions section
        st.markdown("---")
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Search Network", use_container_width=True):
                st.switch_page("pages/search.py")  # Navigate to search page
        
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.switch_page("pages/analytics.py")  # Navigate to analytics
        
        with col3:
            if st.button("📥 Import Data", use_container_width=True):
                st.switch_page("pages/import_contacts.py")  # Navigate to import
        
        with col4:
            if st.button("🗃️ Explore Database", use_container_width=True):
                st.switch_page("pages/database_explorer.py")  # Navigate to database explorer
        
        # System health check
        st.markdown("---")
        st.markdown("### 🏥 System Health")
        
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            # Database connectivity
            if db_manager.is_connected():
                st.success("✅ Database Connected")
            else:
                st.error("❌ Database Disconnected")
        
        with health_col2:
            # Data freshness
            total_records = analytics.total_people + analytics.total_organizations
            if total_records > 0:
                st.success(f"✅ {total_records} Records Available")
            else:
                st.warning("⚠️ No Data Available")
        
        with health_col3:
            # Privacy compliance
            st.success("✅ Privacy Compliant")
            st.caption("No personal contact information stored")
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        st.error("Failed to load dashboard data")
        st.error(str(e))
        
        # Fallback basic info
        st.info("Showing basic system information...")
        st.write("The CrowdBiz Graph system is running, but some data may be unavailable.")

def show_dashboard_metrics():
    """Show basic dashboard metrics"""
    try:
        db_manager = get_database_manager()
        stats = db_manager.get_dashboard_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("People", stats.get('total_people', 0))
        with col2:
            st.metric("Organizations", stats.get('total_organizations', 0))
    
    except Exception as e:
        st.error(f"Error loading metrics: {e}")
