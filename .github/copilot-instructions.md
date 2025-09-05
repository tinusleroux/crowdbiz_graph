````instructions
# GitHub Copilot Instructions for CrowdBiz Graph

## 🎯 Project Mission
CrowdBiz Graph is a **privacy-first sports industry professional network** that maps NFL professionals across teams without storing private contact data. We connect professionals through public information only - no emails, phones, or addresses ever stored.

**Core Purpose**: Enable meaningful professional connections while respecting privacy completely.

## 🚨 CRITICAL PRIVACY RULES - NEVER VIOLATE

### ❌ Forbidden Data (Zero Tolerance)
- **NEVER store**: email, phone, address, salary, personal_notes, private_contact_info
- **NEVER accept**: private contact information during imports
- **NEVER create**: database fields that could store private data  
- **NEVER display**: private information even if it exists in source data
- **NEVER bypass**: privacy filtering anywhere in the codebase

### ✅ Allowed Professional Data Only
- Names, titles, organizations, industry roles
- Professional work history and achievements
- Public social media profiles (LinkedIn URLs)
- Professional skills and expertise areas
- Team affiliations and professional networks

### 🛡️ Required Privacy Patterns
```python
# ALWAYS filter before storage
from app.core.privacy import sanitize_data_for_storage
clean_data = sanitize_data_for_storage(raw_data)

# ALWAYS sanitize before display
from app.core.privacy import sanitize_data_for_display
safe_data = sanitize_data_for_display(db_data)
```

## 🏗️ Critical Architecture Rules

### Streamlit-First Design (NOT React)
- **Direct UI**: This is a Streamlit app - use Streamlit components and patterns
- **Session State**: Leverage `st.session_state` for user state, keep it minimal
- **Caching**: Use `@st.cache_data` and `@st.cache_resource` for performance
- **Native Patterns**: Embrace Streamlit paradigms, don't recreate React patterns

### Mandatory Folder Structure
```
app/core/          # Business logic, models, database (NO UI code here)
app/services/      # Business services: import, search, analytics (NO UI code)
app/ui/            # Streamlit pages and components (NO business logic here)
app/api/           # Optional FastAPI endpoints (minimal usage)
dev_workspace/     # Your experimentation space (gitignored)
```

### Direct Database Pattern
- **Supabase Direct**: Use Supabase client directly via `app/core/database.py`
- **No API Layers**: Avoid unnecessary complexity for simple CRUD operations  
- **Service Layer**: All business logic in `app/services/`, not in UI components
- **Type Safety**: Use Pydantic models in `app/core/models.py`

## 🔄 Development Workflow & Patterns

### Before Making Any Changes
1. **Privacy Check**: Ensure no private data will be stored or displayed
2. **Architecture Check**: Verify changes follow folder structure rules
3. **Experiment First**: Use `dev_workspace/experiments/` for trying new approaches
4. **Run Validation**: `python .ai_checks/check_privacy_compliance.py`

### Required Data Flows

**CSV Import Pipeline:**
```
CSV → app/services/import_service.py → privacy filter → validate → database → audit log
```

**Search & Display Pipeline:**  
```
User query → app/services/search_service.py → database → sanitize → UI components
```

**All data MUST flow through privacy filtering at every stage**

### Database Schema (Supabase)
- **people**: Professional profiles (name, title, linkedin_url, no private data)
- **organizations**: Teams, leagues, agencies (name, league, city, state)  
- **roles**: Professional position history with temporal tracking
- **Critical**: No private data fields exist anywhere in schema

## 💻 Essential Code Patterns

### Streamlit Caching (Required for Performance)
```python
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

@st.cache_data(ttl=300)  # 5 minutes for dynamic data
def search_people(query: str):
    return get_search_service().search_people(query)
```

### Service Layer Usage (Required Pattern)
```python
# CSV Import
from app.services.import_service import get_import_service
result = get_import_service().import_csv_file(file_content, filename)

# Search Operations  
from app.services.search_service import get_search_service
results = get_search_service().search_all(query, limit=100)

# Analytics
from app.services.analytics_service import get_analytics_service
stats = get_analytics_service().get_dashboard_stats()
```

### UI Component Structure (Required Pattern)
```python
import streamlit as st
from app.services.search_service import get_search_service
from app.core.privacy import sanitize_data_for_display

def render_search_page():
    st.title("Professional Search")
    
    query = st.text_input("Search professionals...")
    if query:
        # Use service layer for business logic
        results = get_search_service().search_people(query)
        # Always sanitize before display
        safe_results = sanitize_data_for_display(results)
        
        for person in safe_results:
            st.write(f"{person.name} - {person.title}")
```

## ⚠️ Critical Anti-Patterns (NEVER DO)

### Code Organization Violations
- ❌ Database queries directly in UI components (use services layer)
- ❌ Streamlit code in `app/core/` or `app/services/` (keep UI separate)
- ❌ Business logic in UI files (belongs in core/services)
- ❌ Bypassing the established folder structure

### Privacy Violations  
- ❌ Storing any PII data (violates core architecture principle)
- ❌ Bypassing privacy filters anywhere in codebase
- ❌ Creating database fields for private information
- ❌ Displaying unfiltered data from database

### Streamlit Anti-Patterns
- ❌ Creating React-like patterns in Streamlit
- ❌ Ignoring Streamlit caching opportunities
- ❌ Complex state management (keep it simple)
- ❌ Heavy computations in UI refresh cycles

## 🎯 Target Users & Use Cases

### Primary Users
- **Sports Industry Professionals**: Mapping their professional networks
- **Recruiters & Talent Scouts**: Finding talent and connections
- **Journalists & Analysts**: Researching industry movements
- **Business Development**: Identifying decision-makers and opportunities

### Core Use Cases
1. **Professional Discovery**: Find people by name, role, team, organization
2. **Network Mapping**: Understand professional relationships and hierarchies
3. **Industry Intelligence**: Track professional movements and trends
4. **Talent Research**: Identify professionals with specific experience
5. **Data Analytics**: Generate insights about sports industry networks

## 🚀 Essential Commands & Validation

### Development Commands
```bash
# Start application
python run.py streamlit

# Run all validation checks
python run.py checks

# Privacy compliance validation (run before any changes)
python .ai_checks/check_privacy_compliance.py
```

### Entry Points
- `app/main.py` - Main Streamlit application entry point
- `app/core/database.py` - Single source for all database operations
- `app/core/privacy.py` - All privacy filtering and sanitization
- `dev_workspace/` - Your experimentation and debugging space

## 🔍 Current System Status

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Database**: Supabase (PostgreSQL with real-time features)
- **Data Processing**: pandas, custom privacy filtering
- **Visualization**: Streamlit native components, plotly for charts

### Data Coverage
- NFL professional network with comprehensive coverage
- Professional profiles across teams, leagues, and organizations
- Role history and career progression tracking
- Zero private data storage (privacy-compliant architecture)

### Performance Considerations
- Use Streamlit caching for database calls and expensive computations
- Paginate large result sets (default: 100 records)
- Database queries go through `DatabaseManager.safe_query()` with error handling
- CSV imports process in batches via `ImportService`

## 💡 Success Principles

**When in doubt:**
1. **Choose privacy-protective option** - err on the side of privacy
2. **Follow existing service layer patterns** - don't create new architecture  
3. **Keep it simple** - Streamlit works best with simple, direct patterns
4. **Test privacy compliance** - validate before committing any changes

This codebase prioritizes **simplicity**, **privacy compliance**, and **Streamlit-native patterns** above all else. The goal is professional networking without compromising personal privacy.

````
