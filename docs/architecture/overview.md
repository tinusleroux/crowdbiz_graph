# System Architecture Overview

## 🏗️ Architecture Principles

CrowdBiz Graph follows a **Streamlit-first, privacy-by-design** architecture optimized for AI development and rapid iteration.

### **Core Design Decisions**

1. **Streamlit-Native**: Direct UI development without React complexity
2. **Privacy-First**: Zero PII storage with automatic filtering
3. **Direct Database**: Supabase client without complex API layers
4. **Service-Oriented**: Clean separation between UI and business logic
5. **AI-Optimized**: Extensive documentation for coding agent productivity

## 📁 Modular Structure

```
app/
├── core/           # Foundation layer (NO UI code)
│   ├── config.py      # Environment and settings
│   ├── database.py    # Supabase client and queries
│   ├── models.py      # Pydantic data models
│   ├── privacy.py     # PII filtering and sanitization
│   └── logger.py      # Centralized logging
│
├── services/       # Business logic layer (NO UI code)
│   ├── import_service.py    # CSV import and validation
│   ├── search_service.py    # Search and discovery
│   └── analytics_service.py # Dashboard and insights
│
├── ui/            # Presentation layer (ONLY UI code)
│   ├── pages/         # Streamlit page modules
│   └── components/    # Reusable UI components
│
├── api/           # Optional FastAPI endpoints
│   └── main.py        # REST API for external access
│
└── main.py        # Streamlit application entry point
```

## 🔄 Data Flow Architecture

### **Import Pipeline**
```
CSV Upload → Privacy Filter → Validation → Database → Audit Log
     ↓             ↓            ↓          ↓         ↓
[Streamlit]  [privacy.py] [ImportService] [Supabase] [Logger]
```

### **Search Pipeline**
```
User Query → Service Layer → Database Query → Privacy Filter → UI Display
     ↓           ↓              ↓              ↓            ↓
[Streamlit]  [SearchService]  [DatabaseManager] [privacy.py] [Streamlit]
```

### **Analytics Pipeline**
```
Dashboard Request → Analytics Service → Cached Queries → Data Visualization
        ↓               ↓                  ↓              ↓
   [Streamlit]    [AnalyticsService]   [DatabaseManager] [Streamlit Charts]
```

## 💾 Database Architecture

### **Supabase PostgreSQL**
- **Direct Connection**: REST API and direct PostgreSQL access
- **Schema**: Three core tables (person, organization, role)
- **Security**: Row-level security and API key authentication
- **Performance**: Indexed searches and query optimization

### **Privacy-First Schema**
```sql
-- NO PII fields in any table
person: [id, first_name, last_name, linkedin_url]
organization: [id, name, league, city, state, type]
role: [id, person_id, organization_id, title, dates]
```

## 🧩 Service Layer Patterns

### **Import Service**
```python
class ImportService:
    def import_csv_file(self, content, filename):
        # 1. Parse CSV data
        # 2. Apply privacy filters
        # 3. Validate data integrity
        # 4. Insert into database
        # 5. Generate audit logs
        return ImportResult(...)
```

### **Search Service**
```python
class SearchService:
    def search_all(self, query, limit=100):
        # 1. Sanitize search query
        # 2. Execute parallel searches (people + organizations)
        # 3. Filter results for display
        # 4. Return consolidated results
        return SearchResults(...)
```

### **Analytics Service**
```python
class AnalyticsService:
    def get_dashboard_stats(self):
        # 1. Execute cached database queries
        # 2. Calculate derived metrics
        # 3. Format for visualization
        return DashboardStats(...)
```

## 🎨 Streamlit UI Patterns

### **Page Structure**
```python
# Standard page pattern
def render_page():
    st.title("Page Title")
    
    # Sidebar navigation
    with st.sidebar:
        render_filters()
    
    # Main content
    with st.container():
        data = get_cached_data()
        display_results(data)
    
    # Footer actions
    render_page_actions()
```

### **Caching Strategy**
```python
@st.cache_resource
def get_database_manager():
    """Singleton database connection"""
    return DatabaseManager()

@st.cache_data(ttl=300)  # 5 minute cache
def search_people(query: str):
    """Cache search results"""
    return get_search_service().search_people(query)
```

### **Session State Management**
```python
# Minimal session state usage
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

if 'last_import' not in st.session_state:
    st.session_state.last_import = None
```

## 🔒 Privacy Architecture

### **Automatic PII Filtering**
```python
# All data flows through privacy filters
SENSITIVE_COLUMNS = [
    'email', 'phone', 'address', 'salary',
    'personal_email', 'mobile', 'home_phone'
]

def sanitize_data_for_storage(data):
    """Remove PII before database"""
    return filter_sensitive_data(data)

def sanitize_data_for_display(data):
    """Ensure display safety"""
    return ensure_no_pii_exposure(data)
```

### **Privacy Checkpoints**
1. **Import**: CSV columns filtered before processing
2. **Storage**: Database schema has no PII fields
3. **Query**: All results filtered before display
4. **Export**: Any data export goes through sanitization
5. **API**: External endpoints apply same privacy filters

## ⚡ Performance Architecture

### **Database Performance**
- **Indexing**: Strategic indexes on search and join columns
- **Query Optimization**: Efficient JOIN patterns and WHERE clauses
- **Connection Pooling**: Supabase handles connection management
- **Caching**: Application-level caching via Streamlit

### **Application Performance**
- **Lazy Loading**: Data loaded on-demand per page
- **Result Pagination**: Default 100-record limits
- **Background Processing**: Long imports handled asynchronously
- **Memory Management**: Minimal session state usage

### **Caching Layers**
```python
# Resource-level (persistent)
@st.cache_resource
def get_services():
    return initialize_services()

# Data-level (TTL-based)
@st.cache_data(ttl=300)
def get_analytics():
    return compute_dashboard_metrics()

# Query-level (parameter-based)
@st.cache_data
def search_by_params(query, filters):
    return execute_search(query, filters)
```

## 🔧 Development Architecture

### **AI-First Development**
- **Comprehensive Docs**: Extensive `.md` files for AI agents
- **Clear Patterns**: Consistent code structure and conventions
- **Privacy Rules**: Non-negotiable constraints in `.ai_constraints/`
- **Architecture Rules**: System integrity guidelines

### **Modular Development**
```python
# Clear separation of concerns
app/core/     # Data models, database, privacy (foundation)
app/services/ # Business logic (application layer)
app/ui/       # Streamlit components (presentation layer)
```

### **Testing Strategy**
```python
tests/
├── core/         # Test data models, database, privacy
├── services/     # Test business logic
└── ui/          # Test UI components and pages
```

## 🚀 Deployment Architecture

### **Production Stack**
- **Application**: Streamlit Cloud or Docker container
- **Database**: Supabase (managed PostgreSQL)
- **Monitoring**: Application logs and Supabase metrics
- **Security**: Environment variables and API key management

### **Development Stack**
- **Local**: Python virtual environment + local Streamlit
- **Database**: Direct Supabase connection (same as production)
- **Testing**: Pytest with database fixtures
- **AI Development**: Comprehensive documentation system

## 🔍 Monitoring Architecture

### **Application Monitoring**
- **Logging**: Structured logs in `logs/` directory
- **Performance**: Query timing and response metrics
- **Usage**: Page views and feature utilization
- **Errors**: Exception tracking and debugging

### **Database Monitoring**
- **Supabase Dashboard**: Built-in performance metrics
- **Query Analysis**: Slow query identification
- **Connection Health**: Database connectivity status
- **Data Integrity**: Automated consistency checks

## 📊 Scalability Considerations

### **Current Scale**
- **Data**: Professional network with comprehensive organizational coverage
- **Performance**: Sub-second search responses
- **Concurrent Users**: Designed for 10-50 simultaneous users
- **Storage**: Minimal storage footprint due to no PII

### **Growth Planning**
- **Horizontal**: Additional organizations and leagues
- **Vertical**: Enhanced analytics and reporting
- **Performance**: Database indexing and query optimization
- **Features**: Advanced search and relationship mapping

---

**Architecture Version**: 1.0 (Streamlit-First)  
**Last Review**: September 2025  
**Next Evolution**: Advanced relationship analytics

For detailed implementation guidance, see [AI Development Guide](../../.github/copilot-instructions.md) or [Database Schema](database-schema.md).
