"""
Search Service
Handles all search operations across people and organizations
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

from ..core.database import get_database_manager, search_database
from ..core.privacy import sanitize_data_for_display
from ..core.logger import get_logger
from ..core.models import SearchResponse

logger = get_logger("search_service")

class SearchService:
    """Service for handling search operations"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    def search_all(self, query: str, limit: int = 100, offset: int = 0, 
                   filters: Dict[str, Any] = None) -> SearchResponse:
        """
        Search across all entities (people and organizations)
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            offset: Number of results to skip
            filters: Additional search filters
        
        Returns:
            SearchResponse with combined results
        """
        logger.info(f"Performing unified search: '{query}' (limit: {limit}, offset: {offset})")
        
        try:
            # Use the unified search from database
            search_results = search_database(query, "all", limit, offset)
            
            if search_results.get('error'):
                logger.error(f"Search failed: {search_results['error']}")
                return SearchResponse(
                    results=[],
                    total=0,
                    page=offset // limit + 1,
                    limit=limit,
                    query=query,
                    search_type="all"
                )
            
            # Sanitize results for display
            sanitized_results = []
            for result in search_results.get('results', []):
                sanitized_result = sanitize_data_for_display(result)
                sanitized_results.append(sanitized_result)
            
            # Apply additional filters if provided
            if filters:
                sanitized_results = self._apply_filters(sanitized_results, filters)
            
            logger.info(f"Search completed: {len(sanitized_results)} results returned")
            
            return SearchResponse(
                results=sanitized_results,
                total=len(sanitized_results),
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="all"
            )
            
        except Exception as e:
            logger.error(f"Search operation failed: {e}")
            return SearchResponse(
                results=[],
                total=0,
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="all"
            )
    
    def search_people(self, query: str, limit: int = 100, offset: int = 0,
                     filters: Dict[str, Any] = None) -> SearchResponse:
        """
        Search specifically for people
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Results offset
            filters: Additional filters (job_title, organization, etc.)
        
        Returns:
            SearchResponse with people results
        """
        logger.info(f"Searching people: '{query}' (limit: {limit}, offset: {offset})")
        
        try:
            # Search people using database manager
            people_results = self.db_manager.search_people(query, limit, offset)
            
            # Sanitize results
            sanitized_results = []
            for person in people_results:
                sanitized_person = sanitize_data_for_display(person)
                sanitized_person['result_type'] = 'person'
                sanitized_results.append(sanitized_person)
            
            # Apply additional filters
            if filters:
                sanitized_results = self._apply_people_filters(sanitized_results, filters)
            
            logger.info(f"People search completed: {len(sanitized_results)} results")
            
            return SearchResponse(
                results=sanitized_results,
                total=len(sanitized_results),
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="people"
            )
            
        except Exception as e:
            logger.error(f"People search failed: {e}")
            return SearchResponse(
                results=[],
                total=0,
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="people"
            )
    
    def search_organizations(self, query: str, limit: int = 100, offset: int = 0,
                           filters: Dict[str, Any] = None) -> SearchResponse:
        """
        Search specifically for organizations
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Results offset
            filters: Additional filters (league, city, state, etc.)
        
        Returns:
            SearchResponse with organization results
        """
        logger.info(f"Searching organizations: '{query}' (limit: {limit}, offset: {offset})")
        
        try:
            # Search organizations using database manager
            org_results = self.db_manager.search_organizations(query, limit, offset)
            
            # Sanitize results
            sanitized_results = []
            for org in org_results:
                sanitized_org = sanitize_data_for_display(org)
                sanitized_org['result_type'] = 'organization'
                sanitized_results.append(sanitized_org)
            
            # Apply additional filters
            if filters:
                sanitized_results = self._apply_organization_filters(sanitized_results, filters)
            
            logger.info(f"Organization search completed: {len(sanitized_results)} results")
            
            return SearchResponse(
                results=sanitized_results,
                total=len(sanitized_results),
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="organizations"
            )
            
        except Exception as e:
            logger.error(f"Organization search failed: {e}")
            return SearchResponse(
                results=[],
                total=0,
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="organizations"
            )
    
    def advanced_search(self, criteria: Dict[str, Any]) -> SearchResponse:
        """
        Perform advanced search with multiple criteria
        
        Args:
            criteria: Dictionary of search criteria including:
                - query: Text search query
                - person_filters: Filters specific to people
                - org_filters: Filters specific to organizations
                - search_type: 'people', 'organizations', or 'all'
                - limit, offset: Pagination
        
        Returns:
            SearchResponse with filtered results
        """
        query = criteria.get('query', '')
        search_type = criteria.get('search_type', 'all')
        limit = criteria.get('limit', 100)
        offset = criteria.get('offset', 0)
        
        logger.info(f"Advanced search: query='{query}', type={search_type}")
        
        if search_type == 'people':
            return self.search_people(
                query, limit, offset, 
                filters=criteria.get('person_filters', {})
            )
        elif search_type == 'organizations':
            return self.search_organizations(
                query, limit, offset,
                filters=criteria.get('org_filters', {})
            )
        else:
            # Combined search with separate filters
            results = []
            
            if not criteria.get('org_filters'):  # Include people if no org-specific filters
                people_results = self.search_people(
                    query, limit // 2, offset,
                    filters=criteria.get('person_filters', {})
                )
                results.extend(people_results.results)
            
            if not criteria.get('person_filters'):  # Include orgs if no people-specific filters
                org_results = self.search_organizations(
                    query, limit // 2, offset,
                    filters=criteria.get('org_filters', {})
                )
                results.extend(org_results.results)
            
            return SearchResponse(
                results=results[:limit],
                total=len(results),
                page=offset // limit + 1,
                limit=limit,
                query=query,
                search_type="advanced"
            )
    
    def _apply_filters(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply general filters to search results"""
        filtered_results = results
        
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue
            
            filtered_results = [
                result for result in filtered_results
                if self._matches_filter(result, filter_key, filter_value)
            ]
        
        return filtered_results
    
    def _apply_people_filters(self, people: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply people-specific filters"""
        filtered_people = people
        
        # Job title filter
        if filters.get('job_title'):
            job_title = filters['job_title'].lower()
            filtered_people = [
                person for person in filtered_people
                if person.get('job_title', '').lower().find(job_title) >= 0
            ]
        
        # Organization filter
        if filters.get('organization'):
            org_name = filters['organization'].lower()
            filtered_people = [
                person for person in filtered_people
                if person.get('organization', '').lower().find(org_name) >= 0
            ]
        
        # Department filter
        if filters.get('department'):
            dept = filters['department'].lower()
            filtered_people = [
                person for person in filtered_people
                if person.get('department', '').lower().find(dept) >= 0
            ]
        
        return filtered_people
    
    def _apply_organization_filters(self, orgs: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply organization-specific filters"""
        filtered_orgs = orgs
        
        # League filter
        if filters.get('league'):
            league = filters['league'].lower()
            filtered_orgs = [
                org for org in filtered_orgs
                if org.get('league', '').lower().find(league) >= 0
            ]
        
        # City filter
        if filters.get('city'):
            city = filters['city'].lower()
            filtered_orgs = [
                org for org in filtered_orgs
                if org.get('city', '').lower().find(city) >= 0
            ]
        
        # State filter
        if filters.get('state'):
            state = filters['state'].lower()
            filtered_orgs = [
                org for org in filtered_orgs
                if org.get('state', '').lower().find(state) >= 0
            ]
        
        return filtered_orgs
    
    def _matches_filter(self, item: Dict, filter_key: str, filter_value: Any) -> bool:
        """Check if an item matches a specific filter"""
        item_value = item.get(filter_key, '')
        
        if isinstance(item_value, str) and isinstance(filter_value, str):
            return filter_value.lower() in item_value.lower()
        
        return item_value == filter_value
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search text
            limit: Maximum suggestions to return
        
        Returns:
            List of suggested search terms
        """
        if len(partial_query) < 2:
            return []
        
        try:
            suggestions = set()
            
            # Get people name suggestions
            people_results = self.db_manager.search_people(partial_query, limit=limit * 2)
            for person in people_results:
                if person.get('full_name'):
                    suggestions.add(person['full_name'])
                if person.get('organization'):
                    suggestions.add(person['organization'])
                if person.get('job_title'):
                    suggestions.add(person['job_title'])
            
            # Get organization suggestions
            org_results = self.db_manager.search_organizations(partial_query, limit=limit * 2)
            for org in org_results:
                if org.get('name'):
                    suggestions.add(org['name'])
                if org.get('league'):
                    suggestions.add(org['league'])
            
            # Sort by relevance (starts with query first)
            suggestions_list = list(suggestions)
            partial_lower = partial_query.lower()
            
            # Priority: exact match > starts with > contains
            exact_matches = [s for s in suggestions_list if s.lower() == partial_lower]
            starts_with = [s for s in suggestions_list if s.lower().startswith(partial_lower) and s.lower() != partial_lower]
            contains = [s for s in suggestions_list if partial_lower in s.lower() and not s.lower().startswith(partial_lower)]
            
            return (exact_matches + starts_with + contains)[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []

# Global search service instance
_search_service: Optional[SearchService] = None

def get_search_service() -> SearchService:
    """Get or create the global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
