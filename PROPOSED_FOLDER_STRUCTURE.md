# Proposed Folder Structure for CrowdBiz Graph

## AI-Friendly Project Organization

Based on the current architecture, this structure separates concerns clearly and makes it easy for AI agents to locate, understand, and modify code.

```
crowdbiz_db/
├── README.md                           # Project overview and quick start
├── architecture.md                     # Technical architecture documentation
├── requirements.txt                    # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── run.py                             # Single entry point script
│
├── AI_AGENT_README.md                 # Primary instructions for AI agents
├── .ai_constraints/                   # AI agent guidelines (committed to git)
│   ├── CODING_STANDARDS.md            # Code style and patterns to follow
│   ├── PRIVACY_RULES.md               # Privacy compliance requirements
│   ├── ARCHITECTURE_RULES.md          # Architecture patterns and constraints
│   ├── TESTING_REQUIREMENTS.md        # Testing standards and requirements  
│   ├── PERFORMANCE_TARGETS.md         # Performance requirements and limits
│   └── FORBIDDEN_PATTERNS.md          # Anti-patterns to avoid
│
├── .ai_context/                       # AI context files (committed to git)
│   ├── PROJECT_MISSION.md             # Core mission and objectives
│   ├── USER_PERSONAS.md               # Who uses this system and how
│   ├── BUSINESS_LOGIC.md              # Key business rules and logic
│   ├── DATA_FLOW.md                   # How data flows through the system
│   ├── CURRENT_PRIORITIES.md          # Current development priorities
│   └── INTEGRATION_POINTS.md          # External system integration points
│
├── .ai_templates/                     # Code templates (committed to git)
│   ├── service_template.py            # Template for new services
│   ├── ui_page_template.py            # Template for new UI pages
│   ├── api_route_template.py          # Template for new API routes
│   ├── test_template.py               # Template for test files
│   └── model_template.py              # Template for data models
│
├── .ai_instructions/                  # Detailed AI instructions
│   ├── ONBOARDING.md                  # How to understand this codebase
│   ├── MAKING_CHANGES.md              # Step-by-step change process
│   ├── TESTING_GUIDE.md               # How to test changes
│   └── DEBUGGING_GUIDE.md             # Common issues and solutions
│
├── .ai_checks/                        # Automated validation scripts
│   ├── check_privacy_compliance.py    # Scan for privacy violations
│   ├── check_architecture_rules.py    # Validate architecture patterns
│   ├── check_code_standards.py        # Code quality checks
│   └── run_all_checks.py              # Run all validation checks
│
├── app/                               # Main application code
│   ├── __init__.py
│   ├── main.py                        # Streamlit entry point (renamed from ui.py)
│   ├── config.py                      # Application configuration
│   ├── logger.py                      # Logging configuration
│   │
│   ├── core/                          # Core business logic
│   │   ├── __init__.py
│   │   ├── models.py                  # Data models and schemas
│   │   ├── database.py                # Database connection and queries
│   │   ├── privacy.py                 # Privacy filtering and compliance
│   │   └── validation.py              # Data validation logic
│   │
│   ├── services/                      # Business services
│   │   ├── __init__.py
│   │   ├── import_service.py          # CSV import processing
│   │   ├── search_service.py          # Search functionality
│   │   ├── analytics_service.py       # Analytics and reporting
│   │   ├── linkedin_service.py        # LinkedIn CSV processing
│   │   └── news_service.py            # News/press release processing
│   │
│   ├── ui/                            # Streamlit UI components
│   │   ├── __init__.py
│   │   ├── pages/                     # Individual page components
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py           # Dashboard page
│   │   │   ├── search.py              # Search page
│   │   │   ├── analytics.py           # Analytics page
│   │   │   ├── import_data.py         # Data import page
│   │   │   ├── database_explorer.py   # Database explorer
│   │   │   └── settings.py            # Settings page
│   │   │
│   │   ├── components/                # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── forms.py               # Form components
│   │   │   ├── charts.py              # Chart components
│   │   │   ├── tables.py              # Table components
│   │   │   └── filters.py             # Filter components
│   │   │
│   │   └── utils/                     # UI utilities
│   │       ├── __init__.py
│   │       ├── session.py             # Session management
│   │       ├── cache.py               # Caching utilities
│   │       └── styling.py             # Custom CSS and styling
│   │
│   └── api/                           # Optional FastAPI service
│       ├── __init__.py
│       ├── main.py                    # FastAPI app (renamed from api_simple.py)
│       ├── routes/                    # API routes
│       │   ├── __init__.py
│       │   ├── people.py              # People endpoints
│       │   ├── organizations.py       # Organization endpoints
│       │   ├── search.py              # Search endpoints
│       │   ├── analytics.py           # Analytics endpoints
│       │   └── import.py              # Import endpoints
│       │
│       ├── middleware/                # API middleware
│       │   ├── __init__.py
│       │   ├── auth.py                # Authentication middleware
│       │   └── logging.py             # Request logging
│       │
│       └── schemas/                   # API request/response schemas
│           ├── __init__.py
│           ├── people.py              # People schemas
│           ├── organizations.py       # Organization schemas
│           └── common.py              # Common schemas
│
├── data/                              # Data-related files
│   ├── imports/                       # CSV import files
│   │   ├── nfl/                       # NFL-specific imports
│   │   ├── linkedin/                  # LinkedIn network exports
│   │   ├── news/                      # News and press releases
│   │   └── manual/                    # Manual data entries
│   │
│   ├── exports/                       # Generated export files
│   ├── templates/                     # CSV templates for users
│   └── samples/                       # Sample data files
│
├── database/                          # Database-related files
│   ├── supabase/                      # Supabase configuration
│   │   ├── config.toml                # Supabase settings
│   │   └── migrations/                # SQL migration files
│   │
│   ├── schemas/                       # Database schema definitions
│   │   ├── tables.sql                 # Table definitions
│   │   ├── indexes.sql                # Index definitions
│   │   ├── functions.sql              # Database functions
│   │   └── policies.sql               # RLS policies (future)
│   │
│   └── seeds/                         # Initial data seeds
│       ├── organizations.sql          # Organization seed data
│       └── data_sources.sql           # Data source definitions
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── maintenance/                   # Maintenance scripts
│   │   ├── __init__.py
│   │   ├── data_quality.py            # Data quality checks
│   │   ├── cleanup.py                 # Data cleanup utilities
│   │   └── backup.py                  # Backup utilities
│   │
│   ├── imports/                       # Import scripts
│   │   ├── __init__.py
│   │   ├── bulk_import.py             # Bulk data import
│   │   ├── validate_csv.py            # CSV validation
│   │   └── process_linkedin.py        # LinkedIn processing
│   │
│   └── deployment/                    # Deployment scripts
│       ├── __init__.py
│       ├── setup.py                   # Environment setup
│       └── health_check.py            # Health check script
│
├── tests/                             # Test files
│   ├── __init__.py
│   ├── conftest.py                    # Test configuration
│   ├── test_core/                     # Core logic tests
│   │   ├── test_models.py
│   │   ├── test_database.py
│   │   └── test_validation.py
│   │
│   ├── test_services/                 # Service tests
│   │   ├── test_import_service.py
│   │   ├── test_search_service.py
│   │   └── test_analytics_service.py
│   │
│   ├── test_api/                      # API tests
│   │   ├── test_people.py
│   │   ├── test_organizations.py
│   │   └── test_search.py
│   │
│   ├── test_ui/                       # UI tests
│   │   └── test_components.py
│   │
│   ├── fixtures/                      # Test fixtures
│   │   ├── sample_data.json
│   │   └── test_csvs/
│   │
│   └── utils/                         # Test utilities
│       ├── __init__.py
│       └── helpers.py
│
├── docs/                              # Documentation
│   ├── README.md                      # Documentation overview
│   ├── api/                           # API documentation
│   │   ├── endpoints.md
│   │   └── schemas.md
│   │
│   ├── user_guide/                    # User guides
│   │   ├── getting_started.md
│   │   ├── importing_data.md
│   │   └── using_analytics.md
│   │
│   ├── development/                   # Development guides
│   │   ├── setup.md
│   │   ├── contributing.md
│   │   └── testing.md
│   │
│   └── architecture/                  # Technical documentation
│       ├── database_schema.md
│       ├── data_flow.md
│       └── privacy_compliance.md
│
├── logs/                              # Application logs (gitignored)
├── .streamlit/                        # Streamlit configuration
│   └── config.toml                    # Streamlit settings
│
├── dev_workspace/                     # AI agent workspace (gitignored)
│   ├── README.md                      # Guidelines for AI agents
│   ├── diagnostics/                   # Diagnostic scripts
│   │   ├── debug_import.py            # Debug CSV import issues
│   │   ├── test_connections.py        # Test database connections
│   │   ├── analyze_performance.py     # Performance analysis
│   │   └── check_data_quality.py      # Data quality diagnostics
│   │
│   ├── experiments/                   # Experimental code
│   │   ├── new_features/              # Feature prototypes
│   │   ├── performance_tests/         # Performance experiments
│   │   └── ui_mockups/                # UI experiments
│   │
│   ├── quick_tests/                   # Quick test scripts
│   │   ├── test_query.py              # Quick database queries
│   │   ├── validate_csv.py            # Quick CSV validation
│   │   └── sample_data_gen.py         # Generate sample data
│   │
│   ├── debugging/                     # Debugging utilities
│   │   ├── trace_issues.py            # Issue tracing
│   │   ├── log_analysis.py            # Log file analysis
│   │   └── memory_profiling.py        # Memory usage analysis
│   │
│   ├── temp/                          # Temporary files (auto-cleanup)
│   │   ├── .gitkeep
│   │   └── temp_data/                 # Temporary data files
│   │
│   └── notes/                         # Development notes
│       ├── bugs_found.md              # Bug tracking
│       ├── performance_issues.md      # Performance notes
│       └── feature_ideas.md           # Feature brainstorming
│
└── deployment/                        # Deployment configurations
    ├── docker/                        # Docker configurations
    │   ├── Dockerfile.streamlit
    │   ├── Dockerfile.api
    │   └── docker-compose.yml
    │
    ├── vercel/                        # Future Vercel deployment
    │   └── vercel.json
    │
    └── env/                           # Environment configurations
        ├── development.env
        ├── staging.env
        └── production.env
```

## Benefits for AI Coding Agents

### 1. **Clear Separation of Concerns**
- **`app/core/`**: Database models, validation, privacy - AI knows this is core business logic
- **`app/services/`**: Business services - AI can easily locate import, search, analytics logic
- **`app/ui/`**: All UI components organized by pages and reusable components
- **`app/api/`**: Optional API clearly separated with routes, middleware, schemas

### 2. **Predictable File Locations**
- Need to modify search? Look in `app/services/search_service.py` and `app/ui/pages/search.py`
- Need to add LinkedIn import feature? Check `app/services/linkedin_service.py`
- Need to update database models? Look in `app/core/models.py`

### 3. **Logical Groupings**
- All data files in `data/` with clear subdirectories
- All database-related files in `database/`
- All tests mirror the app structure
- All documentation organized by audience (users, developers, API)

### 4. **Scalability Support**
- Easy to add new services in `app/services/`
- Easy to add new UI pages in `app/ui/pages/`
- Easy to add new API routes in `app/api/routes/`
- Database migrations clearly organized

### 5. **Development Workflow Support**
- `scripts/` for all maintenance and utility operations
- `tests/` mirror the app structure for easy test location
- `docs/` provide context for AI agents to understand requirements

### 6. **Privacy & Compliance**
- `app/core/privacy.py` - Centralized privacy logic
- Clear separation of data import vs. processing
- Template and sample files for user guidance

## Updated Migration Strategy for AI Agent Execution

### **Phase 1: Preparation and AI Guidance Setup (30 minutes)**

```bash
# Step 1.1: Create AI guidance structure
mkdir -p .ai_constraints .ai_context .ai_templates .ai_instructions .ai_checks

# Step 1.2: Create core AI files
touch AI_AGENT_README.md
touch .ai_constraints/{CODING_STANDARDS,PRIVACY_RULES,ARCHITECTURE_RULES,TESTING_REQUIREMENTS,PERFORMANCE_TARGETS,FORBIDDEN_PATTERNS}.md
touch .ai_context/{PROJECT_MISSION,USER_PERSONAS,BUSINESS_LOGIC,DATA_FLOW,CURRENT_PRIORITIES,INTEGRATION_POINTS}.md
touch .ai_instructions/{ONBOARDING,MAKING_CHANGES,TESTING_GUIDE,DEBUGGING_GUIDE}.md

# Step 1.3: Create development workspace
mkdir -p dev_workspace/{diagnostics,experiments,quick_tests,debugging,temp,notes}
touch dev_workspace/README.md

# Step 1.4: Update .gitignore
echo "
# AI Development Workspace
dev_workspace/temp/
dev_workspace/quick_tests/*.py
dev_workspace/experiments/*/temp_*
!dev_workspace/README.md
!dev_workspace/.gitkeep

# Logs
logs/
*.log

# Environment
.env
" >> .gitignore
```

### **Phase 2: Create New Folder Structure (15 minutes)**

```bash
# Step 2.1: Create main app structure
mkdir -p app/{core,services,ui/{pages,components,utils},api/{routes,middleware,schemas}}

# Step 2.2: Create supporting directories
mkdir -p data/{imports/{nfl,linkedin,news,manual},exports,templates,samples}
mkdir -p database/{supabase,schemas,seeds}
mkdir -p scripts/{maintenance,imports,deployment}
mkdir -p tests/{test_core,test_services,test_api,test_ui,fixtures,utils}
mkdir -p docs/{api,user_guide,development,architecture}
mkdir -p deployment/{docker,vercel,env}
mkdir -p .streamlit

# Step 2.3: Create __init__.py files for Python packages
find app tests scripts -type d -exec touch {}/__init__.py \;

# Step 2.4: Create placeholder files
touch app/main.py app/config.py app/logger.py
touch database/supabase/{config.toml,migrations/.gitkeep}
touch tests/conftest.py
touch .streamlit/config.toml
touch run.py
```

### **Phase 3: Migrate Core Files (45 minutes)**

```bash
# Step 3.1: Move and rename main files
# Current ui.py becomes the main Streamlit entry point
cp ui.py app/main.py

# Current api_simple.py becomes FastAPI entry point  
cp api_simple.py app/api/main.py

# Move configuration files
cp config.py app/config.py
cp logger.py app/logger.py

# Step 3.2: Move data files
mv imports/* data/imports/nfl/ 2>/dev/null || true
mv supabase/* database/supabase/ 2>/dev/null || true

# Step 3.3: Move existing scripts
mv *cleanup*.py scripts/maintenance/ 2>/dev/null || true
mv check_*.py scripts/maintenance/ 2>/dev/null || true
```

### **Phase 4: Refactor Code Structure (60 minutes)**

**Task 4.1: Extract Core Components from app/main.py**
```python
# Create app/core/database.py
# Move all Supabase connection logic here

# Create app/core/privacy.py  
# Move sanitize_data_for_display and privacy filtering

# Create app/core/models.py
# Define data models and schemas

# Create app/core/validation.py
# Move data validation logic
```

**Task 4.2: Extract Services from app/main.py**
```python
# Create app/services/import_service.py
# Move CSV import processing logic

# Create app/services/search_service.py  
# Move search functionality

# Create app/services/analytics_service.py
# Move analytics and reporting logic

# Create app/services/linkedin_service.py
# Create LinkedIn CSV processing service
```

**Task 4.3: Extract UI Components**
```python
# Create app/ui/pages/dashboard.py
# Move dashboard page logic

# Create app/ui/pages/search.py
# Move search page logic

# Create app/ui/pages/analytics.py
# Move analytics page logic

# Create app/ui/pages/import_data.py
# Move data import page logic

# Create app/ui/components/forms.py
# Extract reusable form components

# Create app/ui/components/charts.py  
# Extract chart components
```

### **Phase 5: Update Imports and References (30 minutes)**

**Task 5.1: Update app/main.py imports**
```python
# Replace local imports with new structure
from app.core.database import supabase
from app.core.privacy import sanitize_data_for_display
from app.services.import_service import ImportService
from app.services.search_service import SearchService
from app.ui.pages import dashboard, search, analytics, import_data
```

**Task 5.2: Create run.py entry point**
```python
#!/usr/bin/env python3
"""CrowdBiz Graph - Single Entry Point"""
import sys
import subprocess
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [streamlit|api|tests|checks]")
        print("  streamlit  - Start Streamlit UI")
        print("  api        - Start FastAPI service")  
        print("  tests      - Run test suite")
        print("  checks     - Run AI compliance checks")
        return
    
    mode = sys.argv[1]
    
    if mode == "streamlit":
        subprocess.run(["streamlit", "run", "app/main.py", "--server.port", "8501"])
    elif mode == "api":
        subprocess.run(["python", "app/api/main.py"])
    elif mode == "tests":
        subprocess.run(["pytest", "tests/"])
    elif mode == "checks":
        subprocess.run(["python", ".ai_checks/run_all_checks.py"])
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
```

### **Phase 6: Create AI Guidance Files (45 minutes)**

**Task 6.1: Create AI_AGENT_README.md**
```markdown
# AI Agent Instructions for CrowdBiz Graph

## 🎯 Your Mission
Build a privacy-first sports industry professional network without storing private contact data.

## ⚠️ Critical Rules (NEVER VIOLATE)
1. **Privacy First**: Never store email, phone, or private contact data
2. **Streamlit Focus**: This is a Streamlit app, not React  
3. **Direct DB Access**: Use Supabase directly, not complex API layers
4. **Test Everything**: Always test changes before committing

## 📁 Code Organization
- app/core/ = Business logic and data models
- app/services/ = Business services (import, search, analytics)
- app/ui/ = Streamlit UI components  
- dev_workspace/ = Your experimentation space

## 🔄 Before Making Changes
1. Read relevant .ai_constraints/ files
2. Check .ai_context/ for business understanding
3. Use .ai_templates/ for new code
4. Test in dev_workspace/ first

## 🚫 What NOT to Do
- Don't reference code in dev_workspace/ as examples
- Don't create API-first solutions (this is Streamlit-first)
- Don't add React/frontend complexity
- Don't store private data ever

## 🏃 Quick Start
```bash
python run.py streamlit  # Start the application
python run.py checks     # Validate your changes
```
```

**Task 6.2: Create .ai_constraints/PRIVACY_RULES.md**
```markdown
# PRIVACY COMPLIANCE RULES - NEVER VIOLATE

## Forbidden Data Fields
- ❌ NEVER store: email, phone, address, salary, personal_notes
- ❌ NEVER accept: private contact information in any form
- ❌ NEVER create: fields that could store private data

## Required Privacy Patterns
- ✅ ALWAYS filter private data in app/core/privacy.py before storage
- ✅ ALWAYS use sanitize_data_for_display() before showing data
- ✅ ALWAYS validate CSV imports remove private columns

## Code Patterns
```python
# ✅ CORRECT: Always sanitize before display
from app.core.privacy import sanitize_data_for_display

def display_people_data(data):
    sanitized = sanitize_data_for_display(data)
    return sanitized

# ❌ WRONG: Direct data display
def display_people_data(data):
    return data  # Could expose private info
```

### **Phase 7: Testing and Validation (30 minutes)**

```bash
# Step 7.1: Test the new structure
python run.py streamlit  # Should start successfully

# Step 7.2: Run validation checks
python run.py checks     # Should pass all checks

# Step 7.3: Test basic functionality
# - Dashboard loads
# - Search works
# - CSV import functions
# - No private data exposed

# Step 7.4: Clean up old files
mkdir old_structure
mv ui.py api_simple.py old_structure/
mv *.py old_structure/ 2>/dev/null || true  # Move any remaining loose files
```

### **Phase 8: Documentation Update (15 minutes)**

```bash
# Step 8.1: Update README.md with new structure
# Step 8.2: Update requirements.txt if needed
# Step 8.3: Commit changes to git

git add .
git commit -m "Migrate to AI-friendly folder structure

- Organized code into clear app/core, app/services, app/ui structure
- Added AI guidance files for consistent development
- Created dev_workspace for AI experimentation
- Implemented single entry point with run.py
- Maintained all existing functionality
- Enhanced privacy compliance structure"
```

## **🎯 Success Criteria**

After migration, the AI agent should be able to:
- ✅ Start the application with `python run.py streamlit`
- ✅ Understand the codebase structure from AI_AGENT_README.md
- ✅ Follow privacy rules from .ai_constraints/
- ✅ Use templates from .ai_templates/ for new code
- ✅ Test changes in dev_workspace/ before implementing
- ✅ Validate changes with `python run.py checks`

## **🕒 Total Estimated Time: 4-5 hours**

This migration can be executed by an AI agent following the step-by-step instructions, with clear success criteria and rollback capability using the `old_structure/` backup folder.

### **4. Development Workflow Support**
- `scripts/` for all maintenance and utility operations
- `tests/` mirror the app structure for easy test location
- `docs/` provide context for AI agents to understand requirements
- `dev_workspace/` for AI agent experimentation and diagnostics (gitignored)

### **5. Privacy & Compliance**
- `app/core/privacy.py` - Centralized privacy logic
- Clear separation of data import vs. processing
- Template and sample files for user guidance

### **6. AI Agent Workspace**
- **Isolation**: Keeps experimental code separate from production code
- **Clean Context**: AI agents won't reference temporary debugging code when making production changes  
- **Organized Chaos**: Provides structure even for temporary work
- **Easy Cleanup**: Entire folder can be gitignored or cleaned periodically

## **🤖 AI Agent Development Guidelines**

### **dev_workspace/ Usage:**
1. **Diagnostics**: Create scripts to debug specific issues in `diagnostics/`
2. **Experiments**: Try new approaches in `experiments/` before implementing
3. **Quick Tests**: Write one-off test scripts in `quick_tests/`
4. **Debugging**: Create debugging utilities in `debugging/`
5. **Notes**: Document findings and issues in `notes/`

### **Gitignore Configuration:**
```gitignore
# AI Development Workspace - keep out of version control
dev_workspace/temp/
dev_workspace/quick_tests/*.py
dev_workspace/experiments/*/temp_*
!dev_workspace/README.md
!dev_workspace/.gitkeep

# But keep important AI guidance files
!.ai_constraints/
!.ai_context/  
!.ai_templates/
!.ai_instructions/
!AI_AGENT_README.md

# Logs and environment
logs/
*.log
.env
```
