"""
Analytics Service
Provides business intelligence and analytics for the sports industry data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

from ..core.database import get_database_manager, get_table_data
from ..core.logger import get_logger
from ..core.models import AnalyticsResponse

logger = get_logger("analytics_service")

class AnalyticsService:
    """Service for generating analytics and business intelligence"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    def get_dashboard_analytics(self) -> AnalyticsResponse:
        """
        Get comprehensive dashboard analytics
        
        Returns:
            AnalyticsResponse with key metrics and breakdowns
        """
        logger.info("Generating dashboard analytics")
        
        try:
            # Get basic stats from database manager
            dashboard_stats = self.db_manager.get_dashboard_stats()
            
            # Get additional analytics
            top_organizations = self._get_top_organizations()
            recent_additions = self._get_recent_additions()
            
            return AnalyticsResponse(
                total_people=dashboard_stats.get('total_people', 0),
                total_organizations=dashboard_stats.get('total_organizations', 0),
                league_breakdown=dashboard_stats.get('league_breakdown', []),
                top_organizations=top_organizations,
                recent_additions=recent_additions
            )
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard analytics: {e}")
            return AnalyticsResponse()
    
    def get_organization_analytics(self) -> Dict[str, Any]:
        """
        Get detailed organization analytics
        
        Returns:
            Dictionary with organization statistics and breakdowns
        """
        logger.info("Generating organization analytics")
        
        try:
            # Get all organizations
            organizations = get_table_data('organization', limit=1000)
            
            if not organizations:
                return {
                    'total_organizations': 0,
                    'org_type_breakdown': [],
                    'by_sport': [],
                    'top_organizations': []
                }
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(organizations)
            
            # League breakdown
            league_breakdown = []
            if 'league' in df.columns:
                league_counts = df['league'].value_counts().to_dict()
                league_breakdown = [
                    {'league': league, 'count': count}
                    for league, count in league_counts.items()
                    if league and pd.notna(league)
                ]
            
            # Geographic breakdown
            geographic_breakdown = []
            if 'state' in df.columns:
                state_counts = df['state'].value_counts().head(10).to_dict()
                geographic_breakdown = [
                    {'state': state, 'count': count}
                    for state, count in state_counts.items()
                    if state and pd.notna(state)
                ]
            
            # Establishment timeline (if we have established_year)
            establishment_timeline = []
            if 'established_year' in df.columns:
                year_counts = df['established_year'].value_counts().sort_index().to_dict()
                establishment_timeline = [
                    {'year': int(year), 'count': count}
                    for year, count in year_counts.items()
                    if year and pd.notna(year) and year > 1800
                ]
            
            return {
                'total_organizations': len(organizations),
                'league_breakdown': league_breakdown,
                'geographic_breakdown': geographic_breakdown,
                'establishment_timeline': establishment_timeline,
                'basic_stats': {
                    'total_organizations': len(organizations),
                    'total_leagues': len(league_breakdown),
                    'total_states': len(geographic_breakdown)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate organization analytics: {e}")
            return {'error': str(e)}
    
    def get_people_analytics(self) -> Dict[str, Any]:
        """
        Get detailed people analytics
        
        Returns:
            Dictionary with people statistics and breakdowns
        """
        logger.info("Generating people analytics")
        
        try:
            # Get all people
            people = get_table_data('people', limit=1000)
            
            if not people:
                return {
                    'total_people': 0,
                    'job_title_breakdown': [],
                    'organization_breakdown': [],
                    'department_breakdown': []
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(people)
            
            # Job title breakdown
            job_title_breakdown = []
            if 'job_title' in df.columns:
                title_counts = df['job_title'].value_counts().head(15).to_dict()
                job_title_breakdown = [
                    {'job_title': title, 'count': count}
                    for title, count in title_counts.items()
                    if title and pd.notna(title)
                ]
            
            # Organization breakdown
            organization_breakdown = []
            if 'organization' in df.columns:
                org_counts = df['organization'].value_counts().head(15).to_dict()
                organization_breakdown = [
                    {'organization': org, 'count': count}
                    for org, count in org_counts.items()
                    if org and pd.notna(org)
                ]
            
            # Department breakdown
            department_breakdown = []
            if 'department' in df.columns:
                dept_counts = df['department'].value_counts().head(10).to_dict()
                department_breakdown = [
                    {'department': dept, 'count': count}
                    for dept, count in dept_counts.items()
                    if dept and pd.notna(dept)
                ]
            
            return {
                'total_people': len(people),
                'job_title_breakdown': job_title_breakdown,
                'organization_breakdown': organization_breakdown,
                'department_breakdown': department_breakdown,
                'basic_stats': {
                    'total_people': len(people),
                    'total_job_titles': len(job_title_breakdown),
                    'total_organizations_represented': len(organization_breakdown),
                    'total_departments': len(department_breakdown)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate people analytics: {e}")
            return {'error': str(e)}
    
    def get_industry_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get industry trends and movement analytics
        
        Args:
            days: Number of days to look back for trends
        
        Returns:
            Dictionary with trend analysis
        """
        logger.info(f"Generating industry trends for last {days} days")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get recent additions
            recent_people = self._get_recent_data('people', cutoff_date)
            recent_orgs = self._get_recent_data('organizations', cutoff_date)
            
            # Analyze growth trends
            growth_trends = {
                'people_added': len(recent_people),
                'organizations_added': len(recent_orgs),
                'daily_average_people': len(recent_people) / max(1, days),
                'daily_average_organizations': len(recent_orgs) / max(1, days)
            }
            
            # New organizations by league
            new_orgs_by_league = defaultdict(int)
            for org in recent_orgs:
                league = org.get('league', 'Unknown')
                if league:
                    new_orgs_by_league[league] += 1
            
            # New people by organization
            new_people_by_org = defaultdict(int)
            for person in recent_people:
                org = person.get('organization', 'Unknown')
                if org:
                    new_people_by_org[org] += 1
            
            return {
                'period_days': days,
                'growth_trends': growth_trends,
                'new_organizations_by_league': [
                    {'league': league, 'count': count}
                    for league, count in new_orgs_by_league.items()
                ],
                'new_people_by_organization': [
                    {'organization': org, 'count': count}
                    for org, count in sorted(new_people_by_org.items(), 
                                           key=lambda x: x[1], reverse=True)[:10]
                ],
                'summary': {
                    'total_new_entries': len(recent_people) + len(recent_orgs),
                    'most_active_league': max(new_orgs_by_league.items(), 
                                            key=lambda x: x[1])[0] if new_orgs_by_league else None,
                    'most_hiring_organization': max(new_people_by_org.items(), 
                                                  key=lambda x: x[1])[0] if new_people_by_org else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate industry trends: {e}")
            return {'error': str(e), 'period_days': days}
    
    def get_network_analysis(self) -> Dict[str, Any]:
        """
        Get professional network analysis
        
        Returns:
            Dictionary with network statistics
        """
        logger.info("Generating network analysis")
        
        try:
            # Get all data
            people = get_table_data('person', limit=1000)
            organizations = get_table_data('organization', limit=1000)
            
            # Organization connectivity (how many people per organization)
            org_connectivity = defaultdict(int)
            org_people = defaultdict(list)
            
            for person in people:
                org = person.get('organization')
                if org:
                    org_connectivity[org] += 1
                    org_people[org].append(person)
            
            # Most connected organizations
            top_connected_orgs = [
                {'organization': org, 'people_count': count}
                for org, count in sorted(org_connectivity.items(), 
                                       key=lambda x: x[1], reverse=True)[:15]
            ]
            
            # League connectivity
            league_people_count = defaultdict(int)
            for org in organizations:
                league = org.get('league')
                if league and org.get('name') in org_connectivity:
                    league_people_count[league] += org_connectivity[org.get('name', '')]
            
            league_connectivity = [
                {'league': league, 'total_people': count}
                for league, count in sorted(league_people_count.items(), 
                                          key=lambda x: x[1], reverse=True)
            ]
            
            return {
                'total_network_nodes': len(people) + len(organizations),
                'total_people_connections': len(people),
                'total_organization_nodes': len(organizations),
                'top_connected_organizations': top_connected_orgs,
                'league_connectivity': league_connectivity,
                'network_density': {
                    'avg_people_per_organization': sum(org_connectivity.values()) / max(1, len(org_connectivity)),
                    'organizations_with_people': len(org_connectivity),
                    'empty_organizations': len(organizations) - len(org_connectivity)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate network analysis: {e}")
            return {'error': str(e)}
    
    def _get_top_organizations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top organizations by people count"""
        try:
            people = get_table_data('person', limit=1000)
            org_counts = defaultdict(int)
            
            for person in people:
                org = person.get('organization')
                if org:
                    org_counts[org] += 1
            
            return [
                {'name': org, 'people_count': count}
                for org, count in sorted(org_counts.items(), 
                                       key=lambda x: x[1], reverse=True)[:limit]
            ]
        except Exception:
            return []
    
    def _get_recent_additions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently added people and organizations"""
        try:
            recent_people = get_table_data('person', limit=limit, filters={})
            recent_orgs = get_table_data('organization', limit=limit, filters={})
            
            # Combine and sort by creation date if available
            recent = []
            
            for person in recent_people[-5:]:  # Last 5 people
                recent.append({
                    'type': 'person',
                    'name': person.get('full_name', 'Unknown'),
                    'organization': person.get('organization'),
                    'created_at': person.get('created_at')
                })
            
            for org in recent_orgs[-5:]:  # Last 5 organizations
                recent.append({
                    'type': 'organization',
                    'name': org.get('name', 'Unknown'),
                    'league': org.get('league'),
                    'created_at': org.get('created_at')
                })
            
            return recent
        except Exception:
            return []
    
    def _get_recent_data(self, table: str, cutoff_date: datetime) -> List[Dict]:
        """Get data added after cutoff date"""
        try:
            all_data = get_table_data(table, limit=1000)
            recent_data = []
            
            for item in all_data:
                created_at = item.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    if created_at > cutoff_date:
                        recent_data.append(item)
            
            return recent_data
        except Exception:
            return []

# Global analytics service instance
_analytics_service: Optional[AnalyticsService] = None

def get_analytics_service() -> AnalyticsService:
    """Get or create the global analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
