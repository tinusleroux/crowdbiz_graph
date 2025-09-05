# CrowdBiz Graph - Updated Database Schema

## 🎯 Schema Overview
This document reflects the **actual production schema** discovered during system analysis (Sep 2025). The schema is richer than originally documented, with additional fields that enhance the product's functionality.

## 📊 Core Tables

### `person` Table
**Purpose**: Professional individuals in the sports industry network

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `id` | UUID | Primary key | ✅ Core |
| `full_name` | TEXT | Complete name | ✅ Core |
| `first_name` | TEXT | First name | ✅ Core |
| `last_name` | TEXT | Last name | ✅ Core |
| `email` | TEXT | Email address | ⚠️ **Privacy Filtered** |
| `linkedin_url` | TEXT | LinkedIn profile URL | ✅ Core |
| `embedding` | VECTOR | Semantic search embeddings | 🚀 **AI Feature** |
| `twitter_url` | TEXT | Twitter profile URL | 🆕 **Discovery** |
| `company_domain` | TEXT | Associated company domain | 🆕 **Discovery** |
| `tags` | TEXT[] | Classification tags | 🆕 **Discovery** |
| `created_at` | TIMESTAMP | Record creation time | ✅ Core |
| `updated_at` | TIMESTAMP | Last modification time | ✅ Core |

**Record Count**: 2,991 people

### `organization` Table  
**Purpose**: Teams, leagues, companies in sports industry

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `id` | UUID | Primary key | ✅ Core |
| `name` | TEXT | Organization name | ✅ Core |
| `org_type` | TEXT | Type (Team, League, etc.) | ✅ Core |
| `sport` | TEXT | Associated sport | ✅ Core |
| `parent_org_id` | UUID | Parent organization | ✅ Core |
| `industry` | TEXT | Industry classification | 🆕 **Discovery** |
| `is_active` | BOOLEAN | Active status flag | 🆕 **Discovery** |

**Record Count**: 363 organizations

### `role` Table
**Purpose**: Professional relationships and positions (with full history)

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `id` | UUID | Primary key | ✅ Core |
| `person_id` | UUID | Foreign key to person | ✅ Core |
| `org_id` | UUID | Foreign key to organization | ✅ Core |
| `job_title` | TEXT | Position title | ✅ Core |
| `start_date` | DATE | Role start date | ✅ Core |
| `end_date` | DATE | Role end date (null = current) | ✅ Core |
| `source_id` | UUID | Data source reference | ✅ Core |
| `ingested_at` | TIMESTAMP | Data ingestion time | 🆕 **Discovery** |
| `reports_to_role_id` | UUID | Reporting relationship | 🆕 **Discovery** |
| `is_executive` | BOOLEAN | Executive level indicator | 🚀 **Key Feature** |
| `is_current` | BOOLEAN | Current role flag | 🚀 **Key Feature** |

**Record Count**: 3,030 roles (3,030 current roles)

**Note**: Department classification is derived from `job_title` via the `job_title_departments` lookup table, not stored in this table.

### `job_title_departments` Table  
**Purpose**: Job title to department classification lookup table

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `id` | UUID | Primary key | ✅ Core |
| `job_title` | TEXT | Exact job title (unique) | ✅ Core |
| `standardized_department` | TEXT | Department category | ✅ Core |
| `created_at` | TIMESTAMP | Record creation time | ✅ Core |
| `updated_at` | TIMESTAMP | Last modification time | ✅ Core |

**Record Count**: 722 unique job titles  
**Purpose**: Maps job titles to 9 standardized departments

**Department Categories**:
- Sales & Partnerships (262 job titles)
- Marketing & Communications (185 job titles)
- Other (112 job titles)
- Technology & Analytics (50 job titles)
- Stadium Operations & Facilities (35 job titles)
- Finance & Administration (27 job titles)
- Executive Leadership (20 job titles)  
- Fan Experience & Events (19 job titles)
- Broadcasting & Media (7 job titles)
- Ticketing & Operations (5 job titles)

### `source` Table
**Purpose**: Data provenance and audit trail

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `id` | UUID | Primary key | ✅ Core |
| `url` | TEXT | Source URL | ✅ Core |
| `license` | TEXT | License information | ✅ Core |
| `confidence` | DECIMAL | Data confidence score | ✅ Core |
| `fetched_at` | TIMESTAMP | Data fetch time | ✅ Core |
| `checksum_sha256` | TEXT | Data integrity hash | ✅ Core |
| `raw_blob_path` | TEXT | Raw data storage path | 🆕 **Discovery** |

## 🔗 Key Relationships

### Primary Connections
```sql
person ←→ role ←→ organization
   ↑         ↓         
   └── source ←┘       
                      
job_title_departments (lookup)
   ↑
   └── role.job_title
```

### Department Lookup Pattern (Recommended)
```sql
-- Get current roles with departments via lookup
SELECT 
    p.full_name, 
    r.job_title, 
    o.name as organization,
    COALESCE(jtd.standardized_department, 'Other') as department
FROM person p
JOIN role r ON p.id = r.person_id 
JOIN organization o ON r.org_id = o.id
LEFT JOIN job_title_departments jtd ON r.job_title = jtd.job_title
WHERE r.is_current = true;
```

### Legacy Current Role Query Pattern (Deprecated)
```sql
-- Old approach: Using end_date (less reliable)
SELECT p.full_name, r.job_title, o.name as organization  
FROM person p
JOIN role r ON p.id = r.person_id
JOIN organization o ON r.org_id = o.id
WHERE r.end_date IS NULL;
```

## 🔍 Materialized Views

### `v_role_current` View
**Purpose**: Pre-computed current role relationships  
**Status**: ⚠️ **Empty (0 rows)** - needs refresh or is deprecated  
**Recommendation**: Use `role.is_current = true` directly instead

**Expected Structure**:
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Role ID |
| `person_id` | UUID | Person reference |
| `org_id` | UUID | Organization reference |
| `job_title` | TEXT | Position title |
| `dept` | TEXT | Department |
| `start_date` | DATE | Role start date |

## 🚀 Key Schema Insights

### 1. **Job Title → Department Classification Architecture**
- `job_title_departments` lookup table contains 722 unique job title mappings
- Department classification is derived, not stored redundantly
- Consistent classification: same job title always maps to same department
- 9 standardized department categories cover the sports industry spectrum

### 2. **Rich Executive Data**
- `role.is_executive` enables leadership analysis
- Executive counts per organization
- Leadership transition tracking

### 3. **Enhanced Current Role Detection**
- `role.is_current` is more reliable than `end_date IS NULL`
- Enables efficient current relationship queries
- Supports real-time role updates

### 4. **AI-Ready Architecture**  
- `person.embedding` enables semantic search
- Vector similarity matching for professional connections
- Supports recommendation engines

### 5. **Comprehensive Reporting Structure**
- `role.reports_to_role_id` enables org chart visualization
- Hierarchical relationship mapping
- Management structure analysis

### 6. **Privacy Considerations**
- `person.email` field exists but should be filtered in UI
- `person.company_domain` may contain sensitive data
- Privacy filtering implemented in enriched query functions

## 🛠️ Performance Optimizations

### Database Query Patterns
```python
# Efficient current role with department query
current_roles_with_dept = client.table('role')\
    .select('''
        job_title, 
        person!inner(full_name), 
        organization!inner(name),
        job_title_departments!left(standardized_department)
    ''')\
    .eq('is_current', True)\
    .order('is_executive', desc=True)\
    .execute()

# Department classification lookup
def get_department(job_title):
    result = client.table('job_title_departments')\
        .select('standardized_department')\
        .eq('job_title', job_title)\
        .single()\
        .execute()
    return result.data['standardized_department'] if result.data else 'Other'

# Executive analysis with departments
executives_by_dept = client.table('role')\
    .select('*, person!inner(*), organization!inner(*)')\
    .eq('is_current', True)\
    .eq('is_executive', True)\
    .execute()
```

### Indexing Recommendations
- `role.is_current` (boolean index)
- `role.is_executive` (boolean index) 
- `person.embedding` (vector index for semantic search)
- `role.person_id, role.org_id` (composite foreign key index)

## 📈 Data Quality Metrics

### Current Status (Sep 2025)
- **Person Records**: 2,991
- **Organizations**: 363  
- **Total Roles**: 3,030
- **Current Roles**: 3,030 (100% current)
- **Executive Roles**: TBD (requires analysis)

### Data Completeness
- **LinkedIn URLs**: High coverage expected
- **Job Titles**: Complete for current roles
- **Organization Types**: Well-categorized
- **Historical Data**: Preserved via role history

## 🎯 UI Integration Benefits

### Enhanced Database Explorer
- Person-Organization relationships now display properly
- Executive status indicators
- Current vs. historical role differentiation
- Enhanced organization employee counts

### Improved Search Functionality
- Semantic search via embeddings
- Executive-filtered searches  
- Current-role-only filtering
- Multi-dimensional relationship queries

This updated schema documentation reflects the production reality and enables full utilization of the rich data structure for the CrowdBiz Graph platform.
