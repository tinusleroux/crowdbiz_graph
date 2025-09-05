# CrowdBiz Graph - Database Schema

## 🗄️ Schema Overview

CrowdBiz Graph uses a **privacy-first PostgreSQL schema** hosted on Supabase with three core tables and supporting audit structures.

### **Current Data Volume**
- **person**: Professional profiles across the sports industry
- **organization**: Teams, leagues, and agencies across various sports
- **role**: Professional position records tracking career progression
- **Last Updated**: September 2025

## 📊 Core Tables

### `person` Table
Professional profiles with **no PII storage**.

```sql
CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    linkedin_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Key Characteristics:**
- ✅ Professional names only
- ✅ LinkedIn profiles for networking
- ❌ No emails, phones, or addresses
- ❌ No salary or compensation data

### `organization` Table
Teams, leagues, agencies, and professional entities.

```sql
CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    league VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    organization_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Key Characteristics:**
- ✅ Public business information
- ✅ Geographic data (city/state)
- ✅ League affiliations (NFL, NBA, etc.)
- ✅ Organization types (team, agency, media)

### `role` Table
Professional position history and relationships.

```sql
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES person(id),
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    title VARCHAR(200),
    department VARCHAR(100),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Key Characteristics:**
- ✅ Professional relationships
- ✅ Career progression tracking
- ✅ Temporal data (start/end dates)
- ✅ Current position indicators

## 🔍 Database Indexes

### Performance Optimization
```sql
-- Search optimization
CREATE INDEX idx_person_name ON person(first_name, last_name);
CREATE INDEX idx_person_linkedin ON person(linkedin_url);

-- Organization lookups
CREATE INDEX idx_organization_name ON organization(name);
CREATE INDEX idx_organization_league ON organization(league);
CREATE INDEX idx_organization_location ON organization(city, state);

-- Role relationships
CREATE INDEX idx_role_person ON role(person_id);
CREATE INDEX idx_role_organization ON role(organization_id);
CREATE INDEX idx_role_current ON role(is_current) WHERE is_current = true;
CREATE INDEX idx_role_dates ON role(start_date, end_date);
```

## 🔒 Privacy & Security Features

### Data Protection Measures
1. **No PII Fields**: Schema designed without sensitive data fields
2. **Professional Only**: Only business-relevant information stored
3. **Audit Logging**: All modifications tracked through triggers
4. **Access Control**: Row-level security policies enforced

### Privacy Filtering Pipeline
```python
# Automatic filtering in app/core/privacy.py
SENSITIVE_COLUMNS = [
    'email', 'phone', 'address', 'salary',
    'personal_email', 'mobile', 'home_phone'
]

def sanitize_data_for_storage(data):
    """Remove all PII before database storage"""
    return {k: v for k, v in data.items() 
            if k.lower() not in SENSITIVE_COLUMNS}
```

## 📈 Query Patterns

### Common Search Queries
```sql
-- Find people by name
SELECT p.first_name, p.last_name, r.title, o.name as organization
FROM person p
JOIN role r ON p.id = r.person_id
JOIN organization o ON r.organization_id = o.id
WHERE p.first_name ILIKE '%John%' 
  AND r.is_current = true;

-- Organizations by league
SELECT name, city, state, COUNT(r.id) as staff_count
FROM organization o
LEFT JOIN role r ON o.id = r.organization_id AND r.is_current = true
WHERE league = 'NFL'
GROUP BY o.id, name, city, state;

-- Career progression
SELECT p.first_name, p.last_name, r.title, o.name, 
       r.start_date, r.end_date, r.is_current
FROM person p
JOIN role r ON p.id = r.person_id
JOIN organization o ON r.organization_id = o.id
WHERE p.id = $1
ORDER BY r.start_date DESC;
```

## 🔄 Data Import Process

### CSV Import Pipeline
1. **Upload**: CSV files processed through `ImportService`
2. **Privacy Filter**: Sensitive columns automatically removed
3. **Validation**: Data integrity and format checks
4. **Deduplication**: Prevent duplicate entries
5. **Storage**: Insert into appropriate tables
6. **Audit**: Log all import operations

### Supported Import Formats
- **People**: `first_name`, `last_name`, `linkedin_url`, `title`, `organization`
- **Organizations**: `name`, `league`, `city`, `state`, `type`
- **Roles**: `person_name`, `title`, `organization_name`, `start_date`, `is_current`

## ⚠️ Schema Constraints & Rules

### Business Rules
1. **Person names required**: `first_name` and `last_name` cannot be null
2. **Organization names unique**: Within same league/location
3. **Role relationships**: Must reference valid person and organization
4. **Date consistency**: `end_date` must be after `start_date`
5. **Current roles**: Only one current role per person per organization

### Data Integrity
```sql
-- Ensure role dates make sense
ALTER TABLE role ADD CONSTRAINT check_role_dates 
CHECK (end_date IS NULL OR end_date >= start_date);

-- LinkedIn URL format validation
ALTER TABLE person ADD CONSTRAINT check_linkedin_format
CHECK (linkedin_url IS NULL OR linkedin_url LIKE 'https://linkedin.com/%');
```

## 🛠️ Database Access Patterns

### Application Layer
- **Direct Access**: `DatabaseManager` in `app/core/database.py`
- **Service Layer**: Business logic in `app/services/`
- **Privacy Layer**: All queries filtered through `app/core/privacy.py`
- **Caching**: Streamlit `@st.cache_data` for performance

### Connection Management
```python
# Supabase client configuration
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"

# Direct query execution
def safe_query(sql, params=None):
    """Execute query with error handling and logging"""
    # Implementation in app/core/database.py
```

## 📊 Analytics & Reporting

### Dashboard Metrics
- Total professionals by organization type
- Geographic distribution of organizations
- Career progression patterns
- Role distribution across leagues
- Recent activity and growth trends

### Performance Monitoring
- Query execution times
- Database connection health
- Import success rates
- Search response times

---

**Schema Version**: 1.0 (Post-Migration)  
**Last Migration**: June 2025  
**Next Review**: December 2025

For development questions, see [Architecture Overview](overview.md) or [AI Development Guide](../../.github/copilot-instructions.md).
