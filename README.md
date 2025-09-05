# CrowdBiz Graph

**Privacy-first professional network for the sports industry**

CrowdBiz Graph maps NFL professionals and organizations without storing private contact information. Built with Streamlit and Supabase.

## 🚀 Quick Start

```bash
git clone https://github.com/tinusleroux/crowdbiz_graph.git
cd crowdbiz_graph
pip install -r requirements.txt
cp .env.example .env  # Add your Supabase credentials
python run.py streamlit
```

Visit http://localhost:8502

## 📚 Documentation

- **[📖 Documentation Hub](docs/README.md)** - Complete documentation
- **[🤖 AI Development Guide](AI_AGENT_README.md)** - For AI coding agents
- **[🔒 Privacy & Compliance](docs/user-guide/overview.md)** - User guide and privacy

## 🎯 What We Track ✅ / Don't Store ❌

✅ Professional names and titles • Organization affiliations • LinkedIn profiles • Career progression  
❌ Email addresses • Phone numbers • Home addresses • Personal information

## 🏗️ Architecture

**Streamlit-first, privacy-by-design**:
- Direct Supabase database access
- Automatic PII filtering at every layer
- Modular structure: `app/core/`, `app/services/`, `app/ui/`

---

**Status**: Production Ready | **Privacy**: Zero PII Storage | **Architecture**: Streamlit + Supabase
