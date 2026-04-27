# OrgGPT - Unified RAG System with Datadog Integration
## Production-Ready Intelligent Knowledge Base

---

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-success.svg)

**Unified Knowledge Base with Vector Search & LLM Integration**

[Quick Start](#-quick-start) • [Features](#-key-features) • [Architecture](#-system-architecture) • [Documentation](#-documentation)

</div>

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.template .env

# Edit and add your API keys
nano .env
```

Add to `.env`:
```bash
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

### 2. Build Unified Index
```bash
source .venv/bin/activate
python3 index_builder.py
```

### 3. Start Application
```bash
uvicorn app_api:app --reload --port 8001
```

### 4. Open Browser
**Go to:** http://localhost:8001/

🎉 **That's it!** Start asking questions about your APIs, services, and SLOs!

---

## 📚 Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick reference guide | All users - Start here! |
| **[README.md](README.md)** | Complete documentation | Developers, DevOps |
| **[CLEANUP_COMPLETE.md](CLEANUP_COMPLETE.md)** | Architecture cleanup notes | Developers |

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [Installation](#-installation)
6. [Usage](#-usage-guide)
7. [API Documentation](#-api-documentation)
8. [Monitoring](#-monitoring)
9. [Troubleshooting](#-troubleshooting)
10. [Development](#-development)

---

## 📊 Overview

**OrgGPT** is a production-ready Retrieval-Augmented Generation (RAG) system that provides a **unified interface** to query organizational knowledge through natural language.

### What is Unified Architecture?

Instead of maintaining separate collections for each data source, OrgGPT uses a **single unified collection** (`unified_knowledge`) that combines:

- 📝 **Swagger API Documentation** - All API endpoints, parameters, responses
- 📊 **Datadog Catalog** - Service entities and metadata
- 🎯 **Datadog SLOs** - Service Level Objectives and corrections

### Why Unified?

- ✅ **Simpler**: One collection, one endpoint, one interface
- ✅ **Smarter**: Cross-source insights and relationships
- ✅ **Faster**: Single query searches all sources
- ✅ **Easier**: No need to choose which source to query

### Business Value

- **⚡ Instant Access**: Natural language queries across all organizational knowledge
- **🎯 One Source of Truth**: All data in a single, searchable collection
- **🔒 POC Ready**: Demo capabilities without API credentials
- **📊 Observable**: Real-time monitoring dashboard
- **🐳 Production Ready**: Docker or local deployment

---

## ✨ Key Features

### 1. Unified Knowledge Base

**One Collection for Everything:**
```
unified_knowledge
├── 📝 Swagger API Documentation (~100+ documents)
├── 📊 Datadog Catalog Entities (~2+ documents)
└── 🎯 Datadog SLO Definitions (variable)
```

**Benefits:**
- ✅ Single query searches all sources
- ✅ Cross-source insights and relationships
- ✅ No need to choose which source to query
- ✅ Simpler architecture and maintenance

### 2. Intelligent Query Processing

- **Natural Language**: Ask questions in plain English
- **Context-Aware**: LLM understands your intent
- **Smart Retrieval**: Vector similarity search finds relevant docs
- **Source Attribution**: Know where answers come from

### 3. Multiple Deployment Options

| Mode | Use Case | Setup | Data Storage |
|------|----------|-------|--------------|
| **Local** | Development | No Docker needed | `./chroma_db/` |
| **Docker** | Production | Docker Compose | `./chroma_data/` |
| **POC** | Demo | No API keys needed | Local or Docker |

### 4. Production Ready

- ✅ **Monitoring**: Real-time dashboard at `/monitor`
- ✅ **Health Checks**: `/health` endpoint
- ✅ **Error Handling**: Graceful failures
- ✅ **Logging**: Comprehensive logs
- ✅ **Persistence**: Data survives restarts

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web UI     │  │  REST API    │  │  Monitor UI  │         │
│  │ (chat.html)  │  │  (FastAPI)   │  │ (Monitoring) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      FASTAPI APPLICATION             │
          │   ┌────────────────────────────┐    │
          │   │   RAG Engine (LLM Layer)   │    │
          │   │  - Query Processing        │    │
          │   │  - Context Retrieval       │    │
          │   │  - LLM Integration         │    │
          │   └────────┬───────────────────┘    │
          │            │                         │
          │   ┌────────▼───────────────────┐    │
          │   │   Vector Store Manager     │    │
          │   │  - unified_knowledge       │    │
          │   │  - Embedding Search        │    │
          │   └────────┬───────────────────┘    │
          └────────────┼────────────────────────┘
                       │
          ┌────────────▼────────────────────────┐
          │     CHROMADB (Vector Database)      │
          │      Local or Docker Container       │
          │                                      │
          │  ┌──────────────────────────────┐   │
          │  │   unified_knowledge          │   │
          │  │  - Swagger (100+ docs)       │   │
          │  │  - Datadog Catalog (2+ docs) │   │
          │  │  - Datadog SLO (variable)    │   │
          │  └──────────────────────────────┘   │
          │                                      │
          │   All sources in ONE collection!     │
          └──────────────────────────────────────┘
```

### Data Flow

```
User Query ("What APIs are available?")
       │
       ▼
┌──────────────────────────────────────────┐
│  1. Web Interface (chat.html)            │
│     └─ POST /query                       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  2. FastAPI Endpoint                     │
│     └─ app_api.py                        │
│        Receives query                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  3. RAG Engine                           │
│     └─ rag_engine.py                     │
│        Creates query embedding           │
│        Model: all-MiniLM-L6-v2           │
│        Output: 384-dim vector            │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  4. Vector Search                        │
│     └─ VectorStore.search()              │
│        ChromaDB.query()                  │
│        Collection: unified_knowledge     │
│        Returns: Top 3 relevant docs      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  5. Context Assembly                     │
│     └─ Concatenate matched documents     │
│        Add metadata                      │
│        Format for LLM                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  6. LLM Processing                       │
│     └─ OpenAI API / Groq                 │
│        Model: GPT-4 or Llama 3.3         │
│        Prompt: Question + Context        │
│        Temperature: 0.7                  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  7. Response Formation                   │
│     └─ Format answer                     │
│        Add source metadata               │
│        Return JSON                       │
└──────┬───────────────────────────────────┘
       │
       ▼
    Answer to User
```

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | Latest | Web framework |
| **Uvicorn** | Latest | ASGI server |
| **ChromaDB** | Latest | Vector database |
| **OpenAI** | GPT-4 / Groq | Language model |
| **Sentence Transformers** | all-MiniLM-L6-v2 | Embeddings |

### Frontend

| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | User interface |
| **JavaScript** | Interactive features |
| **Jinja2** | Template engine |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker (optional) | ChromaDB hosting |
| **Orchestration** | Docker Compose | Multi-container management |
| **Storage** | Local or Volumes | Data persistence |

---

## 💻 Installation

### Prerequisites

- Python 3.11+
- pip
- Docker (optional, for production)
- OpenAI API key or Groq API key

### Step 1: Clone Repository

```bash
git clone https://github.com/karthaveerya-droid/Orgpt.git
cd Orgpt
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.template .env
nano .env  # Edit with your API keys
```

**Required in `.env`:**
```bash
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

### Step 5: Build Unified Index

```bash
python3 index_builder.py
```

### Step 6: Start Application

```bash
uvicorn app_api:app --reload --port 8001
```

### Step 7: Access Application

Open http://localhost:8001 in your browser!

---

## 📖 Usage Guide

### Building the Index

```bash
# Default: Build unified index with POC mode (no API keys needed)
python3 index_builder.py

# Unified with API mode (requires Datadog API keys)
python3 index_builder.py unified

# Unified with POC mode (explicit)
python3 index_builder.py unified --poc
```

### Starting the Server

```bash
# Development mode (auto-reload on file changes)
uvicorn app_api:app --reload --port 8001

# Production mode
uvicorn app_api:app --host 0.0.0.0 --port 8001

# Background mode
nohup uvicorn app_api:app --port 8001 > server.log 2>&1 &
```

### Using the Web Interface

1. Open http://localhost:8001
2. Type your question in the input box
3. Press "Send" or hit Enter
4. View the AI-generated answer

**Example queries:**
- "What API endpoints are available?"
- "List all Datadog services"
- "What are our SLO targets?"
- "How do I authenticate to the API?"

---

## 🔌 API Documentation

### POST /query

**Main query endpoint** - Search the unified knowledge base.

**Request:**
```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What APIs are available?"
```

**Response:**
```json
{
  "answer": "Based on the documentation, the following APIs are available...",
  "source": "unified_knowledge",
  "source_name": "Unified Knowledge Base",
  "source_icon": "🔍",
  "note": "Unified search across all data sources"
}
```

### POST /chat

**Alias for /query** - Same functionality, different endpoint name.

### GET /health

**Health check endpoint** - Verify server is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Orgpt Swagger Agent is running."
}
```

### GET /monitor

**Monitoring dashboard** - Visual interface showing ChromaDB status, collections, and document counts.

### GET /chromadb/status

**ChromaDB status API** - Detailed status information.

**Response:**
```json
{
  "docker": {
    "running": true,
    "health": "Healthy"
  },
  "connection": {
    "success": true,
    "type": "HTTP (localhost:8000)",
    "heartbeat": "1234567890"
  },
  "collections": [
    {
      "name": "unified_knowledge",
      "count": 103
    }
  ],
  "total_documents": 103
}
```

---

## 📊 Monitoring

### Web Dashboard

Access the monitoring dashboard at http://localhost:8001/monitor

**Features:**
- ChromaDB connection status
- Docker container health
- Collection statistics
- Document counts
- Real-time updates

### Command Line

```bash
# Check collection size
python3 -c "
from vector_store.store import VectorStore
vs = VectorStore('unified_knowledge')
print(f'Documents: {vs.collection.count()}')
"

# Check server health
curl http://localhost:8001/health

# Check ChromaDB (if using Docker)
docker-compose ps
docker-compose logs chromadb
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Collection not found"** | Build index: `python3 index_builder.py` |
| **"Could not connect to ChromaDB"** | Check if Docker is running: `docker-compose ps` |
| **"LLM_MODEL must be set"** | Add `LLM_MODEL` to `.env` file |
| **Empty/no results** | Rebuild index: `python3 index_builder.py` |
| **500 Internal Server Error** | Check logs: `tail -f server.log` |
| **Slow queries** | Restart ChromaDB: `docker-compose restart chromadb` |

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true

# Run with verbose output
uvicorn app_api:app --reload --port 8001 --log-level debug
```

### Reset Database

```bash
# Stop application
pkill -f uvicorn

# Remove local database
rm -rf chroma_db/

# Rebuild index
python3 index_builder.py

# Restart app
uvicorn app_api:app --reload --port 8001
```

---

## 👨‍💻 Development

### Project Structure

```
Orgpt/
├── app_api.py              # Main FastAPI application
├── index_builder.py        # Unified index builder
├── main.py                 # CLI interface
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (not in git)
├── .env.template           # Template for .env
├── docker-compose.yml      # Docker setup
│
├── templates/              # Web interfaces
│   ├── chat.html          # Main chat interface
│   └── chromadb_monitor.html
│
├── ingestion/             # Data connectors
│   ├── base_connector.py  # Base interface
│   ├── Swagger_connector/
│   ├── Datadog_connector/
│   └── Document_connector/
│
├── processing/            # NLP pipeline
│   ├── chunker.py        # Text chunking
│   └── embedder.py       # Embeddings
│
├── retrieval/            # RAG engine
│   └── rag_engine.py    # Query processing
│
├── vector_store/        # Database layer
│   └── store.py        # ChromaDB interface
│
└── llm/                # LLM integration
    └── llm_layer.py   # OpenAI/Groq wrapper
```

### Adding New Data Sources

1. Create connector in `ingestion/`:
```python
from ingestion.base_connector import DataSourceConnector

class MyConnector(DataSourceConnector):
    def get_source_name(self) -> str:
        return "my_source"
    
    def extract_documents(self) -> List[str]:
        # Your extraction logic
        return documents
    
    def get_metadata(self) -> Dict[str, Any]:
        return {"source_type": "my_source"}
```

2. Register in `index_builder.py`:
```python
builder = IndexBuilder()
builder.register_connector(MyConnector())
builder.build_unified_index()
```

### Running Tests

```bash
# Test Datadog Catalog connector
python3 test_datadog_catalog.py

# Test Datadog SLO connector
python3 test_datadog_slo.py

# Test Swagger connector
python3 test_swagger_connector.py
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/karthaveerya-droid/Orgpt/issues
- Documentation: [QUICKSTART.md](QUICKSTART.md)

---

**Made with ❤️ by the OrgGPT Team**
