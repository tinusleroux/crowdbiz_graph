# CrowdBiz Graph - Data Imports

## 📁 Directory Structure

- `processed/` - CSV files that have already been imported into the Supabase database
- Upload new CSV files directly to this `imports/` folder for processing

## 🔄 Import Process

1. **Upload CSV files** to this directory
2. **Use the Import Contacts page** in the CrowdBiz Graph application
3. **Privacy filtering** automatically removes sensitive data (emails, phones, addresses)
4. **Data validation** ensures proper format and required fields
5. **Database import** with deduplication and historical role management

## 🔒 Privacy Note

All CSV imports are automatically filtered to remove:
- Email addresses and phone numbers
- Home addresses and personal information  
- Salary/compensation data
- Any other PII (Personally Identifiable Information)

Only professional networking information is retained:
- Names and job titles
- LinkedIn profiles
- Organization affiliations
- Professional roles and departments

## 📊 Processed Files

The `processed/` directory contains CSV files that have been successfully imported into the database. These files are kept for reference but are no longer actively used by the application.
