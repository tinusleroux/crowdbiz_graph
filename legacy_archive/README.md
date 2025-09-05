# Legacy Archive

This directory contains files from the pre-migration CrowdBiz Graph structure.
These files have been replaced by the new modular architecture under `app/`.

## Migration Date
September 5, 2025

## Archived Files

### Core Application Files (Replaced)
- `ui.py` → `app/main.py` + `app/ui/`
- `api_simple.py` → `app/api/main.py`
- `config.py` → `app/core/config.py`
- `logger.py` → `app/core/logger.py`

### Utility Scripts (Deprecated)
- `delete_recent_contacts.py` - Contact cleanup utility
- `cleanup_contacts.py` - Contact data cleanup
- `simple_cleanup.py` - Basic cleanup operations
- `check_nfl_status.py` - NFL status checker

### Test Files (Moved to tests/)
- `test_contacts.csv` - Sample contact data
- `test_import.csv` - Import testing data

## New Structure
All functionality has been migrated to the new modular structure:
```
app/
├── core/        # Business logic (config, logger, database, etc.)
├── services/    # Business services (import, search, analytics)
├── ui/         # Streamlit components and pages
└── api/        # FastAPI endpoints
```

## Usage
To use the new application:
```bash
python run.py streamlit    # Start main application
python run.py api         # Start API service
```

These archived files are kept for reference and can be safely removed after verification that all functionality works correctly in the new structure.
