# CrowdBiz Graph - Sports Industry Professional Network Map

## Vision Statement

Build the **sports industry's living map**: a structured, explainable graph of people, roles, and organizations across teams, leagues, agencies, vendors, and sponsors. Unlike LinkedIn or generic databases, CrowdBiz provides **contextual industry intelligence** without exposing private contact data.

## Privacy-First Approach

🔒 **No Private Contact Information**
- No emails, phone numbers, or private communications stored
- Only **public professional data**: names, titles, organizations, LinkedIn profiles
- Users control visibility at personal, company, and public graph levels
- Shifts narrative from "data mining" to "industry collaboration"

## Overview

# 🏈 CrowdBiz Graph

**Sports Industry Intelligence Platform**  
A comprehensive AI-powered system for mapping professional networks and relationships in the sports industry.

## 🚀 Overview

CrowdBiz Graph is a modern, modular platform that helps professionals in the sports industry discover, analyze, and leverage professional networks. Built with privacy-first principles and AI-friendly architecture.

### Key Features

- **🔍 Intelligent Search**: Search across contacts, companies, and industry articles
- **📊 Network Analytics**: Comprehensive relationship mapping and insights
- **📥 Data Import**: Privacy-compliant CSV import with automatic PII filtering
- **🤖 AI Integration**: OpenAI-powered search and content analysis
- **🔒 Privacy-First**: Built-in PII detection and data protection
- **📈 Dashboard**: Real-time insights and network visualization

## 🏗️ Architecture

### Modern Modular Design
```
app/
├── core/        # Business logic and models
├── services/    # High-level business services
├── ui/         # Streamlit interface components
└── api/        # FastAPI REST endpoints
```

### Technology Stack
- **Frontend**: Streamlit (Interactive web application)
- **Backend**: FastAPI (REST API service)
- **Database**: Supabase PostgreSQL
- **AI**: OpenAI API integration
- **Privacy**: Custom PII filtering and compliance
- **Data**: Pandas, CSV processing with validation

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Supabase account and project
- OpenAI API key (optional, for AI features)

### Setup
```bash
# Clone the repository
git clone https://github.com/tinusleroux/crowdbiz_graph.git
cd crowdbiz_graph

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials

# Run the application
python run.py streamlit
```

### Environment Variables
```env
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key  # Optional
```

## 🚀 Usage

### Starting the Application
```bash
# Start main Streamlit application
python run.py streamlit

# Start FastAPI service (optional)
python run.py api

# Run validation checks
python run.py checks

# Run tests
python run.py tests
```

### Web Interface
- **Dashboard**: Overview of network data and insights
- **Search**: Find contacts, companies, or articles
- **Import**: Upload CSV files with privacy filtering
- **Analytics**: Relationship analysis and reporting
- **Database Explorer**: Direct data exploration

### API Endpoints
- `GET /search` - Search across all entities
- `GET /contacts` - Contact management
- `GET /companies` - Company information
- `GET /analytics` - Network insights
- `POST /import` - Data import with validation

## 🔒 Privacy & Compliance

### Built-in Privacy Protection
- **PII Detection**: Automatic identification of sensitive data
- **Data Redaction**: Configurable privacy filtering levels
- **Audit Trails**: Complete logging of data access and modifications
- **Compliance**: GDPR and privacy regulation adherence

### Privacy Levels
- **MINIMAL**: Basic PII filtering
- **MODERATE**: Enhanced privacy protection
- **STRICT**: Maximum privacy compliance
- **CUSTOM**: Configurable privacy rules

## 🤖 AI Development Support

This project includes comprehensive AI development guidance:

- **`.ai_constraints/`**: Development guidelines and coding standards
- **`.ai_context/`**: Business context and domain knowledge
- **`dev_workspace/`**: AI agent sandbox for experimentation
- **`AI_AGENT_README.md`**: Detailed AI development instructions

### AI-Friendly Features
- Clear module separation and interfaces
- Comprehensive logging and debugging
- Privacy-compliant AI integration
- Modular architecture for easy extension

## 📊 Data Management

### Supported Data Types
- **Contacts**: Professional network connections
- **Companies**: Organization information and relationships
- **Articles**: Industry news and content analysis
- **Events**: Professional gatherings and networking opportunities

### Import Features
- CSV file processing with validation
- Automatic data cleaning and normalization
- Privacy filtering during import
- Duplicate detection and merging
- Error reporting and correction suggestions

## 🧪 Development

### Project Structure
```
crowdbiz_graph/
├── app/                    # Main application code
│   ├── core/              # Business logic
│   ├── services/          # Business services
│   ├── ui/               # Streamlit components
│   └── api/              # FastAPI endpoints
├── .ai_constraints/       # AI development guidelines
├── .ai_context/          # AI business context
├── dev_workspace/        # AI development sandbox
├── docs/                 # Documentation
├── imports/              # CSV import files
├── logs/                 # Application logs
├── scripts/              # Utility scripts
├── supabase/            # Database migrations
├── tests/               # Test suite
└── run.py               # Unified entry point
```

### Development Workflow
1. Review AI development guidelines in `.ai_constraints/`
2. Use modular architecture patterns
3. Maintain privacy-first principles
4. Follow logging and error handling standards
5. Test using `python run.py tests`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Follow the AI development guidelines
4. Ensure privacy compliance
5. Add tests for new features
6. Submit a pull request

## 📈 Analytics & Insights

### Network Analysis
- Relationship mapping and strength scoring
- Influence and centrality metrics
- Community detection and clustering
- Professional pathway analysis

### Business Intelligence
- Industry trend analysis
- Company relationship insights
- Professional network growth tracking
- Event impact measurement

## 🔧 Maintenance

### Regular Tasks
```bash
# Run all validation checks
python run.py checks

# Database maintenance
python scripts/maintenance/data_quality_analysis.py

# Privacy compliance audit
python scripts/maintenance/privacy_audit.py
```

### Monitoring
- Application performance metrics
- Privacy compliance status
- Data quality indicators
- User activity analytics

## 📚 Documentation

- **[Architecture Guide](docs/architecture/overview.md)**: System design and components
- **[Database Schema](docs/architecture/database-schema.md)**: Data structure and relationships
- **[AI Development](AI_AGENT_README.md)**: AI agent development guide
- **[Privacy Guide](docs/privacy/compliance.md)**: Privacy and compliance details

## 🆘 Support

### Getting Help
- Check the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- Review the [Migration Summary](MIGRATION_SUMMARY.md)
- Consult the AI development guidelines

### Issues and Bugs
Please report issues on the [GitHub Issues page](https://github.com/tinusleroux/crowdbiz_graph/issues).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern privacy-first principles
- Designed for AI-assisted development
- Optimized for sports industry professionals
- Community-driven feature development

---

**CrowdBiz Graph** - Empowering sports industry professionals with intelligent network insights.

*For AI agents: Comprehensive development guidance available in `.ai_constraints/` and `AI_AGENT_README.md`*

## 🚀 Quick Start

**Your platform is ready with 2,990+ NFL professional records!**

### 1. Start the Web Interface
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the web UI
streamlit run ui.py
```

### 2. Start the API Server
```bash
# Launch the API
python api_simple.py

# View API documentation
open http://localhost:8000/docs
```

### 3. Verify Your Data
```bash
# Check NFL data status
python check_nfl_status.py
```

## Architecture

### Core Components

1. **Web Interface** (`ui.py`)
   - Streamlit-based dashboard and search interface
   - Professional data import and management (no private contact info)
   - Analytics and visualization
   - Direct Supabase integration

2. **API Layer** (`api_simple.py`)
   - FastAPI-based REST API with Supabase client
   - Search endpoints for people, organizations, and roles
   - Analytics endpoints for insights and statistics
   - Privacy-compliant data handling

3. **Database Layer** (Supabase/PostgreSQL)
   - Professional profile management with relationship mapping
   - Organization and role tracking with temporal data
   - Full-text search capabilities
   - Automated relationship detection

4. **Data Processing** (`check_nfl_status.py`)
   - Data validation and quality assurance
   - Automated deduplication and relationship detection
   - Status verification and reporting

## Database Schema

### Core Tables

#### `people`
- Primary professional profiles with public information only
- LinkedIn profiles and public social media
- AI-generated insights from public data

#### `organizations`
- Sports teams, leagues, and related entities
- Geographic and structural information
- Website and social media presence

#### `roles`
- Position history and current assignments
- Department and hierarchy information
- Temporal tracking of role changes

#### `relationships`
- Professional connections between individuals
- Organizational relationships
- Network analysis support

#### `news_items`
- Industry news and announcements
- Personnel changes and moves
- Event coverage and insights

### Specialized Tables

#### `events`
- Industry conferences and networking events
- Attendee tracking and relationship mapping

#### `articles`
- Research articles and industry analysis
- Source attribution and relevance scoring

## Installation & Setup

### Prerequisites

- Python 3.8+
- Supabase account and project
- Required environment variables:
  - `SUPABASE_URL`
  - `SUPABASE_API_KEY`
  - `OPENAI_API_KEY` (optional)
  - `GEMINI_API_KEY` (optional)

### Installation Steps

1. **Clone and Setup Environment**
   ```bash
   git clone https://github.com/tinusleroux/crowdbiz_db.git
   cd crowdbiz_db
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Start the Web Interface**
   ```bash
   streamlit run ui.py
   ```

5. **Start the API Server** (in another terminal)
   ```bash
   python api_simple.py
   ```

## Usage Guide

### Web Interface

Access the comprehensive web dashboard at `http://localhost:8501` (after running `streamlit run ui.py`):

- **Dashboard**: Overview of your data with key metrics
- **Search**: Advanced search across people, organizations, and roles
- **Import Professional Data**: CSV upload with column mapping (LinkedIn URLs, names, organizations only)
- **Analytics**: Visual insights and role change tracking
- **Database Explorer**: Direct data exploration via API

### API Usage

Access the REST API at `http://localhost:8000` (after running `python api_simple.py`):

```bash
# Get all people
curl http://localhost:8000/people

# Search organizations
curl "http://localhost:8000/search/organizations?query=broncos"

# Get analytics
curl http://localhost:8000/analytics/organizations/stats
```

View interactive API documentation at `http://localhost:8000/docs`

### Data Import

#### Importing Professional Data
- Use the web interface's "Import Contacts" page for all CSV uploads
- Maps columns to database fields automatically (names, titles, organizations, LinkedIn URLs only)
- Validates data during import process
- **No private contact information accepted** (email/phone fields ignored)

#### NFL Data Verification
```bash
# Check current NFL data status
python check_nfl_status.py
```

#### Search Endpoints
```python
import requests

# Search for people
response = requests.get("http://localhost:8000/search", params={
    "q": "head coach",
    "type": "person",
    "limit": 10
})

# Search organizations
response = requests.get("http://localhost:8000/organizations", params={
    "league": "NFL",
    "state": "TX"
})
```

#### Analytics
```python
# Get organization statistics
response = requests.get("http://localhost:8000/analytics/organizations/stats")

# Role change analysis
response = requests.get("http://localhost:8000/analytics/roles/changes", params={
    "days": 90
})
```

## Data Sources

### Current Datasets

1. **NFL Personnel (2,395+ records)**
   - Team rosters and front office staff
   - Coaching staff hierarchies
   - Historical role tracking

2. **Team Directory (237 teams)**
   - Major league coverage (NFL, NBA, MLB, NHL, MLS)
   - Geographic distribution
   - Website and contact information

3. **Event Attendees**
   - Industry conference participation
   - Networking event tracking
   - Professional association memberships

### Data Quality

- **Validation Rules**: LinkedIn URL format, name completeness validation
- **Deduplication**: Name similarity matching, LinkedIn URL uniqueness
- **Relationship Detection**: Organizational connections, role progressions
- **Completeness Scoring**: Professional data richness assessment per record
- **Privacy Compliance**: Automatic filtering of private contact information

## AI Integration

### OpenAI Integration
- Professional profile enrichment from public data
- Natural language search capabilities
- Automated relationship detection from public information
- Content summarization for news/articles

### Gemini Integration
- Large-scale public data research and collection
- Industry trend analysis from public sources
- Personnel move prediction based on public announcements
- Market intelligence from public information

## Monitoring & Analytics

### Key Metrics

1. **Data Quality Metrics**
   - Record completeness scores
   - Validation success rates
   - Duplicate detection statistics
   - Relationship mapping accuracy

2. **Usage Analytics**
   - API endpoint usage patterns
   - Search query analysis
   - Export frequency and types
   - User engagement metrics

3. **Growth Tracking**
   - New record additions
   - Data source expansion
   - Coverage improvements
   - Industry trend identification

### Logging

All operations are logged with structured JSON format:
```json
{
  "timestamp": "2024-12-19T10:30:00Z",
  "level": "INFO",
  "operation": "data_import",
  "source": "nfl_personnel.csv",
  "records_processed": 150,
  "success_count": 147,
  "error_count": 3,
  "duration_seconds": 12.5
}
```

## API Reference

### Endpoints

#### People
- `GET /people` - List people with filtering
- `GET /people/{id}` - Get person details
- `POST /people` - Create new person
- `PUT /people/{id}` - Update person
- `DELETE /people/{id}` - Delete person

#### Organizations
- `GET /organizations` - List organizations
- `GET /organizations/{id}` - Get organization details
- `GET /organizations/{id}/people` - Get organization members

#### Roles
- `GET /roles` - List roles with filtering
- `GET /roles/changes` - Track role changes
- `GET /roles/analytics` - Role analytics

#### Search
- `GET /search` - Universal search
- `GET /search/suggestions` - Search suggestions
- `GET /search/advanced` - Advanced search with filters

#### Analytics
- `GET /analytics/organizations/stats` - Organization statistics
- `GET /analytics/people/network` - Network analysis
- `GET /analytics/trends` - Industry trends

### Authentication

API uses JWT tokens for authentication:
```python
headers = {
    "Authorization": "Bearer <your_jwt_token>",
    "Content-Type": "application/json"
}
```

## Development

### Code Structure

```
crowdbiz_db/
├── api_simple.py          # FastAPI application with Supabase client
├── ui.py                  # Streamlit web interface
├── config.py              # Configuration management
├── logger.py              # Logging system
├── check_nfl_status.py    # Database status verification
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (private)
├── .env.example          # Environment template
├── supabase/             # Database migrations and config
│   ├── config.toml       # Supabase configuration
│   └── migrations/       # SQL migration files
├── imports/              # CSV import data files
│   ├── people_nfl_gemini_ui.csv    # NFL personnel data
│   ├── team_staff_gemini.csv       # Team staff data
│   ├── team_staff_openai.csv       # Additional staff data
│   ├── NSF 2025 Attendee Roster.csv # Event attendees
│   └── client_forum_invite_contacts.csv # Forum contacts
└── logs/                 # Application logs
```

### Contributing

1. Fork the repository from https://github.com/tinusleroux/crowdbiz_db
2. Create a feature branch
3. Test your changes with the verification steps above
4. Submit a pull request with clear description of changes

## Current Status

### Data Loaded ✅
- **2,990+ NFL Professional Profiles**: Complete professional records with roles and organizations
- **33 NFL Teams**: All teams with organizational structure  
- **1,000+ Roles**: Historical and current position tracking
- **363 Organizations**: Teams, leagues, and related entities

### Privacy Compliance ✅
- **No Private Contact Data**: Email/phone fields removed from database
- **Public Data Only**: Names, titles, organizations, LinkedIn profiles
- **User Control**: Transparent data practices and user consent
- **Industry Collaboration**: Value-focused networking without data mining

### Features Available ✅
- **Web Interface**: Full-featured dashboard with search and analytics
- **REST API**: Complete API with documentation at `/docs`
- **Search**: Fast text search across all entities
- **Analytics**: Role change tracking and organizational insights
- **Data Import**: CSV upload with automatic column mapping (via web interface)

### Repository
- **GitHub**: https://github.com/tinusleroux/crowdbiz_db
- **Commits**: Clean codebase with 3 successful commits
- **Structure**: Minimal, focused file organization

## Testing

To verify your platform is working correctly:

1. **Test API Connection**
   ```bash
   # Check if API is running
   curl http://localhost:8000/health
   ```

2. **Test Database Connection**
   ```bash
   # Verify NFL data
   python check_nfl_status.py
   ```

3. **Test Web Interface**
   - Navigate to `http://localhost:8501`
   - Check that dashboard loads with statistics
   - Try searching for "broncos" or "cowboys"
