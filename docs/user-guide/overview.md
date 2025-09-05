# User Guide Overview

## 🎯 Using CrowdBiz Graph

CrowdBiz Graph helps you discover, search, and analyze professional networks in the sports industry while respecting privacy.

## 🚀 Getting Started

### First Time Setup
1. **Access the Application**: Visit http://localhost:8502 after setup
2. **Explore the Dashboard**: Get an overview of available data
3. **Try a Search**: Look for NFL teams, professionals, or organizations
4. **Import Data**: Add your own professional contacts (PII-free)

### Navigation
- **Dashboard**: System overview and key metrics
- **Search**: Find people and organizations
- **Import Contacts**: Upload CSV files with automatic privacy filtering
- **Analytics**: Industry insights and trends
- **Database Explorer**: Direct data exploration

## 🔍 Searching for People & Organizations

### Basic Search
1. Go to the **Search** page
2. Enter search terms in the main search box:
   - Names: "John Smith", "Sarah"
   - Titles: "Head Coach", "General Manager"
   - Organizations: "Cowboys", "NFL", "ESPN"
   - Locations: "Dallas", "Texas"

### Search Tips
- **Partial matches work**: "Cowb" finds "Cowboys"
- **Multiple terms**: Search combines all terms automatically
- **Organization types**: Try "NFL team", "sports agency", "media"
- **Geographic**: "Texas NFL" finds Texas-based NFL organizations

### Understanding Results
- **People Results**: Shows name, current title, organization, LinkedIn
- **Organization Results**: Shows name, type, location, staff count
- **Combined Search**: All results ranked by relevance

## 📊 Using Analytics

### Dashboard Insights
- **Total Counts**: People, organizations, roles tracked
- **Geographic Distribution**: Where professionals are located
- **Organization Types**: Teams, agencies, media breakdown
- **Recent Activity**: Latest additions and updates

### Professional Analytics
- **Career Progression**: Track role changes over time
- **Network Connections**: Professional relationship mapping
- **Industry Trends**: Movement patterns and hiring trends
- **Organization Growth**: Staff changes and expansion

## 📥 Importing Your Data

### Supported Data Types
✅ **Professional Information We Accept**:
- First and last names
- Job titles and departments
- Organization names
- LinkedIn profile URLs
- Professional connections

❌ **Personal Information We Filter Out**:
- Email addresses
- Phone numbers
- Home addresses
- Personal social media
- Salary information

### Import Process

1. **Prepare Your CSV File**
   ```csv
   first_name,last_name,title,organization,linkedin_url
   John,Smith,Head Coach,Dallas Cowboys,https://linkedin.com/in/johnsmith
   Sarah,Johnson,General Manager,ESPN,https://linkedin.com/in/sarahjohnson
   ```

2. **Upload via Web Interface**
   - Go to **Import Contacts** page
   - Click "Choose File" and select your CSV
   - Review the column mapping preview
   - Confirm import settings

3. **Privacy Filtering**
   - System automatically removes PII columns
   - Only professional data is stored
   - Import summary shows what was filtered

4. **Review Results**
   - See import statistics and validation
   - Check for duplicates and conflicts
   - View any errors or suggestions

### Column Mapping
The system automatically maps common column names:
- `name` → `first_name` + `last_name` (if split)
- `company` → `organization`
- `position` → `title`
- `linkedin` → `linkedin_url`

## 🗂️ Database Explorer

### Browsing Data
1. Go to **Database Explorer** page
2. Select entity type: People, Organizations, or Roles
3. Use filters to narrow results:
   - Organization type (team, agency, media)
   - Location (city, state)
   - League affiliation (NFL, NBA, etc.)

### Detailed Views
- **Person Profile**: Complete professional history
- **Organization Profile**: Staff list and basic information
- **Role History**: Career progression and timeline

## 🔒 Privacy Features

### What's Protected
- **No PII Storage**: Personal contact information never stored
- **Professional Only**: Business-relevant data exclusively
- **User Control**: Clear visibility into what data we track
- **Audit Trails**: Complete logging of data access

### Privacy Controls
- **Import Filtering**: Automatic PII removal during upload
- **Display Filtering**: Additional safety checks before display
- **Export Controls**: Same privacy rules apply to data export
- **Access Logging**: Track who accesses what data

## 💡 Tips for Success

### Effective Searching
- **Start broad**: "NFL coach" then narrow down
- **Use filters**: Combine search with location/type filters
- **Try variations**: "GM", "General Manager", "Front Office"
- **LinkedIn connections**: Use LinkedIn URLs for verified profiles

### Quality Data Import
- **Clean your CSV**: Remove empty rows and columns
- **Standard formats**: Use common column names when possible
- **LinkedIn URLs**: Include full LinkedIn profile URLs
- **Organization consistency**: Use standard team/company names

### Building Networks
- **Track connections**: Note professional relationships in LinkedIn
- **Follow movements**: Monitor role changes and career progression
- **Industry events**: Import attendee lists from conferences
- **Verify accuracy**: Cross-reference with public sources

## 🆘 Common Issues & Solutions

### Search Not Working
- **Check spelling**: Try alternative spellings
- **Broaden terms**: Use fewer, more general search terms
- **Clear filters**: Remove any active filters that might limit results

### Import Problems
- **File format**: Ensure CSV file format, not Excel
- **Column headers**: First row should contain column names
- **Character encoding**: Save CSV as UTF-8 if special characters
- **File size**: Large files may take longer to process

### Missing Data
- **Privacy filtering**: Some columns may have been filtered out
- **Validation rules**: Invalid data may be rejected
- **Duplicate detection**: Similar records may be merged
- **Format requirements**: Ensure data meets format expectations

## 📈 Advanced Usage

### Power User Tips
- **Bulk operations**: Import multiple CSV files for comprehensive data
- **Regular updates**: Refresh data periodically for accuracy
- **Export analysis**: Use database explorer for detailed reporting
- **API access**: Use REST API for programmatic access

### Integration Opportunities
- **CRM systems**: Export data to customer relationship platforms
- **Event planning**: Import attendee lists for networking events
- **Business intelligence**: Connect to reporting and analytics tools
- **Social networks**: Cross-reference with LinkedIn for verification

---

**Need more help?** Check the [Troubleshooting Guide](../maintenance/troubleshooting.md) or [Getting Started Guide](../getting-started.md)
