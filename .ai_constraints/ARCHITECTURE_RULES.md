# ARCHITECTURE RULES - MAINTAIN SYSTEM INTEGRITY

## 🏗️ Core Architecture Principles

### **1. Streamlit-First Design**
- This is a **Streamlit application**, not React or other web framework
- Use Streamlit components and patterns consistently
- Leverage Streamlit's built-in state management and caching

### **2. Direct Database Access Pattern**
- Use **Supabase client directly** for database operations
- Avoid unnecessary API layers for simple CRUD operations
- Keep database queries efficient and well-organized

### **3. Privacy-First Architecture**
- All data flows through privacy filters
- No private data storage at any layer
- Privacy compliance is architectural, not just functional

## 📁 Folder Structure Rules

### **Required Structure:**
```
app/
├── core/          # Business logic, models, database operations
├── services/      # Business services (import, search, analytics)  
├── ui/           # Streamlit UI components and pages
└── api/          # Optional API endpoints (if needed)
```

### **Separation of Concerns:**
- **app/core/**: Data models, database operations, business logic
- **app/services/**: High-level business operations (import CSV, run analytics)
- **app/ui/**: UI components, pages, and user interactions
- **app/api/**: API endpoints (only if external access needed)

## 🔄 Data Flow Rules

### **Import Flow:**
1. CSV → `services/import_service.py` → privacy filter → database
2. **Never** bypass privacy filtering
3. **Always** validate data before storage

### **Display Flow:**
1. Database → `core/models.py` → sanitize → UI components
2. **Never** display raw database data
3. **Always** use consistent formatting

### **Search Flow:**
1. User query → `services/search_service.py` → database → sanitize → UI
2. **Always** filter results for privacy compliance
3. **Always** use parameterized queries (no SQL injection)

## 🧩 Component Integration Rules

### **Database Integration:**
- Use `app/core/database.py` for all database connections
- Centralize Supabase configuration
- Use connection pooling where appropriate

### **State Management:**
- Use Streamlit's session state for user state
- Keep state minimal and well-organized
- Clear state appropriately on navigation

### **Error Handling:**
- Centralized error handling in `app/core/errors.py`
- User-friendly error messages
- Proper logging for debugging

## 🚫 Anti-Patterns to Avoid

### **Code Organization:**
- ❌ Don't put business logic in UI files
- ❌ Don't put UI logic in core business files  
- ❌ Don't create circular dependencies
- ❌ Don't bypass the established folder structure

### **Data Handling:**
- ❌ Don't access database directly from UI components
- ❌ Don't store sensitive data in session state
- ❌ Don't create duplicate data processing logic
- ❌ Don't ignore privacy filtering requirements

### **Performance:**
- ❌ Don't create N+1 query problems
- ❌ Don't load entire datasets without pagination
- ❌ Don't ignore Streamlit caching opportunities
- ❌ Don't create memory leaks in long-running processes

## ✅ Required Patterns

### **New Feature Development:**
1. Plan data flow through proper layers
2. Implement privacy filtering from start
3. Create UI components in app/ui/
4. Add business logic to app/core/ or app/services/
5. Test integration thoroughly

### **Code Review Checklist:**
- [ ] Follows folder structure rules
- [ ] Implements privacy filtering
- [ ] Uses proper error handling
- [ ] Includes appropriate tests
- [ ] Documents complex business logic
- [ ] Follows Streamlit best practices
