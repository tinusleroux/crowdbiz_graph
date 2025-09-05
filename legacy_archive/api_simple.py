#!/usr/bin/env python3
"""
CrowdBiz API Server - Simplified Supabase Version
FastAPI-based REST API for sports industry contact intelligence
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client

from fastapi import FastAPI, HTTPException, Query, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import sys

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_API_KEY')
)

# Create FastAPI app
app = FastAPI(
    title="CrowdBiz Graph API",
    description="Sports Industry Contact Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Print Python executable path at startup
print(f"[FastAPI] Python: {sys.executable}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PersonBase(BaseModel):
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    linkedin_url: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: str
    created_at: datetime
    updated_at: datetime

class OrganizationBase(BaseModel):
    name: str
    league: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: str
    established_year: Optional[int] = None
    venue: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    limit: int

# Helper functions
def safe_supabase_query(table: str, operation: str, **kwargs):
    """Safely execute Supabase queries with error handling"""
    try:
        if operation == "select":
            query = supabase.table(table).select("*")
            
            # Apply filters if provided
            if "filters" in kwargs:
                for key, value in kwargs["filters"].items():
                    if value is not None:
                        query = query.ilike(key, f"%{value}%")
            
            # Apply pagination
            if "limit" in kwargs:
                query = query.limit(kwargs["limit"])
            if "offset" in kwargs:
                query = query.offset(kwargs["offset"])
            
            result = query.execute()
            return result.data
            
        elif operation == "insert":
            result = supabase.table(table).insert(kwargs.get("data", {})).execute()
            return result.data
            
        elif operation == "update":
            result = supabase.table(table).update(kwargs.get("data", {})).eq("id", kwargs.get("id")).execute()
            return result.data
            
        elif operation == "delete":
            result = supabase.table(table).delete().eq("id", kwargs.get("id")).execute()
            return result.data
            
    except Exception as e:
        print(f"Supabase query error: {e}")
        return []

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test connection with a simple query
        result = supabase.table('person').select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# People endpoints
@app.get("/people")
async def list_people(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None)
):
    """List people with optional search"""
    try:
        query = supabase.table('person').select("*")
        
        if search:
            query = query.or_(f"full_name.ilike.%{search}%,first_name.ilike.%{search}%,last_name.ilike.%{search}%")
        
        query = query.order('full_name').limit(limit).offset(offset)
        result = query.execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve people: {str(e)}"
        )

@app.get("/people/{person_id}")
async def get_person(person_id: str = Path(...)):
    """Get person by ID"""
    try:
        result = supabase.table('person').select("*").eq("id", person_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve person: {str(e)}"
        )

@app.post("/people")
async def create_person(person: PersonCreate):
    """Create new person with duplicate handling"""
    try:
        # Only include fields that exist in the person table schema
        person_data = {
            'full_name': person.full_name,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'linkedin_url': person.linkedin_url,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values to avoid inserting nulls where not needed
        person_data = {k: v for k, v in person_data.items() if v is not None}
        
        # Check for existing person by linkedin_url only (since no email)
        existing_person = None
        
        if person_data.get("linkedin_url"):
            result = supabase.table('person').select('*').eq('linkedin_url', person_data["linkedin_url"]).execute()
            if result.data:
                existing_person = result.data[0]
        
        if existing_person:
            # Update existing record
            result = supabase.table('person').update(person_data).eq('id', existing_person['id']).execute()
            if result.data:
                return result.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update existing person"
                )
        else:
            # Insert new record
            person_data["created_at"] = datetime.utcnow().isoformat()
            result = supabase.table('person').insert(person_data).execute()
            if result.data:
                return result.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create person"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create person: {str(e)}"
        )

@app.delete("/people/{person_id}")
async def delete_person(person_id: str = Path(...)):
    """Delete person by ID"""
    try:
        # First check if person exists
        result = supabase.table('person').select("*").eq("id", person_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found"
            )
        
        # Delete the person (roles will be deleted via CASCADE if foreign key constraints exist)
        delete_result = supabase.table('person').delete().eq("id", person_id).execute()
        
        return {"message": "Person deleted successfully", "id": person_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete person: {str(e)}"
        )

# Organizations endpoints
@app.get("/organizations")
async def list_organizations(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sport: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """List organizations with optional filtering"""
    try:
        query = supabase.table('organization').select("*")
        
        if sport:
            query = query.ilike('sport', f"%{sport}%")
        
        if search:
            query = query.or_(f"name.ilike.%{search}%,sport.ilike.%{search}%,org_type.ilike.%{search}%")
        
        query = query.order('name').limit(limit).offset(offset)
        result = query.execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve organizations: {str(e)}"
        )

@app.get("/organizations/{org_id}")
async def get_organization(org_id: str = Path(...)):
    """Get organization by ID"""
    try:
        result = supabase.table('organization').select("*").eq("id", org_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve organization: {str(e)}"
        )

# Roles endpoints
@app.get("/roles")
async def list_roles(
    person_id: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List roles with optional filtering"""
    try:
        query = supabase.table('role').select("*, person:person_id(full_name), organization:org_id(name)")
        
        if person_id:
            query = query.eq('person_id', person_id)
        if org_id:
            query = query.eq('org_id', org_id)
        
        query = query.order('start_date', desc=True).limit(limit)
        result = query.execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve roles: {str(e)}"
        )

# Search endpoints
@app.get("/search")
async def search(
    q: str = Query(..., min_length=2),
    type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Universal search across people and organizations"""
    try:
        results = []
        
        # Search people
        if not type or type == "person":
            people_query = supabase.table('person').select("*").or_(
                f"full_name.ilike.%{q}%,first_name.ilike.%{q}%,last_name.ilike.%{q}%"
            ).limit(limit).offset(offset)
            
            people_result = people_query.execute()
            
            for person in people_result.data:
                results.append({
                    "type": "person",
                    "id": person["id"],
                    "name": person["full_name"],
                    "linkedin_url": person.get("linkedin_url"),
                    "description": f"Contact: {person['full_name']}"
                })
        
        # Search organizations
        if not type or type == "organization":
            org_query = supabase.table('organization').select("*").or_(
                f"name.ilike.%{q}%,sport.ilike.%{q}%,org_type.ilike.%{q}%"
            ).limit(limit).offset(offset)
            
            org_result = org_query.execute()
            
            for org in org_result.data:
                results.append({
                    "type": "organization",
                    "id": org["id"],
                    "name": org["name"],
                    "sport": org.get("sport"),
                    "org_type": org.get("org_type"),
                    "description": f"Organization: {org['name']} ({org.get('sport', 'Unknown sport')})"
                })
        
        return SearchResponse(
            results=results,
            total=len(results),
            page=offset // limit + 1,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

# Analytics endpoints
@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get overview analytics"""
    try:
        # Get people count
        people_result = supabase.table('person').select("id", count="exact").execute()
        people_count = people_result.count or 0
        
        # Get organizations count
        org_result = supabase.table('organization').select("id", count="exact").execute()
        org_count = org_result.count or 0
        
        # Get sport breakdown
        sports_result = supabase.table('organization').select("sport").execute()
        sports = {}
        for org in sports_result.data:
            sport = org.get('sport', 'Unknown')
            sports[sport] = sports.get(sport, 0) + 1
        
        return {
            "total_people": people_count,
            "total_organizations": org_count,
            "active_roles": 0,  # Placeholder - would need role table
            "total_connections": people_count + org_count,
            "industry_breakdown": sports
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics failed: {str(e)}"
        )

@app.get("/analytics/growth")
async def get_growth_analytics():
    """Get growth analytics - placeholder"""
    try:
        # This would require actual date-based queries
        # Returning sample data for now
        return [
            {"date": "2024-01-01", "count": 100},
            {"date": "2024-02-01", "count": 150},
            {"date": "2024-03-01", "count": 200},
            {"date": "2024-04-01", "count": 250},
            {"date": "2024-05-01", "count": 300},
            {"date": "2024-06-01", "count": 350}
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Growth analytics failed: {str(e)}"
        )

@app.get("/analytics/network")
async def get_network_analytics():
    """Get network analysis - placeholder"""
    try:
        return {
            "density": 0.25,
            "avg_connections": 3.5,
            "top_connectors": 10,
            "connection_matrix": [[1, 0.5, 0.3], [0.5, 1, 0.7], [0.3, 0.7, 1]]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Network analytics failed: {str(e)}"
        )

@app.get("/analytics/roles/changes")
async def get_role_changes(days: int = Query(30)):
    """Get recent role changes"""
    try:
        # Get recent roles/changes from role table or person table
        # Since we don't have a role table, we'll get recent person updates as a proxy
        result = supabase.table('person').select("*").order('updated_at', desc=True).limit(50).execute()
        
        changes = []
        for person in result.data:
            # Create a mock change entry
            changes.append({
                "person_name": person.get("full_name", "Unknown"),
                "organization_name": "Unknown Organization",  # Would need to join with org table
                "title": "Unknown Role",
                "department": "Unknown Department", 
                "created_at": person.get("updated_at", person.get("created_at", ""))
            })
        
        return {
            "changes": changes[:10],  # Return top 10
            "total_changes": len(changes)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role changes failed: {str(e)}"
        )

@app.get("/analytics/organizations/stats")
async def get_organization_stats():
    """Get organization statistics"""
    try:
        # Get organization breakdown by league/sport
        result = supabase.table('organization').select("*").execute()
        
        league_breakdown = {}
        state_breakdown = {}
        total_organizations = len(result.data)
        
        for org in result.data:
            # League breakdown
            league = org.get('sport', org.get('league', 'Unknown'))
            league_breakdown[league] = league_breakdown.get(league, 0) + 1
            
            # State breakdown
            state = org.get('state', 'Unknown')
            state_breakdown[state] = state_breakdown.get(state, 0) + 1
        
        # Format for frontend
        league_data = [{"league": k, "count": v} for k, v in league_breakdown.items()]
        state_data = [{"state": k, "count": v} for k, v in state_breakdown.items()]
        
        return {
            "basic_stats": {
                "total_organizations": total_organizations,
                "total_leagues": len(league_breakdown),
                "total_states": len(state_breakdown)
            },
            "league_breakdown": league_data,
            "state_breakdown": state_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Organization stats failed: {str(e)}"
        )

# Import endpoints for UI
@app.post("/import/contacts")
async def import_contacts(data: Dict[str, Any]):
    """Import contacts from CSV data with improved handling"""
    try:
        contacts = data.get("contacts", [])
        source = data.get("source", "unknown")
        
        imported = 0
        updated = 0
        errors = []
        
        for contact in contacts:
            try:
                # Basic validation
                if not contact.get("name") and not contact.get("full_name"):
                    errors.append("Missing name field")
                    continue
                
                # Prepare person data - only use columns that exist in the person table
                person_data = {
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Handle name fields
                if contact.get("name"):
                    person_data["full_name"] = str(contact["name"]).strip()
                elif contact.get("full_name"):
                    person_data["full_name"] = str(contact["full_name"]).strip()
                
                if contact.get("first_name"):
                    person_data["first_name"] = str(contact["first_name"]).strip()
                if contact.get("last_name"):
                    person_data["last_name"] = str(contact["last_name"]).strip()
                
                # Handle linkedin only (no email fields)
                if contact.get("linkedin_url"):
                    linkedin = str(contact["linkedin_url"]).strip()
                    if linkedin and linkedin.lower() not in ['', 'nan', 'null']:
                        person_data["linkedin_url"] = linkedin
                
                # Remove None values
                person_data = {k: v for k, v in person_data.items() if v is not None}
                
                # Use upsert to handle duplicates gracefully (linkedin_url only)
                existing_person = None
                
                if person_data.get("linkedin_url"):
                    result = supabase.table('person').select('*').eq('linkedin_url', person_data["linkedin_url"]).execute()
                    if result.data:
                        existing_person = result.data[0]
                
                # Insert or update person
                if existing_person:
                    # Update existing record
                    result = supabase.table('person').update(person_data).eq('id', existing_person['id']).execute()
                    if result.data:
                        person_id = existing_person['id']
                        updated += 1
                    else:
                        errors.append(f"Failed to update person: {person_data.get('full_name', 'unknown')}")
                        continue
                else:
                    # Insert new record
                    person_data["created_at"] = datetime.utcnow().isoformat()
                    result = supabase.table('person').insert(person_data).execute()
                    if result.data:
                        person_id = result.data[0]['id']
                        imported += 1
                    else:
                        errors.append(f"Failed to create person: {person_data.get('full_name', 'unknown')}")
                        continue
                
                # Handle organization and role if provided
                org_name = contact.get("organization") or contact.get("company") or contact.get("company_name")
                job_title = contact.get("job_title") or contact.get("title")
                
                if org_name and job_title:
                    org_name = str(org_name).strip()
                    job_title = str(job_title).strip()
                    
                    if org_name and job_title:
                        try:
                            # Find or create organization
                            org_result = supabase.table('organization').select("*").ilike('name', org_name).execute()
                            
                            if org_result.data:
                                org_id = org_result.data[0]['id']
                            else:
                                # Create new organization
                                org_data = {
                                    'name': org_name
                                }
                                
                                # Try to determine org_type from name patterns
                                org_name_lower = org_name.lower()
                                if any(team in org_name_lower for team in ['vikings', 'patriots', 'cowboys', 'packers', 'eagles', 'giants', 'jets', 'bills', 'dolphins', 'steelers', 'ravens', 'browns', 'bengals', 'texans', 'colts', 'titans', 'jaguars', 'broncos', 'chiefs', 'raiders', 'chargers', '49ers', 'seahawks', 'rams', 'cardinals', 'saints', 'falcons', 'panthers', 'buccaneers', 'bears', 'lions', 'commanders']):
                                    org_data['sport'] = 'NFL'
                                    org_data['org_type'] = 'Team'
                                elif any(term in org_name_lower for term in ['university', 'college', 'school']):
                                    org_data['org_type'] = 'Education'
                                elif any(term in org_name_lower for term in ['inc', 'corp', 'llc', 'company', 'agency', 'group']):
                                    org_data['org_type'] = 'Agency'
                                
                                new_org = supabase.table('organization').insert(org_data).execute()
                                if new_org.data:
                                    org_id = new_org.data[0]['id']
                                else:
                                    continue  # Skip role creation if org creation failed
                            
                            # Create or update role
                            role_data = {
                                'person_id': person_id,
                                'org_id': org_id,
                                'job_title': job_title,
                                'start_date': datetime.now().date().isoformat()
                                # Note: end_date is NULL for current roles
                            }
                            
                            # Handle department if provided
                            dept = contact.get("department") or contact.get("dept")
                            if dept:
                                role_data['dept'] = str(dept).strip()
                            
                            # Check if similar role already exists (current role for this person at this org)
                            existing_role = supabase.table('role').select("*").eq('person_id', person_id).eq('org_id', org_id).is_('end_date', 'null').execute()
                            
                            if existing_role.data:
                                # Update existing role
                                supabase.table('role').update(role_data).eq('id', existing_role.data[0]['id']).execute()
                            else:
                                # Create new role
                                supabase.table('role').insert(role_data).execute()
                                
                        except Exception as role_error:
                            # Don't fail the whole import if role creation fails
                            errors.append(f"Role creation failed for {person_data.get('full_name', 'unknown')}: {str(role_error)}")
                
            except Exception as e:
                errors.append(f"Error importing {contact.get('name', contact.get('full_name', 'unknown'))}: {str(e)}")
        
        return {
            "imported": imported,
            "updated": updated,
            "total": len(contacts),
            "errors": errors,
            "source": source
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

@app.get("/import/history")
async def get_import_history():
    """Get import history - placeholder"""
    return [
        {
            "id": "1",
            "source": "NFL Personnel Import",
            "date": "2024-01-15",
            "imported": 2990,
            "status": "completed"
        },
        {
            "id": "2", 
            "source": "CSV Upload",
            "date": "2024-01-14",
            "imported": 25,
            "status": "completed"
        }
    ]

# Database explorer endpoints
@app.get("/person")
async def get_all_people():
    """Get all people - alias for /people"""
    return await list_people()

@app.get("/organization") 
async def get_all_organizations():
    """Get all organizations - alias for /organizations"""
    return await list_organizations()

@app.get("/news_item")
async def get_news_items():
    """Get news items"""
    try:
        result = supabase.table('news_item').select("*").limit(100).execute()
        return result.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news items: {str(e)}"
        )

# Export endpoint
@app.get("/export")
async def export_data(
    type: str = Query("all_contacts"),
    format: str = Query("csv"),
    fields: str = Query("name,linkedin_url,organization,role")
):
    """Export data - placeholder"""
    return {
        "message": "Export prepared",
        "type": type,
        "format": format,
        "fields": fields.split(","),
        "download_url": "/api/downloads/export.csv"  # Would be actual download link
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "api_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
