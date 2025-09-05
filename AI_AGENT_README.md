# AI Agent Instructions for CrowdBiz Graph

## 🎯 Your Mission
Build and maintain a **privacy-first sports industry professional network** without storing private contact data.

## ⚠️ Critical Rules (NEVER VIOLATE)

### **1. Privacy First**
- **NEVER** store email, phone, address, or private contact data
- **ALWAYS** filter private data before storage
- **ALWAYS** use sanitization before display
- Run privacy checks: `python .ai_checks/check_privacy_compliance.py`

### **2. Streamlit Focus**
- This is a **Streamlit app**, not React or other web framework
- Use Streamlit components, session state, and caching patterns
- Keep UI logic in `app/ui/` components

### **3. Direct Database Access**
- Use **Supabase directly** for database operations
- Avoid complex API layers for simple CRUD operations
- Centralize database operations in `app/core/database.py`

### **4. Test Everything**
- **ALWAYS** test changes before committing
- Use `dev_workspace/` for experimentation
- Run validation: `python run.py checks`

## 📁 Code Organization Rules

### **Folder Structure:**
```
app/
├── core/          # Business logic, models, database (NO UI code here)
├── services/      # Business services - import, search, analytics  
├── ui/           # Streamlit components and pages (NO business logic here)
└── api/          # Optional API endpoints (only if external access needed)
```

### **What Goes Where:**
- **app/core/**: Data models, database operations, business rules, privacy filtering
- **app/services/**: CSV import, search operations, analytics generation, data processing
- **app/ui/**: Streamlit pages, components, forms, displays, user interactions
- **dev_workspace/**: Your experiments, debugging, temporary code (gitignored)

## 🔄 Development Workflow

### **Before Making Changes:**
1. Read relevant `.ai_constraints/` files for rules
2. Check `.ai_context/` files for business understanding  
3. Look at `.ai_templates/` for code patterns
4. Test approach in `dev_workspace/` first

### **Making Changes:**
1. **Plan**: Understand what layer the change belongs in
2. **Implement**: Follow established patterns and templates
3. **Privacy Check**: Ensure no private data violations
4. **Test**: Validate functionality works correctly
5. **Document**: Add comments explaining business logic

### **Code Quality Standards:**
- **Separation of Concerns**: Keep business logic separate from UI
- **Privacy Filtering**: All data flows through privacy checks
- **Error Handling**: Use centralized error handling patterns
- **Documentation**: Comment complex business logic and decisions

## 🚨 Common Mistakes to Avoid

### **Architecture Violations:**
- ❌ Don't put database queries in UI components
- ❌ Don't put Streamlit code in core business logic
- ❌ Don't bypass privacy filtering anywhere
- ❌ Don't ignore the established folder structure

### **Privacy Violations:**
- ❌ Don't store or display email addresses, phone numbers, addresses
- ❌ Don't accept private data in CSV imports
- ❌ Don't create database fields for private data
- ❌ Don't skip sanitization before displaying data

### **Streamlit Anti-Patterns:**
- ❌ Don't recreate React patterns in Streamlit
- ❌ Don't ignore Streamlit caching opportunities  
- ❌ Don't create complex state management (keep it simple)
- ❌ Don't put heavy computations in UI refresh cycles

## 🛠️ Essential Commands

### **Development:**
```bash
# Start the application
python run.py streamlit

# Run all validation checks  
python run.py checks

# Run privacy compliance check
python .ai_checks/check_privacy_compliance.py
```

### **Testing Your Changes:**
```bash
# Test in dev workspace first
cd dev_workspace/experiments/
# Create test script, validate approach

# Then implement in main codebase
cd ../../app/
# Make actual changes following patterns
```

## 📊 Current System Status

### **Database:**
- **Supabase PostgreSQL** with 2,990+ NFL professionals
- **33 NFL teams** with complete organizational data
- **1,000+ professional roles** across the industry
- **Privacy-compliant schema** (no personal contact data)

### **Key Features:**
- **Dashboard**: Overview of network data and analytics
- **Search & Discovery**: Find professionals by name, role, team, organization
- **CSV Import**: Privacy-filtered bulk data import
- **Analytics**: Professional network analysis and insights
- **Database Explorer**: Admin tool for data quality management

### **Technology Stack:**
- **Frontend**: Streamlit (Python web app framework)
- **Database**: Supabase (PostgreSQL with real-time features)
- **Authentication**: Supabase Auth (when needed)
- **Hosting**: Streamlit Cloud or similar Python hosting
- **Dependencies**: pandas, supabase-py, streamlit, plotly

## 🎯 Current Development Priorities

### **High Priority:**
1. **Complete Migration**: Finish moving from monolithic structure to modular app/
2. **LinkedIn Integration**: Add LinkedIn profile URL processing  
3. **Press Release Processing**: Automate industry news ingestion
4. **Search Improvements**: Better search relevance and filtering

### **Medium Priority:**
1. **Performance Optimization**: Improve query performance and caching
2. **Data Quality Tools**: Better data validation and cleanup utilities
3. **Export Features**: Allow users to export their network data
4. **Mobile Responsiveness**: Improve Streamlit mobile experience

## 🔍 Debugging and Troubleshooting

### **Common Issues:**
1. **Database Connection**: Check Supabase credentials and connection
2. **Privacy Violations**: Run privacy compliance checks
3. **Performance**: Use Streamlit caching and optimize database queries
4. **Data Quality**: Validate CSV imports and data consistency

### **Debugging Tools:**
- Use `dev_workspace/diagnostics/` for debugging scripts
- Check `logs/` for application logs
- Use Streamlit's built-in debugging features
- Validate with `.ai_checks/` scripts

## 💡 Pro Tips for AI Agents

### **Understanding the Codebase:**
- Start with this README and `.ai_context/` files
- Look at existing patterns in `app/` before creating new code
- Use `.ai_templates/` as starting points for new files
- Keep experimental code in `dev_workspace/` until proven

### **Staying Aligned:**
- Reference `.ai_constraints/` files frequently
- When unsure, choose the more privacy-protective option
- Keep the Streamlit app simple and user-friendly
- Focus on professional networking value, not feature complexity

### **Efficient Development:**
- Use `dev_workspace/` for rapid experimentation
- Follow established patterns rather than creating new ones
- Test privacy compliance early and often  
- Document your reasoning in code comments
