# Troubleshooting Guide

## 🆘 Common Issues & Solutions

### Database Connection Problems

#### Issue: "Could not connect to Supabase"
**Symptoms:**
- Application fails to start
- "Connection refused" errors
- Database queries timeout

**Solutions:**
1. **Check Environment Variables**
   ```bash
   # Verify .env file exists and has correct values
   cat .env | grep SUPABASE
   ```

2. **Verify Supabase Credentials**
   ```bash
   # Test connection manually
   python -c "
   import os
   from supabase import create_client
   client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_API_KEY'))
   print('Connection successful!')
   "
   ```

3. **Check Network Connectivity**
   ```bash
   # Test if Supabase is reachable
   curl -I https://your-project.supabase.co
   ```

#### Issue: "Authentication failed"
**Solutions:**
- Verify `SUPABASE_API_KEY` is the anon/public key, not service key
- Check if API key has expired or been rotated
- Ensure project URL matches your Supabase project

### Application Startup Issues

#### Issue: "ModuleNotFoundError" when starting Streamlit
**Solutions:**
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python Path**
   ```bash
   # Ensure you're in the project root directory
   python run.py streamlit
   ```

3. **Virtual Environment**
   ```bash
   # Activate virtual environment if using one
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

#### Issue: "Port already in use"
**Solutions:**
```bash
# Check what's using the port
lsof -i :8502

# Kill the process or use different port
python run.py streamlit --port 8503
```

### Search & Data Issues

#### Issue: Search returns no results
**Symptoms:**
- Searches return empty results
- Database appears empty

**Solutions:**
1. **Verify Data Exists**
   ```bash
   python run.py checks
   ```

2. **Check Database Connection**
   - Go to Database Explorer page
   - Try browsing people/organizations directly
   - Verify data is actually in database

3. **Search Query Issues**
   - Try simpler search terms
   - Check for typos
   - Use partial matches

#### Issue: Import fails with validation errors
**Solutions:**
1. **Check CSV Format**
   - Ensure file is actual CSV (not Excel saved as CSV)
   - Verify first row contains column headers
   - Check for special characters

2. **Privacy Filtering**
   - Review which columns were filtered out
   - Ensure required columns (first_name, last_name) are present
   - Check column name mapping

### Performance Issues

#### Issue: Application is slow
**Solutions:**
1. **Clear Browser Cache**
   ```bash
   # Or use incognito/private browsing mode
   ```

2. **Check Database Performance**
   - Review Supabase dashboard for slow queries
   - Consider database indexing for large datasets

3. **Restart Application**
   ```bash
   # Stop current session (Ctrl+C) and restart
   python run.py streamlit
   ```

### Import & Data Processing

#### Issue: CSV import hangs or fails
**Solutions:**
1. **File Size Limits**
   - Large files (>10MB) may timeout
   - Split large files into smaller chunks
   - Process incrementally

2. **Memory Issues**
   - Restart the application
   - Process smaller batches
   - Check available system memory

3. **Data Validation**
   - Review import logs in `logs/import_service.log`
   - Check for malformed data
   - Verify CSV encoding (should be UTF-8)

### Privacy & Compliance

#### Issue: PII data unexpectedly visible
**Immediate Action:**
1. **Stop using the application**
2. **Report the issue immediately**
3. **Check logs for data exposure**

**Investigation:**
```bash
# Check what data was processed
grep -r "email\|phone\|address" logs/

# Verify privacy filtering is working
python run.py checks
```

### UI & Display Issues

#### Issue: Streamlit interface not loading
**Solutions:**
1. **Browser Compatibility**
   - Try different browser (Chrome, Firefox, Safari)
   - Disable browser extensions
   - Clear browser cache and cookies

2. **JavaScript Errors**
   - Open browser developer tools (F12)
   - Check for JavaScript errors in console
   - Refresh page

### API & External Services

#### Issue: API endpoints not responding
**Solutions:**
1. **Check API Service**
   ```bash
   # If using optional API service
   python run.py api
   ```

2. **Port Conflicts**
   ```bash
   # Check if API port (8000) is available
   lsof -i :8000
   ```

## 🔧 Diagnostic Commands

### Health Checks
```bash
# Full system validation
python run.py checks

# Database connection test
python -c "from app.core.database import DatabaseManager; dm = DatabaseManager(); print('DB OK')"

# Privacy filter test
python -c "from app.core.privacy import sanitize_data_for_storage; print('Privacy OK')"
```

### Log Analysis
```bash
# View recent application logs
tail -f logs/main_app.log

# Search for errors
grep -i error logs/*.log

# Import process logs
tail -f logs/import_service.log
```

### Data Verification
```bash
# Count records in database
python -c "
from app.core.database import DatabaseManager
dm = DatabaseManager()
stats = dm.get_dashboard_stats()
print(f'People: {stats.total_people}')
print(f'Organizations: {stats.total_organizations}')
print(f'Roles: {stats.total_roles}')
"
```

## 🚨 Emergency Procedures

### Data Integrity Issues
1. **Immediate assessment**: Run `python run.py checks`
2. **Backup current state** (if Supabase backup configured)
3. **Review recent changes** in application logs
4. **Contact development team** with specific error details

### Privacy Violations
1. **Stop all data processing immediately**
2. **Document the issue** with screenshots and logs
3. **Review audit trail** for data exposure scope
4. **Implement corrective measures** based on findings

### System Down
1. **Check Supabase status** at status.supabase.io
2. **Verify local environment** with diagnostic commands
3. **Review recent deployments** or configuration changes
4. **Escalate to infrastructure team** if needed

## 📞 Getting Additional Help

### Self-Service Resources
- **[Getting Started Guide](../getting-started.md)** - Setup and configuration
- **[Architecture Documentation](../architecture/overview.md)** - System design
- **[User Guide](../user-guide/overview.md)** - Application usage

### Development Resources
- **[AI Development Guide](../../AI_AGENT_README.md)** - For AI coding agents
- **[GitHub Repository](https://github.com/tinusleroux/crowdbiz_graph)** - Source code and issues

### Escalation Process
1. **Self-diagnosis** using this guide
2. **Check application logs** for specific error messages
3. **Document steps taken** and results observed
4. **Create GitHub issue** with detailed information
5. **Contact development team** for critical issues

## 📋 Issue Reporting Template

When reporting issues, please include:

```
**Issue Description:**
Brief summary of the problem

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: (macOS, Windows, Linux)
- Python Version: 
- Browser: (if web interface issue)

**Logs:**
Relevant error messages or log entries

**Screenshots:**
If applicable, attach screenshots
```

---

**Last Updated**: September 2025  
**Next Review**: December 2025

For additional support, see [Documentation Hub](../README.md) or [Getting Started Guide](../getting-started.md)
