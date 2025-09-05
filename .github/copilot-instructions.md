# GitHub Copilot Instructions for CrowdBiz Graph

## Project Overview
CrowdBiz Graph is a **privacy-first sports industry professional network** built with Streamlit and Supabase. It maps NFL professionals across teams without storing private contact data (no emails, phones, addresses).

## Critical Architecture Decisions

### Streamlit-First Design
- **Direct UI**: This is a Streamlit app, not React/Next.js - use Streamlit components and patterns
- **Session State**: Leverage `st.session_state` for user state, keep it minimal
- **Caching**: Use `@st.cache_data` and `@st.cache_resource` for performance

### Privacy-by-Design
- **Zero PII Storage**: Never store email, phone, address, salary in database or code
- **Filter Everything**: All data flows through `app/core/privacy.py` sanitization
- **Professional Only**: Only public professional data (names, titles, organizations, LinkedIn URLs)

### Direct Database Pattern
- **Supabase Direct**: Use Supabase client directly via `app/core/database.py`, not complex API layers
- **Service Layer**: Business logic in `app/services/`, not in UI components
- **Models**: Pydantic models in `app/core/models.py` for type safety

## Essential File Structure
```
app/core/          # Data models, database, privacy filtering (NO UI code)
app/services/      # Business services: import, search, analytics
app/ui/            # Streamlit pages and components (NO business logic)  
app/api/           # Optional FastAPI endpoints (minimal usage)
dev_workspace/     # AI experimentation (gitignored)
```

## Key Business Logic

### CSV Import Pipeline
1. `app/services/import_service.py` - Main import logic
2. `app/core/privacy.py` - Strips sensitive columns automatically
3. Pattern: CSV → privacy filter → validate → database → audit log

### Search Architecture  
- `app/services/search_service.py` handles all search operations
- Searches across people (by name, title) and organizations (by name, league, city)
- Always sanitizes results before display via `sanitize_data_for_display()`

### Database Schema (Supabase)
- `people`: Professional profiles (name, title, linkedin_url) 
- `organizations`: Teams, leagues, agencies (name, league, city, state)
- `roles`: Professional position history with temporal tracking
- **Key**: No private data fields exist in schema

## Development Workflow

### Before Changes
1. Check `.ai_reference/ai_constraints/PRIVACY_RULES.md` and `ARCHITECTURE_RULES.md`
2. Experiment in `dev_workspace/experiments/` first
3. Run: `python .ai_checks/check_privacy_compliance.py`

### Making Changes
- **UI Changes**: Modify `app/ui/pages/` or `app/ui/components/`
- **Business Logic**: Add to `app/core/` or `app/services/`
- **Database**: Use `app/core/database.py` methods only
- **Testing**: `python run.py checks` validates everything

## Common Patterns

### Streamlit Caching
```python
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

@st.cache_data(ttl=300)  # 5 minutes
def search_people(query: str):
    return db.search_people(query)
```

### Privacy Filtering
```python
# Always filter before storage
from app.core.privacy import sanitize_data_for_storage
clean_data = sanitize_data_for_storage(raw_data)

# Always sanitize before display  
from app.core.privacy import sanitize_data_for_display
safe_data = sanitize_data_for_display(db_data)
```

### Service Usage
```python
# Import CSV
from app.services.import_service import get_import_service
result = get_import_service().import_csv_file(file_content, filename)

# Search operations
from app.services.search_service import get_search_service  
results = get_search_service().search_all(query, limit=100)
```

## Anti-Patterns to Avoid
- ❌ Database queries in UI components - use services layer
- ❌ Streamlit code in core/services - keep UI separate  
- ❌ Bypassing privacy filters anywhere in codebase
- ❌ Creating React-like patterns - embrace Streamlit paradigms
- ❌ Storing any PII data - violates core architecture principle

## Entry Points
- `python run.py streamlit` - Start main application
- `python run.py checks` - Run all validation including privacy compliance
- `app/main.py` - Main Streamlit application entry point
- `app/core/database.py` - Single source for all database operations

## Performance Considerations
- Use Streamlit caching for database calls and expensive computations
- Paginate large result sets (default: 100 records)
- Database queries go through `DatabaseManager.safe_query()` with error handling
- CSV imports process in batches via `ImportService`

This codebase prioritizes simplicity, privacy compliance, and Streamlit-native patterns. When in doubt, choose the more privacy-protective option and follow existing service layer patterns rather than creating new architectural approaches.
