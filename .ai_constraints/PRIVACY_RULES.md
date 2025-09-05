# PRIVACY COMPLIANCE RULES - NEVER VIOLATE

## 🚨 Critical Privacy Requirements
This system is designed to be **privacy-first** - we connect professionals without storing private contact information.

## ❌ Forbidden Data Fields
- **NEVER store**: email, phone, address, salary, personal_notes, private_contact_info
- **NEVER accept**: private contact information in any form during imports
- **NEVER create**: database fields that could store private data
- **NEVER display**: private information even if it exists in source data

## ✅ Required Privacy Patterns
- **ALWAYS** filter private data in `app/core/privacy.py` before storage
- **ALWAYS** use `sanitize_data_for_display()` before showing data to users
- **ALWAYS** validate CSV imports remove private columns automatically
- **ALWAYS** document why certain fields are excluded in comments

## 🛡️ Privacy Implementation Requirements
1. **Data Import**: All imports must go through privacy filtering
2. **Data Display**: All data display must be sanitized
3. **Database Schema**: No private data fields allowed
4. **API Responses**: No private data in any API response
5. **Search Results**: No private data in search results

## 📊 Allowed Professional Data
- ✅ Name, title, organization, industry
- ✅ Professional roles and responsibilities  
- ✅ Public work history and achievements
- ✅ Professional networks and connections
- ✅ Public social media profiles (LinkedIn, etc.)
- ✅ Professional skills and expertise areas

## 🔍 Compliance Validation
Run privacy checks before any code changes:
```bash
python .ai_checks/check_privacy_compliance.py
```

## 🚀 Privacy-First Development
When adding new features:
1. **Design**: Ensure no private data is needed
2. **Implement**: Add privacy filtering from day one
3. **Test**: Validate privacy compliance
4. **Document**: Explain privacy decisions in code comments
