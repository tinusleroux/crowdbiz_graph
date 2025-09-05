# CrowdBiz Graph Documentation Hub

## 📚 Documentation Organization

This `/docs` directory contains the centralized, authoritative documentation for CrowdBiz Graph.

### **For Developers**
- **[Setup & Installation](#setup--installation)** - Complete setup guide
- **[Architecture](architecture/overview.md)** - System design and structure
- **[Database Schema](architecture/database-schema.md)** - Data structure and relationships
- **[Privacy & Compliance](#privacy--compliance)** - Privacy-first principles

### **For AI Coding Agents**
- **[AI Development Guide](../AI_AGENT_README.md)** - Comprehensive AI agent instructions
- **[GitHub Copilot Instructions](../.github/copilot-instructions.md)** - Quick AI guidance
- **[AI Reference Hub](../.ai_reference/README.md)** - Complete AI development reference
- **[Privacy Rules](../.ai_reference/ai_constraints/PRIVACY_RULES.md)** - Non-negotiable privacy requirements
- **[Architecture Rules](../.ai_reference/ai_constraints/ARCHITECTURE_RULES.md)** - System integrity guidelines

### **For Users**
- **[User Guide](user-guide/overview.md)** - Using the application

### **For Maintenance**
- **[Troubleshooting](maintenance/troubleshooting.md)** - Common issues and solutions

## 🎯 Current System Status

### **✅ Operational**
- **Database**: Supabase with sports industry professional data
- **Application**: Streamlit web interface fully functional
- **Privacy**: PII filtering active across all data flows
- **Search**: Full-text search across people and organizations
- **Analytics**: Dashboard and insights generation
- **Import**: CSV upload with automatic privacy filtering

### **🏗️ Architecture**
- **Backend**: Direct Supabase connection for simplicity
- **Frontend**: Streamlit for rapid development and deployment
- **Services**: Modular business logic in `app/services/`
- **Core**: Data models and utilities in `app/core/`
- **UI**: Streamlit components in `app/ui/`

### **🔒 Privacy Compliance**
- **Zero PII Storage**: No emails, phones, or addresses stored
- **Professional Only**: Names, titles, organizations, LinkedIn URLs
- **Automatic Filtering**: All data flows through privacy checks
- **Audit Trail**: Complete logging of data access and modifications

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/tinusleroux/crowdbiz_graph.git
cd crowdbiz_graph
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Start application
python run.py streamlit
```

## 📋 Setup & Installation

### **Prerequisites**
- Python 3.8+ (3.11+ recommended)
- Git
- Supabase account

### **Environment Configuration**
Required environment variables in `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-anon-public-key
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/[database]
```

### **Verification**
```bash
python run.py checks      # Test database connection
python run.py streamlit   # Start application (http://localhost:8502)
```

## 🔒 Privacy & Compliance

### **Data Protection**
- **Zero PII Storage**: No emails, phones, or addresses stored
- **Professional Only**: Names, titles, organizations, LinkedIn URLs  
- **Automatic Filtering**: All data flows through privacy checks
- **Audit Trail**: Complete logging of data access and modifications

### **What We Track vs Don't Store**
✅ **Allowed**: Professional names, job titles, organization names, LinkedIn profiles, career history  
❌ **Forbidden**: Email addresses, phone numbers, home addresses, salary information, personal data

## 🆘 Need Help?

1. **AI Development**: See [AI Development Guide](../AI_AGENT_README.md)
2. **Issues**: Check [Troubleshooting](maintenance/troubleshooting.md)
3. **Architecture**: Review [System Architecture](architecture/overview.md)
4. **Privacy Questions**: See [Privacy & Compliance](#privacy--compliance) above

---

**Last Updated**: September 5, 2025  
**Version**: 1.0 (Post-Migration)  
**System Status**: ✅ Fully Operational
