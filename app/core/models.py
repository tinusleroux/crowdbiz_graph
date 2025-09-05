"""
Data models for CrowdBiz Graph
Pydantic models for API and data validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
import uuid

class PersonBase(BaseModel):
    """Base person model"""
    full_name: str = Field(..., description="Full name of the person")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    job_title: Optional[str] = Field(None, description="Current job title")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()

class PersonCreate(PersonBase):
    """Person creation model"""
    pass

class PersonUpdate(BaseModel):
    """Person update model"""
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None

class PersonResponse(PersonBase):
    """Person response model"""
    id: str = Field(..., description="Unique person ID")
    organization: Optional[str] = Field(None, description="Associated organization")
    department: Optional[str] = Field(None, description="Department or division")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    """Base organization model"""
    name: str = Field(..., description="Organization name")
    league: Optional[str] = Field(None, description="Sports league (NFL, NBA, etc.)")
    city: Optional[str] = Field(None, description="City location")
    state: Optional[str] = Field(None, description="State location")
    website: Optional[str] = Field(None, description="Official website")
    
    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Organization name must be at least 2 characters')
        return v.strip()

class OrganizationCreate(OrganizationBase):
    """Organization creation model"""
    pass

class OrganizationUpdate(BaseModel):
    """Organization update model"""
    name: Optional[str] = None
    league: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    """Organization response model"""
    id: str = Field(..., description="Unique organization ID")
    established_year: Optional[int] = Field(None, description="Year established")
    venue: Optional[str] = Field(None, description="Home venue or stadium")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """Search results response model"""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    page: int = Field(1, description="Current page number")
    limit: int = Field(100, description="Results per page")
    query: str = Field(..., description="Search query used")
    search_type: str = Field("all", description="Type of search performed")

class ImportResult(BaseModel):
    """Data import result model"""
    imported: int = Field(0, description="Number of records imported")
    updated: int = Field(0, description="Number of records updated")
    skipped: int = Field(0, description="Number of records skipped")
    errors: List[str] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")
    total: int = Field(0, description="Total records processed")
    source: str = Field(..., description="Import source identifier")
    privacy_filtered_fields: List[str] = Field(default_factory=list, description="Fields filtered for privacy")

class ContactImportRequest(BaseModel):
    """Contact import request model"""
    contacts: List[Dict[str, Any]] = Field(..., description="List of contacts to import")
    source: str = Field(..., description="Source of the import data")
    
    @validator('contacts')
    def validate_contacts(cls, v):
        if not v:
            raise ValueError('At least one contact is required')
        return v

class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    total_people: int = Field(0, description="Total number of people")
    total_organizations: int = Field(0, description="Total number of organizations")
    league_breakdown: List[Dict[str, Any]] = Field(default_factory=list, description="Breakdown by league")
    top_organizations: List[Dict[str, Any]] = Field(default_factory=list, description="Top organizations")
    recent_additions: List[Dict[str, Any]] = Field(default_factory=list, description="Recently added records")

class DatabaseStats(BaseModel):
    """Database statistics model"""
    table_name: str = Field(..., description="Database table name")
    record_count: int = Field(0, description="Number of records")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    columns: List[str] = Field(default_factory=list, description="Table columns")

class HealthCheck(BaseModel):
    """API health check model"""
    status: str = Field("ok", description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    database_connected: bool = Field(False, description="Database connection status")
    version: str = Field("1.0.0", description="API version")
    uptime_seconds: Optional[float] = Field(None, description="Service uptime in seconds")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

# Utility functions for model conversion
def dict_to_person_response(data: Dict[str, Any]) -> PersonResponse:
    """Convert dictionary data to PersonResponse model"""
    # Ensure required fields have defaults
    data.setdefault('id', str(uuid.uuid4()))
    data.setdefault('created_at', datetime.now())
    data.setdefault('updated_at', datetime.now())
    
    return PersonResponse(**data)

def dict_to_organization_response(data: Dict[str, Any]) -> OrganizationResponse:
    """Convert dictionary data to OrganizationResponse model"""
    # Ensure required fields have defaults
    data.setdefault('id', str(uuid.uuid4()))
    data.setdefault('created_at', datetime.now())
    data.setdefault('updated_at', datetime.now())
    
    return OrganizationResponse(**data)

def validate_import_data(contacts: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Validate import data and return clean data plus validation errors
    Returns: (valid_contacts, validation_errors)
    """
    valid_contacts = []
    validation_errors = []
    
    for i, contact in enumerate(contacts):
        try:
            # Check for required fields
            if not contact.get('full_name'):
                validation_errors.append(f"Record {i+1}: Missing required field 'full_name'")
                continue
            
            # Validate name length
            if len(contact['full_name'].strip()) < 2:
                validation_errors.append(f"Record {i+1}: Name too short")
                continue
            
            # Clean and validate data
            cleaned_contact = {
                'full_name': contact['full_name'].strip(),
                'first_name': contact.get('first_name', '').strip() or None,
                'last_name': contact.get('last_name', '').strip() or None,
                'job_title': contact.get('job_title', '').strip() or None,
                'organization': contact.get('organization', '').strip() or None,
                'department': contact.get('department', '').strip() or None,
                'linkedin_url': contact.get('linkedin_url', '').strip() or None
            }
            
            # Validate LinkedIn URL format
            if cleaned_contact['linkedin_url']:
                if not cleaned_contact['linkedin_url'].startswith(('http://', 'https://')):
                    cleaned_contact['linkedin_url'] = f"https://{cleaned_contact['linkedin_url']}"
            
            valid_contacts.append(cleaned_contact)
            
        except Exception as e:
            validation_errors.append(f"Record {i+1}: Validation error - {str(e)}")
    
    return valid_contacts, validation_errors
