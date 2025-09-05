# AI Development Reference

## 🎯 Purpose
This directory contains comprehensive guidance for AI coding agents working on CrowdBiz Graph. It provides the context, constraints, and instructions needed for productive AI-assisted development.

## 📁 Directory Structure

### **ai_constraints/** - Non-Negotiable Rules
- **PRIVACY_RULES.md** - Critical privacy requirements (NEVER violate)
- **ARCHITECTURE_RULES.md** - System architecture integrity rules
- Purpose: Hard constraints that AI agents must always follow

### **ai_context/** - Business Understanding  
- **PROJECT_MISSION.md** - Core mission, users, competitive advantages
- Purpose: Business context for informed decision-making

### **ai_instructions/** - Development Workflows
- Purpose: Step-by-step guides for common development tasks
- Status: Framework ready for expansion

### **ai_templates/** - Code Templates
- Purpose: Boilerplate code following project patterns  
- Status: Framework ready for expansion

### **ai_checks/** - Validation Scripts
- Purpose: Automated compliance and quality checking
- Status: Framework ready for expansion

## 🚀 Quick Start for AI Agents

### **Essential Reading Order:**
1. **[ai_constraints/PRIVACY_RULES.md](ai_constraints/PRIVACY_RULES.md)** - Critical privacy requirements
2. **[ai_constraints/ARCHITECTURE_RULES.md](ai_constraints/ARCHITECTURE_RULES.md)** - System architecture rules
3. **[ai_context/PROJECT_MISSION.md](ai_context/PROJECT_MISSION.md)** - Business context and mission

### **For Immediate Productivity:**
- **GitHub Copilot**: See [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Comprehensive Guide**: See [AI_AGENT_README.md](../AI_AGENT_README.md)

## 🔒 Privacy-First Development

**Critical Rules:**
- ❌ **NEVER store**: emails, phones, addresses, personal information
- ✅ **ALWAYS filter**: data through privacy.py before storage  
- ✅ **PROFESSIONAL ONLY**: names, titles, organizations, LinkedIn URLs

## 🏗️ Architecture Principles

**Streamlit-First:**
- Direct Streamlit UI development (not React)
- Use Streamlit components and caching patterns
- Leverage built-in session state management

**Direct Database:**
- Supabase client direct access (no complex API layers)
- Service layer for business logic
- Privacy filtering at every data flow point

## 🔄 Development Workflow

1. **Read Constraints**: Review privacy and architecture rules
2. **Understand Context**: Check business mission and requirements  
3. **Follow Patterns**: Use established service layer patterns
4. **Test Changes**: Validate with `python run.py checks`
5. **Maintain Privacy**: Ensure zero PII storage throughout

## 📈 System Status

**Current Data:**
- NFL professional profiles
- Sports organizations and teams
- Professional role records  
- Zero PII stored (privacy compliant)

**Architecture:**
- Streamlit web application
- Supabase PostgreSQL database
- Modular app/ structure (core/, services/, ui/)
- Comprehensive privacy filtering system

---

**For AI Agents**: This system is designed for immediate productivity while maintaining privacy compliance and architectural integrity.
