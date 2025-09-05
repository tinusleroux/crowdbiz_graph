# Database Connection Guide - CrowdBiz Graph

## 🎯 **DEFINITIVE CONNECTION APPROACH**

**Always use the Supabase REST API client - NEVER attempt direct PostgreSQL connections.**

### ✅ **CORRECT METHOD**

```python
# This is the ONLY method that works reliably
from app.core.database import get_database_manager

# Get database manager (cached)
db = get_database_manager()

# Check connection
if db.is_connected():
    # Use the client for queries
    result = db.client.table('your_table').select('*').execute()
    data = result.data
else:
    print("Connection failed")
```

### ✅ **FOR SCHEMA INSPECTION**

```python
# Use supabase_schema_explorer.py - it works every time
python supabase_schema_explorer.py

# Or for simple queries:
python -c "
import sys, os
sys.path.insert(0, os.getcwd())
from app.core.database import get_database_manager
db = get_database_manager()
result = db.client.table('network_status').select('*').limit(1).execute()
if result.data:
    print('Columns:', list(result.data[0].keys()))
"
```

## ❌ **METHODS THAT DON'T WORK**

### Direct PostgreSQL Connection
```python
# DON'T DO THIS - always fails with "Tenant or user not found"
import psycopg2
conn = psycopg2.connect(DATABASE_URL)  # ❌ FAILS
```

### Supabase CLI Commands  
```bash
# DON'T DO THIS - unreliable
supabase db pull  # ❌ OFTEN FAILS
```

### Direct Environment Variable Loading
```python
# DON'T DO THIS - environment variables don't load correctly
import os
url = os.getenv('SUPABASE_URL')  # ❌ OFTEN EMPTY
```

## 🔧 **WHY DIRECT POSTGRESQL FAILS**

The error "Tenant or user not found" occurs because:
1. Supabase pooler requires specific authentication
2. The connection string format is not standard PostgreSQL
3. Environment variables are not loading correctly in scripts
4. The pooler port (6543) has restrictions

## 🎯 **SOLUTION ARCHITECTURE**

```
✅ Application Code
     ↓
✅ app.core.database.DatabaseManager
     ↓  
✅ Supabase REST API Client
     ↓
✅ Supabase Cloud Database
```

**NOT THIS:**
```
❌ Direct Script
     ↓
❌ psycopg2/direct PostgreSQL
     ↓
❌ Database (fails at connection)
```

## 📋 **STANDARD PROCEDURES**

### 1. **Check Database Schema**
```bash
python supabase_schema_explorer.py
```

### 2. **Run Database Queries**  
```python
from app.core.database import get_database_manager
db = get_database_manager()
result = db.client.table('table_name').select('*').execute()
```

### 3. **Test Specific Columns**
```python
from app.core.database import get_database_manager
db = get_database_manager()
result = db.client.table('network_status').select('*').limit(1).execute()
columns = list(result.data[0].keys()) if result.data else []
print(columns)
```

### 4. **Debug Connection Issues**
```python
from app.core.database import get_database_manager
db = get_database_manager()
print(f"Connected: {db.is_connected()}")
print(f"Client: {db.client}")
```

## 🚨 **REMEMBER THIS**

Every time you need to connect to the database:

1. **Use `get_database_manager()`** - it's cached and reliable
2. **Access via `db.client.table()`** - uses REST API
3. **Never use direct PostgreSQL** - it will always fail
4. **Use `supabase_schema_explorer.py`** for schema inspection

This approach works 100% of the time and avoids the endless connection troubleshooting cycles.
