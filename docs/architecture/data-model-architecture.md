# CrowdBiz Graph - Data Model Architecture

## 🎯 Core Concepts

### **Job Title vs Role - Key Distinction**

**Job Title**
- Static descriptor: "VP of Corporate Sales", "Director of Marketing" 
- Function-based: Describes the type of work and responsibility level
- Department-mappable: Each job title maps to exactly one department
- Reusable: Same job title can exist across multiple organizations

**Role** 
- Employment instance: A specific person in a job title at an organization during a time period
- Context-bound: Links WHO (person) + WHERE (organization) + WHAT (job title) + WHEN (dates)
- Historical: Roles have start/end dates, people can have multiple roles
- Dynamic: Can change (promotions, job changes, organization moves)

## 🏗️ Database Architecture

### **Primary Tables**

```sql
-- Core entities
person (id, full_name, first_name, last_name, linkedin_url, ...)
organization (id, name, org_type, sport, parent_org_id, ...)

-- Employment relationships (the "roles")
role (
    id, 
    person_id,      -- WHO
    org_id,         -- WHERE
    job_title,      -- WHAT
    start_date,     -- WHEN (started)
    end_date,       -- WHEN (ended, null = current)
    is_current,     -- Current role flag
    is_executive    -- Executive level indicator
)

-- Job title classification (the lookup)
job_title_departments (
    job_title,                -- "VP of Corporate Sales"
    standardized_department   -- "Sales & Partnerships"
)
```

### **Department Classification Logic**

```python
# This is the correct pattern:
job_title = "VP of Corporate Sales"
department = lookup_department(job_title)  # → "Sales & Partnerships"

# NOT this (redundant storage):
# role.department = "Sales & Partnerships"  ❌ Wrong approach
```

**Why this works:**
- ✅ **Consistency**: Same job title always maps to same department
- ✅ **Maintainability**: One place to update department classifications  
- ✅ **Logic**: Department is an attribute of the job title, not the role instance
- ✅ **Scalability**: New job titles get automatically classified

## 📊 Department Categories

### **9 Standardized Departments**

1. **Sales & Partnerships** (262 job titles)
   - Corporate partnerships, sponsorships, business development
   - Account management, premium sales, hospitality

2. **Marketing & Communications** (185 job titles)  
   - Marketing, PR, content, social media, brand management
   - Creative, advertising, community relations

3. **Other** (112 job titles)
   - Miscellaneous roles that don't fit standard categories
   - Consultants, interns, unique positions

4. **Technology & Analytics** (50 job titles)
   - IT, data analytics, software development
   - Digital systems, database management

5. **Stadium Operations & Facilities** (35 job titles)
   - Stadium management, facilities, maintenance
   - Security, grounds keeping, event operations

6. **Finance & Administration** (27 job titles)
   - Finance, accounting, HR, legal, compliance
   - Business operations, executive support

7. **Executive Leadership** (20 job titles)
   - C-suite, presidents, owners, chairmen
   - Senior leadership roles

8. **Fan Experience & Events** (19 job titles)
   - Fan services, guest experience, entertainment
   - Community outreach, youth programs

9. **Broadcasting & Media** (7 job titles)
   - Broadcasting, media production, journalism
   - Video/audio production, announcing

10. **Ticketing & Operations** (5 job titles)
    - Ticketing, box office, concessions
    - Merchandise, retail operations

## 🔍 Query Patterns

### **Getting Roles with Departments**

```sql
-- Recommended approach: JOIN with lookup table
SELECT 
    p.full_name,
    r.job_title,
    o.name as organization,
    COALESCE(jtd.standardized_department, 'Other') as department
FROM role r
JOIN person p ON r.person_id = p.id
JOIN organization o ON r.org_id = o.id  
LEFT JOIN job_title_departments jtd ON r.job_title = jtd.job_title
WHERE r.is_current = true;
```

### **Department Analysis**

```sql
-- Count current roles by department
SELECT 
    COALESCE(jtd.standardized_department, 'Other') as department,
    COUNT(*) as role_count,
    COUNT(DISTINCT r.person_id) as person_count,
    COUNT(DISTINCT r.org_id) as org_count
FROM role r
LEFT JOIN job_title_departments jtd ON r.job_title = jtd.job_title
WHERE r.is_current = true
GROUP BY COALESCE(jtd.standardized_department, 'Other')
ORDER BY role_count DESC;
```

## 🚀 Application Implementation

### **Python Service Layer**

```python
@st.cache_data(ttl=600)
def get_department_for_job_title(job_title: str) -> str:
    """Get department classification for a job title"""
    db = get_database_manager()
    result = db.client.table('job_title_departments')\
        .select('standardized_department')\
        .eq('job_title', job_title)\
        .single().execute()
    return result.data['standardized_department'] if result.data else 'Other'

def enhance_roles_with_departments(roles: List[Dict]) -> List[Dict]:
    """Add department information to role data"""
    enhanced_roles = []
    for role in roles:
        enhanced_role = role.copy()
        enhanced_role['department'] = get_department_for_job_title(
            role.get('current_job_title')
        )
        enhanced_roles.append(enhanced_role)
    return enhanced_roles
```

### **Streamlit UI Integration**

```python
# Display network data with departments
network_data = get_network_status_data()
enhanced_data = enhance_roles_with_departments(network_data)

display_columns = {
    'full_name': 'Name',
    'current_job_title': 'Job Title', 
    'current_organization': 'Organization',
    'department': 'Department'  # ← Derived from job title
}
```

## 📈 Benefits of This Architecture

### **1. Data Integrity**
- No redundant department storage across thousands of role records
- Single source of truth for job title → department mapping
- Consistent classification regardless of context

### **2. Maintainability** 
- Update department classification in one place
- Easy to add new job titles with automatic classification
- Clear separation of concerns

### **3. Performance**
- Cached lookups prevent repeated database calls
- Efficient JOINs for analysis queries
- Reduced storage requirements

### **4. Flexibility**
- Can easily change department classifications
- Support for new department categories
- Historical role data remains intact

### **5. Business Logic Alignment**
- Matches real-world understanding: job titles have inherent departmental functions
- Supports organizational analysis and reporting
- Enables career path and industry trend analysis

## 🎯 Key Takeaways

1. **Job titles are functional descriptors** that map to departments
2. **Roles are contextual employment relationships** with time boundaries  
3. **Department classification is derived, not stored** in role records
4. **Lookup tables provide consistency** and maintainability
5. **The architecture supports both current and historical analysis**

This model accurately reflects how the sports industry organizes professional roles while providing the flexibility needed for comprehensive network analysis and reporting.

---

**Last Updated**: September 2025  
**Next Review**: December 2025
