````instructions
# GitHub Copilot Instructions for CrowdBiz Graph

## 🎯 Project Overview
CrowdBiz Graph is a **Streamlit application** that maps NFL professionals across teams and organizations. Built with **Supabase PostgreSQL** for data persistence and **privacy-filtered imports** for data quality.

## 🔧 Technical Architecture

### Core Stack
- **Frontend**: Streamlit (Python web framework)
- **Database**: Supabase (PostgreSQL with REST API)
- **Data Processing**: pandas, privacy filtering
- **Authentication**: Supabase Auth (optional)

### Folder Structure
```
app/core/          # Database, models, config, privacy (NO UI code)
app/services/      # Business logic: import, search, analytics
app/ui/            # Streamlit pages and components  
app/api/           # Optional FastAPI endpoints
dev_workspace/     # Experimentation space (gitignored)
```

## 🏗️ Database Connection & Schema

### Supabase Credentials Setup
```python
# Located in app/core/config.py
# Environment variables needed:
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_API_KEY=your-anon-public-key
SUPABASE_PERSONAL_ACCESS_TOKEN=optional-for-admin
SUPABASE_DATABASE_PASSWORD=optional-for-direct-sql
```

### Core Database Schema
```sql
-- Primary tables
person (id, full_name, first_name, last_name, linkedin_url, created_at, updated_at)
organization (id, name, org_type, sport, parent_org_id) 
role (id, person_id, org_id, job_title, start_date, end_date, source_id, is_current, is_executive)
source (id, url, license, confidence, fetched_at, checksum_sha256)
job_title_departments (id, job_title, standardized_department, created_at, updated_at)

-- Summary tables for performance
network_status (person_id, full_name, current_job_title, current_organization, current_org_type, etc.)
organization_summary (org_id, name, org_type, sport, current_employees, executive_count, etc.)
```

### Department Classification System
```python
# Job Title → Department Lookup (CORRECT APPROACH)
def get_department_for_job_title(job_title: str) -> str:
    result = db.client.table('job_title_departments')\
        .select('standardized_department')\
        .eq('job_title', job_title)\
        .single().execute()
    return result.data['standardized_department'] if result.data else 'Other'

# 9 Standard Departments:
# - Sales & Partnerships (262 job titles)
# - Marketing & Communications (185 job titles)  
# - Other (112 job titles)
# - Technology & Analytics (50 job titles)
# - Stadium Operations & Facilities (35 job titles)
# - Finance & Administration (27 job titles)
# - Executive Leadership (20 job titles)
# - Fan Experience & Events (19 job titles)
# - Broadcasting & Media (7 job titles)
# - Ticketing & Operations (5 job titles)
```

### Database Connection Pattern
```python
from app.core.database import get_database_manager

@st.cache_resource  # Cache database connection
def get_db():
    return get_database_manager()

# Usage in functions
db = get_db()
results = db.safe_query("person", "select", 
                       filters={"full_name": search_term},
                       limit=100)

# Department lookup pattern
@st.cache_data(ttl=600)
def get_department_for_job_title(job_title: str) -> str:
    db = get_database_manager()
    result = db.client.table('job_title_departments')\
        .select('standardized_department')\
        .eq('job_title', job_title).single().execute()
    return result.data['standardized_department'] if result.data else 'Other'
```

## 💾 Data Quality & Integrity

### Historical Data Preservation
```python
# Roles table maintains history - never delete, only close
def update_person_role(person_id, org_id, new_title):
    # Close current role
    db.safe_query("role", "update", 
                  data={"end_date": datetime.now().date()},
                  filters={"person_id": person_id, "org_id": org_id, "end_date": None})
    
    # Create new role entry
    db.safe_query("role", "insert", 
                  data={"person_id": person_id, "org_id": org_id, 
                        "job_title": new_title, "start_date": datetime.now().date()})
```

### Data Validation Patterns
```python
# Always validate before insert/update
from app.core.models import validate_import_data

def import_csv_data(records):
    # Clean and validate
    valid_records, errors = validate_import_data(records)
    
    # Use unique constraints to prevent duplicates
    for record in valid_records:
        # Upsert pattern - update if exists, insert if new
        existing = db.safe_query("person", "select", 
                                filters={"email": record.get("email")})
        
        if existing:
            db.safe_query("person", "update", 
                         data=record, filters={"id": existing[0]["id"]})
        else:
            db.safe_query("person", "insert", data=record)
```

## 🔍 Search & Query Patterns

### Efficient Search Implementation
```python
@st.cache_data(ttl=300)  # Cache search results for 5 minutes
def search_professionals(query: str, limit: int = 100):
    # Use text search index
    return db.safe_query("person", "select",
                        filters={"full_name": query},
                        limit=limit,
                        order_by="full_name")

# Join queries for relationships
def get_person_with_roles(person_id: str):
    # Use service layer for complex queries
    from app.services.search_service import get_search_service
    return get_search_service().get_person_details(person_id)
```

## 📊 Streamlit Performance Optimization

### Required Caching Patterns
```python
@st.cache_resource  # For connections, singletons
def get_database_manager():
    return DatabaseManager()

@st.cache_data(ttl=600)  # For data that changes slowly
def get_dashboard_stats():
    return {
        "total_people": db.safe_query("person", "count"),
        "total_orgs": db.safe_query("organization", "count")
    }

@st.cache_data(ttl=60)   # For frequently changing data
def get_recent_imports():
    return db.safe_query("source", "select", limit=10, order_by="fetched_at desc")
```

### Session State Management
```python
# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
    
# Update state efficiently
if st.button("Search"):
    st.session_state.search_results = search_professionals(query)
    st.rerun()  # Trigger re-render
```

## 🔄 CSV Import & Data Processing

### Service Layer Pattern
```python
from app.services.import_service import get_import_service

def handle_file_upload(uploaded_file):
    if uploaded_file:
        # Use service layer for business logic
        result = get_import_service().import_csv_file(
            uploaded_file.getvalue(), 
            uploaded_file.name
        )
        
        # Display results in UI
        st.success(f"Imported {result.imported_count} records")
        if result.errors:
            st.error(f"Errors: {result.errors}")
```

### Data Pipeline Flow
```
1. CSV Upload → pandas DataFrame
2. Privacy Filter → Remove sensitive columns automatically  
3. Data Validation → Check required fields, formats
4. Deduplication → Use unique constraints (email, linkedin_url)
5. Historical Updates → Close old roles, create new ones
6. Database Insert → Batch processing for performance
7. Audit Logging → Track source and import metadata
```

## 🏃‍♂️ Common Development Tasks

### Adding New Search Features
1. Add method to `app/services/search_service.py`
2. Add caching with appropriate TTL
3. Create UI component in `app/ui/components/`
4. Use component in page in `app/ui/pages/`

### Database Schema Changes
1. Create migration in `supabase/migrations/`
2. Update models in `app/core/models.py`
3. Update service methods that use affected tables
4. Test with existing data

### Performance Debugging
```python
# Check query performance
import time
start = time.time()
results = db.safe_query("person", "select", limit=1000)
logger.info(f"Query took {time.time() - start:.2f}s")

# Monitor Streamlit performance
with st.spinner("Loading data..."):
    data = expensive_operation()
```

## 🚀 Essential Commands

```bash
# Start application
python run.py streamlit

# Run validation checks  
python run.py checks

# Database migrations (if using Supabase CLI)
supabase db push

# Environment setup
cp .env.example .env  # Add your Supabase credentials
```

## 🎯 Key Success Patterns

1. **Use Service Layer**: Keep business logic in `app/services/`, not UI components
2. **Cache Aggressively**: Use `@st.cache_data` and `@st.cache_resource` everywhere
3. **Preserve History**: Never delete roles, always create new records with timestamps  
4. **Validate Data**: Use unique constraints and validation before database operations
5. **Handle Errors Gracefully**: Use `db.safe_query()` pattern for error handling

The system is optimized for **data quality**, **historical preservation**, and **Streamlit performance**. Focus on practical implementation over theoretical architecture.

````

````
